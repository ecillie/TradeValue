import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_

from app.database import SessionLocal, init_db
from app.models import BasicPlayerStats, Player, Contract 

# Test using cd /Users/evancillie/Documents/GitHub/TradeValue/backend
# python3 -m app.ml.data.dataset_builder

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
    return build_skater_dataset(forwards)
        

def build_defenseman_dataset():
    """Builds a dataset of defensemen and their basic statistics with contracts and player info"""
    init_db()
    db: Session = SessionLocal()

    defensemen = db.query(Player).filter(Player.position.contains('D')).all()    
    return build_skater_dataset(defensemen)

def build_goalie_dataset():
    pass
    
def build_skater_dataset(player_list: list[Player]):
    """Builds a dataset of skaters and their basic statistics with contracts and player info"""
    player_ids = [p.id for p in player_list]

    init_db()
    db: Session = SessionLocal()
    db: Session = SessionLocal()
    try:
        query = db.query(
            Player.firstname,
            Player.lastname,
            Player.position,
            Player.id,
            BasicPlayerStats.season,
            BasicPlayerStats.gp,
            BasicPlayerStats.goals,
            BasicPlayerStats.assists,
            BasicPlayerStats.points,
            BasicPlayerStats.plus_minus,
            BasicPlayerStats.pim,
            BasicPlayerStats.shots,
            BasicPlayerStats.shootpct,
            Contract.cap_hit,
        ).join(
            BasicPlayerStats, Player.id == BasicPlayerStats.player_id
        ).outerjoin( 
            
            Contract, Player.id == Contract.player_id
        ).filter(
        
            Player.id.in_(player_ids)
        )

        
        df = pd.read_sql(query.statement, db.bind)
        
        return df

    except Exception as e:
        print(e)
        return []
    finally:
        db.close()

build_forward_dataset()