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


@pytest.fixture
def sample_advanced_skater_stats_data():
    """Sample advanced skater stats data for testing"""
    return {
        "player_id": 1,
        "contract_id": 1,
        "season": 2023,
        "playoff": False,
        "team": "EDM",
        "situation": "all",
        "games_played": 82,
        "icetime": Decimal("20000.0"),  # More than 300 minutes
        "shifts": 2000,
        "i_f_points": 153,
        "i_f_goals": 64,
        "i_f_primary_assists": 50,
        "i_f_secondary_assists": 39,
        "i_f_x_goals": Decimal("55.5"),
        "i_f_shots_on_goal": 352,
        "i_f_unblocked_shot_attempts": 400,
        "on_ice_x_goals_percentage": Decimal("0.5500"),
        "shots_blocked_by_player": 150,
        "i_f_takeaways": 80,
        "i_f_giveaways": 60,
        "i_f_penalties": 10,
        "penalties_drawn": 25,
        "i_f_o_zone_shift_starts": 800,
        "i_f_d_zone_shift_starts": 400,
        "i_f_neutral_zone_shift_starts": 600
    }


@pytest.fixture
def sample_advanced_goalie_stats_data():
    """Sample advanced goalie stats data for testing"""
    return {
        "player_id": 1,
        "contract_id": 1,
        "season": 2023,
        "playoff": False,
        "team": "EDM",
        "situation": "all",
        "icetime": Decimal("36000.0"),  # 600 minutes
        "x_goals": Decimal("150.0"),
        "goals": Decimal("140.0"),
        "unblocked_shot_attempts": 1800,
        "blocked_shot_attempts": 200,
        "x_rebounds": Decimal("30.0"),
        "rebounds": 28,
        "x_freeze": Decimal("50.0"),
        "act_freeze": 52,
        "x_on_goal": Decimal("1200.0"),
        "on_goal": 1150,
        "x_play_stopped": Decimal("100.0"),
        "play_stopped": 102,
        "x_play_continued_in_zone": Decimal("200.0"),
        "play_continued_in_zone": 195,
        "x_play_continued_outside_zone": Decimal("300.0"),
        "play_continued_outside_zone": 305,
        "flurry_adjusted_x_goals": Decimal("155.0"),
        "low_danger_shots": 800,
        "medium_danger_shots": 600,
        "high_danger_shots": 400,
        "low_danger_x_goals": Decimal("50.0"),
        "medium_danger_x_goals": Decimal("60.0"),
        "high_danger_x_goals": Decimal("40.0"),
        "low_danger_goals": 45,
        "medium_danger_goals": 55,
        "high_danger_goals": 40
    }


@pytest.fixture
def sample_basic_goalie_stats_data():
    """Sample basic goalie stats data for testing"""
    return {
        "player_id": 1,
        "contract_id": 1,
        "season": 2023,
        "playoff": False,
        "team": "EDM",
        "gp": 60,
        "wins": 35,
        "losses": 20,
        "ot_losses": 5,
        "shots_against": 1800,
        "saves": 1660,
        "save_percentage": Decimal("92.22"),
        "goals_against": 140,
        "goals_against_average": Decimal("2.33"),
        "shutouts": 5,
        "time_on_ice": 3600
    }