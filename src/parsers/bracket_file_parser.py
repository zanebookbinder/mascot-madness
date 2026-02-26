from src.parsers.base_parser import BaseBracketParser
from src.bracket import Bracket, Division, Team


class BracketFileParser(BaseBracketParser):

    DIVISION_SIZE = 17       # 1 title line + 16 team lines
    TEAMS_PER_DIVISION = 16
    EXPECTED_DIVISIONS = 4
    EXPECTED_TOTAL_LINES = 68  # 4 * 17

    def parse(self, source: str) -> Bracket:
        """
        Parse a txt file at the given filepath into a Bracket.

        The file must have exactly 68 non-blank lines arranged as:
          - 4 groups of 17 lines each
          - Each group: line 1 = division title, lines 2-17 = team names (1-seed first)

        Args:
            source: Path to the bracket txt file.

        Returns:
            Bracket populated with 4 divisions.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file does not contain exactly 68 non-blank lines.
        """
        lines = self._read_lines(source)
        self._validate_line_count(lines)

        divisions = {}
        for i in range(self.EXPECTED_DIVISIONS):
            offset = i * self.DIVISION_SIZE
            title, teams = self._parse_division(lines, offset)
            divisions[title] = Division(name=title, teams=teams)

        return Bracket(divisions=divisions)

    def _read_lines(self, filepath: str) -> list:
        """Read file, strip whitespace, filter blank lines."""
        with open(filepath, "r", encoding="utf-8-sig") as f:
            raw_lines = f.readlines()

        lines = []
        for line in raw_lines:
            stripped = line.strip()
            if stripped:
                lines.append(stripped)
        return lines

    def _validate_line_count(self, lines: list) -> None:
        """Raise ValueError if not exactly 68 non-blank lines."""
        if len(lines) != self.EXPECTED_TOTAL_LINES:
            raise ValueError(
                f"Expected exactly 68 non-blank lines in bracket file, "
                f"got {len(lines)}. File must have 4 divisions of 17 lines each "
                f"(1 division title + 16 team names)."
            )

    def _parse_division(self, lines: list, offset: int) -> tuple:
        """
        Extract division title and 16 team names from lines[offset:offset+17].

        Args:
            lines: Full list of stripped non-blank lines.
            offset: Starting index for this division.

        Returns:
            (division_title, [team1, team2, ..., team16])
        """
        title = lines[offset].strip().title()
        teams = [
            Team(name=lines[offset + 1 + i], seed=i + 1)
            for i in range(self.TEAMS_PER_DIVISION)
        ]
        return title, teams
