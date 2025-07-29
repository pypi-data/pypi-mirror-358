from atrax.core.qcut import qcut

def test_qcut_basic_quartiles():
    data = [1, 2, 3, 4, 5, 6, 7, 8]
    result = qcut(data, q=4)
    # Should split into bins: [1–2], [3–4], [5–6], [7–8]
    assert result == [0, 0, 0, 1, 1, 2, 2, 3]

def test_qcut_with_labels():
    data = [10, 20, 30, 40]
    labels = ['low', 'med-low', 'med-high', 'high']
    result = qcut(data, q=4, labels=labels)
    assert result == ['low', 'low', 'med-low', 'med-high']

def test_qcut_handles_none():
    data = [5, None, 15, 25, None, 35]
    result = qcut(data, q=2)
    assert result[1] is None and result[4] is None
    assert result[0] in [0, 1] and result[2] in [0, 1]

def test_qcut_empty_input():
    assert qcut([], q=4) == []

def test_qcut_single_value():
    assert qcut([10], q=4) == [0]

def test_qcut_all_same_value():
    assert qcut([5, 5, 5, 5], q=2) == [0, 0, 0, 0]

def test_qcut_custom_q():
    data = [1, 2, 3, 4, 5]
    result = qcut(data, q=5)
    # One item per quantile: [1], [2], [3], [4], [5]
    assert result == [0, 0, 1, 2, 3]


def test_qcut_fallback_last_bin():
    data = [1, 2, 3, 4, 100]  # 100 is far from the rest
    labels = ['Q1', 'Q2', 'Q3', 'Q4']
    result = qcut(data, q=4, labels=labels)
    assert result[-1] == 'Q4'  # should hit the fallback: labels[-1]


def test_qcut_forces_last_bin_return():
    # This forces the final value (10) to exceed computed boundaries
    data = [1, 1, 1, 1, 10]
    labels = ['A', 'B', 'C', 'D']
    result = qcut(data, q=4, labels=labels)
    assert result[-1] == 'D'
