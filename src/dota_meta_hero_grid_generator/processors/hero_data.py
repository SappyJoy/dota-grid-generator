from ..stratz_api import (
    get_game_versions,
    get_hero_best_vs,
    get_hero_best_with,
    get_hero_worst_vs,
    get_hero_worst_with,
    get_heroes,
    get_win_day,
)


class HeroDataProcessor:
    def __init__(self, args):
        self.args = args
        self.hero_lookup = None
        self.game_version_filter_id = None

    def process(self):
        """Main processing method that handles all data fetching and processing"""
        self._process_arguments()
        self._fetch_heroes()
        return self._generate_grid_data()

    def _process_arguments(self):
        """Process command line arguments"""
        if self.args.game_version:
            versions = get_game_versions()
            for version in versions:
                if version.get("name") == self.args.game_version:
                    self.game_version_filter_id = version.get("id")
                    break
            if self.game_version_filter_id is None:
                raise ValueError(f"Game version {self.args.game_version} not found. Available versions: {[version['name'] for version in versions]}")

    def _fetch_heroes(self):
        """Fetch hero data and create lookup table"""
        heroes_list = get_heroes(self.game_version_filter_id, language="ENGLISH")
        self.hero_lookup = {hero["id"]: hero for hero in heroes_list}

    def _generate_grid_data(self):
        """Generate the complete grid data structure"""
        grid_data = {"positions": {}}
        positions = [
            "POSITION_1",
            "POSITION_2",
            "POSITION_3",
            "POSITION_4",
            "POSITION_5",
        ]

        for pos in positions:
            stats = get_win_day(pos, self.args.rank, self.args.modes)

            if self.game_version_filter_id:
                stats = [
                    s
                    for s in stats
                    if s.get("gameVersionId") == self.game_version_filter_id
                ]

            aggregated_stats = self._aggregate_stats(stats)
            processed_stats = self._process_stats(aggregated_stats)
            top_heroes = self._get_top_heroes(processed_stats)

            grid_data["positions"][pos] = {"heroes": top_heroes, "position": pos}

        return grid_data

    def _aggregate_stats(self, stats):
        """Aggregate match statistics for each hero"""
        max_day = max(stat["day"] for stat in stats)
        cutoff = max_day - (self.args.days - 1) * 86400
        filtered_stats = [stat for stat in stats if stat["day"] >= cutoff]

        aggregated = {}
        for stat in filtered_stats:
            hero_id = stat.get("heroId")
            if hero_id in aggregated:
                aggregated[hero_id]["winCount"] += stat.get("winCount", 0)
                aggregated[hero_id]["matchCount"] += stat.get("matchCount", 0)
            else:
                aggregated[hero_id] = {
                    "heroId": hero_id,
                    "winCount": stat.get("winCount", 0),
                    "matchCount": stat.get("matchCount", 0),
                }
        return list(aggregated.values())

    def _process_stats(self, stats):
        """Process and calculate win rates"""
        processed = []
        for stat in stats:
            if stat.get("matchCount", 0) > 0:
                stat["winRate"] = stat["winCount"] / stat["matchCount"]
            else:
                stat["winRate"] = 0
            hero_id = stat.get("heroId")
            details = self.hero_lookup.get(hero_id, {})
            stat["heroName"] = details.get("displayName", f"Hero {hero_id}")
            processed.append(stat)
        return processed

    def _get_top_heroes(self, stats):
        """Get top 16 heroes sorted by win rate"""
        sorted_stats = sorted(stats, key=lambda x: x["winRate"], reverse=True)
        return sorted_stats[:16]
