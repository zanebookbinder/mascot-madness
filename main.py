import os
from datetime import datetime

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

    timestamp = datetime.now().strftime("%m_%d_%Y-%H_%M_%S")
    output_file = f"output/{timestamp}.txt"

    tournament = Tournament(bracket, simulator, output_file)
    tournament.run()

    print(f"Tournament complete! Results written to {output_file}")


if __name__ == "__main__":
    main()
