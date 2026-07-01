from __future__ import annotations

import pytest

from ai_readable_pdf_capture.models import parse_advance, parse_region


def test_parse_region() -> None:
    region = parse_region("1,2,300,400")
    assert region is not None
    assert region.as_tuple() == (1, 2, 300, 400)


@pytest.mark.parametrize("value", ["1,2,3", "1,2,0,4", "a,b,c,d"])
def test_parse_region_invalid(value: str) -> None:
    with pytest.raises(ValueError):
        parse_region(value)


def test_parse_advance_key() -> None:
    action = parse_advance("key:right")
    assert action.kind == "key"
    assert action.value == "right"


def test_parse_advance_click() -> None:
    action = parse_advance("click:10,20")
    assert action.kind == "click"
    assert action.value == (10, 20)


def test_parse_advance_none() -> None:
    action = parse_advance("none")
    assert action.kind == "none"
