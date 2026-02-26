import pytest

from src.fight_result import FightResult


def test_valid_fight_result():
    result = FightResult(
        winner="Tigers",
        loser="Eagles",
        win_probability=72,
        narrative="Tigers dominated from the start.",
    )
    assert result.winner == "Tigers"
    assert result.loser == "Eagles"
    assert result.win_probability == 72
    assert result.narrative == "Tigers dominated from the start."


def test_probability_boundary_values():
    r = FightResult("A", "B", 0, "narrative")
    assert r.win_probability == 0

    r = FightResult("A", "B", 100, "narrative")
    assert r.win_probability == 100


def test_probability_out_of_range():
    with pytest.raises(ValueError, match="win_probability"):
        FightResult("A", "B", 101, "narrative")

    with pytest.raises(ValueError, match="win_probability"):
        FightResult("A", "B", -1, "narrative")


def test_empty_winner_raises():
    with pytest.raises(ValueError, match="winner"):
        FightResult("", "B", 60, "narrative")


def test_empty_loser_raises():
    with pytest.raises(ValueError, match="loser"):
        FightResult("A", "", 60, "narrative")


def test_empty_narrative_raises():
    with pytest.raises(ValueError, match="narrative"):
        FightResult("A", "B", 60, "")
