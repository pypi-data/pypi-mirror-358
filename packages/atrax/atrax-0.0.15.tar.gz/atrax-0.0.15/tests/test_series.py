import pytest
from atrax import Atrax as tx
from datetime import datetime


def test_series_invalid_index_length():
    with pytest.raises(ValueError, match="Length of index must match length of data"):
        tx.Series([1, 2, 3], index=[0, 1])


def test_series_iloc_out_of_bounds():
    s = tx.Series([10, 20, 30])
    with pytest.raises(IndexError, match="list index out of range"):
        s.iloc[5]



def test_series_loc_invalid_label():
    s = tx.Series([10, 20, 30], index=['a', 'b', 'c'])
    with pytest.raises(ValueError, match="'d' is not in list"):
        s.loc['d']

def test_series_infer_type():
    s = tx.Series([1, 2, 3])
    assert s.dtype == 'int'

    s = tx.Series([1.0, 2.0, 3.0])
    assert s.dtype == 'float'

    s = tx.Series(["apple", "banana", 1, True])
    assert s.dtype == 'object'
      

def test_series_repr_truncated_output():
    s = tx.Series(list(range(15)), name="numbers")

    result = repr(s)

    # Check a few key aspects without hardcoding full output
    assert "0   0" in result
    assert "9   9" in result
    assert "...(15 total)" in result
    assert "Name: numbers" in result
    assert "dtype: int" in result

def test_series_len():
    s = tx.Series([10, 20, 30])
    assert len(s) == 3

def test_series_getitem_index():
    s = tx.Series([100, 200, 300])
    assert s[0] == 100
    assert s[1] == 200
    assert s[2] == 300
    

def test_series_greater_than_scalar():
    s = tx.Series([1, 5, 10], name="numbers")
    result = s > 4

    assert isinstance(result, tx.Series)
    assert result.data == [False, True, True]
    assert result.name == "(numbers > 4)"
    assert result.dtype == "int"   

def test_series_less_than_scalar():
    s = tx.Series([1, 5, 10], name="numbers")
    result = s < 5

    assert isinstance(result, tx.Series)
    assert result.data == [True, False, False]    

def test_series_greater_than_or_equal_scalar():
    s = tx.Series([1, 5, 10])
    result = s >= 5
    assert result.data == [False, True, True]     

def test_series_less_than_or_equal_scalar():
    s = tx.Series([1, 5, 10])
    result = s <= 5
    assert result.data == [True, True, False]    

def test_series_equal_scalar():
    s = tx.Series([1, 5, 10])
    result = s == 5
    assert result.data == [False, True, False]

def test_series_not_equal_scalar():
    s = tx.Series([1, 5, 10])
    result = s != 5
    assert result.data == [True, False, True]   

def test_binary_op_series_with_series():
    s1 = tx.Series([1, 2, 3], name="s1")
    s2 = tx.Series([10, 20, 30], name="s2")

    result = s1._binary_op(s2, lambda a, b: a + b)

    assert isinstance(result, tx.Series)
    assert result.data == [11, 22, 33]
    assert result.name == "s1"


def test_binary_op_series_mismatched_length():
    s1 = tx.Series([1, 2, 3])
    s2 = tx.Series([10, 20])

    with pytest.raises(ValueError, match="must have the same length"):
        s1._binary_op(s2, lambda a, b: a + b)

def test_binary_op_series_with_scalar():
    s = tx.Series([2, 4, 6], name="scale")
    result = s._binary_op(2, lambda a, b: a * b)

    assert result.data == [4, 8, 12]
    assert result.name == "scale"


def test_series_and_operator():
    s1 = tx.Series([True, False, True], name="s1")
    s2 = tx.Series([True, True, False], name="s2")

    result = s1 & s2

    assert isinstance(result, tx.Series)
    assert result.data == [True and True, False and True, True and False]  # [True, False, False]
    assert result.name == "(s1) & s2"


def test_series_and_with_non_series():
    s = tx.Series([True, False])

    with pytest.raises(TypeError, match="Operand must be a Series."):
        _ = s & [True, False]

def test_series_and_mismatched_length():
    s1 = tx.Series([True, False])
    s2 = tx.Series([True])  # shorter

    with pytest.raises(ValueError, match="must have the same length"):
        _ = s1 & s2


def test_series_or_operator():
    s1 = tx.Series([True, False, True], name="left")
    s2 = tx.Series([False, False, True], name="right")

    result = s1 | s2

    assert isinstance(result, tx.Series)
    assert result.data == [True, False, True]
    assert result.name == "(left) | right"



def test_series_or_non_series():
    s = tx.Series([True, False])
    
    with pytest.raises(TypeError, match="Operand must be a Series."):
        _ = s | [False, True]

