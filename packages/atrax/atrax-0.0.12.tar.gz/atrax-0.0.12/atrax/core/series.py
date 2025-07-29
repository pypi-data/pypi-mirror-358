from datetime import datetime
from collections import Counter
from .rolling import RollingSeries
from .locators import _Iloc, _Loc
from .customdatetime import _DateTimeAccessor


class Series:

    @property
    def iloc(self):
        """
        Provides integer-location based indexing for the Series.

        Allows access to elements by their integer position, similar to how NumPy or pandas `iloc` works.

        Examples:
        >>> from atrax import Atrax as tx
                 
        >>> s = tx.Series([1, 2, 3], name='example', index=['a', 'b', 'c'])
        >>> s.iloc[0]
        1

        >>> s.iloc[1:3]
        b    2
        c    3
        Name: example, dtype: int

        >>> s = tx.Series([1,2,3,4,5,],  name="numbers", index=['a', 'b', 'c', 'd', 'e'])
        >>> s.iloc[1:4]
        b    2
        c    3
        d    4
        Name: numbers, dtype: int

        >>> s.iloc[::-1]
        e    5
        d    4
        c    3
        b    2
        a    1
        Name: numbers, dtype: int


        """
       
        return _Iloc(self)

    @property
    def loc(self):
        """Provides label-based indexing for the Series.
        Allows access to elements by their labels, similar to how pandas `loc` works.
        Examples:
        >>> from atrax import Atrax as tx
        >>> s = tx.Series([1, 2, 3], name='example', index=['a', 'b', 'c'])
        >>> s.loc['a']
        1
    
        >>> s.loc['b':'c']
        b    2
        c    3
        Name: example, dtype: int
        """
        return _Loc(self)
    
    @property
    def dt(self):
        """
        Provides datetime-like properties for the Series.
        
        Examples:
        >>> from atrax import Atrax as tx
        >>> test_data = [
            {
                'id': 1,
                'sale_date': '1/1/2025'
            },
            {
                'id': 2,
                'sale_date': '1/2/2025'
            },
            {
                'id': 3,
                'sale_date': '1/3/2025'
            }
        ]
        >>> ds = tx.DataSet(test_data)

        >>> ds['weekday'] = ds['sale_date'].dt.weekday
        >>> ds.head()
        id    sale_date    weekday
        1     1/1/2025     2
        2     1/2/2025     3
        3     1/3/2025     4


        >>> ds['is_weekend'] = ds['sale_date'].dt.is_weekend
        >>> ds.head()
        id    sale_date    weekday   is_weekend
        1     1/1/2025     2         False
        2     1/2/2025     3         False
        3     1/3/2025     4         False

        >>> ds['month'] = ds['sale_date'].dt.month
        >>> ds.head()
        id    sale_date    weekday   is_weekend   month
        1     1/1/2025     2         False        1
        2     1/2/2025     3         False        1
        3     1/3/2025     4         False        1

        >>> ds['day'] = ds['sale_date'].dt.day
        >>> ds.head()
        id    sale_date    weekday   is_weekend   month  day
        1     1/1/2025     2         False        1      1
        2     1/2/2025     3         False        1      2
        3     1/3/2025     4         False        1      3

        >>> ds['year'] = ds['sale_date'].dt.year
        >>> ds.head()
        id    sale_date    weekday   is_weekend   month  day  year
        1     1/1/2025     2         False        1      1    2025
        2     1/2/2025     3         False        1      2    2025
        3     1/3/2025     4         False        1      3    2025  


        """
        return _DateTimeAccessor(self)
    
    @property
    def values(self):
        """Returns the underlying data of the Series as a list.
        
        Examples:
        >>> from atrax import Atrax as tx
        >>> s = tx.Series([1, 2, 3], name='example', index=['a', 'b', 'c'])
        >>> s.values
        [1, 2, 3]
        
        >>> type(s.values)
        list"""
        return self.data

    @property
    def name(self):
        """Returns the name of the Series.

        Examples:
        >>> from atrax import Atrax as tx
        >>> s = tx.Series([1, 2, 3], name='example', index=['a', 'b', 'c'])
        >>> s.name
        'example'

        >>> s = tx.Series([1, 2, 3])
        >>> s.name
        ''
        """
        return self._name

    @name.setter
    def name(self, value):
        self._name = value    


    def __init__(self, data, name=None, index=None):
        """
        One-dimensional labeled array for Atrax.

        Parameters
        ----------
        data : list
            A list of values.


        name : str, optional
            The name of the series.
            defaults to None, which means no name is assigned.

        Examples
        --------
        >>> from atrax import Atrax as tx

        >>> s = tx.Series([1,2,3])
        0     1
        1     2
        2     3
        Name: , dtype: int

        >>> s = tx.Series([1, 2, 3, 4, 5], name='numbers', index=['a', 'b', 'c'])
        >>> s
        a     1
        b     2  
        c     3
        Name: numbers, dtype: int

        >>> s = tx.Series([1.0, 2.0, 3.0], name='example', index=['a', 'b', 'c'])
        a     1.0
        b     2.0
        c     3.0
        Name: example, dtype: float

        >>> s = tx.Series(['hello', 'goodbye', 'whatsup'])
        0     hello
        1     goodbye
        2     whatsup
        Name: , dtype: str

        >>> s = tx.Series([1, True, 'sexy', 2.5])
        0     1
        1     True
        2     sexy
        3     2.5
        Name: , dtype: object

        ##### this one is interesting and probably needs attention
        >>> s = tx.Series([True, False, True])
        0    True
        1    False
        2    True
        Name: , dtype: int        
        """
        self.data = data
        """Return the data as a list."""
        self.name = name or ""
        self.index = index or list(range(len(data)))
        """Return the index as a list of labels. If no index is provided, it defaults to a range of integers."""
        if len(self.data) != len(self.index):
            raise ValueError("Length of index must match length of data.")
        self.dtype = self._infer_dtype()
        """Return the data type of the Series based on the data provided."""

    def _infer_dtype(self):
        if all(isinstance(x, int) for x in self.data):
            return "int"
        elif all(isinstance(x, (int, float)) for x in self.data):
            return "float"
        elif all(isinstance(x, bool) for x in self.data):
            return "bool"
        elif all(isinstance(x, datetime) for x in self.data):
            return "datetime"
        elif all(isinstance(x, str) for x in self.data):
            return "str"
        else:
            return "object"

    def __repr__(self):
        lines = [f"{idx}   {val}" for idx, val in zip(self.index[:10], self.data[:10])]
        if len(self.data) > 10:
            lines.append(f"...({len(self.data)} total)")
        lines.append(f"Name: {self.name}, dtype: {self.dtype}")
        return "\n".join(lines)
    
    def __len__(self):
        """Get the number of elements in the Series."""
        return len(self.data)
    
    def __getitem__(self, i):
        """Get an item from the Series by index."""
        return self.data[i]
    
    def __gt__(self, other):
        result =  [x > other for x in self.data]
        return Series(result, name=f"({self.name} > {other})")
    
    
    def __lt__(self, other): 
        result =  [x < other for x in self.data]
        return Series(result, name=f"({self.name} < {other})")
    
    def __ge__(self, other):        
        result =  [x >= other for x in self.data]
        return Series(result, name=f"({self.name} >= {other})")
    
    def __le__(self, other):        
        result = [x <= other for x in self.data]
        return Series(result, name=f"({self.name} <= {other})")
    
    def __eq__(self, other):        
        result = [x == other for x in self.data]
        return Series(result, name=f"({self.name} == {other})")
    
    def __ne__(self, other):        
        result = [x != other for x in self.data]
        return Series(result, name=f"({self.name} != {other})")
    
    def _binary_op(self, other, op):
        if isinstance(other, Series):
            if len(other.data) != len(self.data):
                raise ValueError("Cannot perform operation: Series must have the same length.")
            return Series([op(a,b) for a,b in zip(self.data, other.data)], name=self.name)
        else:
            return Series([op(a, other) for a in self.data], name=self.name)

    def __add__(self, other): return self._binary_op(other, lambda a, b: a + b)
    def __sub__(self, other): return self._binary_op(other, lambda a, b: a - b)
    def __mul__(self, other): return self._binary_op(other, lambda a, b: a * b)
    def __truediv__(self, other): return self._binary_op(other, lambda a, b: a / b)
    def __floordiv__(self, other): return self._binary_op(other, lambda a, b: a // b)
    def __mod__(self, other): return self._binary_op(other, lambda a, b: a % b)
    def __pow__(self, other): return self._binary_op(other, lambda a, b: a ** b)

    def __and__(self, other):
        if not isinstance(other, Series):
            raise TypeError("Operand must be a Series.")
        if len(other.data) != len(self.data):
            raise ValueError("Cannot perform operation: Series must have the same length.")
        return Series([a and b for a,b in zip(self.data, other.data)], name=f"({self.name}) & {other.name}")
    
    def __or__(self, other):
        if not isinstance(other, Series):
            raise TypeError("Operand must be a Series.")
        if len(other.data) != len(self.data):
            raise ValueError("Cannot perform operation: Series must have the same length.")
        return Series([a or b for a, b in zip(self.data, other.data)], name=f"({self.name}) | {other.name}")

    def __invert__(self):
        return Series([not x for x in self.data], name=f"(~{self.name})")

    def head(self, n=5):
        """
        Return the first n elements of the Series.

        Parameters:
        n (int): The number of elements to return. Defaults to 5.


        Returns:
        Series: A new Series containing the first n elements.

        Example usage:
        >>> s = tx.Series([1, 2, 3, 4, 5])
        >>> print(s.head(3))
        0    1
        1    2
        2    3
        Name: , dtype: int
        """
        return Series(self.data[:n], name=self.name, index=self.index[:n])
    
    def tail(self, n=5):
        """
        Return the last n elements of the Series.

        Parameters:
        n (int): The number of elements to return. Defaults to 5.

        Returns:
        Series: A new Series containing the last n elements.

        Example usage:
        >>> s = tx.Series([1, 2, 3, 4, 5])
        >>> print(s.tail(3))
        2    3
        3    4 
        4    5 
        """
        return Series(self.data[-n:], name=self.name, index=self.index[-n:])
    
    def unique(self):
        """
        Return the unique values in the Series.

        Returns:
        Series: A new Series containing the unique values.

        Example usage:
        >>> s = tx.Series([1, 2, 2, 3, 4, 4])
        >>> unique_s = s.unique()
        >>> print(unique_s)
        0    1
        1    2
        2    3
        3    4
        Name: Unique(), dtype: int

        """
        unique_data = list(set(self.data))
        return Series(unique_data, name=f"Unique({self.name})", index=list(range(len(unique_data))))
    
    def nunique(self):
        """
        Return the number of unique values in the Series.

        Returns:
        int: The number of unique values.

        Example usage:
        >>> s = tx.Series([1, 2, 2, 3, 4, 4])
        >>> num_unique = s.nunique()
        >>> print(num_unique)
        4

        """
        return len(set(self.data))
    
    def isin(self, values):
        """
        Check if each element in the Series is in the provided list of values.

        Parameters:
        values (list): A list of values to check against.

        Returns:
        Series: A new Series containing boolean values indicating membership.

        Example usage:
        >>> s = tx.Series([1, 2, 3, 4, 5])
        >>> values = [2, 4, 6]
        >>> result = s.isin(values)
        >>> print(result)
        0     False
        1     True
        2     False
        3     True
        4     False
        Name: IsIn(), dtype: int
        """
        return Series([x in values for x in self.data], name=f"IsIn({self.name})", index=self.index)
    
    def between(self, left, right, inclusive=True):
        """
        Check if each element in the Series is between two values.

        Parameters:
        left (int/float): The lower bound.

        right (int/float): The upper bound.

        inclusive (bool): Whether to include the bounds. Defaults to True.

        Returns:
        Series: A new Series containing boolean values indicating if each element is between the bounds.

        Example usage:
        >>> s = tx.Series([1, 2, 3, 4, 5])
        >>> result = s.between(2, 4)
        >>> print(result)
        0     False
        1     True
        2     True
        3     True
        4     False
        Name: Between(, 2, 4), dtype: int
        """
        if inclusive:
            return Series([left <= x <= right for x in self.data], name=f"Between({self.name}, {left}, {right})")
        else:
            return Series([left < x < right for x in self.data], name=f"Between({self.name}, {left}, {right}, exclusive)")

    def to_list(self):
        """
        Convert the Series to a list.

        Returns:
        list: The data in the Series as a list.

        Example usage:
        >>> s = tx.Series([1, 2, 3])
        >>> lst = s.to_list()
        >>> print(lst)
        [1, 2, 3]

        """
        return self.data
    
    def apply(self, func):
        """Apply a function to each element in the Series.
        
        Parameters:
        func (function): A function to apply to each element.   
        
        Returns:
        Series: A new Series with the function applied to each element.
        
        Example usage:
        >>> s = tx.Series([1, 2, 3])
        >>> result = s.apply(lambda x: x * 2)
        >>> print(result)
        0    2
        1    4
        2    6
        Name: , dtype: int
        
        >>> def square(x):
        >>>     return x** 2
            
        >>> result = s.apply(square)   
        >>> result
        0    1
        1    4  
        2    9
        Name: , dtype: int
        """
        return Series([func(x) for x in self.data], name=self.name)
    
    
    def _repr_html_(self):
        """
        Return a string representation of the Series in HTML format.
        Returns:
        str: HTML representation of the Series.
        """
        html = "<table style='border-collapse: collapse;'>"
        for idx, val in zip(self.index[:10], self.data[:10]):
            html += f"<tr><td style=''>{idx}</td>"
            html += f"<td style=''>{val}</td></tr>"
        html += f"<tr><td colspan='2' style='font-size:16px;'><strong>Name: {self.name}, dtype: {self.dtype}<strong></td></tr>"
        if len(self.data) > 10:
            html += f"<tr><td colspan='2'><i>...{len(self.data) - 10} more</i></td></tr>"
        html += "</table>"
        return html 
    
    def to_datetime(self, format='%Y-%m-%d', errors='raise'):
        """
        Convert the Series to datetime objects.

        I think we need to look at the other to_datetime function as I think it is more robust.
        
        Parameters:

        format (str): The format of the date strings. Defaults to '%m/%d/%Y'.

        errors (str): 'raise' to throw errors, 'coerce' to return None on failure
        
        Returns:
        Series: A new Series with datetime objects.

        Example usage:
        >>> s = tx.Series(['2025-01-01', '2025-01-02', '2025-01-03'])
        >>> dt_series = s.to_datetime(format='%Y-%m-%d', errors='coerce')
        >>> print(dt_series)
        0    2025-01-01 00:00:00
        1    2025-01-02 00:00:00
        2    2025-01-03 00:00:00
        Name: , dtype: datetime
        """
        converted = []

        for val in self.data:
            if isinstance(val, datetime):
                converted.append(val)
            elif isinstance(val, str):
                try:
                    converted.append(datetime.strptime(val, format))
                except Exception as e:
                    if errors == 'coerce':
                        converted.append(None)
                    else:
                        raise ValueError(f"Failed to parse '{val}' as datetime: {e}")
            else:
                if errors == 'coerce':
                    converted.append(None)
                else:
                    raise ValueError(f"Unsupported type for to_datetime: {type(val)}")
        return Series(converted, name=self.name, index=self.index)
    
    def astype(self, dtype):
        """
        Convert the Series to a specified data type.
        
        Parameters:

        dtype (type): The Python type to cast to (e.g., int, float, str)
        
        Returns:

        Series: A new Series with the converted data type.

        Example usage:
        >>> s = tx.Series(['1', '2', '3'])
        >>> i_series = s.astype(int)
        >>> i_series
        0    1
        1    2
        2    3
        Name: , dtype: int

        >>> s = tx.Series(['1', '2', '3'])
        >>> i_series = s.astype('int')
        >>> i_series
        0    1
        1    2
        2    3
        Name: , dtype: int       

        >>> s = tx.Series(['1', '2', '3'])
        >>> f_series = s.astype('float')
        >>> f_series
        0    1.0
        1    2.0
        2    3.0
        Name: , dtype: float           
        """
        type_map = {
            "int": int,
            "float": float,
            "str": str,
            "object": lambda x: x
        }

        if isinstance(dtype, str):
            cast_fn = type_map.get(dtype)
            if cast_fn is None:
                raise ValueError(f"Unsupported dtype: {dtype}")
        else:
            cast_fn = dtype  # assume it's already a Python type

        new_data = []
        for val in self.data:
            try:
                new_data.append(cast_fn(val))
            except:
                new_data.append(None)

        return Series(new_data, name=self.name, index=self.index)
    
    def rolling(self, window):
        """
        Create a rolling window object for the Series.
        
        Parameters:

        window (int): The size of the rolling window.
        
        Returns:

        RollingSeries: A RollingSeries object for performing rolling operations.
        
        
        Example usage:
        >>> s = tx.Series([1, 2, 3, 4, 5])
        >>> rolling_s = s.rolling(window=3)
        >>> rolling_s.mean()
        0    None
        1    None
        2    2.0
        3    3.0
        4    4.0
        Name: rolling_series_rolling_mean, dtype: object
        
        """
        if not isinstance(window, int) or window <= 0:
            raise ValueError("Window size must be a positive integer.")
        return RollingSeries(self.data, window=window, name=self.name)
    
    def cut(self, bins=4, labels=None, precision=3, tie_breaker='upper'):
        """
        Bin the Series into discrete intervals.
        
        Parameters:

        bins (int): Number of bins to create. Defaults to 4.

        labels (list): Optional labels for the bins. If None, default labels will be used.
        
        precision (int): Number of decimal places for bin edges. Defaults to 3.
        
        tie_breaker (str): How to handle ties ('upper', 'lower', 'random'). Defaults to 'upper'.
        
        Returns:

        Series: A new Series with binned data.

        Example usage:
        >>> s = tx.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        >>> binned_s = s.cut(bins=3, labels=['Low', 'Medium', 'High'])
        >>> print(binned_s)
        0      Low
        1      Low
        2      Low
        3      Medium
        4      Medium
        5      Medium
        6      High
        7      High
        8      High
        9      High
        Name: dtype: str

        """
        if not self.data:
            return Series([], name=self.name, index=self.index)
        
        clean_data = [v for v in self.data if v is not None]
        min_val, max_val = min(clean_data), max(clean_data)

        if isinstance(bins, int):
            step = (max_val - min_val) / bins
            bin_edges = [round(min_val + i * step, precision) for i in range(bins + 1)]
        else:
            bin_edges = bins

        def assign_bin(val):
            if tie_breaker == 'lower' and val == bin_edges[0]:
                return labels[0] if labels else 0
            
            
            for i in range(len(bin_edges) - 1):
                left = bin_edges[i]
                right = bin_edges[i + 1]
                if tie_breaker == 'upper':
                    if left <= val < right:
                        return labels[i] if labels else i
                else:
                    if left < val <= right:
                        return labels[i] if labels else i
            if val == bin_edges[-1]:
                return labels[-1] if labels else len(bin_edges) - 2
            return None
        
        binned = [assign_bin(v) if v is not None else None for v in self.data]
        return Series(binned, name=self.name, index=self.index)
    
    def rank(self, method='average', ascending=True):
        """
        Compute numerical data ranks (1 through n) along the Series.
        
        Parameters:

        - method: {'average', 'min', 'max', 'first', 'dense'}, default 'average'
        
        - ascending: boolean, default True
        
        Returns:

        Series: A new Series with ranked values.

        Example usage:
        >>> s = tx.Series([3, 1, 2, 2, 4])
        >>> ranked_s = s.rank(method='average', ascending=True)
        >>> print(ranked_s)
        0    4.0
        1    1.0
        2    2.5
        3    2.5
        4    5.0
        Name: , dtype: float

        >>> s = tx.Series([3, 1, 2, 2, 4])
        >>> ranked_s = s.rank(method='min', ascending=True)
        >>> print(ranked_s)
        0    4
        1    1
        2    2
        3    2
        4    5
        Name: , dtype: int    

        >>> s = tx.Series([3, 1, 2, 2, 4])
        >>> ranked_s = s.rank(method='max', ascending=True)
        >>> print(ranked_s)
        0    4
        1    1
        2    3
        3    3
        4    5
        Name: , dtype: int  

        >>> s = tx.Series([3, 1, 2, 2, 4])
        >>> ranked_s = s.rank(method='first', ascending=True)
        >>> print(ranked_s)
        0    4
        1    1
        2    2
        3    3
        4    5
        Name: , dtype: int   

        >>> s = tx.Series([3, 1, 2, 2, 4])
        >>> ranked_s = s.rank(method='dense', ascending=True)
        >>> print(ranked_s)
        0    3
        1    1
        2    2
        3    2
        4    4
        Name: , dtype: int                           
        """
        values = self.data
        indexed = list(enumerate(values))

        if not ascending:
            indexed.sort(key=lambda x: -x[1])
        else:
            indexed.sort(key=lambda x: x[1])

        ranks = [0] * len(values)
        cur_rank = 1
        dense_rank = 1
        i = 0

        while i < len(indexed):
            j = i
            # find group of tied values
            while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
                j+= 1

            group = indexed[i:j + 1]
            indices = [idx for idx, _ in group]
            group_size = len(group)

            if method == 'average':
                avg_rank = sum(range(cur_rank, cur_rank + group_size)) / group_size
                for idx in indices:
                    ranks[idx] = avg_rank
            elif method == 'min':
                for idx in indices:
                    ranks[idx] = cur_rank
            elif method == 'max':
                for idx in indices:
                    ranks[idx] = cur_rank + group_size - 1
            elif method == 'first':
                for offset, (idx, _) in enumerate(group):
                    ranks[idx] = cur_rank + offset
            elif method == 'dense':
                for idx in indices:
                    ranks[idx] = dense_rank

            i = j + 1
            cur_rank += group_size
            if method == 'dense':
                dense_rank += 1

        return Series(ranks, name=f"{self.name}_rank", index=self.index)
    
    def map(self, arg):
        """
        Map values of the Series using an input mapping or function.
        
        Parameters:

        arg (dict or function): A mapping dictionary or a function to apply to each value.
        
        Returns:

        Series: A new Series with mapped values.

        Example usage:
        >>> s = tx.Series([1, 2, 3], name='example', index=['a', 'b', 'c'])
        >>> mapping = {1: 'one', 2: 'two', 3: 'three'}
        >>> mapped_s = s.map(mapping)
        >>> print(mapped_s)
        a    one
        b    two
        c    three
        Name: example_mapped, dtype: str
        """
        if callable(arg):
            mapped = [arg(x) for x in self.data]
        elif isinstance(arg, dict):
            mapped = [arg.get(x, None) for x in self.data]
        else:
            raise TypeError("Argument must be a callable or a dictionary.")
        return Series(mapped, name=f"{self.name}_mapped", index=self.index)
    
    def quantile(self, q):
        """
        Compute the q-th quantile of the Series.
        
        Parameters:

        q (float): The quantile to compute (0 <= q <= 1).
        
        Returns:

        float: The q-th quantile value.

        Example usage:
        >>> s = tx.Series([1, 2, 3, 4, 5])
        >>> q_value = s.quantile(0.5)
        >>> print(q_value)
        3.0

        >>> s = tx.Series([1, 2, 3, 4, 5])
        >>> q_value = s.quantile(0.25)
        >>> print(q_value)
        2.0       

       >>> s = tx.Series([1, 2, 3, 4, 5])
        >>> q_value = s.quantile(0.75)
        >>> print(q_value)
        4.0           

        """
        if not self.data:
            return None if isinstance(q, float) else [None for _ in q]
        
        sorted_data = sorted(x for x in self.data if x is not None)
        n = len(sorted_data)

        def compute_single_quantile(p):
            if not 0 <= p <= 1:
                raise ValueError("Quantile must be between 0 and 1.")
            idx = p * (n-1)
            lower = int(idx)
            upper = min(lower + 1, n-1)
            weight = idx - lower
            return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight
        
        if isinstance(q, list):
            return [compute_single_quantile(p) for p in q]
        return compute_single_quantile(q)
    
    def percentile(self, p):
        """ Equivalent to quantile
        
        Compute the p-th percentile of the Series.
        
        Parameters:

        p (float or list): The percentile to compute (0 <= p <= 100).
        
        Returns:

        float or list: The p-th percentile value(s).
        
        Example usage:
        >>> s = tx.Series([1, 2, 3, 4, 5])
        >>> p_value = s.percentile(50)
        >>> print(p_value)
        3.0
        """
        if isinstance(p, list):
            return self.quantile([x/100 for x in p])
        return self.quantile(p/100)
    
    def mean(self):
        """
        Compute the mean of the Series.
        
        Returns:

        float: The mean value of the Series.

        Example usage:

        >>> s = tx.Series([1, 2, 3, 4, 5])
        >>> mean_value = s.mean()
        >>> print(mean_value)
        3.0
        """
        if not self.data:
            return None
        
        values = [v for v in self.data if v is not None]
        return sum(values) / len(values)
    
    def std(self, ddof=1):
        """
        Compute the standard deviation of the Series ignoring None.
        
        Parameters:

        ddof (int): Delta degrees of freedom. Defaults to 1.
            The divisor used in calculations is N - ddof, where N is the number of non-None element
        
        Returns:

        float: The standard deviation of the Series.

        Example usage:
        >>> s = tx.Series([1, 2, 3, 4, 5])
        >>> s.std()
        1.5811388300841898
        """
        if not self.data:
            return None
        
        values = [v for v in self.data if v is not None]
        n = len(values)
        if n <= ddof:
            return None
        mean_val = sum(values) / n
        variance = sum((x - mean_val) **2 for x in values) / (n - ddof)
        return variance ** 0.5
    
    def var(self, ddof=1):
        """
        Compute the variance of the Series, ignoring None.

        Parameters:

            ddof (int): Delta Degrees of Freedom. The divisor used in 
                        calculations is N - ddof, where N is the number of non-None elements.

        Returns:

            float: Variance of the values

        Example usage:
        >>> s = tx.Series([1, 2, 3, 4, 5])
        >>> var_value = s.var()
        >>> print(var_value)
        2.5
        """
        values = [v for v in self.data if v is not None]
        n = len(values)
        if n <= ddof:
            return None
        mean_val = sum(values) / n
        return sum((x - mean_val) ** 2 for x in values) / (n - ddof)
    
    def median(self):
        """
        Compute the median of the Series, ignoring None.

        Returns:

            float: Median value

        Example usage:
        >>> s = tx.Series([1, 2, 3, 4, 5])
        >>> median_value = s.median()
        >>> print(median_value)
        3.0
        """
        values = sorted(v for v in self.data if v is not None)
        n = len(values)
        if n == 0:
            return None
        mid = n // 2
        if n % 2 == 1:
            return values[mid]
        return (values[mid - 1] + values[mid]) / 2  

    def mode(self):
        """
        Compute the mode(s) of the Series, ignoring None.

        Returns:

            list: List of the most common value(s)

        Example usage:
        >>> s = tx.Series([1, 2, 2, 3, 4, 4, 4])
        >>> mode_values = s.mode()
        >>> print(mode_values)
        4
        """
        values = [v for v in self.data if v is not None]
        if not values:
            return []
        freq = Counter(values)
        max_count = max(freq.values())
        return min([val for val, count in freq.items() if count == max_count])
      
     
    def min(self):
        """
        Return the minimum value in the Series, ignoring None.

        Returns:

            float: Minimum value

        Example usage:
        >>> s = tx.Series([1, 2, 3, None, 4, 5])
        >>> min_value = s.min()
        >>> print(min_value)
        1
        """
        values = [v for v in self.data if v is not None]
        return None if not values else min(values)

    def max(self):
        """
        Return the maximum value in the Series, ignoring None.

        Returns:

            float: Maximum value

        Example usage:
        >>> s = tx.Series([1, 2, 3, None, 4, 5])
        >>> max_value = s.max()
        >>> print(max_value)
        5
        """
        values = [v for v in self.data if v is not None]
        return None if not values else max(values)  