import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_

from app.database import SessionLocal, init_db
from app.models import BasicPlayerStats, Player, Contract, AdvancedSkaterStats, AdvancedGoalieStats, BasicGoalieStats

# Test using cd /Users/evancillie/Documents/GitHub/TradeValue/backend
# DB_HOST=localhost python3 -m app.ml.data.dataset_builder

def build_forward_dataset():
    """Builds a dataset of forwards and their basic statistics with contracts and player info"""
    init_db()
    db: Session = SessionLocal()
    
    forwards = db.query(Player).filter(
    or_(
        Player.position.contains('C'),
        Player.position.contains('W'),
    )
).all()
    return build_skater_advanced_dataset(forwards)
        

def build_defenseman_dataset():
    """Builds a dataset of defensemen and their basic statistics with contracts and player info"""
    init_db()
    db: Session = SessionLocal()

    defensemen = db.query(Player).filter(Player.position.contains('D')).all()    
    return build_skater_advanced_dataset(defensemen)

def build_goalie_dataset():
    """Builds a dataset of goalies and their basic statistics with contracts and player info"""
    init_db()
    db: Session = SessionLocal()

    goalies = db.query(Player).filter(Player.position.contains('G')).all()
    return goalie_advanced_dataset(goalies)



def build_skater_advanced_dataset(player_list: list[Player]):
    """Builds a dataset of skaters and their advanced statistics with contracts and player info"""
    init_db()
    db: Session = SessionLocal()
    try:
        player_ids = [p.id for p in player_list]
        
        query = db.query(
            # 1. Identifiers
            Player.id,
            AdvancedSkaterStats.contract_id,
            
            # 2. Target Variable (From 'contracts' table)
            Contract.cap_hit,
            
            # 3. Usage & Normalization
            AdvancedSkaterStats.icetime,
            AdvancedSkaterStats.games_played,
            
            # 4. Scoring Production (The "What")
            AdvancedSkaterStats.i_f_points,
            AdvancedSkaterStats.i_f_goals,
            AdvancedSkaterStats.i_f_primary_assists,
            AdvancedSkaterStats.i_f_secondary_assists,
            
            # 5. Shooting & Offense (The "How")
            AdvancedSkaterStats.i_f_x_goals,
            AdvancedSkaterStats.i_f_shots_on_goal,
            AdvancedSkaterStats.i_f_unblocked_shot_attempts,
            
            # 6. Play Driving & Two-Way Impact
            AdvancedSkaterStats.on_ice_x_goals_percentage,
            
            # 7. Defensive Utility
            AdvancedSkaterStats.shots_blocked_by_player,
            AdvancedSkaterStats.i_f_takeaways,
            AdvancedSkaterStats.i_f_giveaways,
            
            # 8. Discipline (Value Add/Subtract)
            AdvancedSkaterStats.i_f_penalties,
            AdvancedSkaterStats.penalties_drawn,
            
            # 9. Deployment / Context (Zone Starts)
            AdvancedSkaterStats.i_f_o_zone_shift_starts,
            AdvancedSkaterStats.i_f_d_zone_shift_starts,
            AdvancedSkaterStats.i_f_neutral_zone_shift_starts,
        ).join(
            AdvancedSkaterStats, Player.id == AdvancedSkaterStats.player_id
        ).outerjoin(
            Contract, Player.id == Contract.player_id
        ).filter(
            Player.id.in_(player_ids),
            AdvancedSkaterStats.situation == 'all',
            Contract.elc == False,
        )
        
        df = pd.read_sql(query.statement, db.bind)
        return df
    except Exception as e:
        print(e)
        return []
    finally:
        db.close()

def goalie_advanced_dataset(player_list: list[Player]):
    """Builds a dataset of goalies and their advanced statistics with contracts and player info"""
    init_db()
    db: Session = SessionLocal()
    try:
        player_ids = [p.id for p in player_list] 
        query = db.query(
            Player.id,
            Contract.cap_hit,
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
        ).join(
            AdvancedGoalieStats, Player.id == AdvancedGoalieStats.player_id
        ).outerjoin(
            Contract, Player.id == Contract.player_id
        ).outerjoin(
            BasicGoalieStats, Player.id == BasicGoalieStats.player_id
        ).filter(
            Player.id.in_(player_ids),
            AdvancedGoalieStats.situation == 'all',
            Contract.elc == False,
        )

        df = pd.read_sql(query.statement, db.bind)
        return df
    except Exception as e:
        print(e)
        return []
    finally:
        db.close()