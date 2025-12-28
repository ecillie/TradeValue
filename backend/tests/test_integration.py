import pytest
from unittest.mock import patch
import pandas as pd
from decimal import Decimal
from app.models import Player, Contract, AdvancedSkaterStats, AdvancedGoalieStats, BasicGoalieStats


class TestPredictionIntegration:
    """Integration tests for full prediction flow"""
    
    @patch('app.routers.players.predict')
    def test_full_prediction_flow_skater(self, mock_predict, client, db_session,
                                           sample_player_data, sample_contract_data,
                                           sample_advanced_skater_stats_data):
        """Test complete flow: stats -> features -> prediction"""
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
        
        # Mock prediction
        mock_result_df = pd.DataFrame({'predicted_cap_hit': [11000000.0]})
        mock_predict.return_value = mock_result_df
        
        # Test contract predictions endpoint
        response = client.get(f"/api/players/{player.id}/contract-predictions")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) > 0
        assert all("year" in item for item in data)
        assert all("actual_cap_hit" in item for item in data)
        assert all("expected_cap_hit" in item for item in data)
        
        # Verify prediction was called
        assert mock_predict.called
    
    @patch('app.routers.players.predict')
    def test_full_prediction_flow_goalie(self, mock_predict, client, db_session,
                                           sample_contract_data,
                                           sample_advanced_goalie_stats_data,
                                           sample_basic_goalie_stats_data):
        """Test complete goalie prediction flow"""
        player = Player(
            firstname="Connor",
            lastname="Hellebuyck",
            team="WPG",
            position="G",
            age=30
        )
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        
        # Add advanced goalie stats
        adv_stats_data = sample_advanced_goalie_stats_data.copy()
        adv_stats_data["player_id"] = player.id
        adv_stats_data["contract_id"] = contract.id
        adv_stats = AdvancedGoalieStats(**adv_stats_data)
        db_session.add(adv_stats)
        
        # Add basic goalie stats
        basic_stats_data = sample_basic_goalie_stats_data.copy()
        basic_stats_data["player_id"] = player.id
        basic_stats_data["contract_id"] = contract.id
        basic_stats = BasicGoalieStats(**basic_stats_data)
        db_session.add(basic_stats)
        db_session.commit()
        
        # Mock prediction
        mock_result_df = pd.DataFrame({'predicted_cap_hit': [6500000.0]})
        mock_predict.return_value = mock_result_df
        
        # Test contract predictions
        response = client.get(f"/api/players/{player.id}/contract-predictions")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) > 0
        # Verify goalie model was used
        call_args = mock_predict.call_args
        assert call_args[1]["model_name"] == "goalie_model"
    
    @patch('app.routers.players.predict')
    def test_contract_predictions_multiple_contracts(self, mock_predict, client, db_session,
                                                       sample_player_data, sample_contract_data,
                                                       sample_advanced_skater_stats_data):
        """Test predictions with multiple contracts across different years"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        # First contract
        contract1_data = sample_contract_data.copy()
        contract1_data["player_id"] = player.id
        contract1_data["start_year"] = 2020
        contract1_data["end_year"] = 2022
        contract1_data["cap_hit"] = Decimal("8000000")
        contract1 = Contract(**contract1_data)
        db_session.add(contract1)
        db_session.commit()
        db_session.refresh(contract1)
        
        # Second contract (non-overlapping)
        contract2_data = sample_contract_data.copy()
        contract2_data["player_id"] = player.id
        contract2_data["start_year"] = 2023
        contract2_data["end_year"] = 2025
        contract2_data["cap_hit"] = Decimal("12000000")
        contract2 = Contract(**contract2_data)
        db_session.add(contract2)
        db_session.commit()
        db_session.refresh(contract2)
        
        # Add stats for both contracts
        stats1_data = sample_advanced_skater_stats_data.copy()
        stats1_data["player_id"] = player.id
        stats1_data["contract_id"] = contract1.id
        stats1_data["season"] = 2020
        stats1 = AdvancedSkaterStats(**stats1_data)
        db_session.add(stats1)
        
        stats2_data = sample_advanced_skater_stats_data.copy()
        stats2_data["player_id"] = player.id
        stats2_data["contract_id"] = contract2.id
        stats2_data["season"] = 2023
        stats2 = AdvancedSkaterStats(**stats2_data)
        db_session.add(stats2)
        db_session.commit()
        
        # Mock prediction
        mock_result_df = pd.DataFrame({'predicted_cap_hit': [10000000.0]})
        mock_predict.return_value = mock_result_df
        
        response = client.get(f"/api/players/{player.id}/contract-predictions")
        assert response.status_code == 200
        data = response.json()
        
        # Should have predictions for all years (2020-2022, 2023-2025)
        years = [item["year"] for item in data]
        assert 2020 in years
        assert 2022 in years
        assert 2023 in years
        assert 2025 in years
        
        # Verify non-overlapping years have correct cap hits
        year_2022 = next(item for item in data if item["year"] == 2022)
        assert year_2022["actual_cap_hit"] == 8000000.0
        
        year_2023 = next(item for item in data if item["year"] == 2023)
        assert year_2023["actual_cap_hit"] == 12000000.0

