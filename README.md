# Dota 2 Meta Hero Grid Generator

It's Python CLI tool to generate a meta hero grid for Dota 2. It uses the Stratz API to get the data.

## Installation

I recommend using `uv` to install project.

```sh
uv venv # create a virtual environment
uv sync # install the dependencies
source venv/bin/activate # activate the virtual environment
```

## Usage

```sh
$ dota-meta-hero-grid-generator
usage: dota-meta-hero-grid-generator [-h] [--days DAYS] --rank RANK --modes MODES [--game_version GAME_VERSION]
dota-meta-hero-grid-generator: error: the following arguments are required: --rank, --modes
```

## Example


```sh
# Generate a meta hero grid for the last 10 days for the rank 'Guardian' and mode 'All Pick'
uv run dota-meta-hero-grid-generator --days 10 --rank GUARDIAN --modes ALL_PICK
```

It will then produce `hero_grid_config.json` that you should put into your Dota 2 directory. 

Find your Steam folder, usually in `C:\Program Files (x86)\Steam`

Go into: `Steam\userdata\[your-id]\570\remote\cfg`

I recommend to to backup your existing file before replacing it.

Copy generated file to the `cfg` directory.

\[your-id\] is your Steam Friend ID (a number), which you can find in the Dota 2 client:
- Open Dota 2
- Go to your profile
- Your Friend ID is the number shown in your profile URL


---

## TODO

- [ ] Package the project to PyPI
