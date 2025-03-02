import argparse
import json

from .stratz_api import (
    get_game_version,
    get_game_versions,
    get_hero_details,
    get_hero_matchup,
    get_hero_stats,
    get_heroes,
    get_player_stats,
    get_win_day,
    get_win_game_version,
)


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


def main():
    args = parse_arguments()
    days = (
        args.days if args.days <= 12 else 12
    )  # API provides at most 12 days of data. # TODO: use weeks and months to extend this
    rank = args.rank
    modes = [mode.strip() for mode in args.modes.split(",")]
    game_version_filter_str = args.game_version

    # Convert the provided game version string (e.g. "7.38") into a game version ID
    game_version_filter_id = None
    if game_version_filter_str:
        versions = get_game_versions()
        for version in versions:
            if version.get("name") == game_version_filter_str:
                game_version_filter_id = version.get("id")
                break
        if game_version_filter_id is None:
            print(f"Error: Game version {game_version_filter_str} not found.")
            return

    print(
        f"Parsed arguments:\n  Days: {days}\n  Rank: {rank}\n  Modes: {modes}\n  Game Version Filter: {game_version_filter_str} (ID: {game_version_filter_id})"
    )

    # Fetch all heroes for the selected game version to build a hero lookup.
    heroes_list = get_heroes(game_version_filter_id, language="ENGLISH")
    hero_lookup = {hero["id"]: hero for hero in heroes_list}

    hero_grid = {"positions": {}}
    positions = ["POSITION_1", "POSITION_2", "POSITION_3", "POSITION_4", "POSITION_5"]

    # Cache hero details to avoid redundant API calls.
    hero_details_cache = {}

    # For each position, retrieve hero stats via get_win_game_version,
    # filter by game version if provided, compute ratings, and add matchup data.
    for idx, pos in enumerate(positions, start=1):
        stats = get_win_day(pos, rank, modes)

        # Filter stats by game version ID if a filter was provided.
        if game_version_filter_id:
            stats = [
                s for s in stats if s.get("gameVersionId") == game_version_filter_id
            ]

        # For each hero stat, compute a simple winRate and lookup the game version string.
        aggregated_stats = {}
        for s in stats:
            hero_id = s.get("heroId")
            if hero_id in aggregated_stats:
                aggregated_stats[hero_id]["winCount"] += s.get("winCount", 0)
                aggregated_stats[hero_id]["matchCount"] += s.get("matchCount", 0)
            else:
                aggregated_stats[hero_id] = {
                    "heroId": hero_id,
                    "winCount": s.get("winCount", 0),
                    "matchCount": s.get("matchCount", 0),
                }
        aggregated_stats = list(aggregated_stats.values())

        # Compute a simple winRate for each hero and add the hero's display name.
        for s in aggregated_stats:
            if s.get("matchCount", 0) > 0:
                s["winRate"] = s["winCount"] / s["matchCount"]
            else:
                s["winRate"] = 0
            hero_id = s.get("heroId")
            details = hero_lookup.get(hero_id, {})
            s["heroName"] = details.get("displayName", f"Hero {hero_id}")

        # Sort heroes by winRate in descending order and choose the top 16.
        top_heroes = sorted(aggregated_stats, key=lambda x: x["winRate"], reverse=True)[
            :16
        ]
        hero_grid["positions"][str(idx)] = {"heroes": top_heroes}

    # For each top hero, retrieve matchup data.
    # for pos_data in hero_grid["positions"].values():
    #     for hero in pos_data["heroes"]:
    #         hero_id = hero.get("heroId")
    #         matchup = get_hero_matchup(hero_id, days, rank, modes, order_by=0, limit=10)
    #         hero["matchup"] = matchup

    # Write the final configuration to a JSON file.
    with open("hero_grid_config.json", "w") as outfile:
        json.dump(hero_grid, outfile, indent=4)

    print("Hero grid configuration saved to hero_grid_config.json")


if __name__ == "__main__":
    main()
