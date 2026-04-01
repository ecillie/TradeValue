import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, cast, Integer

from app.database import SessionLocal, init_db
from app.models import Player, Contract, AdvancedSkaterStats, AdvancedGoalieStats, BasicGoalieStats, PlayerSalary


# Test using cd /Users/evancillie/Documents/GitHub/TradeValue/backend
# DB_HOST=localhost python3 -m app.ml.data.dataset_builder


def _player_salary_year_matches_start():
    """Match player_salaries.year to contract start (handles int or string year in DB)."""
    return cast(PlayerSalary.year, Integer) == Contract.start_year


def build_forward_dataset():
    """Builds a dataset of forwards: one row per non-ELC contract with aligned stats and salary label."""
    init_db()
    db: Session = SessionLocal()

    forwards = db.query(Player).filter(
        or_(
            Player.position.contains("C"),
            Player.position.contains("W"),
        )
    ).all()
    db.close()
    return build_skater_advanced_dataset(forwards)


def build_defenseman_dataset():
    """Builds a dataset of defensemen: one row per non-ELC contract with aligned stats and salary label."""
    init_db()
    db: Session = SessionLocal()

    defensemen = db.query(Player).filter(Player.position.contains("D")).all()
    db.close()
    return build_skater_advanced_dataset(defensemen)


def build_goalie_dataset():
    """Builds a dataset of goalies: one row per non-ELC contract with aligned stats and salary label."""
    init_db()
    db: Session = SessionLocal()

    goalies = db.query(Player).filter(Player.position.contains("G")).all()
    db.close()
    return goalie_advanced_dataset(goalies)


def build_skater_advanced_dataset(player_list: list[Player]):
    """
    One row per (player, contract): advanced stats at contract start season,
    label from player_salaries for that contract's start year.
    """
    init_db()
    db: Session = SessionLocal()
    try:
        player_ids = [p.id for p in player_list]
        if not player_ids:
            return pd.DataFrame()

        query = (
            db.query(
                Player.id.label("player_id"),
                Player.age,
                Contract.id.label("contract_id"),
                Contract.duration,
                Contract.rfa,
                PlayerSalary.cap_hit,
                PlayerSalary.cap_pct,
                AdvancedSkaterStats.icetime,
                AdvancedSkaterStats.games_played,
                AdvancedSkaterStats.i_f_points,
                AdvancedSkaterStats.i_f_goals,
                AdvancedSkaterStats.i_f_primary_assists,
                AdvancedSkaterStats.i_f_secondary_assists,
                AdvancedSkaterStats.i_f_x_goals,
                AdvancedSkaterStats.i_f_shots_on_goal,
                AdvancedSkaterStats.i_f_unblocked_shot_attempts,
                AdvancedSkaterStats.on_ice_x_goals_percentage,
                AdvancedSkaterStats.on_ice_corsi_percentage,
                AdvancedSkaterStats.on_ice_fenwick_percentage,
                AdvancedSkaterStats.shots_blocked_by_player,
                AdvancedSkaterStats.i_f_takeaways,
                AdvancedSkaterStats.i_f_giveaways,
                AdvancedSkaterStats.i_f_penalties,
                AdvancedSkaterStats.penalties_drawn,
                AdvancedSkaterStats.i_f_o_zone_shift_starts,
                AdvancedSkaterStats.i_f_d_zone_shift_starts,
                AdvancedSkaterStats.i_f_neutral_zone_shift_starts,
            )
            .select_from(Contract)
            .join(Player, Contract.player_id == Player.id)
            .join(
                AdvancedSkaterStats,
                and_(
                    AdvancedSkaterStats.contract_id == Contract.id,
                    AdvancedSkaterStats.season == Contract.start_year,
                    AdvancedSkaterStats.situation == "all",
                    AdvancedSkaterStats.playoff == False,
                ),
            )
            .join(
                PlayerSalary,
                and_(
                    PlayerSalary.contract_id == Contract.id,
                    _player_salary_year_matches_start(),
                ),
            )
            .filter(
                Contract.elc == False,
                PlayerSalary.is_slide == False,
                Player.id.in_(player_ids),
            )
        )

        df = pd.read_sql(query.statement, db.bind)
        if not df.empty:
            df = df.drop_duplicates(subset=["contract_id"], keep="first")
        return df
    except Exception:
        return pd.DataFrame()
    finally:
        db.close()


