import pytest
from datetime import datetime
from atrax import Atrax as tx
import pandas as pd


def test_init_from_list_of_dicts():
    data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    ds = tx.DataSet(data)
    assert ds.shape() == (2, 2)
    assert ds.columns == ['a', 'b']

def test_init_from_dict_of_lists():
    data = {"a": [1, 3], "b": [2, 4]}
    ds = tx.DataSet(data)
    assert ds.shape() == (2, 2)
    assert ds.columns == ['a', 'b']

def test_init_column_length_mismatch():
    bad_data = {
        "a": [1, 2, 3],
        "b": [4, 5],  # Shorter column
    }

    with pytest.raises(ValueError, match="All columns must have the same length"):
        tx.DataSet(bad_data)   

def test_get_column_series():
    ds = tx.DataSet([{"a": 1}, {"a": 2}])
    s = ds["a"]
    assert isinstance(s, tx.Series)
    assert s.data == [1, 2]

def test_boolean_mask_filtering():
    ds = tx.DataSet([{"a": 1}, {"a": 2}, {"a": 3}])
    mask = tx.Series([True, False, True])
    filtered = ds[mask]
    assert filtered.shape() == (2, 1)
    assert filtered.data == [{"a": 1}, {"a": 3}]

def test_column_subset():
    ds = tx.DataSet([{"a": 1, "b": 2}])
    subset = ds[["a"]]
    assert subset.columns == ["a"]
    assert subset.data == [{"a": 1}]

def test_concat_axis_0():
    ds1 = tx.DataSet([{"a": 1}])
    ds2 = tx.DataSet([{"b": 2}])
    result = tx.DataSet.concat([ds1, ds2], axis=0)
    assert result.shape() == (2, 2)

def test_concat_axis_1():
    ds1 = tx.DataSet([{"a": 1}])
    ds1.set_index("a")
    ds2 = tx.DataSet([{"b": 2}])
    ds2.set_index("b")
    result = tx.DataSet.concat([ds1, ds2], axis=1)
    assert result.shape()[1] >= 2  # at least 2 columns combined    


def test_apply_function_to_rows():
    ds = tx.DataSet([{"a": 1}, {"a": 2}])
    result = ds.apply(lambda row: {"b": row["a"] * 2})
    assert result.data == [{"b": 2}, {"b": 4}]

def test_sort_ascending():
    ds = tx.DataSet([{"a": 3}, {"a": 1}, {"a": 2}])
    sorted_ds = ds.sort("a")
    assert [r["a"] for r in sorted_ds.data] == [1, 2, 3]

def test_drop_columns():
    ds = tx.DataSet([{"a": 1, "b": 2}])
    dropped = ds.drop(columns=["b"])
    assert dropped.columns == ["a"]

def test_rename_columns():
    ds = tx.DataSet([{"x": 1}])
    renamed = ds.rename(columns={"x": "y"})
    assert renamed.columns == ["y"]
    assert renamed.data == [{"y": 1}]

def test_reset_index():
    ds = tx.DataSet([{"id": 10}, {"id": 20}])
    ds.set_index("id")
    reset = ds.reset_index()
    assert reset._index == [0, 1]

def test_to_dict_conversion():
    ds = tx.DataSet([{"a": 1}])
    result = ds.to_dict()
    assert result == [{"a": 1}]

def test_to_csv_string():
    ds = tx.DataSet([{"a": 1, "b": 2}])
    csv_output = ds.to_csv()
    assert "a,b" in csv_output
    assert "1,2" in csv_output

def test_to_pandas_conversion():
    ds = tx.DataSet([{"a": 1}])
    df = ds.to_pandas()
    assert df.shape == (1, 1)
    assert df.iloc[0]["a"] == 1

def test_describe_numeric_column():
    ds = tx.DataSet([{"x": 1}, {"x": 3}, {"x": 5}])
    summary = ds.describe()
    assert any("x" in row for row in summary.data)  

def test_merge_inner_join():
    ds1 = tx.DataSet([{"id": 1, "x": 100}, {"id": 2, "x": 200}])
    ds2 = tx.DataSet([{"id": 2, "y": 999}])
    result = ds1.merge(ds2, on="id", how="inner")
    assert len(result.data) == 1
    assert result.data[0]["id"] == 2
    assert "x_x" in result.data[0]
    assert "y" in result.data[0]

