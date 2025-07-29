from atrax import Atrax as tx
from atrax.core.rolling import RollingSeries

def test_rolling_mean_basic():
    data = [1, 2, 3, 4, 5]
    r = RollingSeries(data, window=3)
    result = r.mean()
    
    assert isinstance(result, tx.Series)
    assert result.data == [None, None, 2.0, 3.0, 4.0]
    assert result.name == "rolling_series_rolling_mean"

def test_rolling_sum_basic():
    data = [1, 2, 3, 4, 5]
    r = RollingSeries(data, window=2)
    result = r.sum()
    
    assert isinstance(result, tx.Series)
    assert result.data == [None, 3, 5, 7, 9]
    assert result.name == "rolling_series_rolling_sum"

def test_rolling_with_custom_name():
    data = [10, 20, 30]
    r = RollingSeries(data, window=2, name="my_series")
    result = r.mean()
    
    assert result.name == "my_series_rolling_mean"

def test_rolling_window_larger_than_data():
    data = [1, 2]
    r = RollingSeries(data, window=5)
    mean_result = r.mean()
    sum_result = r.sum()
    
    assert mean_result.data == [None, None]
    assert sum_result.data == [None, None]

def test_rolling_exact_window_match():
    data = [4, 5, 6]
    r = RollingSeries(data, window=3)
    result = r.sum()
    
    assert result.data == [None, None, 15]
