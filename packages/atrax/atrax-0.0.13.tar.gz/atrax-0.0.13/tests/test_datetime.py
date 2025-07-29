from datetime import datetime
from atrax import to_datetime
from atrax import date_range
from atrax import Atrax as tx
import pytest

def test_to_datetime():

    assert to_datetime("2025-06-23") == datetime(2025, 6, 23)
    assert to_datetime(["06/23/2025", "06/24/2025"]) == [
        datetime(2025, 6, 23), datetime(2025, 6, 24)
    ]

def test_to_datetime_with_format():
    assert to_datetime("23-06-2025", format="%d-%m-%Y") == datetime(2025, 6, 23)
    assert to_datetime(["23-06-2025", "24-06-2025"], format="%d-%m-%Y") == [
        datetime(2025, 6, 23), datetime(2025, 6, 24)
    ] 

# ---------- Tests for to_datetime ----------

def test_to_datetime_single_string():
    assert to_datetime("2024-06-25") == datetime(2024, 6, 25)

def test_to_datetime_list():
    dates = ["2024-01-01", "2024-02-01"]
    result = to_datetime(dates)
    assert result == [datetime(2024, 1, 1), datetime(2024, 2, 1)]

def test_to_datetime_with_format():
    date = "25-06-2024"
    fmt = "%d-%m-%Y"
    assert to_datetime(date, fmt) == datetime(2024, 6, 25)

def test_to_datetime_invalid_type():
    with pytest.raises(TypeError):
        to_datetime(123)       



# tests for date_range function
def test_date_range_with_end_days():
    result = date_range("2023-01-01", "2023-01-03", freq='D')
    expected = [
        datetime(2023, 1, 1),
        datetime(2023, 1, 2),
        datetime(2023, 1, 3)
    ]
    assert result == expected


def test_date_range_with_periods_days():
    result = date_range("2023-01-01", periods=3, freq='D')
    expected = [
        datetime(2023, 1, 1),
        datetime(2023, 1, 2),
        datetime(2023, 1, 3)
    ]
    assert result == expected


def test_date_range_with_hours():
    result = date_range("2023-01-01T00:00:00", "2023-01-01T03:00:00", freq='H')
    expected = [
        datetime(2023, 1, 1, 0, 0),
        datetime(2023, 1, 1, 1, 0),
        datetime(2023, 1, 1, 2, 0),
        datetime(2023, 1, 1, 3, 0)
    ]
    assert result == expected

def test_date_range_with_minutes():
    result = date_range("2023-01-01T00:00:00", periods=3, freq='T')
    expected = [
        datetime(2023, 1, 1, 0, 0),
        datetime(2023, 1, 1, 0, 1),
        datetime(2023, 1, 1, 0, 2)
    ]
    assert result == expected


def test_date_range_with_custom_format():
    result = date_range("01-01-2023", "03-01-2023", freq='D', fmt='%d-%m-%Y')
    expected = [
        datetime(2023, 1, 1),
        datetime(2023, 1, 2),
        datetime(2023, 1, 3)
    ]
    assert result == expected


def test_date_range_invalid_freq():
    with pytest.raises(ValueError, match="Unsupported frequency"):
        date_range("2023-01-01", periods=3, freq='X')


def test_date_range_missing_end_and_periods():
    with pytest.raises(ValueError, match="Either 'end' or 'periods' must be specified"):
        date_range("2023-01-01")    

def test_date_range_invalid_start_type():
    with pytest.raises(TypeError, match="Start and end must be strings or datetime objects"):
        date_range(12345, periods=3)


def test_date_range_empty_result():
    result = date_range("2023-01-03", "2023-01-01", freq='D')
    assert result == []        
 


# new suite !!!!!!!!!!!!!!!!!!!!!!!!

def test_to_datetime_single_iso():
    assert to_datetime("2023-10-01") == datetime(2023, 10, 1)

def test_to_datetime_single_custom_format():
    assert to_datetime("01/10/2023", fmt="%d/%m/%Y") == datetime(2023, 10, 1)

def test_to_datetime_list():
    result = to_datetime(["2023-10-01", "2023-10-02"])
    expected = [datetime(2023, 10, 1), datetime(2023, 10, 2)]
    assert result == expected

def test_to_datetime_invalid_format():
    with pytest.raises(ValueError):
        to_datetime("not a date")

def test_to_datetime_wrong_type():
    with pytest.raises(TypeError):
        to_datetime(12345)

# ---------- Tests for date_range ----------

def test_date_range_with_end():
    result = date_range("2023-01-01", "2023-01-03", freq='D')
    expected = [datetime(2023, 1, 1), datetime(2023, 1, 2), datetime(2023, 1, 3)]
    assert result == expected

def test_date_range_with_periods():
    result = date_range("2023-01-01", periods=3, freq='D')
    expected = [datetime(2023, 1, 1), datetime(2023, 1, 2), datetime(2023, 1, 3)]
    assert result == expected

def test_date_range_with_invalid_freq():
    with pytest.raises(ValueError):
        date_range("2023-01-01", periods=3, freq='Z')

def test_date_range_missing_end_and_periods():
    with pytest.raises(ValueError):
        date_range("2023-01-01")

def test_date_range_reverse_start_end():
    result = date_range("2023-01-03", "2023-01-01", freq='D')
    assert result == []


