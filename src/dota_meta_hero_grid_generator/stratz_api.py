import requests

from .config import API_TOKEN, STRATZ_API_URL


def run_graphql_query(query: str, variables: dict):
    """
    Execute a GraphQL query against the Stratz API.
    """
    headers = {
        "User-Agent": "STRATZ_API",
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        STRATZ_API_URL, json={"query": query, "variables": variables}, headers=headers
    )
    response.raise_for_status()
    return response.json()


def get_player_stats(steam_id):
    query = """
    query ($steamId: Long!) {
        player(steamAccountId: $steamId) {
            ranks { 
                rank 
            }
            leaderboardRanks {
                rank
            }
            matchCount
            winCount
            behaviorScore
            firstMatchDate
            lastMatchDate
        }
    }
    """

    variables = {"steamId": steam_id}

    print(f"Fetching player stats for steam_id {steam_id}")
    result = run_graphql_query(query, variables)
    return result.get("data", {}).get("player", [])


def get_hero_stats(position: str, days: int, rank: str, modes: list):
    """
    Fetch hero statistics for a given position, time frame, and rank.

    Parameters:
        position (str): Position ID (e.g. "POSITION_1").
        days (int): Number of days to parse (placeholder to calculate week if needed).
        rank (str): Rank tier filter matching a value from RankBracketBasicEnum.
        modes (list): List of game mode identifiers.

    Returns:
        list: List of hero stats data.
    """
    # Placeholder GraphQL query for hero stats
    query = """
    query($position: MatchPlayerPositionType!, $week: Long, $bracket: [RankBracketBasicEnum!]) {
        heroStats {
            stats(
                positionIds: [$position],
                week: $week,
                bracketBasicIds: $bracket
            ) {
                heroId
                matchCount
                winCount
                # Add additional fields as needed, e.g., ratingScore if available
            }
        }
    }
    """
    # For now, we pass `None` for week. Later, you might convert `days` into a timestamp/week value.
    variables = {"position": position, "week": None, "bracket": [rank]}
    print(
        f"Fetching hero stats for position {position}, days {days}, rank {rank}, modes {modes}"
    )
    result = run_graphql_query(query, variables)
    print(f"Result: {result}")
    return result.get("data", {}).get("heroStats", {}).get("stats", [])


# TODO: Currently not working (also test is false)
def get_hero_matchup(
    hero_id: int, days: int, rank: str, modes: list, order_by: int, limit: int
):
    """
    Fetch hero matchup data for a specific hero.

    Parameters:
        hero_id (int): The hero's ID.
        days (int): Number of days to parse (placeholder to calculate week if needed).
        rank (str): Rank tier filter.
        modes (list): List of game mode identifiers.
        order_by (int): Ordering parameter to distinguish best vs. worst matchups.
        limit (int): Maximum number of matchup entries to return.

    Returns:
        dict: A dictionary with matchup details (includes advantage and disadvantage lists).
    """
    # Placeholder GraphQL query for hero matchup data using heroVsHeroMatchup
    query = """
    query($heroId: Short!, $week: Long, $bracket: [RankBracketBasicEnum!], $matchLimit: Int) {
        heroStats {
            heroVsHeroMatchup(
                heroId: $heroId,
                week: $week,
                bracketBasicIds: $bracket,
                matchLimit: $matchLimit
            ) {
                advantage {
                    heroId
                    with {
                        heroId1
                        winRateHeroId1
                    }
                }
                disadvantage {
                    heroId
                    with {
                        heroId1
                        winRateHeroId1
                    }
                }
            }
        }
    }
    """
    variables = {
        "heroId": hero_id,
        "week": None,
        "bracket": [rank],
        "matchLimit": limit,
    }
    print(
        f"Fetching hero matchup for hero_id {hero_id}, days {days}, rank {rank}, modes {modes}, order_by {order_by}, limit {limit}"
    )
    result = run_graphql_query(query, variables)
    return result.get("data", {}).get("heroVsHeroMatchup", {})


