import pytest
from atrax.core.cut import cut  # Replace with the actual import path


def test_cut_empty_input():
    assert cut([]) == []


def test_cut_default_bins():
    values = [1, 2, 3, 4, 5]
    result = cut(values, bins=2)
    assert result == [0, 0, 1, 1, 1]


def test_cut_with_labels():
    values = [1, 2, 3, 4, 5]
    labels = ['Low', 'High']
    result = cut(values, bins=2, labels=labels)
    assert result == ['Low', 'Low', 'High', 'High', 'High']


def test_cut_with_custom_bin_edges():
    values = [10, 20, 30, 40, 50]
    bin_edges = [10, 25, 50]
    labels = ['Small', 'Large']
    result = cut(values, bins=bin_edges, labels=labels)
    assert result == ['Small', 'Small', 'Large', 'Large', 'Large']


def test_cut_upper_tie_breaker():
    values = [10, 20, 30]
    bins = [10, 20, 30]
    labels = ['A', 'B']
    result = cut(values, bins=bins, labels=labels, tie_breaker='upper')
    assert result == ['A', 'B', 'B']  # 20 should go to 'B' because of 'upper'


def test_cut_lower_tie_breaker():
    values = [10, 20, 30]
    bins = [10, 20, 30]
    labels = ['A', 'B']
    result = cut(values, bins=bins, labels=labels, tie_breaker='lower')
    assert result == ['A', 'A', 'B']  # 20 goes to 'A' due to 'lower'


def test_cut_with_none_values():
    values = [10, None, 30, None]
    bins = [10, 20, 40]
    labels = ['Low', 'High']
    result = cut(values, bins=bins, labels=labels)
    assert result == ['Low', None, 'High', None]


def test_cut_edge_value_on_upper_bin():
    values = [10, 20]
    bins = [10, 20]
    result = cut(values, bins=bins)
    assert result == [0, 0]  # Because value == max gets mapped to last bin index