def test_astype_conversion():
    ds = tx.DataSet([{"num": "1"}, {"num": "2"}])
    converted = ds.astype({"num": int})
    assert converted.data == [{"num": 1}, {"num": 2}]

def test_filter_by_items():
    ds = tx.DataSet([{"a": 1, "b": 2}])
    filtered = ds.filter(items=["a"])
    assert filtered.columns == ["a"]

def test_filter_by_like():
    ds = tx.DataSet([{"price_usd": 100, "price_eur": 80}])
    filtered = ds.filter(like="usd")
    assert filtered.columns == ["price_usd"]

def test_copy_dataset():
    ds = tx.DataSet([{"a": 1}])
    ds2 = ds.copy()
    ds2["a"] = tx.Series([2])
    assert ds.data[0]["a"] == 1
    assert ds2.data[0]["a"] == 2    

def test_set_index_drop_true():
    ds = tx.DataSet([{"a": 1, "b": 2}])
    ds.set_index("a", drop=True)
    assert ds._index == [1]
    assert "a" not in ds.columns

def test_set_index_drop_false():
    ds = tx.DataSet([{"a": 1, "b": 2}])
    ds.set_index("a", drop=False)
    assert ds._index == [1]
    assert "a" in ds.columns    

def test_index_default():
    ds = tx.DataSet([{"a": 10}, {"a": 20}, {"a": 30}])
    assert ds.index == [0, 1, 2]    

def test_index_after_set_index():
    ds = tx.DataSet([
        {"date": "2024-01-01", "val": 1},
        {"date": "2024-01-02", "val": 2},
    ])
    ds.set_index("date")
    assert ds.index == ["2024-01-01", "2024-01-02"]    


def test_loc_returns_indexer():
    ds = tx.DataSet([{"a": 1}])
    loc_obj = ds.loc
    assert loc_obj.__class__.__name__ == "_LocIndexer"  

def test_loc_label_based_lookup():
    ds = tx.DataSet([
        {"date": "2024-01-01", "val": 100},
        {"date": "2024-01-02", "val": 200},
    ])
    ds.set_index("date")
    result = ds.loc["2024-01-02"]
    assert result.shape() == (1, 2)
    assert result.data[0]["val"] == 200

def test_loc_tuple_row_and_column_filter():
    ds = tx.DataSet([
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
    ])
    result = ds.loc[(lambda row: row["a"] > 1, "b")]
    assert result.shape() == (1, 1)
    assert result.data[0]["b"] == 4   

def test_loc_callable_row_filter():
    ds = tx.DataSet([
        {"a": 1, "b": 2},
        {"a": 5, "b": 8},
    ])
    result = ds.loc[lambda row: row["a"] > 2]
    assert result.shape() == (1, 2)
    assert result.data[0]["b"] == 8

def test_loc_boolean_mask():
    ds = tx.DataSet([
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
    ])
    result = ds.loc[[True, False]]
    assert result.shape() == (1, 2)
    assert result.data[0]["a"] == 1    

def test_loc_with_datetime_string_index():
    ds = tx.DataSet([
        {"dt": datetime(2024, 1, 1), "x": 5},
        {"dt": datetime(2024, 1, 2), "x": 10},
    ])
    ds.set_index("dt")
    result = ds.loc["2024-01-02"]
    assert result.shape() == (1, 2)
    assert result.data[0]["x"] == 10    

def test_iloc_returns_indexer():
    ds = tx.DataSet([{"a": 1, "b": 2}])
    iloc_obj = ds.iloc
    assert iloc_obj.__class__.__name__ == "_iLocIndexer"

def test_iloc_single_row_and_column():
    ds = tx.DataSet([
        {"a": 10, "b": 20},
        {"a": 30, "b": 40},
    ])
    result = ds.iloc[1, [0]]  # row 1, column index 0 ("a")
    assert result.shape() == (1, 1)
    assert result.data[0]["a"] == 30     

def test_iloc_row_slice_column_slice():
    ds = tx.DataSet([
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
        {"a": 5, "b": 6},
    ])
    result = ds.iloc[0:2, 0:2]
    assert result.shape() == (2, 2)
    assert result.data[0]["a"] == 1
    assert result.data[1]["b"] == 4

