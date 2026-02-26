from pathlib import Path

from src.bracket import Bracket
from src.fight_result import FightResult
from src.fight_simulator import FightSimulator

DIVISION_ROUND_NAMES = ["Round of 64", "Round of 32", "Sweet 16", "Elite 8"]
DIVISION_ORDER = ["West", "East", "South", "Midwest"]


class Tournament:

    def __init__(
        self,
        bracket: Bracket,
        simulator: FightSimulator,
        output_file: str = "output/run1.txt",
    ) -> None:
        """
        Args:
            bracket: Populated Bracket instance.
            simulator: FightSimulator to use for each matchup.
            output_file: Path to write results. Parent dirs created if needed.
        """
        self.bracket = bracket
        self.simulator = simulator
        self.output_file = output_file
        self._results: list = []  # Buffer for output lines

    def run(self) -> None:
        """
        Execute the full tournament end-to-end and write the output file.

        Sequence:
          1. Round of 64, Round of 32, Sweet 16, Elite 8 (per division)
          2. Final Four (2 semifinal games)
          3. Championship (1 game)
          4. Write output file
        """
        self._record("=" * 60)
        self._record("       MASCOT MADNESS TOURNAMENT - FULL RESULTS")
        self._record("=" * 60)

        region_winners = self._run_division_rounds()

        self._run_final_four_and_championship(region_winners)

        self._write_output()

    def _run_division_rounds(self) -> dict:
        """
        Run Rounds of 64, 32, Sweet 16, and Elite 8 for all four divisions.

        Returns:
            {"West": Team, "East": Team, "South": Team, "Midwest": Team}
        """
        region_winners = {}

        for division_name in DIVISION_ORDER:
            if division_name not in self.bracket.divisions:
                continue

            self._record("")
            self._record("-" * 60)
            self._record(f"{division_name.upper()} DIVISION")
            self._record("-" * 60)

            teams_count = len(self.bracket.divisions[division_name].teams)
            round_idx = 0

            while teams_count > 1:
                round_name = (
                    DIVISION_ROUND_NAMES[round_idx]
                    if round_idx < len(DIVISION_ROUND_NAMES)
                    else f"Round of {teams_count}"
                )
                winners = self._run_single_division_round(division_name, round_name)
                self.bracket.advance_round(division_name, winners)
                teams_count = len(winners)
                round_idx += 1

            champion = self.bracket.divisions[division_name].teams[0]
            region_winners[division_name] = champion
            self._record("")
            self._record(f"  *** {division_name.upper()} CHAMPION: {champion.name.upper()} ***")

        return region_winners

    def _run_single_division_round(
        self, division_name: str, round_name: str
    ) -> list:
        """
        Simulate all games in one round for one division.

        Returns:
            List of winning Team objects in matchup order.
        """
        matchups = self.bracket.get_division_matchups(division_name)
        self._record("")
        self._record(f"  --- {round_name} ---")

        winners = []
        for i, (team1, team2) in enumerate(matchups, start=1):
            result = self.simulator.simulate_fight(team1.name, team2.name)
            self._format_game(i, team1.name, team2.name, result)
            winner = team1 if result.winner == team1.name else team2
            winners.append(winner)

        return winners

    def _run_final_four_and_championship(self, region_winners: dict) -> None:
        """Run the Final Four and Championship games."""
        self._record("")
        self._record("=" * 60)
        self._record("FINAL FOUR")
        self._record("=" * 60)

        matchups = self.bracket.get_final_four_matchups(region_winners)
        semifinal_labels = ["West vs East", "South vs Midwest"]
        final_four_winners = []

        for i, (team1, team2) in enumerate(matchups):
            label = semifinal_labels[i] if i < len(semifinal_labels) else f"Semifinal {i + 1}"
            self._record("")
            self._record(f"  --- Semifinal {i + 1}: {label} ---")
            result = self.simulator.simulate_fight(team1.name, team2.name)
            self._format_game(1, team1.name, team2.name, result)
            winner = team1 if result.winner == team1.name else team2
            final_four_winners.append(winner)

        # Championship
        finalist1, finalist2 = self.bracket.get_championship_matchup(final_four_winners)

        self._record("")
        self._record("=" * 60)
        self._record("CHAMPIONSHIP")
        self._record("=" * 60)
        self._record("")

        result = self.simulator.simulate_fight(finalist1.name, finalist2.name)
        self._format_game(1, finalist1.name, finalist2.name, result)

        self._record("")
        self._record("=" * 60)
        self._record(f"     MASCOT MADNESS CHAMPION: {result.winner.upper()}")
        self._record("=" * 60)

    def _format_game(
        self, game_num: int, team1: str, team2: str, result: FightResult
    ) -> None:
        """Append a formatted game result to the output buffer."""
        self._record("")
        self._record(f"  Game {game_num}: {team1} vs {team2}")
        self._record(
            f"  WINNER: {result.winner} (Win probability: {result.win_probability}%)"
        )
        # Wrap narrative with quotes, indented
        self._record(f'  "{result.narrative}"')

    def _record(self, line: str) -> None:
        """Append a line to the in-memory results buffer."""
        self._results.append(line)

    def _write_output(self) -> None:
        """Flush the results buffer to the output file, creating dirs as needed."""
        output_path = Path(self.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self._results))
            f.write("\n")
