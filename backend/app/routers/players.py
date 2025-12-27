from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import BaseModel
from decimal import Decimal
from app.database import get_db
from app.models import Player as PlayerModel, Contract as ContractModel, BasicPlayerStats, AdvancedSkaterStats, AdvancedGoalieStats
from app.schemas import Player, Contract, BasicPlayerStats as StatsSchema
from app.ml.inference.predictor import predict
import pandas as pd

router = APIRouter()

@router.get("", response_model=List[Player])
def get_players(db: Session = Depends(get_db)):
    """Get all players"""
    players = db.query(PlayerModel).all()
    return players

@router.get("/search", response_model=List[Player])
def search_players(
    name: Optional[str] = None,
    team: Optional[str] = None,
    position: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Search players by name, team, or position"""
    query = db.query(PlayerModel)
    
    if name:
        name_filter = f"%{name}%"
        query = query.filter(
            or_(
                PlayerModel.firstname.ilike(name_filter),
                PlayerModel.lastname.ilike(name_filter)
            )
        )
    
    if team:
        query = query.filter(PlayerModel.team.ilike(team))
    
    if position:
        query = query.filter(PlayerModel.position.ilike(f"%{position}%"))
    
    players = query.all()
    return players

@router.get("/contracts", response_model=List[Contract])
def get_contracts(db: Session = Depends(get_db)):
    """Get all contracts"""
    contracts = db.query(ContractModel).all()
    return contracts

@router.get("/contracts/{contract_id}", response_model=Contract)
def get_contract(contract_id: int, db: Session = Depends(get_db)):
    """Get a specific contract by ID"""
    contract = db.query(ContractModel).filter(ContractModel.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail=f"Contract with id {contract_id} not found")
    return contract

@router.get("/{player_id}", response_model=Player)
def get_player(player_id: int, db: Session = Depends(get_db)):
    """Get a specific player by ID"""
    player = db.query(PlayerModel).filter(PlayerModel.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail=f"Player with id {player_id} not found")
    return player

@router.get("/{player_id}/contracts", response_model=List[Contract])
def get_player_contracts(player_id: int, db: Session = Depends(get_db)):
    """Get all contracts for a specific player"""
    player = db.query(PlayerModel).filter(PlayerModel.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail=f"Player with id {player_id} not found")
    
    contracts = db.query(ContractModel).filter(ContractModel.player_id == player_id).all()
    return contracts

@router.get("/{player_id}/stats", response_model=List[StatsSchema])
def get_player_stats(
    player_id: int,
    season: Optional[int] = None,
    team: Optional[str] = None,
    playoff: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get statistics for a specific player"""
    player = db.query(PlayerModel).filter(PlayerModel.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail=f"Player with id {player_id} not found")
    
    query = db.query(BasicPlayerStats).filter(BasicPlayerStats.player_id == player_id)
    
    if season:
        query = query.filter(BasicPlayerStats.season == season)
    
    if team:
        query = query.filter(BasicPlayerStats.team.ilike(team))
    
    if playoff is not None:
        query = query.filter(BasicPlayerStats.playoff == playoff)
    
    stats = query.all()
    return stats

class YearPrediction(BaseModel):
    year: int
    actual_cap_hit: float
    expected_cap_hit: float

@router.get("/{player_id}/contract-predictions", response_model=List[YearPrediction])
def get_player_contract_predictions(player_id: int, db: Session = Depends(get_db)):
    """Get actual vs expected cap hit predictions aggregated by year for all of a player's contracts"""
    player = db.query(PlayerModel).filter(PlayerModel.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail=f"Player with id {player_id} not found")
    
    contracts = db.query(ContractModel).filter(ContractModel.player_id == player_id).all()
    if not contracts:
        return []
    
    # Determine position and model name
    position = player.position.lower()
    if 'd' in position:
        model_name = 'defenseman_model'
    elif 'g' in position:
        model_name = 'goalie_model'
    else:
        model_name = 'forward_model'
    
    # First, get predictions for each contract
    contract_predictions = []
    
    for contract in contracts:
        # Get stats for this contract
        if model_name == 'goalie_model':
            stats_query = db.query(
                AdvancedGoalieStats.icetime,
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
            ).filter(
                AdvancedGoalieStats.contract_id == contract.id,
                AdvancedGoalieStats.situation == 'all',
                AdvancedGoalieStats.playoff == False,
                AdvancedGoalieStats.season == contract.start_year
            ).first()
            
            if not stats_query:
                continue
                
            # Convert to dict for DataFrame
            stats_dict = {
                'icetime': float(stats_query.icetime) if stats_query.icetime else 0,
                'x_goals': float(stats_query.x_goals) if stats_query.x_goals else 0,
                'goals': float(stats_query.goals) if stats_query.goals else 0,
                'unblocked_shot_attempts': int(stats_query.unblocked_shot_attempts) if stats_query.unblocked_shot_attempts else 0,
                'blocked_shot_attempts': int(stats_query.blocked_shot_attempts) if stats_query.blocked_shot_attempts else 0,
                'x_rebounds': float(stats_query.x_rebounds) if stats_query.x_rebounds else 0,
                'rebounds': int(stats_query.rebounds) if stats_query.rebounds else 0,
                'x_freeze': float(stats_query.x_freeze) if stats_query.x_freeze else 0,
                'act_freeze': int(stats_query.act_freeze) if stats_query.act_freeze else 0,
                'x_on_goal': float(stats_query.x_on_goal) if stats_query.x_on_goal else 0,
                'on_goal': int(stats_query.on_goal) if stats_query.on_goal else 0,
                'x_play_stopped': float(stats_query.x_play_stopped) if stats_query.x_play_stopped else 0,
                'play_stopped': int(stats_query.play_stopped) if stats_query.play_stopped else 0,
                'x_play_continued_in_zone': float(stats_query.x_play_continued_in_zone) if stats_query.x_play_continued_in_zone else 0,
                'play_continued_in_zone': int(stats_query.play_continued_in_zone) if stats_query.play_continued_in_zone else 0,
                'x_play_continued_outside_zone': float(stats_query.x_play_continued_outside_zone) if stats_query.x_play_continued_outside_zone else 0,
                'play_continued_outside_zone': int(stats_query.play_continued_outside_zone) if stats_query.play_continued_outside_zone else 0,
                'flurry_adjusted_x_goals': float(stats_query.flurry_adjusted_x_goals) if stats_query.flurry_adjusted_x_goals else 0,
                'low_danger_shots': int(stats_query.low_danger_shots) if stats_query.low_danger_shots else 0,
                'medium_danger_shots': int(stats_query.medium_danger_shots) if stats_query.medium_danger_shots else 0,
                'high_danger_shots': int(stats_query.high_danger_shots) if stats_query.high_danger_shots else 0,
                'low_danger_x_goals': float(stats_query.low_danger_x_goals) if stats_query.low_danger_x_goals else 0,
                'medium_danger_x_goals': float(stats_query.medium_danger_x_goals) if stats_query.medium_danger_x_goals else 0,
                'high_danger_x_goals': float(stats_query.high_danger_x_goals) if stats_query.high_danger_x_goals else 0,
                'low_danger_goals': int(stats_query.low_danger_goals) if stats_query.low_danger_goals else 0,
                'medium_danger_goals': int(stats_query.medium_danger_goals) if stats_query.medium_danger_goals else 0,
                'high_danger_goals': int(stats_query.high_danger_goals) if stats_query.high_danger_goals else 0,
            }
            
            # Get basic goalie stats
            from app.models import BasicGoalieStats
            basic_stats = db.query(BasicGoalieStats).filter(
                BasicGoalieStats.contract_id == contract.id,
                BasicGoalieStats.playoff == False,
                BasicGoalieStats.season == contract.start_year
            ).first()
            
            if basic_stats:
                stats_dict['gp'] = int(basic_stats.gp) if basic_stats.gp else 0
                stats_dict['wins'] = int(basic_stats.wins) if basic_stats.wins else 0
                stats_dict['losses'] = int(basic_stats.losses) if basic_stats.losses else 0
                stats_dict['ot_losses'] = int(basic_stats.ot_losses) if basic_stats.ot_losses else 0
                stats_dict['shutouts'] = int(basic_stats.shutouts) if basic_stats.shutouts else 0
            else:
                stats_dict['gp'] = 0
                stats_dict['wins'] = 0
                stats_dict['losses'] = 0
                stats_dict['ot_losses'] = 0
                stats_dict['shutouts'] = 0
        else:
            # Skater stats
            stats_query = db.query(
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
                AdvancedSkaterStats.shots_blocked_by_player,
                AdvancedSkaterStats.i_f_takeaways,
                AdvancedSkaterStats.i_f_giveaways,
                AdvancedSkaterStats.i_f_penalties,
                AdvancedSkaterStats.penalties_drawn,
                AdvancedSkaterStats.i_f_o_zone_shift_starts,
                AdvancedSkaterStats.i_f_d_zone_shift_starts,
                AdvancedSkaterStats.i_f_neutral_zone_shift_starts,
            ).filter(
                AdvancedSkaterStats.contract_id == contract.id,
                AdvancedSkaterStats.situation == 'all',
                AdvancedSkaterStats.playoff == False,
                AdvancedSkaterStats.season == contract.start_year
            ).first()
            
            if not stats_query:
                continue
                
            stats_dict = {
                'icetime': float(stats_query.icetime) if stats_query.icetime else 0,
                'games_played': int(stats_query.games_played) if stats_query.games_played else 0,
                'i_f_points': int(stats_query.i_f_points) if stats_query.i_f_points else 0,
                'i_f_goals': int(stats_query.i_f_goals) if stats_query.i_f_goals else 0,
                'i_f_primary_assists': int(stats_query.i_f_primary_assists) if stats_query.i_f_primary_assists else 0,
                'i_f_secondary_assists': int(stats_query.i_f_secondary_assists) if stats_query.i_f_secondary_assists else 0,
                'i_f_x_goals': float(stats_query.i_f_x_goals) if stats_query.i_f_x_goals else 0,
                'i_f_shots_on_goal': int(stats_query.i_f_shots_on_goal) if stats_query.i_f_shots_on_goal else 0,
                'i_f_unblocked_shot_attempts': int(stats_query.i_f_unblocked_shot_attempts) if stats_query.i_f_unblocked_shot_attempts else 0,
                'on_ice_x_goals_percentage': float(stats_query.on_ice_x_goals_percentage) if stats_query.on_ice_x_goals_percentage else 0,
                'shots_blocked_by_player': int(stats_query.shots_blocked_by_player) if stats_query.shots_blocked_by_player else 0,
                'i_f_takeaways': int(stats_query.i_f_takeaways) if stats_query.i_f_takeaways else 0,
                'i_f_giveaways': int(stats_query.i_f_giveaways) if stats_query.i_f_giveaways else 0,
                'i_f_penalties': int(stats_query.i_f_penalties) if stats_query.i_f_penalties else 0,
                'penalties_drawn': int(stats_query.penalties_drawn) if stats_query.penalties_drawn else 0,
                'i_f_o_zone_shift_starts': int(stats_query.i_f_o_zone_shift_starts) if stats_query.i_f_o_zone_shift_starts else 0,
                'i_f_d_zone_shift_starts': int(stats_query.i_f_d_zone_shift_starts) if stats_query.i_f_d_zone_shift_starts else 0,
                'i_f_neutral_zone_shift_starts': int(stats_query.i_f_neutral_zone_shift_starts) if stats_query.i_f_neutral_zone_shift_starts else 0,
            }
        
        try:
            # Make prediction
            df = pd.DataFrame([stats_dict])
            result_df = predict(df, model_name=model_name)
            expected_cap_hit = float(result_df['predicted_cap_hit'].iloc[0])
            
            contract_predictions.append({
                'contract': contract,
                'actual_cap_hit': float(contract.cap_hit),
                'expected_cap_hit': expected_cap_hit
            })
        except Exception as e:
            # Skip contracts where prediction fails
            continue
    
    # Now aggregate by year
    if not contract_predictions:
        return []
    
    # Find all years covered by contracts
    all_years = set()
    for cp in contract_predictions:
        contract = cp['contract']
        for year in range(contract.start_year, contract.end_year + 1):
            all_years.add(year)
    
    # Aggregate cap hits by year
    year_data = {}
    for year in sorted(all_years):
        year_data[year] = {
            'actual_cap_hit': 0.0,
            'expected_cap_hit': 0.0
        }
    
    # Sum up cap hits for each year from all active contracts
    for cp in contract_predictions:
        contract = cp['contract']
        actual = cp['actual_cap_hit']
        expected = cp['expected_cap_hit']
        
        for year in range(contract.start_year, contract.end_year + 1):
            year_data[year]['actual_cap_hit'] += actual
            year_data[year]['expected_cap_hit'] += expected
    
    # Convert to list of YearPrediction objects
    predictions = [
        YearPrediction(
            year=year,
            actual_cap_hit=data['actual_cap_hit'],
            expected_cap_hit=data['expected_cap_hit']
        )
        for year, data in sorted(year_data.items())
    ]
    
    return predictions