def test_iloc_multiple_column_indices():
    ds = tx.DataSet([{"x": 1, "y": 2, "z": 3}])
    result = ds.iloc[0, [1, 2]]  # cols y, z
    assert result.columns == ["y", "z"]
    assert result.data == [{"y": 2, "z": 3}]      

def test_iloc_row_out_of_bounds_raises():
    ds = tx.DataSet([{"a": 1}])
    try:
        ds.iloc[5, [0]]
        assert False, "Expected IndexError"
    except IndexError:
        assert True

def test_iloc_column_index_out_of_bounds_raises():
    ds = tx.DataSet([{"a": 1}])
    try:
        ds.iloc[0, [5]]
        assert False, "Expected IndexError"
    except IndexError:
        assert True  

def test_concat_missing_dataset():
    result = tx.DataSet.concat(None)
    assert result.data == []     

def test_concat_invalid_axis():
    ds1 = tx.DataSet([{"a": 1}])
    ds2 = tx.DataSet([{"b": 2}])
    try:
        tx.DataSet.concat([ds1, ds2], axis=3)
        assert False, "Expected ValueError"
    except ValueError:
        assert True 

def test_getitem_boolean_series_length_mismatch():
    ds = tx.DataSet([
        {"a": 1},
        {"a": 2},
        {"a": 3}
    ])
    mask = tx.Series([True, False])  # Too short

    with pytest.raises(ValueError, match="Boolean Series must match the length of the dataset."):
        _ = ds[mask]   

def test_getitem_invalid_key_type():
    ds = tx.DataSet([{"a": 1}])
    
    with pytest.raises(TypeError, match="Key must be a string"):
        _ = ds[42]  # Invalid key type (int) 

def test_getitem_non_boolean_series():
    ds = tx.DataSet([
        {"a": 1},
        {"a": 2}
    ])
    s = tx.Series([1, 0])  # Not boolean values

    with pytest.raises(TypeError):  # or allow, depending on your rules
        _ = ds[s]  

def test_setitem_series_length_mismatch():
    ds = tx.DataSet([
        {"a": 1},
        {"a": 2}
    ])
    s = tx.Series([10])  # Too short

    with pytest.raises(ValueError, match="Series length must match Dataset length."):
        ds["b"] = s 


def test_setitem_valid_series():
    ds = tx.DataSet([
        {"a": 1},
        {"a": 2}
    ])
    s = tx.Series([10, 20])
    ds["b"] = s
    assert ds.columns == ["a", "b"]
    assert ds.data[0]["b"] == 10
    assert ds.data[1]["b"] == 20

def test_repr_under_10_rows():
    ds = tx.DataSet([
        {"a": 1, "b": 2},
        {"a": 3, "b": 4}
    ])
    output = repr(ds)
    expected_lines = [
        "a, b",
        "1, 2",
        "3, 4"
    ]
    for line in expected_lines:
        assert line in output
    assert "... (" not in output


def test_repr_over_10_rows():
    data = [{"a": i, "b": i * 2} for i in range(15)]
    ds = tx.DataSet(data)
    output = repr(ds)

    # Header and first 10 rows
    assert output.startswith("a, b")
    assert "0, 0" in output
    assert "9, 18" in output

    # Ellipsis indicator
    assert "... (15 rows total)" in output


def test_repr_empty_dataset():
    ds = tx.DataSet([])
    output = repr(ds)
    assert output == ""


def test_repr_html_empty_dataset():
    ds = tx.DataSet([])
    html = ds._repr_html_()
    assert html.strip() == "<i>Empty DataSet</i>"


def test_repr_html_basic():
    ds = tx.DataSet([
        {"a": 1, "b": 2},
        {"a": 3, "b": 4}
    ])
    html = ds._repr_html_()
    assert "<table>" in html
    assert "<th>a</th>" in html
    assert "<th>b</th>" in html
    assert "<td>1</td>" in html
    assert "<td>4</td>" in html
    assert "<thead>" in html and "<tbody>" in html


def test_repr_html_with_index():
    ds = tx.DataSet([
        {"id": 100, "val": "apple"},
        {"id": 200, "val": "banana"}
    ])
    ds.set_index("id")
    html = ds._repr_html_()
    
    assert "<th>val</th>" in html
    assert "<td><strong>100<strong></td>" in html
    assert "<td>apple</td>" in html


