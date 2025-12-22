import pytest
from decimal import Decimal
from app.models import Player, Contract, BasicPlayerStats


class TestGetPlayers:
    """Test GET /api/players endpoint"""
    
    def test_get_players_empty(self, client):
        """Test getting players when database is empty"""
        response = client.get("/api/players")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_players_single(self, client, db_session, sample_player_data):
        """Test getting a single player"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        response = client.get("/api/players")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["firstname"] == "Connor"
        assert data[0]["lastname"] == "McDavid"
        assert data[0]["team"] == "EDM"
        assert data[0]["position"] == "C"
        assert data[0]["age"] == 27
    
    def test_get_players_multiple(self, client, db_session, sample_players_data):
        """Test getting multiple players"""
        players = [Player(**data) for data in sample_players_data]
        db_session.add_all(players)
        db_session.commit()
        
        response = client.get("/api/players")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4


class TestGetPlayerById:
    """Test GET /api/players/{player_id} endpoint"""
    
    def test_get_player_by_id_success(self, client, db_session, sample_player_data):
        """Test getting a specific player by ID"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        response = client.get(f"/api/players/{player.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == player.id
        assert data["firstname"] == "Connor"
        assert data["lastname"] == "McDavid"
    
    def test_get_player_by_id_not_found(self, client):
        """Test getting a player that doesn't exist"""
        response = client.get("/api/players/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_player_by_id_invalid(self, client):
        """Test getting a player with invalid ID type"""
        response = client.get("/api/players/abc")
        assert response.status_code == 422  # Validation error


class TestSearchPlayers:
    """Test GET /api/players/search endpoint"""
    
    def test_search_by_name_firstname(self, client, db_session, sample_players_data):
        """Test searching players by first name"""
        players = [Player(**data) for data in sample_players_data]
        db_session.add_all(players)
        db_session.commit()
        
        response = client.get("/api/players/search?name=Connor")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["firstname"] == "Connor"
    
    def test_search_by_name_lastname(self, client, db_session, sample_players_data):
        """Test searching players by last name"""
        players = [Player(**data) for data in sample_players_data]
        db_session.add_all(players)
        db_session.commit()
        
        response = client.get("/api/players/search?name=Makar")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["lastname"] == "Makar"
    
    def test_search_by_name_case_insensitive(self, client, db_session, sample_player_data):
        """Test searching is case insensitive"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        
        response = client.get("/api/players/search?name=connor")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
    
    def test_search_by_name_partial_match(self, client, db_session, sample_players_data):
        """Test partial name matching"""
        players = [Player(**data) for data in sample_players_data]
        db_session.add_all(players)
        db_session.commit()
        
        response = client.get("/api/players/search?name=Mc")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "Mc" in data[0]["lastname"]
    
    def test_search_by_team(self, client, db_session, sample_players_data):
        """Test searching players by team"""
        players = [Player(**data) for data in sample_players_data]
        db_session.add_all(players)
        db_session.commit()
        
        response = client.get("/api/players/search?team=EDM")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(player["team"] == "EDM" for player in data)
    
    def test_search_by_position(self, client, db_session, sample_players_data):
        """Test searching players by position"""
        players = [Player(**data) for data in sample_players_data]
        db_session.add_all(players)
        db_session.commit()
        
        response = client.get("/api/players/search?position=D")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["position"] == "D"
    
    def test_search_multiple_filters(self, client, db_session, sample_players_data):
        """Test searching with multiple filters"""
        players = [Player(**data) for data in sample_players_data]
        db_session.add_all(players)
        db_session.commit()
        
        response = client.get("/api/players/search?team=EDM&position=C")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(player["team"] == "EDM" and player["position"] == "C" for player in data)
    
    def test_search_no_results(self, client, db_session, sample_players_data):
        """Test search with no matching results"""
        players = [Player(**data) for data in sample_players_data]
        db_session.add_all(players)
        db_session.commit()
        
        response = client.get("/api/players/search?name=NonExistent")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


class TestGetPlayerContracts:
    """Test GET /api/players/{player_id}/contracts endpoint"""
    
    def test_get_player_contracts_success(self, client, db_session, sample_player_data, sample_contract_data):
        """Test getting contracts for a specific player"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()
        
        response = client.get(f"/api/players/{player.id}/contracts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["player_id"] == player.id
        assert float(data[0]["cap_hit"]) == 12500000.0
    
    def test_get_player_contracts_no_contracts(self, client, db_session, sample_player_data):
        """Test getting contracts for player with no contracts"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        response = client.get(f"/api/players/{player.id}/contracts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_get_player_contracts_player_not_found(self, client):
        """Test getting contracts for non-existent player"""
        response = client.get("/api/players/999/contracts")
        assert response.status_code == 404


class TestGetPlayerStats:
    """Test GET /api/players/{player_id}/stats endpoint"""
    
    def test_get_player_stats_success(self, client, db_session, sample_player_data, sample_contract_data, sample_stats_data):
        """Test getting stats for a specific player"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        
        stats_data = sample_stats_data.copy()
        stats_data["player_id"] = player.id
        stats_data["contract_id"] = contract.id
        stats = BasicPlayerStats(**stats_data)
        db_session.add(stats)
        db_session.commit()
        
        response = client.get(f"/api/players/{player.id}/stats")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["player_id"] == player.id
        assert data[0]["points"] == 153
    
    def test_get_player_stats_filter_by_season(self, client, db_session, sample_player_data, sample_contract_data, sample_stats_data):
        """Test filtering stats by season"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        
        stats_data = sample_stats_data.copy()
        stats_data["player_id"] = player.id
        stats_data["contract_id"] = contract.id
        
        stats1 = BasicPlayerStats(**stats_data)
        stats2_data = stats_data.copy()
        stats2_data["season"] = 2022
        stats2 = BasicPlayerStats(**stats2_data)
        db_session.add_all([stats1, stats2])
        db_session.commit()
        
        response = client.get(f"/api/players/{player.id}/stats?season=2023")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["season"] == 2023
    
    def test_get_player_stats_filter_by_playoff(self, client, db_session, sample_player_data, sample_contract_data, sample_stats_data):
        """Test filtering stats by playoff"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        
        stats_data = sample_stats_data.copy()
        stats_data["player_id"] = player.id
        stats_data["contract_id"] = contract.id
        
        stats1 = BasicPlayerStats(**stats_data)
        stats2_data = stats_data.copy()
        stats2_data["playoff"] = True
        stats2 = BasicPlayerStats(**stats2_data)
        db_session.add_all([stats1, stats2])
        db_session.commit()
        
        response = client.get(f"/api/players/{player.id}/stats?playoff=false")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["playoff"] == False
    
    def test_get_player_stats_player_not_found(self, client):
        """Test getting stats for non-existent player"""
        response = client.get("/api/players/999/stats")
        assert response.status_code == 404


class TestGetAllContracts:
    """Test GET /api/players/contracts endpoint"""
    
    def test_get_all_contracts_empty(self, client):
        """Test getting all contracts when database is empty"""
        response = client.get("/api/players/contracts")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_all_contracts_success(self, client, db_session, sample_player_data, sample_contract_data):
        """Test getting all contracts"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()
        
        response = client.get("/api/players/contracts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["player_id"] == player.id


class TestGetContractById:
    """Test GET /api/players/contracts/{contract_id} endpoint"""
    
    def test_get_contract_by_id_success(self, client, db_session, sample_player_data, sample_contract_data):
        """Test getting a specific contract by ID"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        
        response = client.get(f"/api/players/contracts/{contract.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == contract.id
        assert data["player_id"] == player.id
        assert float(data["cap_hit"]) == 12500000.0
    
    def test_get_contract_by_id_not_found(self, client):
        """Test getting a contract that doesn't exist"""
        response = client.get("/api/players/contracts/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()