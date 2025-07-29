from datetime import datetime, timedelta
from typing import List, Union, Optional, Literal

def to_datetime(values: Union[str, List[str]], fmt: str = None) -> Union[datetime, List[datetime]]:
    """Convert a string or list of strings to datetime objects.

    Parameters:
        value (str | list[str]): The string or list of strings to convert.
        fmt (str): Optional format string for parsing.

    Returns:
        datetime | list[datetime]: A single datetime object if a string is provided,
                                    or a list of datetime objects if a list is provided.

    Example usage:
    >>> tx.to_datetime("2023-10-01")
    datetime.datetime(2023, 10, 1, 0, 0)

    >>> tx.to_datetime(["2023-10-01", "2023-10-02"])
    [datetime.datetime(2023, 10, 1, 0, 0), datetime.datetime(2023, 10, 2, 0, 0)]


    """
    from .series import Series
    def parse_single(val: str) -> datetime:
        if fmt:
            return datetime.strptime(val, fmt)
        else:
            # automatic fallback using fromisoformat or common formats
            try: 
                if isinstance(val,str):
                    return datetime.fromisoformat(val)
                elif isinstance(val, datetime):
                    return val
                else:
                    return datetime(val)
            except ValueError:
                for trial_fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d-%M-%Y", "%Y/%m/%d"):
                    try:
                        return datetime.strptime(val, trial_fmt)
                    except ValueError:
                        continue
                raise ValueError(f"Cannot parse date: {val}")
    
    if isinstance(values, str):
        return parse_single(values)
    elif isinstance(values, list):
        return [parse_single(val) for val in values]
    elif isinstance(values, Series):
        return [parse_single(val) for val in values]
    else:
        raise TypeError(f"Input must be a string or a list of strings. found type: {type(values)}")
    
def date_range(
        start: Union[str, datetime],
        end: Optional[Union[str, datetime]] = None,
        periods: Optional[int] = None,
        freq: Literal['D', 'H' 'T', 'min', 'S'] = 'D',
        fmt: Optional[str] = None
)-> List[datetime]:
    """Generate a list of datetime values.

    Parameters:
        start (str | datetime): Start date.
        end (str | datetime): End date Required is 'periods' is not specified.
        periods (int): Number of periods to generate. Required if 'end is not specified
        freq (str): Frequency string ('D'/day, 'H'/hour, 'T'/min, 'min'/min, 'S'/second).
        fmt (str): Optional format string for parsing.

    Returns:
        list[datetime]: List of datetime objects.

    Example usage:
    >>> tx.date_range("2023-10-01", "2023-10-10", freq='D')
    [datetime.datetime(2023, 10, 1, 0, 0), datetime.datetime(2023, 10, 2, 0, 0), ...]   

    >>> tx.date_range("2023-10-01", periods=5, freq='D')
    [datetime.datetime(2023, 10, 1, 0, 0), datetime.datetime(2023, 10, 2, 0, 0), ...]

    

    """
    def parse_date(val):
        if isinstance(val, datetime):
            return val
        elif isinstance(val, str):
            if fmt:
                return datetime.strptime(val, fmt)
            else:
                return datetime.fromisoformat(val)
        else:
            raise TypeError("Start and end must be strings or datetime objects.")
        
    start_dt = parse_date(start)

    delta_map = {
        'D': timedelta(days=1),
        'H': timedelta(hours=1),
        'T': timedelta(minutes=1),
        'min': timedelta(minutes=1),
        'S': timedelta(seconds=1)
    }

    if freq not in delta_map:
        raise ValueError(f"Unsupported frequency: {freq}. Supported frequencies are: {list(delta_map.keys())}")
    
    delta = delta_map[freq]

    if end is not None:
        end_dt = parse_date(end)
        result = []
        current = start_dt
        while current <= end_dt:
            result.append(current)
            current += delta
        return result
    elif periods is not None:
        return [start_dt + i * delta for i in range(periods)]
    else:
        raise ValueError("Either 'end' or 'periods' must be specified.")
    
def try_parse_date(d):
    """Try to parse a date string into a datetime object using multiple formats.

    Parameters:
        d (str): The date string to parse.
    
    Returns:
        datetime: The parsed datetime object.

    Example usage:
    >>> try_parse_date("2023-10-01")
    datetime.datetime(2023, 10, 1, 0, 0)
    """
    formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%b %d, %Y', '%d %b %Y']
    for fmt in formats:
        try:
            return datetime.strptime(d, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {d}. Supported formats are: {formats}")

class _DateTimeAccessor:
    def __init__(self, series):
        self.series = series

    def _convert(self, d, mode='date'):
        if isinstance(d, str):
            date = try_parse_date(d)
            if mode == 'date':
                return date.weekday()
            elif mode == 'day':
                return date.day
            elif mode == 'month':
                return date.month
            elif mode == 'year':
                return date.year
            
        elif isinstance(d, datetime):
            if mode == 'date':
                return d.weekday()
            elif mode == 'day':
                return d.day
            elif mode == 'month':
                return d.month
            elif mode == 'year':
                return d.year
        else:
            raise TypeError(f"Unsupported type for date: {type(d)}")   

    @property
    def day(self):
        """
        Get the day of the month for each date in the Series.
        
        Returns:
        Series: A new Series with the day of the month.
        """
        from .series import Series

        return Series([self._convert(d, mode='day') for d in self.series.data], 
                      name=f"{self.series.name}_day", 
                      index=self.series.index)

    @property
    def month(self):
        """
        Get the month for each date in the Series.
        
        Returns:
        Series: A new Series with the month (1-12).
        """
        from .series import Series

        return Series([self._convert(d, mode='month') for d in self.series.data], 
                      name=f"{self.series.name}_month", 
                      index=self.series.index)     
    
    @property
    def year(self):
        """
        Get the year for each date in the Series.
        
        Returns:
        Series: A new Series with the year.
        """
        from .series import Series

        return Series([self._convert(d, mode='year') for d in self.series.data], 
                      name=f"{self.series.name}_year", 
                      index=self.series.index)

    @property
    def weekday(self):
        """
        Get the weekday of each date in the Series.
        
        Returns:
        Series: A new Series with the weekday (0=Monday, 6=Sunday).
        """
        from .series import Series

        return Series([self._convert(d) for d in self.series.data], 
                      name=f"{self.series.name}_weekday", 
                      index=self.series.index) 

    @property
    def is_weekend(self):
        """
        Check if each date in the Series is a weekend (Saturday or Sunday).
        
        Returns:
        Series: A new Series with int values indicating if the date is a weekend (1=yes, 0=no).
        """
        from .series import Series

        return Series([self._convert(d) >= 5 for d in self.series.data], 
                      name=f"{self.series.name}_is_weekend", 
                      index=self.series.index) 