from datetime import datetime

def test_repr_html_with_datetime_index():
    ds = tx.DataSet([
        {"dt": datetime(2024, 1, 1), "x": 10},
        {"dt": datetime(2024, 1, 2), "x": 20}
    ])
    ds.set_index("dt")
    html = ds._repr_html_()
    
    assert "<td><strong>2024-01-01<strong></td>" in html
    assert "<td>10</td>" in html

def test_head_default():
    ds = tx.DataSet([
        {"a": 1}, {"a": 2}, {"a": 3}, {"a": 4}, {"a": 5}, {"a": 6}
    ])
    head = ds.head()
    assert head.shape() == (5, 1)
    assert head.data == [{"a": 1}, {"a": 2}, {"a": 3}, {"a": 4}, {"a": 5}]

def test_head_custom_n():
    ds = tx.DataSet([
        {"a": i} for i in range(10)
    ])
    head = ds.head(3)
    assert head.data == [{"a": 0}, {"a": 1}, {"a": 2}]

def test_tail_default():
    ds = tx.DataSet([
        {"a": 1}, {"a": 2}, {"a": 3}, {"a": 4}, {"a": 5}, {"a": 6}
    ])
    tail = ds.tail()
    assert tail.shape() == (5, 1)
    assert tail.data == [{"a": 2}, {"a": 3}, {"a": 4}, {"a": 5}, {"a": 6}]

def test_tail_custom_n():
    ds = tx.DataSet([
        {"a": i} for i in range(10)
    ])
    tail = ds.tail(3)
    assert tail.data == [{"a": 7}, {"a": 8}, {"a": 9}]

def test_head_more_than_length():
    ds = tx.DataSet([{"a": 1}, {"a": 2}])
    head = ds.head(5)
    assert head.data == [{"a": 1}, {"a": 2}]

def test_info_basic(capsys):
    ds = tx.DataSet([
        {"a": 1, "b": "hello"},
        {"a": 2, "b": "world"},
        {"a": None, "b": "!"}
    ])

    ds.info()
    captured = capsys.readouterr().out

    assert "<class 'atrax.Atrax'>" in captured
    assert "columns (total 2):" in captured
    assert "a" in captured and "b" in captured
    assert "int" in captured or "str" in captured
    assert "Non-Null" in captured

def test_info_with_index(capsys):
    ds = tx.DataSet([
        {"date": "2024-01-01", "val": 100},
        {"date": "2024-01-02", "val": 200}
    ])
    ds.set_index("date")

    ds.info()
    captured = capsys.readouterr().out

    assert "Index:" in captured
    assert "name: date" in captured
    assert "dtype: str" in captured

def test_info_empty_dataset(capsys):
    ds = tx.DataSet([])
    ds.info()
    captured = capsys.readouterr().out

    assert "No data available" in captured

def test_info_datetime_index(capsys):
    from datetime import datetime
    ds = tx.DataSet([
        {"dt": datetime(2023, 1, 1), "val": 1},
        {"dt": datetime(2023, 1, 2), "val": 2},
    ])
    ds.set_index("dt")
    ds.info()
    captured = capsys.readouterr().out
    assert "dtype: datetime" in captured


def test_info_int_index(capsys):
    ds = tx.DataSet([
        {"id": 1, "val": "a"},
        {"id": 2, "val": "b"},
    ])
    ds.set_index("id")
    ds.info()
    captured = capsys.readouterr().out
    assert "dtype: int" in captured


def test_info_float_index(capsys):
    ds = tx.DataSet([
        {"id": 1.1, "val": "x"},
        {"id": 2.2, "val": "y"},
    ])
    ds.set_index("id")
    ds.info()
    captured = capsys.readouterr().out
    assert "dtype: float" in captured


def test_info_str_index(capsys):
    ds = tx.DataSet([
        {"key": "one", "val": 10},
        {"key": "two", "val": 20},
    ])
    ds.set_index("key")
    ds.info()
    captured = capsys.readouterr().out
    assert "dtype: str" in captured


class CustomKey: pass

