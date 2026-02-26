import pytest

from src.bracket import Bracket, Division, Team, ROUND_ONE_BRACKET


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_test_bracket() -> Bracket:
    """Create a bracket with 4 divisions, Team objects named 'Div_Team_N' (seed N)."""
    divisions = {}
    for div_name in ["West", "East", "South", "Midwest"]:
        teams = [Team(name=f"{div_name}_Team_{i}", seed=i) for i in range(1, 17)]
        divisions[div_name] = Division(name=div_name, teams=teams)
    return Bracket(divisions=divisions)


def _team(name: str, seed: int = 0) -> Team:
    """Shorthand for creating a Team in tests."""
    return Team(name=name, seed=seed)


# ---------------------------------------------------------------------------
# Tests: get_round_one_matchups / get_division_matchups (Round of 64)
# ---------------------------------------------------------------------------

class TestRoundOneMatchups:

    def test_returns_all_four_divisions(self):
        bracket = _make_test_bracket()
        matchups = bracket.get_round_one_matchups()
        assert set(matchups.keys()) == {"West", "East", "South", "Midwest"}

    def test_eight_games_per_division(self):
        bracket = _make_test_bracket()
        matchups = bracket.get_round_one_matchups()
        for division_matchups in matchups.values():
            assert len(division_matchups) == 8

    def test_first_game_is_1v16(self):
        bracket = _make_test_bracket()
        west = bracket.get_division_matchups("West")
        t1, t2 = west[0]
        assert t1.seed == 1
        assert t2.seed == 16

    def test_second_game_is_8v9(self):
        """8 vs 9 must be in the same bracket half as 1v16 for Round 2 to work."""
        bracket = _make_test_bracket()
        west = bracket.get_division_matchups("West")
        t1, t2 = west[1]
        assert t1.seed == 8
        assert t2.seed == 9

    def test_last_game_is_2v15(self):
        """2 vs 15 must be in the same bracket half as 7v10 for Round 2 to work."""
        bracket = _make_test_bracket()
        west = bracket.get_division_matchups("West")
        t1, t2 = west[7]
        assert t1.seed == 2
        assert t2.seed == 15

    def test_second_to_last_game_is_7v10(self):
        bracket = _make_test_bracket()
        west = bracket.get_division_matchups("West")
        t1, t2 = west[6]
        assert t1.seed == 7
        assert t2.seed == 10

    def test_round_one_bracket_order(self):
        """Verify the full game order matches the ROUND_ONE_BRACKET constant."""
        bracket = _make_test_bracket()
        west = bracket.get_division_matchups("West")
        for game_idx, (expected_s1, expected_s2) in enumerate(ROUND_ONE_BRACKET):
            t1, t2 = west[game_idx]
            assert t1.seed == expected_s1, f"Game {game_idx}: expected seed {expected_s1}, got {t1.seed}"
            assert t2.seed == expected_s2, f"Game {game_idx}: expected seed {expected_s2}, got {t2.seed}"

    def test_all_sixteen_teams_appear_exactly_once(self):
        bracket = _make_test_bracket()
        west_matchups = bracket.get_division_matchups("West")
        all_names = [team.name for pair in west_matchups for team in pair]
        assert len(all_names) == 16
        assert len(set(all_names)) == 16

    def test_returns_team_objects(self):
        bracket = _make_test_bracket()
        west = bracket.get_division_matchups("West")
        for t1, t2 in west:
            assert isinstance(t1, Team)
            assert isinstance(t2, Team)

    def test_15_seed_plays_7_seed_in_round_two(self):
        """
        Core correctness test: if the 15-seed upsets the 2-seed in Round 1,
        they should face the 7/10-seed winner in Round 2.

        Bracket half containing 2/15: games at indices 6 and 7 (7v10, 2v15).
        After Round 1 winners advance, consecutive pairing gives:
          round2_game_3 = winner(7v10) vs winner(2v15)
        """
        bracket = _make_test_bracket()
        r1 = bracket.get_division_matchups("West")

        # Simulate: 15-seed beats 2-seed; 7-seed beats 10-seed
        seed7_team = r1[6][0]   # slot 6 first team = seed 7
        seed15_team = r1[7][1]  # slot 7 second team = seed 15

        round1_winners = [
            r1[0][0],   # 1-seed beats 16
            r1[1][0],   # 8-seed beats 9
            r1[2][0],   # 5-seed beats 12
            r1[3][0],   # 4-seed beats 13
            r1[4][0],   # 6-seed beats 11
            r1[5][0],   # 3-seed beats 14
            seed7_team,    # 7-seed beats 10
            seed15_team,   # 15-seed UPSETS 2-seed
        ]
        bracket.advance_round("West", round1_winners)

        r2 = bracket.get_division_matchups("West")
        # Last Round 2 game must be slot 6 vs slot 7 = 7-seed vs 15-seed
        t1, t2 = r2[3]
        assert {t1.seed, t2.seed} == {7, 15}


