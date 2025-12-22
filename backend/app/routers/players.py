from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.database import get_db
from app.models import Player as PlayerModel, Contract as ContractModel, BasicPlayerStats
from app.schemas import Player, Contract, BasicPlayerStats as StatsSchema

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