def test_series_or_mismatched_length():
    s1 = tx.Series([True, False])
    s2 = tx.Series([False])  # shorter

    with pytest.raises(ValueError, match="same length"):
        _ = s1 | s2


def test_series_invert():
    s = tx.Series([True, False, True], name="flags")

    result = ~s

    assert isinstance(result, tx.Series)
    assert result.data == [False, True, False]
    assert result.name == "(~flags)"

def test_series_head():
    s = tx.Series(list(range(20)), name="numbers")

    result = s.head(5)

    assert isinstance(result, tx.Series)
    assert result.data == [0, 1, 2, 3, 4]
    assert result.name == "numbers"
    assert len(result) == 5    

def test_series_tail():
    s = tx.Series(list(range(20)), name="numbers")

    result = s.tail(5)

    assert isinstance(result, tx.Series)
    assert result.data == [15, 16, 17, 18, 19]
    assert result.name == "numbers"
    assert len(result) == 5

def test_series_unique():
    s = tx.Series([1, 2, 2, 3, 3, 3], name="numbers")

    result = s.unique()

    assert isinstance(result, tx.Series)
    assert result.data == [1, 2, 3]
    assert result.name == "Unique(numbers)"
    assert len(result) == 3

def test_series_nunique():
    s = tx.Series([1, 2, 2, 3, 3, 3], name="numbers")

    result = s.nunique()

    assert result == 3  # There are 3 unique values: 1, 2, and 3        

def test_series_isin():
    s = tx.Series([1, 2, 3, 4, 5], name="numbers")
    values = [2, 4, 6]

    result = s.isin(values)

    assert isinstance(result, tx.Series)
    assert result.data == [False, True, False, True, False]
    assert result.name == "IsIn(numbers)"
    assert len(result) == 5    

def test_series_between_inclusive():
    s = tx.Series([1, 5, 10, 15], name="vals")
    result = s.between(5, 10)

    assert isinstance(result, tx.Series)
    assert result.data == [False, True, True, False]
    assert result.name == "Between(vals, 5, 10)"
    assert result.dtype == "int"


def test_series_between_exclusive():
    s = tx.Series([1, 5, 10, 15], name="vals")
    result = s.between(5, 10, inclusive=False)

    assert result.data == [False, False, False, False]  # only 5 and 10 match the bounds, but they're excluded
    assert result.name == "Between(vals, 5, 10, exclusive)"


def test_series_to_list():
    s = tx.Series([10, 20, 30], name="nums")
    result = s.to_list()

    assert isinstance(result, list)
    assert result == [10, 20, 30]


def test_series_to_list_empty():
    s = tx.Series([], name="empty")
    result = s.to_list()

    assert result == []


def test_series_to_list_strings():
    s = tx.Series(["apple", "banana", "cherry"])
    result = s.to_list()

    assert result == ["apple", "banana", "cherry"]


def test_series_apply_square():
    s = tx.Series([1, 2, 3, 4], name="nums")
    result = s.apply(lambda x: x**2)

    assert isinstance(result, tx.Series)
    assert result.data == [1, 4, 9, 16]
    assert result.name == "nums"


def test_series_apply_uppercase():
    s = tx.Series(["apple", "banana", "cherry"], name="fruits")
    result = s.apply(str.upper)

    assert result.data == ["APPLE", "BANANA", "CHERRY"]
    assert result.name == "fruits"


def test_series_apply_boolean_filter():
    s = tx.Series([10, 20, 30], name="values")
    result = s.apply(lambda x: x > 15)

    assert result.data == [False, True, True]
    assert result.dtype == "int"


def test_series_apply_empty():
    s = tx.Series([], name="empty")
    result = s.apply(lambda x: x + 1)

    assert result.data == []


def test_series_astype_to_float():
    s = tx.Series([1, 2, 3], name="ints")
    result = s.astype('float')

    assert isinstance(result, tx.Series)
    assert result.data == [1.0, 2.0, 3.0]
    assert result.dtype == 'float'


def test_series_astype_to_str():
    s = tx.Series([1.5, 2.0, 3.25], name="floats")
    result = s.astype('str')

    assert result.data == ['1.5', '2.0', '3.25']
    assert result.dtype == 'str'

def test_series_astype_to_int():
    s = tx.Series([1.5, 2.0, 3.25], name="floats")
    result = s.astype('int')

    assert result.data == [1,2,3]   

def test_series_astype_string_and_callable():
    s = tx.Series(["1", "2", "3"])

    result1 = s.astype(int)
    assert result1.data == [1, 2, 3]

    result2 = s.astype("float")
    assert result2.data == [1.0, 2.0, 3.0]


