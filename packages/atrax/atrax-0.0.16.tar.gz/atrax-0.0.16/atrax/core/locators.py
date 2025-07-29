
## Series functions
class _Iloc:
    """This class provides integer-location based indexing for a Series object.
    It allows for both single item access and slicing operations.

    Example usage:
    >>> from atrax.core.series import Series
    >>> s = Series([1, 2, 3], name='example', index=['a', 'b', 'c'])
    >>> iloc = _Iloc(s)
    >>> s
    a    1
    b    2
    c    3
    Name: example, dtype: int
    """
    def __init__(self, series):
        self.series = series

    def __getitem__(self, i):
        if isinstance(i, slice):
            from .series import Series
            return Series(self.series.data[i], name=self.series.name, index=self.series.index[i])
        return self.series.data[i]
    
class _Loc:
    def __init__(self, series):
        self.series = series

    def __getitem__(self, key):
        from .series import Series
        if isinstance(key, list):            
            index_map = {k:v for k, v in zip(self.series.index, self.series.data)}
            return Series([index_map[k] for k in key], name=self.series.name, index=key)
        elif isinstance(key, slice):
            start_label = key.start
            end_label = key.stop

            try:
                start_idx = self.series.index.index(start_label)
                end_idx = self.series.index.index(end_label)
            except ValueError:
                raise KeyError("Label not found in index")
            
            # +1 because label-based slicin is inclusive
            data = self.series.data[start_idx:end_idx + 1]
            index = self.series.index[start_idx:end_idx + 1]
            return Series(data, name=self.series.name, index=index)

        else:
            # single label lookup
            idx = self.series.index.index(key)
            return self.series.data[idx]   


## Dataset Functions

class _LocIndexer:
    def __init__(self, dataset):
        self.dataset = dataset

    def __getitem__(self, key):
        from .dataset import DataSet
        from datetime import datetime
        # ✅ CASE 1: Tuple → (row_filter, col_filter)
        if isinstance(key, tuple):
            row_filter, col_filter = key

        # ✅ CASE 2: Single filter → callable or boolean list
        elif callable(key) or (isinstance(key, list) and all(isinstance(b, bool) for b in key)):
            row_filter = key
            col_filter = self.dataset.columns  # return all columns

        # ✅ CASE 3: Single label (e.g., "2025-03-02")
        else:
            key_val = key
            if self.dataset._index:
                index_sample = self.dataset._index[0]
                if isinstance(index_sample, datetime) and isinstance(key, str):
                    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
                        try:
                            key_val = datetime.strptime(key, fmt)
                            break
                        except ValueError:
                            continue
            matched_rows = [
                row for idx, row in zip(self.dataset._index, self.dataset.data)
                if idx == key_val
            ]
            return DataSet(matched_rows)

        # ✅ Apply row filtering
        if isinstance(row_filter, list) and all(isinstance(b, bool) for b in row_filter):
            filtered = [row for row, keep in zip(self.dataset.data, row_filter) if keep]
        elif callable(row_filter):
            filtered = [row for row in self.dataset.data if row_filter(row)]
        else:
            filtered = self.dataset.data  # fallback (no filter)

        # ✅ Apply column projection
        if isinstance(col_filter, str):
            col_filter = [col_filter]

        result_data = [{col: row.get(col) for col in col_filter} for row in filtered]
        return DataSet(result_data)    

class _iLocIndexer:
    def __init__(self, dataset):
        self.dataset = dataset

    def __getitem__(self, key):
        from .dataset import DataSet
        row_idx, col_idx = key

        rows = self.dataset.data[row_idx] if isinstance(row_idx, slice) else [self.dataset.data[row_idx]]

        col_names = self.dataset.columns[col_idx] if isinstance(col_idx, slice) else [self.dataset.columns[i] for i in col_idx]

        filtered = [{k: row[k] for k in col_names if k in row} for row in rows]
        return DataSet(filtered)          