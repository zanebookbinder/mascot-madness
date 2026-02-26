import os
import pytest

from src.bracket import Bracket, Division, Team
from src.fight_result import FightResult
from src.fight_simulator import FightSimulator
from src.tournament import Tournament


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_test_bracket() -> Bracket:
    """Create a bracket with 4 divisions, 16 Team objects each."""
    divisions = {}
    for div_name in ["West", "East", "South", "Midwest"]:
        teams = [Team(name=f"{div_name}_Team_{i}", seed=i) for i in range(1, 17)]
        divisions[div_name] = Division(name=div_name, teams=teams)
    return Bracket(divisions=divisions)


class AlwaysFirstSimulator:
    """Mock simulator that always picks team1 (the first argument) as winner."""

    def simulate_fight(self, team1: str, team2: str) -> FightResult:
        return FightResult(
            winner=team1,
            loser=team2,
            win_probability=99,
            narrative=f"{team1} crushed {team2} without breaking a sweat.",
        )


class CountingSimulator:
    """Mock simulator that counts calls and always picks team1."""

    def __init__(self):
        self.call_count = 0

    def simulate_fight(self, team1: str, team2: str) -> FightResult:
        self.call_count += 1
        return FightResult(
            winner=team1,
            loser=team2,
            win_probability=60,
            narrative="Win.",
        )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestTournamentRun:

    def test_full_run_creates_output_file(self, tmp_path):
        output_file = str(tmp_path / "run1.txt")
        tournament = Tournament(_make_test_bracket(), AlwaysFirstSimulator(), output_file)
        tournament.run()
        assert os.path.exists(output_file)

    def test_output_contains_championship_header(self, tmp_path):
        output_file = str(tmp_path / "run1.txt")
        tournament = Tournament(_make_test_bracket(), AlwaysFirstSimulator(), output_file)
        tournament.run()
        content = open(output_file).read()
        assert "CHAMPIONSHIP" in content

    def test_output_contains_champion_line(self, tmp_path):
        output_file = str(tmp_path / "run1.txt")
        tournament = Tournament(_make_test_bracket(), AlwaysFirstSimulator(), output_file)
        tournament.run()
        content = open(output_file).read()
        assert "MASCOT MADNESS CHAMPION" in content

    def test_output_contains_final_four_header(self, tmp_path):
        output_file = str(tmp_path / "run1.txt")
        tournament = Tournament(_make_test_bracket(), AlwaysFirstSimulator(), output_file)
        tournament.run()
        content = open(output_file).read()
        assert "FINAL FOUR" in content

    def test_output_contains_all_division_names(self, tmp_path):
        output_file = str(tmp_path / "run1.txt")
        tournament = Tournament(_make_test_bracket(), AlwaysFirstSimulator(), output_file)
        tournament.run()
        content = open(output_file).read()
        for div in ["WEST", "EAST", "SOUTH", "MIDWEST"]:
            assert div in content

    def test_output_dir_created_if_missing(self, tmp_path):
        nested_output = str(tmp_path / "deep" / "nested" / "run1.txt")
        tournament = Tournament(_make_test_bracket(), AlwaysFirstSimulator(), nested_output)
        tournament.run()
        assert os.path.exists(nested_output)

    def test_correct_total_game_count(self, tmp_path):
        """63 total games: 32+16+8+4+2+1."""
        output_file = str(tmp_path / "run1.txt")
        sim = CountingSimulator()
        tournament = Tournament(_make_test_bracket(), sim, output_file)
        tournament.run()
        assert sim.call_count == 63

    def test_winner_appears_as_champion(self, tmp_path):
        output_file = str(tmp_path / "run1.txt")
        tournament = Tournament(_make_test_bracket(), AlwaysFirstSimulator(), output_file)
        tournament.run()
        content = open(output_file).read()
        assert "MASCOT MADNESS CHAMPION" in content

    def test_default_output_path(self):
        tournament = Tournament(_make_test_bracket(), AlwaysFirstSimulator())
        assert tournament.output_file == "output/run1.txt"

    def test_game_narratives_appear_in_output(self, tmp_path):
        output_file = str(tmp_path / "run1.txt")
        tournament = Tournament(_make_test_bracket(), AlwaysFirstSimulator(), output_file)
        tournament.run()
        content = open(output_file).read()
        assert "crushed" in content  # from AlwaysFirstSimulator narrative

    def test_win_probability_appears_in_output(self, tmp_path):
        output_file = str(tmp_path / "run1.txt")
        tournament = Tournament(_make_test_bracket(), AlwaysFirstSimulator(), output_file)
        tournament.run()
        content = open(output_file).read()
        assert "99%" in content  # AlwaysFirstSimulator uses 99%

    def test_mock_fight_simulator_integration(self, tmp_path):
        """Full run with the real FightSimulator in mock mode."""
        output_file = str(tmp_path / "run1.txt")
        sim = FightSimulator(mock_mode=True)
        tournament = Tournament(_make_test_bracket(), sim, output_file)
        tournament.run()
        assert os.path.exists(output_file)
        content = open(output_file).read()
        assert "MASCOT MADNESS CHAMPION" in content
