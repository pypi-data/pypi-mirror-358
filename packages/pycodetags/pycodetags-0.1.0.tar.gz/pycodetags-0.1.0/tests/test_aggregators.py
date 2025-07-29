from __future__ import annotations

from code_tags.aggregate import aggregate_all_kinds


def test_aggregate_all_kinds():
    # TODO: make stronger assertions
    assert aggregate_all_kinds("code_tags", __file__)
