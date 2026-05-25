from __future__ import annotations

from jarvis_app.parsers.level_parser import parse_levels


def test_parse_levels_ignores_non_level_text() -> None:
    assert parse_levels("Please ignore this text") is None


def test_parse_levels_parses_basement_word_range() -> None:
    parsed = parse_levels("Basement 3 to Basement 1")
    assert parsed is not None
    assert parsed["levels"] == ["B3", "B2", "B1"]


def test_parse_levels_parses_exclusions() -> None:
    parsed = parse_levels("Levels L1 to L4, exclude L2, L3")
    assert parsed is not None
    assert parsed["levels"] == ["L1", "L4"]


def test_parse_levels_parses_mezzanine_variants() -> None:
    parsed = parse_levels("Mezzanine on L1, L2 and L5; Level 11 Mezzanine")
    assert parsed is not None
    assert "L1 Mezzanine" in parsed["levels"]
    assert "L2 Mezzanine" in parsed["levels"]
    assert "L5 Mezzanine" in parsed["levels"]
    assert "L11 Mezzanine" in parsed["levels"]


def test_parse_levels_parses_gf_to_level_range() -> None:
    parsed = parse_levels("GF to Level 3")
    assert parsed is not None
    assert parsed["levels"] == ["GF", "L1", "L2", "L3"]