def goalie_advanced_dataset(player_list: list[Player]):
    """Goalie rows: stats + basic stats aligned to contract start; label from player_salaries."""
    init_db()
    db: Session = SessionLocal()
    try:
        player_ids = [p.id for p in player_list]
        if not player_ids:
            return pd.DataFrame()

        query = (
            db.query(
                Player.id.label("player_id"),
                Player.age,
                Contract.id.label("contract_id"),
                Contract.duration,
                Contract.rfa,
                PlayerSalary.cap_hit,
                PlayerSalary.cap_pct,
                AdvancedGoalieStats.icetime,
                AdvancedGoalieStats.season,
                AdvancedGoalieStats.playoff,
                AdvancedGoalieStats.team,
                AdvancedGoalieStats.x_goals,
                AdvancedGoalieStats.goals,
                AdvancedGoalieStats.unblocked_shot_attempts,
                AdvancedGoalieStats.blocked_shot_attempts,
                AdvancedGoalieStats.x_rebounds,
                AdvancedGoalieStats.rebounds,
                AdvancedGoalieStats.x_freeze,
                AdvancedGoalieStats.act_freeze,
                AdvancedGoalieStats.x_on_goal,
                AdvancedGoalieStats.on_goal,
                AdvancedGoalieStats.x_play_stopped,
                AdvancedGoalieStats.play_stopped,
                AdvancedGoalieStats.x_play_continued_in_zone,
                AdvancedGoalieStats.play_continued_in_zone,
                AdvancedGoalieStats.x_play_continued_outside_zone,
                AdvancedGoalieStats.play_continued_outside_zone,
                AdvancedGoalieStats.flurry_adjusted_x_goals,
                AdvancedGoalieStats.low_danger_shots,
                AdvancedGoalieStats.medium_danger_shots,
                AdvancedGoalieStats.high_danger_shots,
                AdvancedGoalieStats.low_danger_x_goals,
                AdvancedGoalieStats.medium_danger_x_goals,
                AdvancedGoalieStats.high_danger_x_goals,
                AdvancedGoalieStats.low_danger_goals,
                AdvancedGoalieStats.medium_danger_goals,
                AdvancedGoalieStats.high_danger_goals,
                BasicGoalieStats.gp,
                BasicGoalieStats.wins,
                BasicGoalieStats.losses,
                BasicGoalieStats.ot_losses,
                BasicGoalieStats.shutouts,
            )
            .select_from(Contract)
            .join(Player, Contract.player_id == Player.id)
            .join(
                AdvancedGoalieStats,
                and_(
                    AdvancedGoalieStats.contract_id == Contract.id,
                    AdvancedGoalieStats.season == Contract.start_year,
                    AdvancedGoalieStats.situation == "all",
                    AdvancedGoalieStats.playoff == False,
                ),
            )
            .join(
                BasicGoalieStats,
                and_(
                    BasicGoalieStats.contract_id == Contract.id,
                    BasicGoalieStats.season == Contract.start_year,
                    BasicGoalieStats.playoff == False,
                ),
            )
            .join(
                PlayerSalary,
                and_(
                    PlayerSalary.contract_id == Contract.id,
                    _player_salary_year_matches_start(),
                ),
            )
            .filter(
                Contract.elc == False,
                PlayerSalary.is_slide == False,
                Player.id.in_(player_ids),
            )
        )

        df = pd.read_sql(query.statement, db.bind)
        if not df.empty:
            df = df.drop_duplicates(subset=["contract_id"], keep="first")
        return df
    except Exception:
        return pd.DataFrame()
    finally:
        db.close()