def test_info_custom_index_type(capsys):
    ds = tx.DataSet([
        {"key": CustomKey(), "val": 123},
        {"key": CustomKey(), "val": 456},
    ])
    ds.set_index("key")
    ds.info()
    captured = capsys.readouterr().out
    assert "dtype: CustomKey" in captured



def test_loc_invalid_date_string_triggers_valueerror_continue():
    ds = tx.DataSet([
        {"dt": datetime(2024, 1, 1), "val": 100},
        {"dt": datetime(2024, 1, 2), "val": 200},
    ])
    ds.set_index("dt")

    # This string doesn't match any of the three formats
    result = ds.loc["bad-date-format"]
    
    # Should return empty DataSet, not crash
    assert result.shape() == (0, 0)  # 0 rows, 1 column ("val")

def test_loc_fallback_to_all_rows_on_invalid_filter():
    ds = tx.DataSet([
        {"a": 1, "b": 10},
        {"a": 2, "b": 20},
    ])

    result = ds.loc[(["not", "a", "filter"], "a")]
    
    # Should return all rows, only column "a"
    assert result.shape() == (2, 1)
    assert result.data == [{"a": 1}, {"a": 2}]


def test_merge_inner_join():
    left = tx.DataSet([
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ])
    right = tx.DataSet([
        {"id": 2, "score": 90},
        {"id": 3, "score": 95},
    ])
    result = left.merge(right, on="id", how="inner")
    assert result.shape() == (1, 3)
    assert result.data[0]["id"] == 2
    assert result.data[0]["name_x"] == "Bob"
    assert result.data[0]["score"] == 90

def test_merge_left_join():
    left = tx.DataSet([
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ])
    right = tx.DataSet([
        {"id": 2, "score": 90},
        {"id": 3, "score": 95},
    ])
    result = left.merge(right, on="id", how="left")
    assert result.shape() == (2, 2)
    assert result.data[0]["id"] == 1
    assert result.data[0].get("score") is None    

def test_merge_right_join():
    left = tx.DataSet([
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ])
    right = tx.DataSet([
        {"id": 2, "score": 90},
        {"id": 3, "score": 95},
    ])
    result = left.merge(right, on="id", how="right")
    assert result.shape() == (2, 3)
    assert result.data[1].get("name_x") is None    


def test_merge_with_column_name_collision():
    left = tx.DataSet([
        {"id": 1, "value": 100},
    ])
    right = tx.DataSet([
        {"id": 1, "value": 999},
    ])
    result = left.merge(right, on="id")
    row = result.data[0]
    assert row["value_x"] == 100
    assert row["value_y"] == 999    


def test_merge_invalid_other_type():
    left = tx.DataSet([{"id": 1}])
    with pytest.raises(TypeError, match="Can only merge with another DataSet"):
        left.merge("not_a_dataset", on="id")    

def test_astype_conversion_failure_sets_none():
    ds = tx.DataSet([
        {"x": "not-a-number"},
        {"x": "42"},
    ])
    converted = ds.astype({"x": int})

    assert converted.data[0]["x"] is None  # failed conversion
    assert converted.data[1]["x"] == 42    # successful conversion

def test_convert_column_successful():
    ds = tx.DataSet([
        {"x": "1"},
        {"x": "2"}
    ])
    ds.convert_column("x", int)

    assert ds.data[0]["x"] == 1
    assert ds.data[1]["x"] == 2


def test_convert_column_with_failure():
    ds = tx.DataSet([
        {"x": "100"},
        {"x": "not-a-number"}
    ])
    ds.convert_column("x", int)

    assert ds.data[0]["x"] == 100
    assert ds.data[1]["x"] == "not-a-number"  # unchanged due to exception


def test_convert_column_missing_column():
    ds = tx.DataSet([
        {"a": 1},
        {"b": 2},
    ])
    ds.convert_column("x", lambda v: v * 2)

    # Should not throw; dataset stays unchanged
    assert ds.data == [{"a": 1}, {"b": 2}]


def test_convert_column_identity():
    ds = tx.DataSet([
        {"x": 10},
        {"x": 20}
    ])
    ds.convert_column("x", lambda x: x)
    assert ds.data == [{"x": 10}, {"x": 20}]


def test_to_pandas_basic():
    ds = tx.DataSet([
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
    ])
    df = ds.to_pandas()
    
    assert df.shape == (2, 2)
    assert list(df.columns) == ["a", "b"]
    assert df.iloc[0]["a"] == 1
    assert df.iloc[1]["b"] == 4


