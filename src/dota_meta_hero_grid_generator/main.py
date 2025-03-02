# main.py
import argparse
import json

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Dota 2 Hero Grid CLI Tool using Stratz API"
    )
    parser.add_argument("--days", type=int, required=True, help="Number of days to parse")
    parser.add_argument("--rank", type=str, required=True, help="Rank tier filter (e.g., DIVINE_IMMORTAL)")
    parser.add_argument(
        "--modes",
        type=str,
        required=True,
        help="Comma-separated game mode identifiers (e.g., ALL_PICK,CAPTAINS_MODE)"
    )
    return parser.parse_args()

def main():
    # Parse CLI arguments
    args = parse_arguments()
    days = args.days
    rank = args.rank
    modes = [mode.strip() for mode in args.modes.split(",")]

    # Debug: Print parsed arguments
    print("Parsed arguments:")
    print(f"Days: {days}")
    print(f"Rank: {rank}")
    print(f"Game Modes: {modes}")

    # Placeholder: Create a dummy hero grid config for positions 1-5
    hero_grid = {"positions": {}}
    for pos in range(1, 6):
        hero_grid["positions"][str(pos)] = {
            "heroes": [
                {
                    "hero_id": None,
                    "hero_name": f"Placeholder Hero {i+1}",
                    "ratingScore": None,
                    "best_versus": ["Dummy Hero"] * 10,
                    "worst_versus": ["Dummy Hero"] * 10
                }
                for i in range(16)
            ]
        }
    
    # Save the configuration to a JSON file
    with open("hero_grid_config.json", "w") as outfile:
        json.dump(hero_grid, outfile, indent=4)
    
    print("Hero grid configuration saved to hero_grid_config.json")

if __name__ == "__main__":
    main()

