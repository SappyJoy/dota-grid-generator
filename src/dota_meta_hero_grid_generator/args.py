import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Dota 2 Hero Grid CLI Tool using Stratz API"
    )
    parser.add_argument(
        "--days", type=int, required=False, default=30, help="Number of days to parse"
    )
    parser.add_argument(
        "--rank", type=str, required=True, help="Rank tier filter (e.g., CRUSADER)"
    )
    parser.add_argument(
        "--modes",
        type=str,
        required=True,
        help="Comma-separated game mode identifiers (e.g., ALL_PICK,CAPTAINS_MODE)",
    )
    parser.add_argument(
        "--game_version",
        type=str,
        required=False,
        help="Dota version filter (e.g., '7.38')",
    )
    return parser.parse_args()
