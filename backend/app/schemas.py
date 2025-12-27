from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from decimal import Decimal

class Player(BaseModel):
    id: int
    firstname: str
    lastname: str
    team: str
    position: str
    age: int
    
    model_config = ConfigDict(from_attributes=True)  

class Contract(BaseModel):
    id: int
    player_id: int
    team: str
    start_year: int
    end_year: int
    duration: int
    cap_hit: Decimal
    rfa: bool
    elc: bool
    cap_pct: Decimal
    total_value: Optional[Decimal] = None
    
    model_config = ConfigDict(from_attributes=True)

class BasicPlayerStats(BaseModel):
    id: int
    player_id: int
    contract_id: int
    season: int
    playoff: bool
    team: str
    gp: int
    goals: int
    assists: int
    points: int
    plus_minus: int
    pim: int
    shots: int
    shootpct: Decimal
    
    model_config = ConfigDict(from_attributes=True)

class PredictionRequest(BaseModel):
    position: str  # 'forward', 'defenseman', or 'goalie'
    
    icetime: Optional[float] = None  # in seconds
    games_played: Optional[int] = None
    i_f_points: Optional[int] = None
    i_f_goals: Optional[int] = None
    i_f_primary_assists: Optional[int] = None
    i_f_secondary_assists: Optional[int] = None
    i_f_x_goals: Optional[float] = None
    i_f_shots_on_goal: Optional[int] = None
    i_f_unblocked_shot_attempts: Optional[int] = None
    on_ice_x_goals_percentage: Optional[float] = None
    shots_blocked_by_player: Optional[int] = None
    i_f_takeaways: Optional[int] = None
    i_f_giveaways: Optional[int] = None
    i_f_penalties: Optional[int] = None
    penalties_drawn: Optional[int] = None
    i_f_o_zone_shift_starts: Optional[int] = None
    i_f_d_zone_shift_starts: Optional[int] = None
    i_f_neutral_zone_shift_starts: Optional[int] = None
    
    # For goalies - advanced stats
    x_goals: Optional[float] = None
    goals: Optional[float] = None
    unblocked_shot_attempts: Optional[int] = None
    blocked_shot_attempts: Optional[int] = None
    x_rebounds: Optional[float] = None
    rebounds: Optional[int] = None
    x_freeze: Optional[float] = None
    act_freeze: Optional[int] = None
    x_on_goal: Optional[float] = None
    on_goal: Optional[int] = None
    x_play_stopped: Optional[float] = None
    play_stopped: Optional[int] = None
    x_play_continued_in_zone: Optional[float] = None
    play_continued_in_zone: Optional[int] = None
    x_play_continued_outside_zone: Optional[float] = None
    play_continued_outside_zone: Optional[int] = None
    flurry_adjusted_x_goals: Optional[float] = None
    low_danger_shots: Optional[int] = None
    medium_danger_shots: Optional[int] = None
    high_danger_shots: Optional[int] = None
    low_danger_x_goals: Optional[float] = None
    medium_danger_x_goals: Optional[float] = None
    high_danger_x_goals: Optional[float] = None
    low_danger_goals: Optional[int] = None
    medium_danger_goals: Optional[int] = None
    high_danger_goals: Optional[int] = None
    gp: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    ot_losses: Optional[int] = None
    shutouts: Optional[int] = None

class PredictionResponse(BaseModel):
    predicted_cap_hit: float