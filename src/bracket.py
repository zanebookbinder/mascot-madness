from dataclasses import dataclass, field

# NCAA Final Four pairings: West vs East, South vs Midwest
FINAL_FOUR_PAIRS = [("West", "East"), ("South", "Midwest")]

# NCAA Round of 64 bracket order.
# Arranging games this way means simple consecutive-slot pairing in Round 2
# naturally produces the correct matchups:
#   slot 0 (1/16 winner) vs slot 1 (8/9 winner)
#   slot 2 (5/12 winner) vs slot 3 (4/13 winner)
#   slot 4 (6/11 winner) vs slot 5 (3/14 winner)
#   slot 6 (7/10 winner) vs slot 7 (2/15 winner)  <- 15-seed plays 7-seed here
ROUND_ONE_BRACKET = [(1, 16), (8, 9), (5, 12), (4, 13), (6, 11), (3, 14), (7, 10), (2, 15)]


@dataclass
class Team:
    name: str
    seed: int  # 1 = best (1-seed), 16 = worst (16-seed)

    def __str__(self) -> str:
        return self.name


@dataclass
class Division:
    name: str
    teams: list  # list[Team]


@dataclass
class Bracket:
    divisions: dict = field(default_factory=dict)
    # keys: "West", "East", "South", "Midwest"

    def get_round_one_matchups(self) -> dict:
        """
        Returns Round of 64 matchups for all divisions.

        Returns:
            {"West": [(Team_1seed, Team_16seed), (Team_8seed, Team_9seed), ...], ...}
        """
        return {name: self.get_division_matchups(name) for name in self.divisions}

    def get_division_matchups(self, division_name: str) -> list:
        """
        Returns matchups for a division.

        Round of 64 (16 teams): uses ROUND_ONE_BRACKET seed order so that
        consecutive-slot pairing in Round 2 produces correct opponents.
        E.g. a 15-seed that beats the 2-seed will face the 7-seed (or 10-seed
        winner) in Round 2.

        Subsequent rounds: consecutive slot pairs [0]v[1], [2]v[3], etc.
        Winners stay in the same half of the bracket they started in.

        Returns:
            List of (Team, Team) tuples.
        """
        teams = self.divisions[division_name].teams
        n = len(teams)

        if n == 16:
            seed_to_team = {team.seed: team for team in teams}
            return [(seed_to_team[s1], seed_to_team[s2]) for s1, s2 in ROUND_ONE_BRACKET]

        # Subsequent rounds: pair consecutive slots
        matchups = []
        for i in range(0, n, 2):
            matchups.append((teams[i], teams[i + 1]))
        return matchups

    def advance_round(self, division_name: str, winners: list) -> None:
        """
        Replace the current teams in a division with the round winners.

        Args:
            division_name: One of "West", "East", "South", "Midwest".
            winners: List of winning Team objects in matchup order.
        """
        self.divisions[division_name].teams = list(winners)

    def get_final_four_matchups(self, region_winners: dict) -> list:
        """
        Pairs Final Four teams per NCAA convention: West vs East, South vs Midwest.

        Returns:
            [(west_Team, east_Team), (south_Team, midwest_Team)]
        """
        return [
            (region_winners[pair[0]], region_winners[pair[1]])
            for pair in FINAL_FOUR_PAIRS
        ]

    def get_championship_matchup(self, final_four_winners: list) -> tuple:
        """
        Returns the championship matchup from the two Final Four survivors.

        Args:
            final_four_winners: [semifinal1_Team, semifinal2_Team]

        Returns:
            (finalist_1, finalist_2)
        """
        return (final_four_winners[0], final_four_winners[1])
