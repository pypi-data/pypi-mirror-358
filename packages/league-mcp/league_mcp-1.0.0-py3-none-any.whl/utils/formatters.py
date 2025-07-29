"""Formatters for various Riot API responses."""

import datetime
import json
from typing import Dict, List, Any


def format_account(account_data: dict) -> str:
    """Format account data into a readable string."""
    return json.dumps(account_data, indent=2, ensure_ascii=False)


def format_active_game(game_data: dict) -> str:
    """Format active game data into a readable string."""
    return json.dumps(game_data, indent=2, ensure_ascii=False)


def format_featured_games(games_data: dict) -> str:
    """Format featured games data into a readable string."""
    return json.dumps(games_data, indent=2, ensure_ascii=False)


def format_summoner(summoner_data: dict) -> str:
    """Format summoner data into a readable string."""
    return json.dumps(summoner_data, indent=2, ensure_ascii=False)


def format_champion_rotation(rotation_data: dict) -> str:
    """Format champion rotation data into a readable string."""
    return json.dumps(rotation_data, indent=2, ensure_ascii=False)


def format_clash_player(player_data: list) -> str:
    """Format clash player data into a readable string."""
    return json.dumps(player_data, indent=2, ensure_ascii=False)


def format_clash_team(team_data: dict) -> str:
    """Format clash team data into a readable string."""
    return json.dumps(team_data, indent=2, ensure_ascii=False)


def format_clash_tournaments(tournaments_data: list) -> str:
    """Format clash tournaments data into a readable string."""
    return json.dumps(tournaments_data, indent=2, ensure_ascii=False)


def format_clash_tournament(tournament_data: dict) -> str:
    """Format single clash tournament data into a readable string."""
    return json.dumps(tournament_data, indent=2, ensure_ascii=False)


def format_league_list(league_data: dict) -> str:
    """Format league list data (challenger/grandmaster/master/league by ID) into a readable string."""
    return json.dumps(league_data, indent=2, ensure_ascii=False)


def format_league_entries(entries_data: list) -> str:
    """Format league entries data into a readable string."""
    return json.dumps(entries_data, indent=2, ensure_ascii=False)


def format_challenge_configs(configs_data: list) -> str:
    """Format challenge configs data into a readable string."""
    return json.dumps(configs_data, indent=2, ensure_ascii=False)


def format_challenge_config(config_data: dict) -> str:
    """Format single challenge config data into a readable string."""
    return json.dumps(config_data, indent=2, ensure_ascii=False)


def format_challenge_leaderboard(leaderboard_data: list, level: str) -> str:
    """Format challenge leaderboard data into a readable string."""
    return json.dumps(leaderboard_data, indent=2, ensure_ascii=False)


def format_player_challenges(player_data: dict) -> str:
    """Format player challenge data into a readable string."""
    return json.dumps(player_data, indent=2, ensure_ascii=False)


def format_platform_status(status_data: dict) -> str:
    """Format platform status data into a readable string."""
    return json.dumps(status_data, indent=2, ensure_ascii=False)


def format_match_ids(match_ids: list, puuid: str) -> str:
    """Format match IDs list into a readable string."""
    return json.dumps({
        "puuid": puuid,
        "match_ids": match_ids
    }, indent=2, ensure_ascii=False)


def format_match_detail(match_data: dict) -> str:
    """Format detailed match data into a readable string."""
    return json.dumps(match_data, indent=2, ensure_ascii=False)


def format_match_timeline(timeline_data: dict) -> str:
    """Format match timeline data into a readable string."""
    return json.dumps(timeline_data, indent=2, ensure_ascii=False) 