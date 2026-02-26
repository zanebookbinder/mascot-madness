import json
import os
import random
import re

from src.fight_result import FightResult

CLAUDE_MODEL = "claude-haiku-4-5-20251001"

MOCK_NARRATIVES = [
    "{winner} dominated {loser} from the opening bell. The {loser} barely had time to react before the decisive blow ended it all.",
    "In a brutal upset, {winner} dismantled {loser} piece by piece, using raw power and cunning to seal the victory.",
    "{winner} toyed with {loser} early, then unleashed a furious finishing combination that left no doubt about the outcome.",
    "It was a bloodbath from the start — {winner} absorbed everything {loser} had and came back twice as hard, ending it emphatically.",
    "{winner} used superior reach and ferocity to keep {loser} off-balance all fight, landing a haymaker that sealed the deal.",
]

CLAUDE_PROMPT_TEMPLATE = """You are the official referee and narrator for the Mascot Fight Simulator, a tournament where college sports mascots battle each other for supremacy.

Two mascots are about to fight. Simulate this battle and return the result as JSON.

FIGHTER 1: {team1}
FIGHTER 2: {team2}

JUDGING CRITERIA — weigh each factor when deciding the winner:
1. Animal/creature strength and physicality (size, natural weapons, predator vs. prey)
2. Mythical tier (gods and demons vs. dragons vs. monsters, vs. animals)
3. Weapon access (armed mascots have a significant edge)
4. Environmental advantage (set the fight wherever is most interesting)
5. Historical intimidation factor and cultural power
6. Overall coolness of mascot

NARRATIVE GUIDELINES:
- Be SPECIFIC about WHY the winner wins — name their actual physical attributes, weapons, or powers
- Choose a creative, evocative setting for the fight (not just a generic arena)
- Tone: PG-13 with a touch of Rated R edge — vivid, intense, a little brutal but not gratuitous
- Length: exactly 2-4 sentences, punchy and cinematic

RESPONSE FORMAT — return ONLY valid JSON with no markdown, no code blocks, no extra text:
{{"winner": "<exact team name as provided above>", "win_probability": <integer 51-100>, "narrative": "<2-4 sentence fight description>"}}"""


class FightSimulator:

    def __init__(self, mock_mode: bool = False) -> None:
        """
        Initialize the simulator.

        Automatically switches to mock mode if ANTHROPIC_API_KEY is not set.

        Args:
            mock_mode: Force mock mode even if API key is present.
        """
        self.mock_mode = mock_mode or not os.environ.get("ANTHROPIC_API_KEY")
        self._client = None
        if not self.mock_mode:
            from anthropic import Anthropic

            self._client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    def simulate_fight(self, team1: str, team2: str) -> FightResult:
        """
        Simulate a mascot fight between two teams.

        Args:
            team1: Name of the first team.
            team2: Name of the second team.

        Returns:
            FightResult with winner, loser, probability, and narrative.
        """
        if self.mock_mode:
            return self._mock_fight(team1, team2)
        return self._claude_fight(team1, team2)

    def _mock_fight(self, team1: str, team2: str) -> FightResult:
        """Return a deterministic mock result based on the team names."""
        # Sort names to ensure same result regardless of argument order
        seed_string = "".join(sorted([team1.lower(), team2.lower()]))
        rng = random.Random(abs(hash(seed_string)) % (2**32))

        # Choose from sorted list so result is identical regardless of argument order
        sorted_teams = sorted([team1, team2])
        winner = rng.choice(sorted_teams)
        loser = sorted_teams[1] if winner == sorted_teams[0] else sorted_teams[0]
        probability = rng.randint(54, 95)

        template = rng.choice(MOCK_NARRATIVES)
        narrative = template.format(winner=winner, loser=loser)

        return FightResult(
            winner=winner,
            loser=loser,
            win_probability=probability,
            narrative=narrative,
        )

    def _claude_fight(self, team1: str, team2: str) -> FightResult:
        """Call the Claude API and parse the JSON response."""
        prompt = CLAUDE_PROMPT_TEMPLATE.format(team1=team1, team2=team2)
        response = self._client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text = response.content[0].text
        return self._parse_claude_response(raw_text, team1, team2)

    def _parse_claude_response(
        self, raw_text: str, team1: str, team2: str
    ) -> FightResult:
        """
        Parse Claude's JSON response into a FightResult.

        Args:
            raw_text: Raw string from Claude's response.
            team1: First team name (used for validation).
            team2: Second team name (used for validation).

        Returns:
            Validated FightResult.

        Raises:
            ValueError: If JSON is malformed or winner is not one of the two teams.
        """
        # Extract the first balanced {...} JSON object from the response.
        # This handles code fences, extra trailing braces, and surrounding text.
        start = raw_text.find("{")
        if start == -1:
            raise ValueError(
                f"Claude returned no JSON object.\nRaw response: {raw_text!r}"
            )
        depth = 0
        end = start
        for i, ch in enumerate(raw_text[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i
                    break
        else:
            raise ValueError(
                f"Claude returned unbalanced JSON.\nRaw response: {raw_text!r}"
            )
        json_str = raw_text[start : end + 1]

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Claude returned invalid JSON: {e}\nRaw response: {raw_text!r}"
            ) from e

        raw_winner = data.get("winner", "")
        probability = data.get("win_probability", 0)
        narrative = data.get("narrative", "")

        # Validate winner is one of the two teams (case-insensitive)
        if raw_winner.lower() == team1.lower():
            winner, loser = team1, team2
        elif raw_winner.lower() == team2.lower():
            winner, loser = team2, team1
        else:
            # Try substring matching as fallback
            if (
                team1.lower() in raw_winner.lower()
                or raw_winner.lower() in team1.lower()
            ):
                winner, loser = team1, team2
            elif (
                team2.lower() in raw_winner.lower()
                or raw_winner.lower() in team2.lower()
            ):
                winner, loser = team2, team1
            else:
                raise ValueError(
                    f"Claude's winner {raw_winner!r} is not one of the two teams: "
                    f"{team1!r} or {team2!r}"
                )

        return FightResult(
            winner=winner,
            loser=loser,
            win_probability=int(probability),
            narrative=narrative,
        )
