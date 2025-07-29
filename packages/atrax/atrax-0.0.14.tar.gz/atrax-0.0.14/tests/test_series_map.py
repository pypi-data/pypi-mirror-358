import pytest
from atrax import Series  # Adjust import path if needed

def test_map_with_function():
    s = Series([1, 2, 3], name="x")
    result = s.map(lambda x: x * 10)
    assert result.data == [10, 20, 30]
    assert result.index == s.index

def test_map_with_dict():
    s = Series(['a', 'b', 'c'], name="x")
    mapping = {'a': 1, 'b': 2, 'c': 3}
    result = s.map(mapping)
    assert result.data == [1, 2, 3]

def test_map_with_dict_missing_key():
    s = Series(['a', 'b', 'z'], name="x")
    mapping = {'a': 1, 'b': 2}
    result = s.map(mapping)
    assert result.data == [1, 2, None]  # 'z' is not in dict, maps to None

def test_map_invalid_argument():
    s = Series([1, 2, 3], name="x")
    with pytest.raises(TypeError):
        s.map(123)  # not a function or dict
