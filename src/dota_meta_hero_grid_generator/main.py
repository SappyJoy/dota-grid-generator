import argparse
import json

from .stratz_api import (
    get_game_versions,
    get_hero_best_vs,
    get_hero_best_with,
    get_hero_worst_vs,
    get_hero_worst_with,
    get_heroes,
    get_win_day,
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
    # positions = ["POSITION_1"]

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

    # For each top hero, retrieve matchup data and annotate with hero display names.
    for pos_data in hero_grid["positions"].values():
        for hero in pos_data["heroes"]:
            hero_id = hero.get("heroId")
            best_vs = get_hero_best_vs(hero_id, rank, limit=10, hero_lookup=hero_lookup)
            worst_vs = get_hero_worst_vs(
                hero_id, rank, limit=10, hero_lookup=hero_lookup
            )
            best_with = get_hero_best_with(
                hero_id, rank, limit=10, hero_lookup=hero_lookup
            )
            worst_with = get_hero_worst_with(
                hero_id, rank, limit=10, hero_lookup=hero_lookup
            )
            hero["matchup"] = {
                "best_vs": best_vs,
                "worst_vs": worst_vs,
                "best_with": best_with,
                "worst_with": worst_with,
            }

    # Define layout constants (adjust these as needed)
    HERO_X = 0.0
    HERO_WIDTH = 59.48

    BEST_VS_X = 32.09
    BEST_VS_WIDTH = 293.48

    WORST_VS_X = 354.52
    WORST_VS_WIDTH = 291.91

    BEST_WITH_X = 664.43
    BEST_WITH_WIDTH = 291.91

    WORST_WITH_X = 932.09
    WORST_WITH_WIDTH = 291.91

    ROW_HEIGHT = 50.0  # Each row is 50 pixels high

    # Assume latest_game_version_str is available (e.g. from your API calls)
    latest_game_version_str = "7.38"

    # Build the final grid configuration.
    grid_config = {"version": 3, "configs": []}

    # For each position (assuming hero_grid["positions"] uses keys like "1", "2", etc.)
    for pos_str, pos_data in hero_grid["positions"].items():
        # Use a config name like "1 Pos. 7.38"
        config_name = f"{pos_str} Pos. {latest_game_version_str}"
        heroes = pos_data.get("heroes", [])

        # Prepare a flat list to store each cell (block) for this config.
        categories = []

        # For each hero row (each of the top 16 heroes)
        for row_index, hero in enumerate(heroes):
            y_position = row_index * ROW_HEIGHT

            # For the first column (the hero itself)
            hero_block = {
                "category_name": "",  # No label for hero column
                "x_position": HERO_X,
                "y_position": y_position,
                "width": HERO_WIDTH,
                "height": ROW_HEIGHT,
                "hero_ids": [hero["heroId"]],
            }
            categories.append(hero_block)

            # For the second column (Best VS)
            best_vs_ids = [
                entry.get("heroId2")
                for entry in hero.get("matchup", {}).get("best_vs", [])
            ]
            best_vs_block = {
                "category_name": "Best VS" if row_index == 0 else "",
                "x_position": BEST_VS_X,
                "y_position": y_position,
                "width": BEST_VS_WIDTH,
                "height": ROW_HEIGHT,
                "hero_ids": best_vs_ids,
            }
            categories.append(best_vs_block)

            # For the third column (Worst VS)
            worst_vs_ids = [
                entry.get("heroId2")
                for entry in hero.get("matchup", {}).get("worst_vs", [])
            ]
            worst_vs_block = {
                "category_name": "Worst VS" if row_index == 0 else "",
                "x_position": WORST_VS_X,
                "y_position": y_position,
                "width": WORST_VS_WIDTH,
                "height": ROW_HEIGHT,
                "hero_ids": worst_vs_ids,
            }
            categories.append(worst_vs_block)

            # For the fourth column (Best With)
            best_with_ids = [
                entry.get("heroId2")
                for entry in hero.get("matchup", {}).get("best_with", [])
            ]
            best_with_block = {
                "category_name": "Best With" if row_index == 0 else "",
                "x_position": BEST_WITH_X,
                "y_position": y_position,
                "width": BEST_WITH_WIDTH,
                "height": ROW_HEIGHT,
                "hero_ids": best_with_ids,
            }
            categories.append(best_with_block)

            # For the fifth column (Worst With)
            worst_with_ids = [
                entry.get("heroId2")
                for entry in hero.get("matchup", {}).get("worst_with", [])
            ]
            worst_with_block = {
                "category_name": "Worst With" if row_index == 0 else "",
                "x_position": WORST_WITH_X,
                "y_position": y_position,
                "width": WORST_WITH_WIDTH,
                "height": ROW_HEIGHT,
                "hero_ids": worst_with_ids,
            }
            categories.append(worst_with_block)

        # Create a single config for this position with all blocks under "categories".
        config = {"config_name": config_name, "categories": categories}
        grid_config["configs"].append(config)

    # Write the final grid configuration to a JSON file.
    with open("hero_grid_config.json", "w") as outfile:
        json.dump(grid_config, outfile, indent=4)

    print("Hero grid configuration saved to hero_grid_config.json")


if __name__ == "__main__":
    main()
