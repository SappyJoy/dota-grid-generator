import json

from .args import parse_arguments
from .builders.hero_grid import HeroGridBuilder
from .processors.hero_data import HeroDataProcessor


def main():
    args = parse_arguments()

    print("Parsing arguments...")
    processor = HeroDataProcessor(args)
    grid_data = processor.process()

    print("Building grid configuration...")
    builder = HeroGridBuilder(grid_data, processor.hero_lookup)
    grid_config = builder.build()

    print("Saving configuration to file...")
    with open("hero_grid_config.json", "w") as outfile:
        json.dump(grid_config, outfile, indent=4)

    print("Hero grid configuration saved to hero_grid_config.json")


if __name__ == "__main__":
    main()
