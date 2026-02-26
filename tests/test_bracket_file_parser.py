import pytest

from src.bracket import Team
from src.parsers.bracket_file_parser import BracketFileParser


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_bracket_content(
    divisions=None,
    teams_per_division=16,
    extra_blank_lines=False,
) -> str:
    """Generate a valid 68-line bracket file content."""
    if divisions is None:
        divisions = ["West", "East", "South", "Midwest"]

    lines = []
    for div_idx, div_name in enumerate(divisions):
        if extra_blank_lines and div_idx > 0:
            lines.append("")  # blank line between divisions
        lines.append(div_name)
        for seed in range(1, teams_per_division + 1):
            lines.append(f"{div_name}_Team_{seed}")

    return "\n".join(lines) + "\n"


def _write_bracket_file(tmp_path, content: str) -> str:
    f = tmp_path / "bracket.txt"
    f.write_text(content)
    return str(f)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestBracketFileParser:

    def test_parse_valid_file(self, tmp_path):
        content = _make_bracket_content()
        filepath = _write_bracket_file(tmp_path, content)

        parser = BracketFileParser()
        bracket = parser.parse(filepath)

        assert len(bracket.divisions) == 4
        assert "West" in bracket.divisions
        assert "East" in bracket.divisions
        assert "South" in bracket.divisions
        assert "Midwest" in bracket.divisions

    def test_parse_correct_team_count(self, tmp_path):
        content = _make_bracket_content()
        filepath = _write_bracket_file(tmp_path, content)

        bracket = BracketFileParser().parse(filepath)

        for division in bracket.divisions.values():
            assert len(division.teams) == 16

    def test_teams_are_team_objects(self, tmp_path):
        content = _make_bracket_content()
        filepath = _write_bracket_file(tmp_path, content)

        bracket = BracketFileParser().parse(filepath)

        for team in bracket.divisions["West"].teams:
            assert isinstance(team, Team)

    def test_parse_seed_order_preserved(self, tmp_path):
        content = _make_bracket_content()
        filepath = _write_bracket_file(tmp_path, content)

        bracket = BracketFileParser().parse(filepath)

        west_teams = bracket.divisions["West"].teams
        assert west_teams[0].name == "West_Team_1"    # 1-seed first
        assert west_teams[15].name == "West_Team_16"   # 16-seed last

    def test_seeds_assigned_from_file_position(self, tmp_path):
        content = _make_bracket_content()
        filepath = _write_bracket_file(tmp_path, content)

        bracket = BracketFileParser().parse(filepath)

        west_teams = bracket.divisions["West"].teams
        assert west_teams[0].seed == 1    # first in file = 1-seed
        assert west_teams[15].seed == 16  # last in file = 16-seed
        # Verify every seed 1-16 is assigned exactly once
        seeds = [team.seed for team in west_teams]
        assert sorted(seeds) == list(range(1, 17))

    def test_parse_division_names_set_correctly(self, tmp_path):
        content = _make_bracket_content()
        filepath = _write_bracket_file(tmp_path, content)

        bracket = BracketFileParser().parse(filepath)

        for name, division in bracket.divisions.items():
            assert division.name == name

    def test_parse_file_with_blank_lines_between_divisions(self, tmp_path):
        content = _make_bracket_content(extra_blank_lines=True)
        filepath = _write_bracket_file(tmp_path, content)

        bracket = BracketFileParser().parse(filepath)

        assert len(bracket.divisions) == 4
        for division in bracket.divisions.values():
            assert len(division.teams) == 16

    def test_parse_strips_whitespace(self, tmp_path):
        content = _make_bracket_content()
        content_with_spaces = "\n".join(
            line + "   " for line in content.splitlines()
        ) + "\n"
        filepath = _write_bracket_file(tmp_path, content_with_spaces)

        bracket = BracketFileParser().parse(filepath)

        west_teams = bracket.divisions["West"].teams
        assert west_teams[0].name == "West_Team_1"

    def test_parse_division_titles_normalized_to_title_case(self, tmp_path):
        content = _make_bracket_content(divisions=["WEST", "east", "sOuTh", "midwest"])
        filepath = _write_bracket_file(tmp_path, content)

        bracket = BracketFileParser().parse(filepath)

        assert "West" in bracket.divisions
        assert "East" in bracket.divisions
        assert "South" in bracket.divisions
        assert "Midwest" in bracket.divisions

    def test_parse_too_few_lines_raises(self, tmp_path):
        lines = ["West"] + [f"West_Team_{i}" for i in range(1, 16)]  # only 15 teams
        for div in ["East", "South", "Midwest"]:
            lines.append(div)
            lines += [f"{div}_Team_{i}" for i in range(1, 17)]
        content = "\n".join(lines) + "\n"
        filepath = _write_bracket_file(tmp_path, content)

        with pytest.raises(ValueError, match="68"):
            BracketFileParser().parse(filepath)

    def test_parse_too_many_lines_raises(self, tmp_path):
        content = _make_bracket_content()
        content += "ExtraTeam\n"
        filepath = _write_bracket_file(tmp_path, content)

        with pytest.raises(ValueError, match="68"):
            BracketFileParser().parse(filepath)

    def test_parse_file_not_found_raises(self):
        with pytest.raises(FileNotFoundError):
            BracketFileParser().parse("/nonexistent/path/bracket.txt")
