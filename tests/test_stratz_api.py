import pytest
import requests

from dota_meta_hero_grid_generator.stratz_api import (
    get_game_version,
    get_hero_matchup,
    get_hero_stats,
    get_win_game_version,
)


# A dummy response class to simulate requests.Response
class DummyResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.HTTPError(f"Status code: {self.status_code}")


def dummy_post_stats(url, json, headers):
    dummy_data = {
        "data": {
            "heroStats": {"stats": [{"heroId": 1, "matchCount": 100, "winCount": 50}]}
        }
    }
    return DummyResponse(dummy_data)


def dummy_post_matchup(url, json, headers):
    dummy_data = {
        "data": {
            "heroVsHeroMatchup": {
                "advantage": [
                    {"heroId": 2, "with": [{"heroId1": 2, "winRateHeroId1": 60.0}]}
                ],
                "disadvantage": [
                    {"heroId": 3, "with": [{"heroId1": 3, "winRateHeroId1": 40.0}]}
                ],
            }
        }
    }
    return DummyResponse(dummy_data)


def dummy_post_win_game_version(url, json, headers):
    dummy_data = {
        "data": {
            "heroStats": {
                "winGameVersion": [
                    {
                        "gameVersionId": 178,
                        "heroId": 1,
                        "winCount": 754783,
                        "matchCount": 1500326,
                    },
                    {
                        "gameVersionId": 178,
                        "heroId": 2,
                        "winCount": 500000,
                        "matchCount": 1200000,
                    },
                ]
            }
        }
    }
    return DummyResponse(dummy_data)


def dummy_post_game_version(url, json, headers):
    dummy_data = {
        "data": {
            "constants": {
                "gameVersion": {"id": json["variables"]["id"], "versionString": "7.30d"}
            }
        }
    }
    return DummyResponse(dummy_data)


def test_get_hero_stats(monkeypatch):
    monkeypatch.setattr(requests, "post", dummy_post_stats)
    stats = get_hero_stats("POSITION_1", 30, "DIVINE_IMMORTAL", ["ALL_PICK"])
    print(stats)
    assert isinstance(stats, list)
    assert len(stats) == 1
    assert stats[0]["heroId"] == 1


def test_get_hero_matchup(monkeypatch):
    monkeypatch.setattr(requests, "post", dummy_post_matchup)
    matchup = get_hero_matchup(
        1, 30, "DIVINE_IMMORTAL", ["ALL_PICK"], order_by=0, limit=10
    )
    assert "advantage" in matchup
    assert "disadvantage" in matchup
    assert matchup["advantage"][0]["heroId"] == 2


def test_get_win_game_version(monkeypatch):
    monkeypatch.setattr(requests, "post", dummy_post_win_game_version)
    stats = get_win_game_version("POSITION_1", "CRUSADER", ["ALL_PICK"])
    assert isinstance(stats, list)
    assert len(stats) == 2
    assert stats[0]["gameVersionId"] == 178


def test_get_game_version(monkeypatch):
    monkeypatch.setattr(requests, "post", dummy_post_game_version)
    gv = get_game_version(178)
    assert gv["id"] == 178
    assert gv["versionString"] == "7.30d"