def test_to_pandas_with_index():
    ds = tx.DataSet([
        {"date": "2024-01-01", "value": 10},
        {"date": "2024-01-02", "value": 20}
    ])
    ds.set_index("date")

    df = ds.to_pandas()
    
    assert df.index.name == "date"
    assert list(df.index) == ["2024-01-01", "2024-01-02"]
    assert df.loc["2024-01-02"]["value"] == 20


def test_to_pandas_empty():
    ds = tx.DataSet([])
    df = ds.to_pandas()
    
    assert df.empty
    assert isinstance(df, pd.DataFrame)

def test_to_csv_string_output():
    ds = tx.DataSet([
        {"a": 1, "b": 2},
        {"a": 3, "b": 4}
    ])
    csv_str = ds.to_csv()
    
    assert "a,b" in csv_str
    assert "1,2" in csv_str
    assert "3,4" in csv_str


import tempfile
import os

def test_to_csv_file_write():
    ds = tx.DataSet([
        {"x": 10, "y": 20}
    ])

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        path = tmp.name

    try:
        ds.to_csv(path=path)
        with open(path, "r") as f:
            content = f.read()

        assert "x,y" in content
        assert "10,20" in content
    finally:
        os.remove(path)


def test_to_csv_empty_dataset():
    ds = tx.DataSet([])
    csv_str = ds.to_csv()

    assert csv_str.strip() == ""  # no headers, no rows


def test_set_index_inplace():
    ds = tx.DataSet([
        {"id": 1, "val": "a"},
        {"id": 2, "val": "b"}
    ])
    ds.set_index("id", inplace=True)

    assert ds._index == [1, 2]
    assert ds._index_name == "id"
    assert "id" in ds.columns  # should still be present


def test_set_index_inplace_with_drop():
    ds = tx.DataSet([
        {"id": 10, "x": "foo"},
        {"id": 20, "x": "bar"}
    ])
    ds.set_index("id", drop=True)

    assert ds._index == [10, 20]
    assert "id" not in ds.columns


def test_set_index_return_new_dataset():
    ds = tx.DataSet([
        {"key": "a", "val": 1},
        {"key": "b", "val": 2}
    ])
    new_ds = ds.set_index("key", inplace=False)

    assert new_ds._index_name == "key"
    assert new_ds._index == ["a", "b"]
    assert ds._index_name is None  # original remains unchanged



def test_set_index_column_not_found():
    ds = tx.DataSet([
        {"a": 1, "b": 2}
    ])
    with pytest.raises(KeyError, match="Column 'z' not found in dataset."):
        ds.set_index("z")


def test_set_index_values_are_correct():
    ds = tx.DataSet([
        {"idx": "i1", "val": 9},
        {"idx": "i2", "val": 8}
    ])
    ds.set_index("idx")

    assert ds._index == ["i1", "i2"]


def test_reset_index_returns_new_dataset():
    ds = tx.DataSet([
        {"id": 10, "val": "a"},
        {"id": 20, "val": "b"}
    ])
    ds.set_index("id")
    new_ds = ds.reset_index()

    assert new_ds._index == [0, 1]
    assert new_ds._index_name is None
    assert new_ds.data == ds.data  # data should be the same
    assert ds._index != new_ds._index  # original not modified

def test_reset_index_inplace():
    ds = tx.DataSet([
        {"id": 1}, {"id": 2}
    ])
    ds.set_index("id")
    ds.reset_index(inplace=True)

    assert ds._index == [1, 2]


def test_reset_index_preserves_data():
    ds = tx.DataSet([
        {"a": "x"},
        {"a": "y"}
    ])
    ds.set_index("a")
    new_ds = ds.reset_index()

    assert new_ds.data == [{"a": "x"}, {"a": "y"}]

def test_rename_columns_new_dataset():
    ds = tx.DataSet([
        {"a": 1, "b": 2},
        {"a": 3, "b": 4}
    ])
    new_ds = ds.rename(columns={"a": "x"})

    assert new_ds.columns == ["x", "b"]
    assert new_ds.data == [{"x": 1, "b": 2}, {"x": 3, "b": 4}]
    assert ds.columns == ["a", "b"]  # original unchanged


