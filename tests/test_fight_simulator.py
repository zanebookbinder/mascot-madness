import json
import pytest

from src.fight_result import FightResult
from src.fight_simulator import FightSimulator


# ---------------------------------------------------------------------------
# Tests: Mock mode initialization
# ---------------------------------------------------------------------------

class TestMockModeInit:

    def test_explicit_mock_mode(self):
        sim = FightSimulator(mock_mode=True)
        assert sim.mock_mode is True

    def test_auto_mock_without_api_key(self):
        # conftest.py removes ANTHROPIC_API_KEY for all tests
        sim = FightSimulator()
        assert sim.mock_mode is True

    def test_mock_mode_does_not_create_client(self):
        sim = FightSimulator(mock_mode=True)
        assert sim._client is None


# ---------------------------------------------------------------------------
# Tests: Mock fight results
# ---------------------------------------------------------------------------

class TestMockFight:

    def test_returns_fight_result_instance(self):
        sim = FightSimulator(mock_mode=True)
        result = sim.simulate_fight("Wildcats", "Tigers")
        assert isinstance(result, FightResult)

    def test_winner_is_one_of_two_teams(self):
        sim = FightSimulator(mock_mode=True)
        result = sim.simulate_fight("Wildcats", "Tigers")
        assert result.winner in ("Wildcats", "Tigers")

    def test_loser_is_the_other_team(self):
        sim = FightSimulator(mock_mode=True)
        result = sim.simulate_fight("Wildcats", "Tigers")
        teams = {"Wildcats", "Tigers"}
        assert result.loser in teams
        assert result.winner != result.loser

    def test_probability_in_valid_range(self):
        sim = FightSimulator(mock_mode=True)
        result = sim.simulate_fight("Eagles", "Bears")
        assert 0 <= result.win_probability <= 100

    def test_narrative_is_nonempty(self):
        sim = FightSimulator(mock_mode=True)
        result = sim.simulate_fight("Eagles", "Bears")
        assert len(result.narrative) > 0

    def test_mock_is_deterministic(self):
        sim = FightSimulator(mock_mode=True)
        r1 = sim.simulate_fight("Eagles", "Bears")
        r2 = sim.simulate_fight("Eagles", "Bears")
        assert r1.winner == r2.winner
        assert r1.win_probability == r2.win_probability

    def test_mock_same_result_regardless_of_argument_order(self):
        sim = FightSimulator(mock_mode=True)
        r1 = sim.simulate_fight("Eagles", "Bears")
        r2 = sim.simulate_fight("Bears", "Eagles")
        assert r1.winner == r2.winner
        assert r1.win_probability == r2.win_probability

    def test_different_matchups_can_produce_different_winners(self):
        sim = FightSimulator(mock_mode=True)
        results = set()
        pairs = [
            ("Wildcats", "Tigers"),
            ("Eagles", "Bears"),
            ("Spartans", "Hurricanes"),
            ("Bulldogs", "Gators"),
            ("Blue Devils", "Tar Heels"),
            ("Boilermakers", "Hawkeyes"),
        ]
        for t1, t2 in pairs:
            r = sim.simulate_fight(t1, t2)
            results.add(r.winner)
        # With 6 different matchups we expect at least 2 distinct winners
        assert len(results) >= 2


# ---------------------------------------------------------------------------
# Tests: _parse_claude_response
# ---------------------------------------------------------------------------

class TestParseClaudeResponse:

    def test_valid_json_returns_fight_result(self):
        sim = FightSimulator(mock_mode=True)
        raw = json.dumps({
            "winner": "Wildcats",
            "win_probability": 72,
            "narrative": "Wildcats pounced with terrifying speed.",
        })
        result = sim._parse_claude_response(raw, "Wildcats", "Tigers")
        assert result.winner == "Wildcats"
        assert result.loser == "Tigers"
        assert result.win_probability == 72
        assert result.narrative == "Wildcats pounced with terrifying speed."

    def test_winner_can_be_second_team(self):
        sim = FightSimulator(mock_mode=True)
        raw = json.dumps({
            "winner": "Tigers",
            "win_probability": 63,
            "narrative": "Tigers roared back.",
        })
        result = sim._parse_claude_response(raw, "Wildcats", "Tigers")
        assert result.winner == "Tigers"
        assert result.loser == "Wildcats"

    def test_strips_markdown_code_fence(self):
        sim = FightSimulator(mock_mode=True)
        raw = "```json\n" + json.dumps({
            "winner": "Wildcats",
            "win_probability": 80,
            "narrative": "Dominant.",
        }) + "\n```"
        result = sim._parse_claude_response(raw, "Wildcats", "Tigers")
        assert result.winner == "Wildcats"

    def test_strips_plain_code_fence(self):
        sim = FightSimulator(mock_mode=True)
        raw = "```\n" + json.dumps({
            "winner": "Tigers",
            "win_probability": 55,
            "narrative": "Barely.",
        }) + "\n```"
        result = sim._parse_claude_response(raw, "Wildcats", "Tigers")
        assert result.winner == "Tigers"

    def test_invalid_json_raises_value_error(self):
        sim = FightSimulator(mock_mode=True)
        with pytest.raises(ValueError, match="JSON"):
            sim._parse_claude_response("not json at all", "Wildcats", "Tigers")

    def test_unknown_winner_raises_value_error(self):
        sim = FightSimulator(mock_mode=True)
        raw = json.dumps({
            "winner": "UnknownTeam",
            "win_probability": 60,
            "narrative": "Mystery winner.",
        })
        with pytest.raises(ValueError, match="winner"):
            sim._parse_claude_response(raw, "Wildcats", "Tigers")

    def test_case_insensitive_winner_matching(self):
        sim = FightSimulator(mock_mode=True)
        raw = json.dumps({
            "winner": "wildcats",  # lowercase
            "win_probability": 70,
            "narrative": "Won.",
        })
        result = sim._parse_claude_response(raw, "Wildcats", "Tigers")
        assert result.winner == "Wildcats"  # normalized to original casing
