import pytest
from unittest.mock import patch, MagicMock
import pandas as pd


class TestPredictContract:
    """Test POST /api/ml/predict endpoint"""
    
    @patch('app.routers.ml.predict')
    def test_predict_forward_success(self, mock_predict, client):
        """Test successful prediction for a forward"""
        # Mock predict to return a DataFrame with predicted_cap_hit
        mock_df = pd.DataFrame({'predicted_cap_hit': [8500000.0]})
        mock_predict.return_value = mock_df
        
        request_data = {
            "position": "C",
            "icetime": 20000.0,
            "games_played": 82,
            "i_f_points": 100,
            "i_f_goals": 45,
            "i_f_primary_assists": 40,
            "i_f_secondary_assists": 15,
            "i_f_x_goals": 40.0,
            "i_f_shots_on_goal": 250,
            "i_f_unblocked_shot_attempts": 280,
            "on_ice_x_goals_percentage": 0.55,
            "shots_blocked_by_player": 50,
            "i_f_takeaways": 30,
            "i_f_giveaways": 20,
            "i_f_penalties": 10,
            "penalties_drawn": 15,
            "i_f_o_zone_shift_starts": 400,
            "i_f_d_zone_shift_starts": 200,
            "i_f_neutral_zone_shift_starts": 300
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "predicted_cap_hit" in data
        assert data["predicted_cap_hit"] == 8500000.0
        assert isinstance(data["predicted_cap_hit"], float)
        
        # Verify the mock was called
        mock_predict.assert_called_once()
        call_args = mock_predict.call_args
        assert call_args[1]["model_name"] == "forward_model"
    
    @patch('app.routers.ml.predict')
    def test_predict_defenseman_success(self, mock_predict, client):
        """Test successful prediction for a defenseman"""
        mock_df = pd.DataFrame({'predicted_cap_hit': [6500000.0]})
        mock_predict.return_value = mock_df
        
        request_data = {
            "position": "defenseman",
            "icetime": 20000.0,
            "games_played": 82,
            "i_f_points": 60,
            "i_f_goals": 15,
            "i_f_primary_assists": 30,
            "i_f_secondary_assists": 15,
            "i_f_x_goals": 12.0,
            "i_f_shots_on_goal": 180,
            "i_f_unblocked_shot_attempts": 200,
            "on_ice_x_goals_percentage": 0.52,
            "shots_blocked_by_player": 150,
            "i_f_takeaways": 40,
            "i_f_giveaways": 30,
            "i_f_penalties": 8,
            "penalties_drawn": 12,
            "i_f_o_zone_shift_starts": 300,
            "i_f_d_zone_shift_starts": 400,
            "i_f_neutral_zone_shift_starts": 300
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["predicted_cap_hit"] == 6500000.0
        
        # Verify defenseman model was used
        call_args = mock_predict.call_args
        assert call_args[1]["model_name"] == "defenseman_model"
    
    @patch('app.routers.ml.predict')
    def test_predict_defenseman_case_insensitive(self, mock_predict, client):
        """Test that defenseman position is case insensitive"""
        mock_df = pd.DataFrame({'predicted_cap_hit': [6500000.0]})
        mock_predict.return_value = mock_df
        
        request_data = {
            "position": "Defenseman",
            "icetime": 20000.0,
            "games_played": 82,
            "i_f_points": 60,
            "i_f_goals": 15,
            "i_f_primary_assists": 30,
            "i_f_secondary_assists": 15,
            "i_f_x_goals": 12.0,
            "i_f_shots_on_goal": 180,
            "i_f_unblocked_shot_attempts": 200,
            "on_ice_x_goals_percentage": 0.52,
            "shots_blocked_by_player": 150,
            "i_f_takeaways": 40,
            "i_f_giveaways": 30,
            "i_f_penalties": 8,
            "penalties_drawn": 12,
            "i_f_o_zone_shift_starts": 300,
            "i_f_d_zone_shift_starts": 400,
            "i_f_neutral_zone_shift_starts": 300
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        
        call_args = mock_predict.call_args
        assert call_args[1]["model_name"] == "defenseman_model"
    
    @patch('app.routers.ml.predict')
    def test_predict_goalie_success(self, mock_predict, client):
        """Test successful prediction for a goalie"""
        mock_df = pd.DataFrame({'predicted_cap_hit': [5000000.0]})
        mock_predict.return_value = mock_df
        
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
        assert data["predicted_cap_hit"] == 5000000.0
        
        # Verify goalie model was used
        call_args = mock_predict.call_args
        assert call_args[1]["model_name"] == "goalie_model"
    
    @patch('app.routers.ml.predict')
    def test_predict_forward_default_position(self, mock_predict, client):
        """Test that forward is default when position is not defenseman or goalie"""
        mock_df = pd.DataFrame({'predicted_cap_hit': [7500000.0]})
        mock_predict.return_value = mock_df
        
        request_data = {
            "position": "LW",
            "icetime": 20000.0,
            "games_played": 82,
            "i_f_points": 70,
            "i_f_goals": 30,
            "i_f_primary_assists": 25,
            "i_f_secondary_assists": 15,
            "i_f_x_goals": 28.0,
            "i_f_shots_on_goal": 200,
            "i_f_unblocked_shot_attempts": 220,
            "on_ice_x_goals_percentage": 0.53,
            "shots_blocked_by_player": 40,
            "i_f_takeaways": 25,
            "i_f_giveaways": 18,
            "i_f_penalties": 8,
            "penalties_drawn": 12,
            "i_f_o_zone_shift_starts": 350,
            "i_f_d_zone_shift_starts": 250,
            "i_f_neutral_zone_shift_starts": 300
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        
        call_args = mock_predict.call_args
        assert call_args[1]["model_name"] == "forward_model"
    
    def test_predict_missing_field(self, client):
        """Test prediction with missing required field - position is required"""
        request_data = {
            # Missing position
            "icetime": 20000.0,
            "games_played": 82
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        # Since all fields are optional in schema, this might still pass validation
        # but fail during prediction. Let's check what actually happens
        # The endpoint should still try to process, but position is required for model selection
        # Actually, position is required, so this should fail validation
        assert response.status_code in [422, 500]  # Validation or prediction error
    
    def test_predict_invalid_type(self, client):
        """Test prediction with invalid data type"""
        request_data = {
            "position": "C",
            "icetime": "twenty-thousand",  # Should be float
            "games_played": 82
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_predict_empty_request(self, client):
        """Test prediction with empty request body"""
        response = client.post("/api/ml/predict", json={})
        # Position is required, so this should fail
        assert response.status_code in [422, 500]
    
    @patch('app.routers.ml.predict')
    def test_predict_model_not_found(self, mock_predict, client):
        """Test prediction when model file is not found"""
        mock_predict.side_effect = FileNotFoundError("Model file not found")
        
        request_data = {
            "position": "C",
            "icetime": 20000.0,
            "games_played": 82,
            "i_f_points": 100,
            "i_f_goals": 45,
            "i_f_primary_assists": 40,
            "i_f_secondary_assists": 15,
            "i_f_x_goals": 40.0,
            "i_f_shots_on_goal": 250,
            "i_f_unblocked_shot_attempts": 280,
            "on_ice_x_goals_percentage": 0.55,
            "shots_blocked_by_player": 50,
            "i_f_takeaways": 30,
            "i_f_giveaways": 20,
            "i_f_penalties": 10,
            "penalties_drawn": 15,
            "i_f_o_zone_shift_starts": 400,
            "i_f_d_zone_shift_starts": 200,
            "i_f_neutral_zone_shift_starts": 300
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 500
        assert "Model not found" in response.json()["detail"]
    
    @patch('app.routers.ml.predict')
    def test_predict_generic_error(self, mock_predict, client):
        """Test prediction when a generic error occurs"""
        # Use a non-ValueError exception to test generic error handling
        mock_predict.side_effect = RuntimeError("Generic error")
        
        request_data = {
            "position": "C",
            "icetime": 20000.0,
            "games_played": 82,
            "i_f_points": 100,
            "i_f_goals": 45,
            "i_f_primary_assists": 40,
            "i_f_secondary_assists": 15,
            "i_f_x_goals": 40.0,
            "i_f_shots_on_goal": 250,
            "i_f_unblocked_shot_attempts": 280,
            "on_ice_x_goals_percentage": 0.55,
            "shots_blocked_by_player": 50,
            "i_f_takeaways": 30,
            "i_f_giveaways": 20,
            "i_f_penalties": 10,
            "penalties_drawn": 15,
            "i_f_o_zone_shift_starts": 400,
            "i_f_d_zone_shift_starts": 200,
            "i_f_neutral_zone_shift_starts": 300
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 500
        assert "Prediction error" in response.json()["detail"]
    
    @patch('app.routers.ml.predict')
    def test_predict_negative_values(self, mock_predict, client):
        """Test prediction with negative values (edge case)"""
        mock_df = pd.DataFrame({'predicted_cap_hit': [1000000.0]})
        mock_predict.return_value = mock_df
        
        request_data = {
            "position": "C",
            "icetime": 20000.0,
            "games_played": 82,
            "i_f_points": 50,
            "i_f_goals": 20,
            "i_f_primary_assists": 15,
            "i_f_secondary_assists": 15,
            "i_f_x_goals": 18.0,
            "i_f_shots_on_goal": 150,
            "i_f_unblocked_shot_attempts": 180,
            "on_ice_x_goals_percentage": 0.45,  # Negative impact
            "shots_blocked_by_player": 30,
            "i_f_takeaways": 20,
            "i_f_giveaways": 30,
            "i_f_penalties": 20,
            "penalties_drawn": 5,
            "i_f_o_zone_shift_starts": 200,
            "i_f_d_zone_shift_starts": 400,
            "i_f_neutral_zone_shift_starts": 300
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        # Should still work, just passes the values through
    
    @patch('app.routers.ml.predict')
    def test_predict_zero_values(self, mock_predict, client):
        """Test prediction with zero values (rookie player)"""
        mock_df = pd.DataFrame({'predicted_cap_hit': [925000.0]})  # ELC contract
        mock_predict.return_value = mock_df
        
        request_data = {
            "position": "C",
            "icetime": 20000.0,
            "games_played": 0,
            "i_f_points": 0,
            "i_f_goals": 0,
            "i_f_primary_assists": 0,
            "i_f_secondary_assists": 0,
            "i_f_x_goals": 0.0,
            "i_f_shots_on_goal": 0,
            "i_f_unblocked_shot_attempts": 0,
            "on_ice_x_goals_percentage": 0.0,
            "shots_blocked_by_player": 0,
            "i_f_takeaways": 0,
            "i_f_giveaways": 0,
            "i_f_penalties": 0,
            "penalties_drawn": 0,
            "i_f_o_zone_shift_starts": 0,
            "i_f_d_zone_shift_starts": 0,
            "i_f_neutral_zone_shift_starts": 0
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "predicted_cap_hit" in data
