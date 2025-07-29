import math
def qcut(values, q=4, labels=None):
    """
    Quantile-based discretization function.
    
    Parameters:
    - values: list or array-like, the input values to be discretized.
    - q: int, number of quantiles to create (default is 4).
    - labels: list of labels for the quantiles (optional).
    
    Returns:
    - A list of quantile labels corresponding to the input values.
    """
    if not values:
        return []
    
    sorted_vals = sorted((v for v in values if v is not None))
    n = len(sorted_vals)

    # compute quantile boundaries
    boundaries = [sorted_vals[int(n * i / q)] for i in range(q)]
    boundaries.append(sorted_vals[-1]) # include upper bound

    def find_bin(val):
        for i in range(q):
            if val <= boundaries[i + 1]:
                return labels[i] if labels else i
        return labels[-1] if labels else q - 1
    
    return [find_bin(v) if v is not None else None for v in values]