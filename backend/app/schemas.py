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
    position: str
    gp: int
    goals: int
    assists: int
    points: int
    plus_minus: int
    pim: int
    shots: int
    shootpct: float

class PredictionResponse(BaseModel):
    predicted_cap_hit: float