def get_win_day(
    hero_ids: list,
    position: str,
    bracket: str,
    modes: list,
    take: int,
    skip: int,
    group_by: str = "HERO_ID",
):
    """
    Fetch aggregated win/match statistics for the last N days.

    Parameters:
      hero_ids: List of hero IDs to query.
      position: Position filter (e.g., "POSITION_1").
      bracket: Rank bracket filter (e.g., "CRUSADER").
      modes: List of game mode identifiers.
      take: Number of days to consider (max 12).
      skip: Offset (usually 0).
      group_by: Grouping method (default "HERO_ID").

    Returns:
      List of objects with heroId, matchCount, and winCount.
    """
    query = """
    query($heroIds: [Short]!, $take: Int, $skip: Int, $bracketIds: [RankBracket!], $positionIds: [MatchPlayerPositionType!], $gameModeIds: [GameModeEnumType!], $groupBy: FilterHeroWinRequestGroupBy!) {
      winDay(
        heroIds: $heroIds,
        take: $take,
        skip: $skip,
        bracketIds: $bracketIds,
        positionIds: $positionIds,
        gameModeIds: $gameModeIds,
        groupBy: $groupBy
      ) {
        heroId
        matchCount
        winCount
      }
    }
    """
    variables = {
        "heroIds": hero_ids,
        "take": take,
        "skip": skip,
        "bracketIds": [bracket],
        "positionIds": [position],
        "gameModeIds": modes,
        "groupBy": group_by,
    }
    print(
        f"Fetching winDay stats for heroes {hero_ids}, position {position}, bracket {bracket}, modes {modes}"
    )
    result = run_graphql_query(query, variables)
    return result.get("data", {}).get("winDay", [])


def get_win_game_version(position: str, rank: str, modes: list):
    """
    Fetch hero statistics for a given position, rank, and game mode.

    Parameters:
        position (str): Position ID (e.g. "POSITION_1").
        rank (str): Rank tier filter matching a value from RankBracket.
        modes (list): List of game mode identifiers.

    Returns:
        list: List of hero stats data.
    """
    query = """
    query($position: MatchPlayerPositionType!, $bracket: [RankBracket!]) {
        heroStats {
            winGameVersion(
                positionIds: [$position],
                bracketIds: $bracket,
            ) {
                gameVersionId
                heroId
                winCount
                matchCount
            }
        }
    }
    """
    variables = {
        "position": position,  # HACK: get position ENUMS and apply them or just make enum here
        "bracket": [rank],
    }
    print(f"Fetching hero stats for position {position}, rank {rank}, modes {modes}")
    result = run_graphql_query(query, variables)
    return result.get("data", {}).get("heroStats", {}).get("winGameVersion", [])


def get_game_version(game_version_id: int):
    """
    Fetch game version details for a given game version ID.

    Parameters:
        game_version_id (int): The game version ID.

    Returns:
        dict: A dictionary with game version details.
    """
    query = """
    query($id: Short!) {
      constants {
        gameVersion(id: $id) {
          id
          versionString
        }
      }
    }
    """
    variables = {"id": game_version_id}
    print(f"Fetching game version for id {game_version_id}")
    result = run_graphql_query(query, variables)
    return result.get("data", {}).get("constants", {}).get("gameVersion", {})


def get_game_versions():
    """
    Fetch all available game versions.

    Returns:
        list: List of game versions with their id and versionString.
    """
    query = """
    query {
      constants {
        gameVersions {
          id
          name
          asOfDateTime
        }
      }
    }
    """
    result = run_graphql_query(query, {})
    return result.get("data", {}).get("constants", {}).get("gameVersions", [])


def get_heroes(game_version_id: int, language: str = "ENGLISH"):
    """
    Fetch all heroes for a given game version and language.

    Returns:
        list: List of hero details.
    """
    query = """
    query($gameVersionId: Short, $language: LanguageEnum) {
      constants {
        heroes(gameVersionId: $gameVersionId, language: $language) {
          id
          name
          displayName
          shortName
          aliases
        }
      }
    }
    """
    variables = {"gameVersionId": game_version_id, "language": language}
    print(f"Fetching heroes for game_version_id {game_version_id}, language {language}")
    result = run_graphql_query(query, variables)
    return result.get("data", {}).get("constants", {}).get("heroes", [])


def get_hero_details(hero_id: int, game_version_id: int, language: str = "ENGLISH"):
    """
    Fetch details for a hero given its ID, game version, and language.

    Parameters:
        hero_id (int): The hero's ID.
        game_version_id (int): The game version ID.
        language (str): The language code (default "en").

    Returns:
        dict: Hero details (including displayName) from the ConstantQuery.
    """
    query = """
    query($id: Short!, $gameVersionId: Short, $language: LanguageEnum) {
      constants {
        hero(id: $id, gameVersionId: $gameVersionId, language: $language) {
          id
          name
          displayName
          shortName
          aliases
        }
      }
    }
    """
    variables = {"id": hero_id, "gameVersionId": game_version_id, "language": language}
    print(
        f"Fetching hero details for hero_id {hero_id}, game_version_id {game_version_id}"
    )
    result = run_graphql_query(query, variables)
    return result.get("data", {}).get("constants", {}).get("hero", {})
