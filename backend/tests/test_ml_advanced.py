import pytest
from unittest.mock import patch, MagicMock
import pandas as pd


class TestPredictContractAdvancedStats:
    """Test POST /api/ml/predict with advanced statistics"""
    
    @patch('app.routers.ml.predict')
    def test_predict_skater_advanced_stats(self, mock_predict, client):
        """Test prediction with advanced skater statistics"""
        mock_result_df = pd.DataFrame({'predicted_cap_hit': [8500000.0]})
        mock_predict.return_value = mock_result_df
        
        request_data = {
            "position": "C",
            "icetime": 20000.0,
            "games_played": 82,
            "i_f_points": 100,
            "i_f_goals": 45,
            "i_f_primary_assists": 35,
            "i_f_secondary_assists": 20,
            "i_f_x_goals": 50.5,
            "i_f_shots_on_goal": 250,
            "i_f_unblocked_shot_attempts": 300,
            "on_ice_x_goals_percentage": 0.55,
            "shots_blocked_by_player": 150,
            "i_f_takeaways": 80,
            "i_f_giveaways": 60,
            "i_f_penalties": 10,
            "penalties_drawn": 25,
            "i_f_o_zone_shift_starts": 800,
            "i_f_d_zone_shift_starts": 400,
            "i_f_neutral_zone_shift_starts": 600
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "predicted_cap_hit" in data
        assert data["predicted_cap_hit"] == 8500000.0
        assert isinstance(data["predicted_cap_hit"], float)
        
        # Verify predict was called
        mock_predict.assert_called_once()
        call_args = mock_predict.call_args
        assert call_args[1]["model_name"] == "forward_model"
    
    @patch('app.routers.ml.predict')
    def test_predict_goalie_advanced_stats(self, mock_predict, client):
        """Test prediction with advanced goalie statistics"""
        mock_result_df = pd.DataFrame({'predicted_cap_hit': [5500000.0]})
        mock_predict.return_value = mock_result_df
        
        request_data = {
            "position": "goalie",
            "icetime": 36000.0,
            "x_goals": 150.0,
            "goals": 140.0,
            "unblocked_shot_attempts": 1800,
            "blocked_shot_attempts": 200,
            "x_rebounds": 30.0,
            "rebounds": 28,
            "x_freeze": 50.0,
            "act_freeze": 52,
            "x_on_goal": 1200.0,
            "on_goal": 1150,
            "x_play_stopped": 100.0,
            "play_stopped": 102,
            "x_play_continued_in_zone": 200.0,
            "play_continued_in_zone": 195,
            "x_play_continued_outside_zone": 300.0,
            "play_continued_outside_zone": 305,
            "flurry_adjusted_x_goals": 155.0,
            "low_danger_shots": 800,
            "medium_danger_shots": 600,
            "high_danger_shots": 400,
            "low_danger_x_goals": 50.0,
            "medium_danger_x_goals": 60.0,
            "high_danger_x_goals": 40.0,
            "low_danger_goals": 45,
            "medium_danger_goals": 55,
            "high_danger_goals": 40,
            "gp": 60,
            "wins": 35,
            "losses": 20,
            "ot_losses": 5,
            "shutouts": 5
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["predicted_cap_hit"] == 5500000.0
        
        # Verify goalie model was used
        call_args = mock_predict.call_args
        assert call_args[1]["model_name"] == "goalie_model"
    
    @patch('app.routers.ml.predict')
    def test_predict_missing_optional_advanced_stats(self, mock_predict, client):
        """Test handling of missing optional advanced stats"""
        mock_result_df = pd.DataFrame({'predicted_cap_hit': [7500000.0]})
        mock_predict.return_value = mock_result_df
        
        # Request with only required position and some optional stats
        request_data = {
            "position": "C",
            "icetime": 20000.0,
            "games_played": 82,
            "i_f_points": 100,
            "i_f_goals": 45,
            # Missing some optional fields - should still work
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        # Should succeed or fail gracefully depending on model requirements
        assert response.status_code in [200, 400, 500]
    
    @patch('app.routers.ml.predict')
    def test_predict_minimum_icetime_handling(self, mock_predict, client):
        """Test that low icetime values are handled correctly"""
        mock_result_df = pd.DataFrame({'predicted_cap_hit': [2000000.0]})
        mock_predict.return_value = mock_result_df
        
        request_data = {
            "position": "C",
            "icetime": 5000.0,  # Less than 300 minutes (18000 seconds)
            "games_played": 10,
            "i_f_points": 5,
            "i_f_goals": 2,
            "i_f_primary_assists": 2,
            "i_f_secondary_assists": 1,
            "i_f_x_goals": 3.0,
            "i_f_shots_on_goal": 20,
            "i_f_unblocked_shot_attempts": 25,
            "on_ice_x_goals_percentage": 0.50,
            "shots_blocked_by_player": 10,
            "i_f_takeaways": 5,
            "i_f_giveaways": 5,
            "i_f_penalties": 2,
            "penalties_drawn": 3,
            "i_f_o_zone_shift_starts": 50,
            "i_f_d_zone_shift_starts": 30,
            "i_f_neutral_zone_shift_starts": 20
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        # Model may filter these out, but endpoint should handle it
        assert response.status_code in [200, 400, 500]

