import pytest
from decimal import Decimal


@pytest.fixture
def sample_player_data():
    """Sample player data for testing"""
    return {
        "firstname": "Connor",
        "lastname": "McDavid",
        "team": "EDM",
        "position": "C",
        "age": 27
    }


@pytest.fixture
def sample_players_data():
    """Multiple sample players for testing"""
    return [
        {
            "firstname": "Connor",
            "lastname": "McDavid",
            "team": "EDM",
            "position": "C",
            "age": 27
        },
        {
            "firstname": "Leon",
            "lastname": "Draisaitl",
            "team": "EDM",
            "position": "C",
            "age": 28
        },
        {
            "firstname": "Auston",
            "lastname": "Matthews",
            "team": "TOR",
            "position": "C",
            "age": 26
        },
        {
            "firstname": "Cale",
            "lastname": "Makar",
            "team": "COL",
            "position": "D",
            "age": 25
        }
    ]


@pytest.fixture
def sample_contract_data():
    """Sample contract data for testing"""
    return {
        "player_id": 1,
        "team": "EDM",
        "start_year": 2023,
        "end_year": 2030,
        "duration": 8,
        "cap_hit": Decimal("12500000"),
        "rfa": False,
        "elc": False,
        "cap_pct": Decimal("0.1497"),
        "total_value": Decimal("100000000")
    }


@pytest.fixture
def sample_stats_data():
    """Sample stats data for testing"""
    return {
        "player_id": 1,
        "contract_id": 1,
        "season": 2023,
        "playoff": False,
        "team": "EDM",
        "gp": 82,
        "goals": 64,
        "assists": 89,
        "points": 153,
        "plus_minus": 27,
        "pim": 18,
        "shots": 352,
        "shootpct": Decimal("18.18")
    }