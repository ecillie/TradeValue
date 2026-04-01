"""Shared ORM factories for API tests."""
from decimal import Decimal

from app.models import AdvancedGoalieStats, AdvancedSkaterStats, BasicGoalieStats


def advanced_skater_row(player_id: int, contract_id: int, season: int) -> AdvancedSkaterStats:
    """Minimal AdvancedSkaterStats row (icetime above skater model minimum)."""
    return AdvancedSkaterStats(
        player_id=player_id,
        contract_id=contract_id,
        season=season,
        playoff=False,
        team="EDM",
        situation="all",
        icetime=Decimal("500000"),
        games_played=82,
        i_f_points=90,
        i_f_goals=40,
        i_f_primary_assists=30,
        i_f_secondary_assists=20,
        i_f_x_goals=Decimal("45.0"),
        i_f_shots_on_goal=220,
        i_f_unblocked_shot_attempts=280,
        on_ice_x_goals_percentage=Decimal("0.5200"),
        on_ice_corsi_percentage=Decimal("0.5100"),
        on_ice_fenwick_percentage=Decimal("0.5050"),
        shots_blocked_by_player=45,
        i_f_takeaways=35,
        i_f_giveaways=30,
        i_f_penalties=10,
        penalties_drawn=15,
        i_f_o_zone_shift_starts=400,
        i_f_d_zone_shift_starts=300,
        i_f_neutral_zone_shift_starts=350,
    )


def advanced_goalie_row(player_id: int, contract_id: int, season: int) -> AdvancedGoalieStats:
    """Minimal AdvancedGoalieStats row (icetime above goalie model minimum)."""
    return AdvancedGoalieStats(
        player_id=player_id,
        contract_id=contract_id,
        season=season,
        playoff=False,
        team="NYR",
        situation="all",
        icetime=Decimal("400000"),
        x_goals=Decimal("120.0"),
        goals=Decimal("115.0"),
        unblocked_shot_attempts=1500,
        blocked_shot_attempts=200,
        x_rebounds=Decimal("25.0"),
        rebounds=24,
        x_freeze=Decimal("40.0"),
        act_freeze=42,
        x_on_goal=Decimal("1100.0"),
        on_goal=1050,
        x_play_stopped=Decimal("80.0"),
        play_stopped=78,
        x_play_continued_in_zone=Decimal("150.0"),
        play_continued_in_zone=148,
        x_play_continued_outside_zone=Decimal("200.0"),
        play_continued_outside_zone=205,
        flurry_adjusted_x_goals=Decimal("118.0"),
        low_danger_shots=600,
        medium_danger_shots=500,
        high_danger_shots=400,
        low_danger_x_goals=Decimal("40.0"),
        medium_danger_x_goals=Decimal("45.0"),
        high_danger_x_goals=Decimal("35.0"),
        low_danger_goals=38,
        medium_danger_goals=42,
        high_danger_goals=35,
    )


def basic_goalie_row(player_id: int, contract_id: int, season: int) -> BasicGoalieStats:
    return BasicGoalieStats(
        player_id=player_id,
        contract_id=contract_id,
        season=season,
        playoff=False,
        team="NYR",
        gp=55,
        wins=32,
        losses=18,
        ot_losses=5,
        shots_against=1600,
        saves=1485,
        save_percentage=Decimal("0.928"),
        goals_against=115,
        goals_against_average=Decimal("2.10"),
        shutouts=5,
        time_on_ice=3300,
    )
