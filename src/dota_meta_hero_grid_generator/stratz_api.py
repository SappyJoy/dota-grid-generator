import requests

from .config import API_TOKEN, STRATZ_API_URL
from .utils import translate_rank_to_basic


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
# def get_hero_matchup(
#     hero_id: int, days: int, rank: str, modes: list, order_by: int, limit: int
# ):
#     """
#     Fetch hero matchup data for a specific hero.
#
#     Parameters:
#         hero_id (int): The hero's ID.
#         days (int): Number of days to parse (placeholder to calculate week if needed).
#         rank (str): Rank tier filter.
#         modes (list): List of game mode identifiers.
#         order_by (int): Ordering parameter to distinguish best vs. worst matchups.
#         limit (int): Maximum number of matchup entries to return.
#
#     Returns:
#         dict: A dictionary with matchup details (includes advantage and disadvantage lists).
#     """
#     basic_rank = translate_rank_to_basic(rank)
#     # Placeholder GraphQL query for hero matchup data using heroVsHeroMatchup
#     query = """
#     query($heroId: Short!, $week: Long, $bracket: [RankBracketBasicEnum!], $matchLimit: Int) {
#         heroStats {
#             heroVsHeroMatchup(
#                 heroId: $heroId,
#                 week: $week,
#                 bracketBasicIds: $bracket,
#                 matchLimit: $matchLimit
#             ) {
#                 advantage {
#                     heroId
#                     with {
#                         heroId1
#                         winRateHeroId1
#                     }
#                 }
#                 disadvantage {
#                     heroId
#                     with {
#                         heroId1
#                         winRateHeroId1
#                     }
#                 }
#             }
#         }
#     }
#     """
#     variables = {
#         "heroId": hero_id,
#         "week": None,
#         "bracket": [basic_rank],
#         "matchLimit": limit,
#     }
#     print(
#         f"Fetching hero matchup for hero_id {hero_id}, days {days}, rank {rank}, modes {modes}, order_by {order_by}, limit {limit}"
#     )
#     result = run_graphql_query(query, variables)
#     print(result)
#     return result.get("data", {}).get("heroVsHeroMatchup", {})


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
    basic_rank = translate_rank_to_basic(rank)
    # Placeholder GraphQL query for hero matchup data using heroVsHeroMatchup
    query = """
    query($heroId: Short!, $week: Long, $bracket: [RankBracketBasicEnum!], $matchLimit: Int) {
        heroStats {
            matchUp(
                heroId: $heroId,
                week: $week,
                bracketBasicIds: $bracket,
                matchLimit: $matchLimit
            ) {
                heroId
                with {
                    heroId1
                    heroId2
                    week
                    matchCount
                    winCount
                    synergy
                    winRateHeroId1
                    winRateHeroId2
                    winsAverage
                }
                vs {
                    heroId1
                    heroId2
                    week
                    matchCount
                    winCount
                    synergy
                    winRateHeroId1
                    winRateHeroId2
                    winsAverage
                }
            }
        }
    }
    """
    variables = {
        "heroId": hero_id,
        "week": None,
        "bracket": [basic_rank],
        "matchLimit": limit,
    }
    print(
        f"Fetching hero matchup for hero_id {hero_id}, days {days}, rank {rank}, modes {modes}, order_by {order_by}, limit {limit}"
    )
    result = run_graphql_query(query, variables)
    print(result)
    return result.get("data", {}).get("heroStats", {}).get("matchUp", [])


def get_hero_matchup_by_order(hero_id: int, rank: str, order_by: int, limit: int):
    """
    Helper function to fetch hero matchup data with a given order.

    Parameters:
        hero_id (int): The hero's ID.
        rank (str): Rank tier filter.
        order_by (int): Ordering parameter (Byte). Accepted values:
            - 0: Synergy
            - 3: Loss
            - 4: Disadvantage
            - 5: Advantage
        limit (int): Maximum number of matchup entries.

    Returns:
        list: The result of the matchUp query.
    """
    # Translate rank to RankBracketBasicEnum using your helper.
    basic_rank = translate_rank_to_basic(rank)
    query = """
    query($heroId: Short!, $week: Long, $bracket: [RankBracketBasicEnum!], $orderBy: Byte, $matchLimit: Int) {
        heroStats {
            matchUp(
                heroId: $heroId,
                week: $week,
                bracketBasicIds: $bracket,
                orderBy: $orderBy,
                matchLimit: $matchLimit
            ) {
                heroId
                with {
                    heroId1
                    heroId2
                    week
                    matchCount
                    winCount
                    synergy
                    winRateHeroId1
                    winRateHeroId2
                    winsAverage
                }
                vs {
                    heroId1
                    heroId2
                    week
                    matchCount
                    winCount
                    synergy
                    winRateHeroId1
                    winRateHeroId2
                    winsAverage
                }
            }
        }
    }
    """
    variables = {
        "heroId": hero_id,
        "week": None,  # Placeholder – adjust if needed.
        "bracket": [basic_rank],
        "orderBy": order_by,
        "matchLimit": limit,
    }
    print(
        f"Fetching hero matchup for hero_id {hero_id} with orderBy {order_by}, rank {rank} (translated: {basic_rank}), limit {limit}"
    )
    result = run_graphql_query(query, variables)
    # Our query returns an array under matchUp. We assume one record in the array.
    return result.get("data", {}).get("heroStats", {}).get("matchUp", [])


