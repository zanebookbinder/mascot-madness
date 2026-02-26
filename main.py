import os

from dotenv import load_dotenv

from src.fight_simulator import FightSimulator
from src.parsers.bracket_file_parser import BracketFileParser
from src.tournament import Tournament


def main() -> None:
    load_dotenv()

    parser = BracketFileParser()
    bracket = parser.parse("input/bracket.txt")

    simulator = FightSimulator()  # Auto-detects mock mode if API key not set
    if simulator.mock_mode:
        print("No ANTHROPIC_API_KEY found — running in mock mode.")
    else:
        print("API key detected — using Claude for fight simulations.")

    tournament = Tournament(bracket, simulator)
    tournament.run()

    print("Tournament complete! Results written to output/run1.txt")


if __name__ == "__main__":
    main()