def test_astype_to_int():
    s = tx.Series(["1", "2", "3"])
    result = s.astype("int")

    assert result.data == [1, 2, 3]
    assert isinstance(result.data[0], int)


def test_astype_to_float():
    s = tx.Series(["1.1", "2.2", "3.3"])
    result = s.astype("float")

    assert result.data == [1.1, 2.2, 3.3]
    assert isinstance(result.data[1], float)


def test_astype_to_object():
    s = tx.Series(["a", "b", "c"])
    result = s.astype("object")

    assert result.data == ["a", "b", "c"]
    assert result.data == s.data  # Should match exactly

def test_astype_invalid_dtype():
    s = tx.Series([1, 2, 3])
    
    with pytest.raises(ValueError, match="Unsupported dtype: bool"):
        s.astype("bool")

def test_astype_cast_failure_falls_back_to_none():
    s = tx.Series(["abc", "123", "4.5"])
    result = s.astype(int)

    # "abc" can't be cast to int, expect None
    assert result.data == [None, 123, None]




def test_to_datetime_valid_default_format():
    s = tx.Series(["2025-01-01", "2025-06-15"])
    result = s.to_datetime()

    assert result.data == [datetime(2025, 1, 1), datetime(2025, 6, 15)]
    
def test_to_datetime_custom_format():
    s = tx.Series(["01/01/2025", "06/15/2025"])
    result = s.to_datetime(format="%m/%d/%Y")

    assert result.data == [datetime(2025, 1, 1), datetime(2025, 6, 15)]


def test_to_datetime_already_datetime():
    original = [datetime(2025, 1, 1), datetime(2025, 2, 2)]
    s = tx.Series(original)
    result = s.to_datetime()

    assert result.data == original  # Should match exactly

def test_to_datetime_invalid_string_raise():
    s = tx.Series(["not_a_date"])

    with pytest.raises(ValueError, match="Failed to parse 'not_a_date' as datetime"):
        s.to_datetime()

def test_to_datetime_invalid_string_coerce():
    s = tx.Series(["not_a_date"])
    result = s.to_datetime(errors='coerce')

    assert result.data == [None]

def test_to_datetime_unsupported_type_raise():
    s = tx.Series([12345])  # Not str or datetime

    with pytest.raises(ValueError, match="Unsupported type for to_datetime"):
        s.to_datetime()

def test_to_datetime_unsupported_type_coerce():
    s = tx.Series([12345])
    result = s.to_datetime(errors='coerce')

    assert result.data == [None]


def test_repr_html_basic():
    s = tx.Series([1, 2, 3], name="test_series")
    html = s._repr_html_()

    assert "<table" in html
    assert "<td style=''>0</td>" in html
    assert "<td style=''>1</td>" in html
    assert "Name: test_series" in html
    assert "dtype: int" in html
    assert "... more" not in html  # Should not trigger truncation


def test_repr_html_truncated():
    s = tx.Series(list(range(15)), name="long_series")
    html = s._repr_html_()

    assert "...5 more" in html  # 15 - 10 = 5 rows truncated


def test_repr_html_structure():
    s = tx.Series([42])
    html = s._repr_html_()

    assert html.startswith("<table")
    assert html.endswith("</table>")

def test_series_rolling_valid():
    s = tx.Series([1, 2, 3, 4, 5], name="test")
    r = s.rolling(window=3)

    assert r.window == 3
    assert r.data == [1, 2, 3, 4, 5]
    assert r.name == "test"


def test_series_rolling_zero_window():
    s = tx.Series([1, 2, 3])
    with pytest.raises(ValueError, match="Window size must be a positive integer."):
        s.rolling(0)


def test_iloc_integer_access():
    s = tx.Series([10, 20, 30], name="test")
    assert s.iloc[0] == 10
    assert s.iloc[2] == 30


def test_iloc_slice_access():
    s = tx.Series([10, 20, 30, 40], name="slice_test")
    sliced = s.iloc[1:3]

    assert isinstance(sliced, tx.Series)
    assert sliced.data == [20, 30]
    assert sliced.index == [1, 2]
    assert sliced.name == "slice_test"

def test_loc_single_label():
    s = tx.Series([10, 20, 30], index=["a", "b", "c"])
    assert s.loc["a"] == 10
    assert s.loc["c"] == 30


def test_loc_list_of_labels():
    s = tx.Series([10, 20, 30], index=["a", "b", "c"])
    result = s.loc[["b", "a"]]
    
    assert isinstance(result, tx.Series)
    assert result.data == [20, 10]
    assert result.index == ["b", "a"]