def test_rename_columns_inplace():
    ds = tx.DataSet([
        {"col1": 10, "col2": 20}
    ])
    ds.rename(columns={"col2": "renamed"}, inplace=True)

    assert ds.columns == ["col1", "renamed"]
    assert ds.data[0] == {"col1": 10, "renamed": 20}


def test_rename_no_columns_dict_returns_self():
    ds = tx.DataSet([
        {"a": 1}
    ])
    result = ds.rename(columns=None)

    assert result is ds


def test_rename_partial_columns():
    ds = tx.DataSet([
        {"a": 1, "b": 2}
    ])
    new_ds = ds.rename(columns={"a": "x"})

    assert new_ds.columns == ["x", "b"]


def test_drop_columns_non_inplace():
    ds = tx.DataSet([
        {"a": 1, "b": 2, "c": 3}
    ])
    new_ds = ds.drop(columns=["b", "c"])
    assert new_ds.columns == ["a"]
    assert new_ds.data == [{"a": 1}]
    assert ds.columns == ["a", "b", "c"]  # original unchanged


def test_drop_rows_by_index():
    ds = tx.DataSet([
        {"a": 1},
        {"a": 2},
        {"a": 3}
    ])
    new_ds = ds.drop(index=[0, 2])
    assert new_ds.data == [{"a": 2}]


def test_drop_columns_and_rows():
    ds = tx.DataSet([
        {"a": 1, "b": 2},
        {"a": 3, "b": 4}
    ])
    new_ds = ds.drop(columns=["b"], index=[1])
    assert new_ds.data == [{"a": 1}]


def test_drop_inplace_modification():
    ds = tx.DataSet([
        {"x": 1, "y": 2}
    ])
    ds.drop(columns=["y"], inplace=True)
    assert ds.columns == ["x"]
    assert ds.data == [{"x": 1}]


def test_drop_no_args_returns_same():
    ds = tx.DataSet([
        {"a": 1, "b": 2}
    ])
    new_ds = ds.drop()
    assert new_ds.data == [{"a": 1, "b": 2}]


def test_drop_all_columns_results_empty_rows():
    ds = tx.DataSet([
        {"a": 1, "b": 2}
    ])
    new_ds = ds.drop(columns=["a", "b"])
    assert new_ds.data == [{}]
    assert new_ds.columns == []

def test_filter_raises_value_error_without_args():
    ds = tx.DataSet([
        {"a": 1, "b": 2}
    ])
    
    with pytest.raises(ValueError, match="Must provide 'items' or 'like"):
        ds.filter()


def test_sort_raises_keyerror_for_missing_column():
    ds = tx.DataSet([
        {"a": 1, "b": 2}
    ])

    with pytest.raises(KeyError, match="Column 'c' not found in dataset."):
        ds.sort("c")


def test_sort_valid_column():
    ds = tx.DataSet([
        {"a": 3},
        {"a": 1},
        {"a": 2}
    ])
    sorted_ds = ds.sort("a")
    assert [row["a"] for row in sorted_ds.data] == [1, 2, 3]
  


def test_apply_axis_not_supported():
    ds = tx.DataSet([
        {"x": 1}, {"x": 2}
    ])
    with pytest.raises(NotImplementedError, match="Only row-wise operations"):
        ds.apply(lambda row: row, axis=0)


def test_apply_returns_dataset():
    ds = tx.DataSet([
        {"a": 1},
        {"a": 2}
    ])
    result = ds.apply(lambda row: {"a_squared": row["a"] ** 2})
    
    assert isinstance(result, tx.DataSet)
    assert result.data == [{"a_squared": 1}, {"a_squared": 4}]


def test_apply_returns_list():
    ds = tx.DataSet([
        {"a": 1},
        {"a": 2}
    ])
    result = ds.apply(lambda row: row["a"] + 1)
    
    assert isinstance(result, list)
    assert result == [2, 3]


def test_apply_custom_logic():
    ds = tx.DataSet([
        {"name": "Alice", "score": 90},
        {"name": "Bob", "score": 80}
    ])
    result = ds.apply(lambda row: {"name": row["name"], "passed": row["score"] >= 85})

    assert result.data == [
        {"name": "Alice", "passed": True},
        {"name": "Bob", "passed": False}
    ]
