from atrax import Atrax as tx
import pytest

# Simple dataset for reuse
DATA = [
    {"dept": "A", "sales": 100, "units": 2},
    {"dept": "A", "sales": 150, "units": 3},
    {"dept": "B", "sales": 200, "units": 5},
]

def test_groupby_basic_sum():
    ds = tx.DataSet(DATA)
    grouped = ds.groupby("dept").sum()
    result = {row["dept"]: row["sales"] for row in grouped.data}
    assert result["A"] == 250
    assert result["B"] == 200

def test_groupby_basic_mean():
    ds = tx.DataSet(DATA)
    grouped = ds.groupby("dept").mean()
    result = {row["dept"]: row["sales"] for row in grouped.data}
    assert result["A"] == 125
    assert result["B"] == 200

def test_groupby_agg_with_string_function():
    ds = tx.DataSet(DATA)
    grouped = ds.groupby("dept").agg({"sales": "sum", "units": "count"})
    row_a = [r for r in grouped.data if r["dept"] == "A"][0]
    assert row_a["sales_sum"] == 250
    assert row_a["units_count"] == 2

def test_groupby_agg_with_multiple_aggs():
    ds = tx.DataSet(DATA)
    grouped = ds.groupby("dept").agg({"sales": ["sum", "max"]})
    row_a = [r for r in grouped.data if r["dept"] == "A"][0]
    assert row_a["sales_sum"] == 250
    assert row_a["sales_max"] == 150

def test_groupby_agg_with_custom_function():
    ds = tx.DataSet(DATA)
    grouped = ds.groupby("dept").agg({"sales": lambda x: max(x) - min(x)})
    row_a = [r for r in grouped.data if r["dept"] == "A"][0]
    assert row_a["sales_<lambda>"] == 50

@pytest.mark.skip(reason="We may not need this anymore.")
def test_groupby_agg_unsupported_function():
    ds = tx.DataSet(DATA)
    with pytest.raises(ValueError, match="Unsupported agg: badagg"):
        ds.groupby("dept").agg({"sales": "badagg"})

@pytest.mark.skip(reason="We may not need this anymore.")
def test_groupby_agg_invalid_function_type():
    ds = tx.DataSet(DATA)
    with pytest.raises(TypeError, match="Aggregation must be string or function"):
        ds.groupby("dept").agg({"sales": 123})

def test_groupby_on_multiple_keys():
    ds = tx.DataSet([
        {"dept": "A", "region": "X", "sales": 10},
        {"dept": "A", "region": "X", "sales": 20},
        {"dept": "A", "region": "Y", "sales": 30},
    ])
    grouped = ds.groupby(["dept", "region"]).sum()
    assert any(row["region"] == "X" and row["sales"] == 30 for row in grouped.data)
    assert any(row["region"] == "Y" and row["sales"] == 30 for row in grouped.data)

def test_groupby_agg_min():
    ds = tx.DataSet([
        {"dept": "A", "sales": 100},
        {"dept": "A", "sales": 80},
        {"dept": "B", "sales": 300},
    ])
    grouped = ds.groupby("dept").agg({"sales": "min"})

    result = {row["dept"]: row["sales_min"] for row in grouped.data}
    assert result["A"] == 80
    assert result["B"] == 300

def test_groupby_agg_mean():
    ds = tx.DataSet([
        {"dept": "A", "sales": 100},
        {"dept": "A", "sales": 200},
        {"dept": "B", "sales": 300},
    ])
    grouped = ds.groupby("dept").agg({"sales": "mean"})

    result = {row["dept"]: row["sales_mean"] for row in grouped.data}
    assert result["A"] == 150  # (100 + 200) / 2
    assert result["B"] == 300
