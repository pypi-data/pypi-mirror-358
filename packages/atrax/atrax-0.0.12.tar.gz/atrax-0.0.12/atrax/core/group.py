

class GroupBy:
    """GroupBy class for aggregating data based on specified keys.
    
    This class allows you to group a dataset by one or more columns 
    and perform aggregations such as sum, mean, count, min, max, 
    first, and last.
    
    """
    def __init__(self, data, by):
        self.by = by if isinstance(by, list) else [by]
        self.data = data
        self.groups = self._group_data()

    def _group_data(self):
        from collections import defaultdict
        grouped = defaultdict(list)
        for row in self.data:
            key = tuple(row[k] for k in self.by)
            grouped[key].append(row)
        return grouped
    
    def agg(self, *args, **kwargs):
        from .dataset import DataSet
        result = []

        # determine aggregation mode
        if args and isinstance(args[0], dict):
            agg_spec = args[0]
            named_agg = False
        elif kwargs:
            agg_spec = kwargs
            named_agg = True
        else:
            raise ValueError("agg() requires either a dict or named arguments")
        
        for group_key, rows in self.groups.items():
            col_data = {}
            for row in rows:
                for col, val in row.items():
                    col_data.setdefault(col, []).append(val)

            aggregated_row = {}

            if named_agg:
                for output_col, (input_col, agg_func) in agg_spec.items():
                    values = col_data.get(input_col, [])

                    if isinstance(agg_func, str):
                        if agg_func == 'sum':
                            aggregated_row[output_col] = sum(values)
                        elif agg_func == 'mean':
                            aggregated_row[output_col] = sum(values) / len(values) if values else 0
                        elif agg_func == 'count':
                            aggregated_row[output_col] = len(values)
                        elif agg_func == 'min':
                            aggregated_row[output_col] = min(values) if values else None
                        elif agg_func == 'max':
                            aggregated_row[output_col] = max(values) if values else None
                        elif agg_func == 'first':
                            aggregated_row[output_col] = values[0] if values else None
                        elif agg_func == 'last':
                            aggregated_row[output_col] = values[-1] if values else None
                        else:
                            raise ValueError(f"Unknown aggregation function: {agg_func}")
                    elif callable(agg_func):
                        aggregated_row[output_col] = agg_func(values)
                    else:
                        raise TypeError(f"Aggregation function must be a string or callable, got {type(agg_func)}")
            else:
                for input_col, agg_funcs in agg_spec.items():
                    values = col_data.get(input_col, [])

                    if not isinstance(agg_funcs, list):
                        agg_funcs = [agg_funcs]

                    for agg_func in agg_funcs:
                        if isinstance(agg_func, str):
                            if agg_func == 'sum':
                                aggregated_row[input_col + '_sum'] = sum(values)
                            elif agg_func == 'mean':
                                aggregated_row[input_col + '_mean'] = sum(values) / len(values) if values else 0
                            elif agg_func == 'count':
                                aggregated_row[input_col + '_count'] = len(values)
                            elif agg_func == 'min':
                                aggregated_row[input_col + '_min'] = min(values) if values else None
                            elif agg_func == 'max':
                                aggregated_row[input_col + '_max'] = max(values) if values else None
                            elif agg_func == 'first':
                                aggregated_row[input_col + '_first'] = values[0] if values else None
                            elif agg_func == 'last':
                                aggregated_row[input_col + '_last'] = values[-1] if values else None
                            else:
                                raise ValueError(f"Unknown aggregation function: {agg_func}")
                        elif callable(agg_func):
                            colname = f"{input_col}_{agg_func.__name__}"
                            aggregated_row[colname] = agg_func(values)
                        else:
                            raise TypeError(f"Aggregation function must be a string or callable, got {type(agg_func)}")
                        
            for i, col in enumerate(self.by):
                aggregated_row[col] = group_key[i]

            result.append(aggregated_row)
        return DataSet(result)

    def sum(self):
        """Calculate the sum of each group."""
        from .dataset import DataSet
        result = []
        for group_key, rows in self.groups.items():
            summary = {col: 0 for col in rows[0] if isinstance(rows[0][col], (int, float))}
            for row in rows:
                for col in summary:
                    summary[col] += row.get(col, 0)
            # add group key back
            for i, col in enumerate(self.by):
                summary[col] = group_key[i]
            result.append(summary)
        return DataSet(result)

    def mean(self):
        """Calculate the mean of each group."""
        from .dataset import DataSet
        result = []
        for group_key, rows in self.groups.items():
            count = len(rows)
            summary = {col: 0 for col in rows[0] if isinstance(rows[0][col], (int, float))}
            for row in rows:
                for col in summary:
                    summary[col] += row.get(col, 0)
            for col in summary:
                summary[col] /= count
            for i, col in enumerate(self.by):
                summary[col] = group_key[i]
            result.append(summary)
        return DataSet(result)        



