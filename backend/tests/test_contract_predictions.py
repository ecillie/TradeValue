import pytest
import pandas as pd
from decimal import Decimal
from unittest.mock import patch
from app.models import Player, Contract, AdvancedSkaterStats, AdvancedGoalieStats, BasicGoalieStats


class TestGetPlayerContractPredictions:
    """Test GET /api/players/{player_id}/contract-predictions endpoint"""
    
    @patch('app.routers.players.predict')
    def test_get_contract_predictions_success(self, mock_predict, client, db_session, 
                                               sample_player_data, sample_contract_data, 
                                               sample_advanced_skater_stats_data):
        """Test successful retrieval of contract predictions by year"""
        import pandas as pd
        
        # Setup player
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        # Setup contract
        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        
        # Setup advanced stats
        stats_data = sample_advanced_skater_stats_data.copy()
        stats_data["player_id"] = player.id
        stats_data["contract_id"] = contract.id
        stats = AdvancedSkaterStats(**stats_data)
        db_session.add(stats)
        db_session.commit()
        
        # Mock prediction - return a DataFrame with predicted_cap_hit column
        mock_result_df = pd.DataFrame({'predicted_cap_hit': [11500000.0]})
        mock_predict.return_value = mock_result_df
        
        response = client.get(f"/api/players/{player.id}/contract-predictions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have predictions for each year (2023-2030 = 8 years)
        assert len(data) == 8
        assert all("year" in item for item in data)
        assert all("actual_cap_hit" in item for item in data)
        assert all("expected_cap_hit" in item for item in data)
        # Check that years are sequential
        years = [item["year"] for item in data]
        assert years == sorted(years)
        assert years[0] == 2023
        assert years[-1] == 2030
    
    def test_get_contract_predictions_player_not_found(self, client):
        """Test 404 when player doesn't exist"""
        response = client.get("/api/players/999/contract-predictions")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_contract_predictions_no_contracts(self, client, db_session, sample_player_data):
        """Test empty list when player has no contracts"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        response = client.get(f"/api/players/{player.id}/contract-predictions")
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    @patch('app.routers.players.predict')
    def test_get_contract_predictions_year_aggregation(self, mock_predict, client, db_session,
                                                        sample_player_data, sample_contract_data,
                                                        sample_advanced_skater_stats_data):
        """Test that predictions are correctly aggregated by year"""
        # Setup player
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        # Create two contracts that overlap in years
        contract1_data = sample_contract_data.copy()
        contract1_data["player_id"] = player.id
        contract1_data["start_year"] = 2023
        contract1_data["end_year"] = 2025
        contract1_data["cap_hit"] = Decimal("5000000")
        contract1 = Contract(**contract1_data)
        db_session.add(contract1)
        db_session.commit()
        db_session.refresh(contract1)
        
        contract2_data = sample_contract_data.copy()
        contract2_data["player_id"] = player.id
        contract2_data["start_year"] = 2024
        contract2_data["end_year"] = 2026
        contract2_data["cap_hit"] = Decimal("7000000")
        contract2 = Contract(**contract2_data)
        db_session.add(contract2)
        db_session.commit()
        db_session.refresh(contract2)
        
        # Setup stats for both contracts
        stats1_data = sample_advanced_skater_stats_data.copy()
        stats1_data["player_id"] = player.id
        stats1_data["contract_id"] = contract1.id
        stats1_data["season"] = 2023
        stats1 = AdvancedSkaterStats(**stats1_data)
        db_session.add(stats1)
        
        stats2_data = sample_advanced_skater_stats_data.copy()
        stats2_data["player_id"] = player.id
        stats2_data["contract_id"] = contract2.id
        stats2_data["season"] = 2024
        stats2 = AdvancedSkaterStats(**stats2_data)
        db_session.add(stats2)
        db_session.commit()
        
        # Mock prediction to return values
        mock_result_df = pd.DataFrame({'predicted_cap_hit': [6000000.0]})
        mock_predict.return_value = mock_result_df
        
        response = client.get(f"/api/players/{player.id}/contract-predictions")
        assert response.status_code == 200
        data = response.json()
        
        # 2024 and 2025 should have aggregated cap hits (5M + 7M = 12M)
        year_2024 = next(item for item in data if item["year"] == 2024)
        assert year_2024["actual_cap_hit"] == 12000000.0
        
        # 2023 should only have contract1
        year_2023 = next(item for item in data if item["year"] == 2023)
        assert year_2023["actual_cap_hit"] == 5000000.0
    
    @patch('app.routers.players.predict')
    def test_get_contract_predictions_no_stats(self, mock_predict, client, db_session,
                                                sample_player_data, sample_contract_data):
        """Test handling when contract has no advanced stats"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()
        
        # Don't add any stats, so prediction should be skipped
        response = client.get(f"/api/players/{player.id}/contract-predictions")
        assert response.status_code == 200
        data = response.json()
        # Should return empty list since no stats available
        assert data == []
    
    @patch('app.routers.players.predict')
    def test_get_contract_predictions_model_selection_forward(self, mock_predict, client, db_session,
                                                               sample_player_data, sample_contract_data,
                                                               sample_advanced_skater_stats_data):
        """Test correct model selection for forward"""
        player = Player(**sample_player_data)  # Position is "C"
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        
        stats_data = sample_advanced_skater_stats_data.copy()
        stats_data["player_id"] = player.id
        stats_data["contract_id"] = contract.id
        stats = AdvancedSkaterStats(**stats_data)
        db_session.add(stats)
        db_session.commit()
        
        import pandas as pd
        mock_result_df = pd.DataFrame({'predicted_cap_hit': [10000000.0]})
        mock_predict.return_value = mock_result_df
        
        response = client.get(f"/api/players/{player.id}/contract-predictions")
        assert response.status_code == 200
        
        # Verify forward_model was called
        assert mock_predict.called
        call_args = mock_predict.call_args
        assert call_args[1]["model_name"] == "forward_model"
    
    @patch('app.routers.players.predict')
    def test_get_contract_predictions_model_selection_defenseman(self, mock_predict, client, db_session,
                                                                  sample_contract_data,
                                                                  sample_advanced_skater_stats_data):
        """Test correct model selection for defenseman"""
        player = Player(firstname="Cale", lastname="Makar", team="COL", position="D", age=25)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        
        stats_data = sample_advanced_skater_stats_data.copy()
        stats_data["player_id"] = player.id
        stats_data["contract_id"] = contract.id
        stats = AdvancedSkaterStats(**stats_data)
        db_session.add(stats)
        db_session.commit()
        
        import pandas as pd
        mock_result_df = pd.DataFrame({'predicted_cap_hit': [8000000.0]})
        mock_predict.return_value = mock_result_df
        
        response = client.get(f"/api/players/{player.id}/contract-predictions")
        assert response.status_code == 200
        
        # Verify defenseman_model was called
        call_args = mock_predict.call_args
        assert call_args[1]["model_name"] == "defenseman_model"
    
    @patch('app.routers.players.predict')
    def test_get_contract_predictions_model_selection_goalie(self, mock_predict, client, db_session,
                                                              sample_contract_data,
                                                              sample_advanced_goalie_stats_data,
                                                              sample_basic_goalie_stats_data):
        """Test correct model selection for goalie"""
        player = Player(firstname="Connor", lastname="Hellebuyck", team="WPG", position="G", age=30)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        
        stats_data = sample_advanced_goalie_stats_data.copy()
        stats_data["player_id"] = player.id
        stats_data["contract_id"] = contract.id
        stats = AdvancedGoalieStats(**stats_data)
        db_session.add(stats)
        
        basic_stats_data = sample_basic_goalie_stats_data.copy()
        basic_stats_data["player_id"] = player.id
        basic_stats_data["contract_id"] = contract.id
        basic_stats = BasicGoalieStats(**basic_stats_data)
        db_session.add(basic_stats)
        db_session.commit()
        
        import pandas as pd
        mock_result_df = pd.DataFrame({'predicted_cap_hit': [6000000.0]})
        mock_predict.return_value = mock_result_df
        
        response = client.get(f"/api/players/{player.id}/contract-predictions")
        assert response.status_code == 200
        
        # Verify goalie_model was called
        call_args = mock_predict.call_args
        assert call_args[1]["model_name"] == "goalie_model"
    
    @patch('app.routers.players.predict')
    def test_get_contract_predictions_prediction_error_handling(self, mock_predict, client, db_session,
                                                                 sample_player_data, sample_contract_data,
                                                                 sample_advanced_skater_stats_data):
        """Test that contracts with prediction errors are skipped"""
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
        
        stats_data = sample_advanced_skater_stats_data.copy()
        stats_data["player_id"] = player.id
        stats_data["contract_id"] = contract.id
        stats = AdvancedSkaterStats(**stats_data)
        db_session.add(stats)
        db_session.commit()
        
        # Mock prediction to raise an error
        mock_predict.side_effect = ValueError("Missing features")
        
        response = client.get(f"/api/players/{player.id}/contract-predictions")
        assert response.status_code == 200
        data = response.json()
        # Should return empty list when prediction fails
        assert data == []

