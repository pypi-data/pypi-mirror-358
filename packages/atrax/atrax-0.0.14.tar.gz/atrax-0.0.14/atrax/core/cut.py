def cut(values, bins=4, labels=None, precision=3, tie_breaker='upper'):
    """
    Bin values into equal-width intervals.

    Parameters
    ----------
    values : (array-like) The input values to be cut.
    bins : int or sequence of scalars, optional
        If an int, defines the number of equal-width bins in the range of values.
        If a sequence, defines the bin edges.
    labels : array-like, optional
        Labels for the bins. If None, integer labels are used.
    precision : int, optional
        Number of decimal places to round the bin edges.
    tie_breaker : {'upper', 'lower'}, optional
        Determines how to handle values that fall exactly on the bin edges.
        'upper' assigns them to the upper bin, 'lower' assigns them to the lower bin.

    Returns
    -------
    binned_values : array-like
        The binned values.

    Example usage:
    >>> from atrax import Atrax as tx
    >>> cut([1, 2, 3, 4, 5], bins=3)
    [0, 0, 1, 2, 2]

    >>> cut([1, 2, 3, 4, 5], bins=[0, 2, 4, 6], labels=['low', 'medium', 'high'])
    ['low', 'medium', 'medium', 'high', 'high']

    >>> cut([1, 2, 3, 4, 5], bins=3, precision=2, tie_breaker='lower')
    [0, 0, 1, 2, 2]

    >>> cut([1, 2, 3, 4, 5], bins=3, precision=2, tie_breaker='upper')
    [0, 0, 1, 2, 2]

    >>> ages = [19, 23, 37, 45, 50, 61, 70, 82]
    >>> age_bins = [0, 20, 50, 100]
    >>> age_labels = ['young', 'middle-ages', 'senior']
    >>> cut(ages, bins=age_bins, labels=age_labels, tie_breaker='upper')
    ['young', 'middle-ages', 'middle-ages', 'middle-ages', 'senior', 'senior', 'senior', 'senior]

    >>> sales = [0, 20, 50, 75, 110, 130, 170, 200]
    >>> binned_sales = cut(sales, bins=4)
    >>> binned_sales
    [0, 0, 1, 1, 2, 2, 3, 3]

    >>> cholesterol = [120, 140, 160, 190, 210, 250]
    >>> risk_bins = [0, 160, 20, 300]
    >>> risk_labels = ['Low', 'Moderate', 'High']
    >>> cut(cholesterol, bins=risk_bins, labels=risk_labels, tie_breaker='lower')
    ['Low', 'Low', 'Low', 'High', 'High', 'High]
    """
    if not values:
        return []
    
    clean_values = [v for v in values if v is not None]
    min_val, max_val = min(clean_values), max(clean_values)

    if isinstance(bins, int):
        step = (max_val - min_val) / bins
        bin_edges = [round(min_val + i * step, precision) for i in range(bins + 1)]
    else:
        bin_edges = bins

    # bin assignment
    def assign_bin(val):
        if tie_breaker == 'lower' and val == bin_edges[0]:
            return labels[0] if labels else 0
        
        
        for i in range(len(bin_edges) - 1):
            left = bin_edges[i]
            right = bin_edges[i + 1]
            if tie_breaker == 'upper':
                if left <= val < right:
                    return labels[i] if labels else i
            else: # lower
                if left < val <= right:
                    return labels[i] if labels else i
                
        if val == bin_edges[-1]:
            return labels[-1] if labels else len(bin_edges) - 2
        return None
    
    return [assign_bin(v) if v is not None else None for v in values]