def test_series_cut_basic_equal_width():
    s = tx.Series([1, 2, 3, 4, 5])
    result = s.cut(bins=2)
    assert result.data == [0, 0, 1, 1, 1]

def test_series_cut_with_labels():
    s = tx.Series([1, 2, 3, 4, 5])
    result = s.cut(bins=2, labels=['Low', 'High'])
    assert result.data == ['Low', 'Low', 'High', 'High', 'High']

def test_series_cut_with_explicit_edges():
    s = tx.Series([10, 20, 30, 40, 50])
    result = s.cut(bins=[10, 30, 50], labels=['Small', 'Large'])
    assert result.data == ['Small', 'Small', 'Large', 'Large', 'Large']

def test_series_cut_tie_breaker_upper():
    s = tx.Series([10, 20, 30])
    result = s.cut(bins=[10, 20, 30], labels=['A', 'B'], tie_breaker='upper')
    assert result.data == ['A', 'B', 'B']

def test_series_cut_tie_breaker_lower():
    s = tx.Series([10, 20, 30])
    result = s.cut(bins=[10, 20, 30], labels=['A', 'B'], tie_breaker='lower')
    assert result.data == ['A', 'A', 'B']

def test_series_cut_handles_none():
    s = tx.Series([10, None, 30, None])
    result = s.cut(bins=[10, 20, 40], labels=['Low', 'High'])
    assert result.data == ['Low', None, 'High', None]

def test_series_cut_includes_first_bin_edge_on_lower():
    s = tx.Series([10, 11, 20])
    result = s.cut(bins=[10, 20], labels=['X'], tie_breaker='lower')
    assert result.data == ['X', 'X', 'X']

def test_series_cut_returns_series_type():
    s = tx.Series([1, 2, 3])
    result = s.cut(bins=2)
    assert isinstance(result, tx.Series)      

def test_rank_basic_order():
    s = tx.Series([10, 20, 30])
    result = s.rank()
    assert result.data == [1.0, 2.0, 3.0]

def test_rank_with_duplicates_average():
    s = tx.Series([10, 20, 20, 40])
    result = s.rank()
    # 10 -> 1, 20s -> average of 2 and 3 = 2.5, 40 -> 4
    assert result.data == [1.0, 2.5, 2.5, 4.0]

def test_rank_with_duplicates_min():
    s = tx.Series([10, 20, 20, 40])
    result = s.rank(method='min')
    assert result.data == [1.0, 2.0, 2.0, 4.0]

def test_rank_with_duplicates_max():
    s = tx.Series([10, 20, 20, 40])
    result = s.rank(method='max')
    assert result.data == [1.0, 3.0, 3.0, 4.0]

def test_rank_with_duplicates_dense():
    s = tx.Series([10, 20, 20, 40])
    result = s.rank(method='dense')
    # 10 -> 1, 20s -> 2, 40 -> 3
    assert result.data == [1.0, 2.0, 2.0, 3.0]

def test_rank_with_duplicates_first():
    s = tx.Series([10, 20, 20, 40])
    result = s.rank(method='first')
    # based on position: 10->1, first 20->2, second 20->3, 40->4
    assert result.data == [1.0, 2.0, 3.0, 4.0]

def test_rank_descending():
    s = tx.Series([10, 20, 30])
    result = s.rank(ascending=False)
    assert result.data == [3.0, 2.0, 1.0]

@pytest.mark.skip(reason="We have not implemented this yet.")
def test_rank_handles_none():
    s = tx.Series([10, None, 30])
    result = s.rank()
    # None is skipped; 10->1, 30->2
    assert result.data == [1.0, None, 2.0]

def test_rank_returns_series():
    s = tx.Series([5, 1, 3])
    result = s.rank()
    assert isinstance(result, tx.Series)

def test_rank_preserves_index():
    s = tx.Series([100, 50, 75], index=['a', 'b', 'c'])
    result = s.rank()
    assert result.index == ['a', 'b', 'c']
    assert result.data == [3.0, 1.0, 2.0]

def test_series_quantile():
    s = tx.Series([10, 20, 30, 40, 50])
    assert s.quantile(0.5) == 30
    assert s.quantile([0.25, 0.5, 0.75]) == [20.0, 30.0, 40.0] 

def test_series_quantile_empty_dataset():
    s = tx.Series([])
    result = s.quantile(0.5)
    assert result is None    

def test_series_quantile_invalid_p():
    s = tx.Series([1,2,3])
    with pytest.raises(ValueError, match="Quantile must be between 0 and 1"):
        s.quantile(2)

def test_series_percentile():
    s = tx.Series([10, 20, 30, 40, 50])
    assert s.percentile(50) == 30
    assert s.percentile([25, 50, 75]) == [20.0, 30.0, 40.0]        

