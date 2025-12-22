"""Database models"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey
from app.database import Base


class Player(Base):
    """Player model matching player_info table schema"""
    __tablename__ = "player_info"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String(50), nullable=False)
    lastname = Column(String(50), nullable=False)
    team = Column(String(50), nullable=False)
    position = Column(String(50), nullable=False)
    age = Column(Integer, nullable=False)


class Contract(Base):
    """Contract model matching contracts table schema"""
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("player_info.id", ondelete="CASCADE"), nullable=False)
    team = Column(String(50), nullable=False)
    start_year = Column(Integer, nullable=False)
    end_year = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)
    cap_hit = Column(Numeric(12, 2), nullable=False)
    rfa = Column(Boolean, nullable=False)
    elc = Column(Boolean, nullable=False)
    cap_pct = Column(Numeric(5, 4), nullable=False)
    total_value = Column(Numeric(15, 2), nullable=True)




class BasicPlayerStats(Base):
    """Basic player statistics model matching basic_player_stats table schema"""
    __tablename__ = "basic_player_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("player_info.id", ondelete="CASCADE"), nullable=False)
    contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    season = Column(Integer, nullable=False)  
    playoff = Column(Boolean, nullable=False)
    team = Column(String(50), nullable=False)
    gp = Column(Integer, nullable=False)  
    goals = Column(Integer, nullable=False)
    assists = Column(Integer, nullable=False)
    points = Column(Integer, nullable=False)
    plus_minus = Column(Integer, nullable=False)
    pim = Column(Integer, nullable=False)
    shots = Column(Integer, nullable=False)
    shootpct = Column(Numeric(5, 2), nullable=False)

class BasicGoalieStats(Base):
    """Basic goalie statistics model matching basic_goalie_stats table schema"""
    __tablename__ = "basic_goalie_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("player_info.id", ondelete="CASCADE"), nullable=False)
    contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    season = Column(Integer, nullable=False)
    playoff = Column(Boolean, nullable=False)
    team = Column(String(50), nullable=False)
    gp = Column(Integer, nullable=False)
    wins = Column(Integer, nullable=False)
    losses = Column(Integer, nullable=False)
    ot_losses = Column(Integer, nullable=False)
    shots_against = Column(Integer, nullable=False)
    saves = Column(Integer, nullable=False)
    save_percentage = Column(Numeric(5, 2), nullable=False)
    goals_against = Column(Integer, nullable=False)
    goals_against_average = Column(Numeric(5, 2), nullable=False)
    shutouts = Column(Integer, nullable=False)
    time_on_ice = Column(Integer, nullable=False)