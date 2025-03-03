from ..processors.hero_data import HeroDataProcessor
from ..stratz_api import (
    get_hero_best_vs,
    get_hero_best_with,
    get_hero_worst_vs,
    get_hero_worst_with,
)


class HeroGridBuilder:
    def __init__(self, grid_data, hero_lookup):
        self.grid_data = grid_data
        self.hero_lookup = hero_lookup
        self.layout_constants = self._define_layout()

    def _define_layout(self):
        """Define the layout constants for the grid"""
        return {
            "HERO_X": 0.0,
            "HERO_WIDTH": 59.48,
            "BEST_VS_X": 32.09,
            "BEST_VS_WIDTH": 293.48,
            "WORST_VS_X": 354.52,
            "WORST_VS_WIDTH": 291.91,
            "BEST_WITH_X": 664.43,
            "BEST_WITH_WIDTH": 291.91,
            "WORST_WITH_X": 932.09,
            "WORST_WITH_WIDTH": 291.91,
            "ROW_HEIGHT": 50.0,
        }

    def build(self):
        """Build the complete grid configuration"""
        grid_config = {"version": 3, "configs": []}

        for position_data in self.grid_data["positions"].values():
            config_name = f"{position_data['position']} Pos. 7.38"
            heroes = position_data.get("heroes", [])
            categories = self._build_categories(heroes)

            grid_config["configs"].append(
                {"config_name": config_name, "categories": categories}
            )

        return grid_config

    def _build_categories(self, heroes):
        """Build categories for each position"""
        categories = []
        layout = self.layout_constants
        row_height = layout["ROW_HEIGHT"]

        for row_index, hero in enumerate(heroes):
            y_position = row_index * row_height
            self._add_hero_block(categories, hero, y_position, layout)
            self._add_best_vs_block(categories, hero, y_position, layout)
            self._add_worst_vs_block(categories, hero, y_position, layout)
            self._add_best_with_block(categories, hero, y_position, layout)
            self._add_worst_with_block(categories, hero, y_position, layout)

        return categories

    def _add_hero_block(self, categories, hero, y_position, layout):
        """Add hero block to categories"""
        categories.append(
            {
                "category_name": "",
                "x_position": layout["HERO_X"],
                "y_position": y_position,
                "width": layout["HERO_WIDTH"],
                "height": layout["ROW_HEIGHT"],
                "hero_ids": [hero["heroId"]],
            }
        )

    def _add_best_vs_block(self, categories, hero, y_position, layout):
        """Add best vs block to categories"""
        best_vs = get_hero_best_vs(
            hero["heroId"], self._get_rank(), limit=10, hero_lookup=self.hero_lookup
        )
        categories.append(
            {
                "category_name": "Best VS" if y_position == 0 else "",
                "x_position": layout["BEST_VS_X"],
                "y_position": y_position,
                "width": layout["BEST_VS_WIDTH"],
                "height": layout["ROW_HEIGHT"],
                "hero_ids": [entry.get("heroId2") for entry in best_vs],
            }
        )

    def _add_worst_vs_block(self, categories, hero, y_position, layout):
        """Add worst vs block to categories"""
        worst_vs = get_hero_worst_vs(
            hero["heroId"], self._get_rank(), limit=10, hero_lookup=self.hero_lookup
        )
        categories.append(
            {
                "category_name": "Worst VS" if y_position == 0 else "",
                "x_position": layout["WORST_VS_X"],
                "y_position": y_position,
                "width": layout["WORST_VS_WIDTH"],
                "height": layout["ROW_HEIGHT"],
                "hero_ids": [entry.get("heroId2") for entry in worst_vs],
            }
        )

    def _add_best_with_block(self, categories, hero, y_position, layout):
        """Add best with block to categories"""
        best_with = get_hero_best_with(
            hero["heroId"], self._get_rank(), limit=10, hero_lookup=self.hero_lookup
        )
        categories.append(
            {
                "category_name": "Best With" if y_position == 0 else "",
                "x_position": layout["BEST_WITH_X"],
                "y_position": y_position,
                "width": layout["BEST_WITH_WIDTH"],
                "height": layout["ROW_HEIGHT"],
                "hero_ids": [entry.get("heroId2") for entry in best_with],
            }
        )

    def _add_worst_with_block(self, categories, hero, y_position, layout):
        """Add worst with block to categories"""
        worst_with = get_hero_worst_with(
            hero["heroId"], self._get_rank(), limit=10, hero_lookup=self.hero_lookup
        )
        categories.append(
            {
                "category_name": "Worst With" if y_position == 0 else "",
                "x_position": layout["WORST_WITH_X"],
                "y_position": y_position,
                "width": layout["WORST_WITH_WIDTH"],
                "height": layout["ROW_HEIGHT"],
                "hero_ids": [entry.get("heroId2") for entry in worst_with],
            }
        )

    def _get_rank(self):
        """Get rank from processor arguments"""
        from ..args import parse_arguments

        args = parse_arguments()
        return args.rank