def get_hero_best_vs(hero_id: int, rank: str, limit: int, hero_lookup: dict = None):
    """
    Fetch the enemy (versus) heroes for which the given hero performs best.
    Uses orderBy = 5 (Advantage).
    Optionally, annotate each matchup entry with hero display name using hero_lookup.
    """
    matchup = get_hero_matchup_by_order(hero_id, rank, order_by=5, limit=limit)
    if matchup:
        vs_list = matchup[0].get("vs", [])
        if hero_lookup:
            for m in vs_list:
                # Annotate using hero_lookup on heroId1
                hero_id_key = m.get("heroId2")
                if hero_id_key in hero_lookup:
                    m["heroName"] = hero_lookup[hero_id_key].get(
                        "displayName", f"Hero {hero_id_key}"
                    )
                else:
                    m["heroName"] = f"Hero {hero_id_key}"
        return vs_list
    return []


def get_hero_worst_vs(hero_id: int, rank: str, limit: int, hero_lookup: dict = None):
    """
    Fetch the enemy (versus) heroes for which the given hero performs worst.
    Uses orderBy = 4 (Disadvantage).
    Optionally, annotate each matchup entry with hero display name using hero_lookup.
    """
    matchup = get_hero_matchup_by_order(hero_id, rank, order_by=4, limit=limit)
    if matchup:
        vs_list = matchup[0].get("vs", [])
        if hero_lookup:
            for m in vs_list:
                hero_id_key = m.get("heroId2")
                if hero_id_key in hero_lookup:
                    m["heroName"] = hero_lookup[hero_id_key].get(
                        "displayName", f"Hero {hero_id_key}"
                    )
                else:
                    m["heroName"] = f"Hero {hero_id_key}"
        return vs_list
    return []


def get_hero_best_with(hero_id: int, rank: str, limit: int, hero_lookup: dict = None):
    """
    Fetch the allied (with) heroes that synergize best with the given hero.
    Uses orderBy = 0 (Synergy).
    Optionally, annotate each matchup entry with hero display name using hero_lookup.
    """
    matchup = get_hero_matchup_by_order(hero_id, rank, order_by=0, limit=limit)
    if matchup:
        with_list = matchup[0].get("with", [])
        if hero_lookup:
            for m in with_list:
                hero_id_key = m.get("heroId2")
                if hero_id_key in hero_lookup:
                    m["heroName"] = hero_lookup[hero_id_key].get(
                        "displayName", f"Hero {hero_id_key}"
                    )
                else:
                    m["heroName"] = f"Hero {hero_id_key}"
        return with_list
    return []


def get_hero_worst_with(hero_id: int, rank: str, limit: int, hero_lookup: dict = None):
    """
    Fetch the allied (with) heroes that have the worst synergy with the given hero.
    Uses orderBy = 3 (Loss) as a proxy for poor synergy.
    Optionally, annotate each matchup entry with hero display name using hero_lookup.
    """
    matchup = get_hero_matchup_by_order(hero_id, rank, order_by=3, limit=limit)
    if matchup:
        with_list = matchup[0].get("with", [])
        if hero_lookup:
            for m in with_list:
                hero_id_key = m.get("heroId2")
                if hero_id_key in hero_lookup:
                    m["heroName"] = hero_lookup[hero_id_key].get(
                        "displayName", f"Hero {hero_id_key}"
                    )
                else:
                    m["heroName"] = f"Hero {hero_id_key}"
        return with_list
    return []


def get_win_day(
    position: str,
    rank: str,
    modes: list,
):
    """
    Fetch aggregated win/match statistics for the last N days.

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
            winDay(
                positionIds: [$position],
                bracketIds: $bracket,
            ) {
                day
                heroId
                winCount
                matchCount
            }
        }
    }
    """
    variables = {
        "position": position,
        "bracket": [rank],
    }
    print(f"Fetching hero stats for position {position}, rank {rank}, modes {modes}")
    result = run_graphql_query(query, variables)
    return result.get("data", {}).get("heroStats", {}).get("winDay", [])


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


def get_heroes(game_version_id, language: str = "ENGLISH"):
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