# ---------------------------------------------------------------------------
# Tests: get_division_matchups for subsequent rounds
# ---------------------------------------------------------------------------

class TestSubsequentRoundMatchups:

    def test_round_of_8_consecutive_pairing(self):
        """After advancing to 8 teams, consecutive slot pairing applies."""
        bracket = _make_test_bracket()
        winners = [_team(f"W{i}", i) for i in range(8)]
        bracket.advance_round("West", winners)
        matchups = bracket.get_division_matchups("West")
        assert len(matchups) == 4
        assert matchups[0] == (_team("W0", 0), _team("W1", 1))
        assert matchups[1] == (_team("W2", 2), _team("W3", 3))
        assert matchups[2] == (_team("W4", 4), _team("W5", 5))
        assert matchups[3] == (_team("W6", 6), _team("W7", 7))

    def test_round_of_4_consecutive_pairing(self):
        bracket = _make_test_bracket()
        a, b, c, d = _team("A", 1), _team("B", 2), _team("C", 3), _team("D", 4)
        bracket.advance_round("West", [a, b, c, d])
        matchups = bracket.get_division_matchups("West")
        assert len(matchups) == 2
        assert matchups[0] == (a, b)
        assert matchups[1] == (c, d)

    def test_round_of_2_consecutive_pairing(self):
        bracket = _make_test_bracket()
        alpha, beta = _team("Alpha", 1), _team("Beta", 2)
        bracket.advance_round("West", [alpha, beta])
        matchups = bracket.get_division_matchups("West")
        assert len(matchups) == 1
        assert matchups[0] == (alpha, beta)


# ---------------------------------------------------------------------------
# Tests: advance_round
# ---------------------------------------------------------------------------

class TestAdvanceRound:

    def test_advance_replaces_team_list(self):
        bracket = _make_test_bracket()
        winners = [_team(f"Winner_{i}", i) for i in range(8)]
        bracket.advance_round("West", winners)
        assert bracket.divisions["West"].teams == winners

    def test_advance_shrinks_team_count(self):
        bracket = _make_test_bracket()
        assert len(bracket.divisions["West"].teams) == 16
        bracket.advance_round("West", [_team(f"W{i}", i) for i in range(8)])
        assert len(bracket.divisions["West"].teams) == 8
        bracket.advance_round("West", [_team(f"W{i}", i) for i in range(4)])
        assert len(bracket.divisions["West"].teams) == 4

    def test_advance_does_not_affect_other_divisions(self):
        bracket = _make_test_bracket()
        original_east = list(bracket.divisions["East"].teams)
        bracket.advance_round("West", [_team(f"W{i}", i) for i in range(8)])
        assert bracket.divisions["East"].teams == original_east


# ---------------------------------------------------------------------------
# Tests: get_final_four_matchups
# ---------------------------------------------------------------------------

class TestFinalFourMatchups:

    def test_west_vs_east_pairing(self):
        bracket = _make_test_bracket()
        tw = _team("TeamW"); te = _team("TeamE")
        ts = _team("TeamS"); tm = _team("TeamM")
        region_winners = {"West": tw, "East": te, "South": ts, "Midwest": tm}
        matchups = bracket.get_final_four_matchups(region_winners)
        assert matchups[0] == (tw, te)

    def test_south_vs_midwest_pairing(self):
        bracket = _make_test_bracket()
        tw = _team("TeamW"); te = _team("TeamE")
        ts = _team("TeamS"); tm = _team("TeamM")
        region_winners = {"West": tw, "East": te, "South": ts, "Midwest": tm}
        matchups = bracket.get_final_four_matchups(region_winners)
        assert matchups[1] == (ts, tm)

    def test_two_semifinal_games(self):
        bracket = _make_test_bracket()
        region_winners = {
            "West": _team("A"), "East": _team("B"),
            "South": _team("C"), "Midwest": _team("D"),
        }
        matchups = bracket.get_final_four_matchups(region_winners)
        assert len(matchups) == 2


# ---------------------------------------------------------------------------
# Tests: get_championship_matchup
# ---------------------------------------------------------------------------

class TestChampionshipMatchup:

    def test_returns_correct_tuple(self):
        bracket = _make_test_bracket()
        ta, tb = _team("TeamA"), _team("TeamB")
        result = bracket.get_championship_matchup([ta, tb])
        assert result == (ta, tb)

    def test_order_preserved(self):
        bracket = _make_test_bracket()
        t1, t2 = _team("Finalist1"), _team("Finalist2")
        result = bracket.get_championship_matchup([t1, t2])
        assert result[0] == t1
        assert result[1] == t2
