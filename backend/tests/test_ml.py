import pytest
from unittest.mock import patch, MagicMock


class TestPredictContract:
    """Test POST /api/ml/predict endpoint"""
    
    @patch('app.routers.ml.predict_single_player')
    def test_predict_forward_success(self, mock_predict, client):
        """Test successful prediction for a forward"""
        mock_predict.return_value = 8500000.0
        
        request_data = {
            "position": "C",
            "gp": 82,
            "goals": 45,
            "assists": 55,
            "points": 100,
            "plus_minus": 20,
            "pim": 30,
            "shots": 250,
            "shootpct": 18.0
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "predicted_cap_hit" in data
        assert data["predicted_cap_hit"] == 8500000.0
        assert isinstance(data["predicted_cap_hit"], float)
        
        # Verify the mock was called with correct arguments
        mock_predict.assert_called_once()
        call_args = mock_predict.call_args
        assert call_args[1]["model_name"] == "forward_model"
        assert call_args[0][0]["position"] == "C"
        assert call_args[0][0]["gp"] == 82
    
    @patch('app.routers.ml.predict_single_player')
    def test_predict_defenseman_success(self, mock_predict, client):
        """Test successful prediction for a defenseman"""
        mock_predict.return_value = 6500000.0
        
        request_data = {
            "position": "defenseman",
            "gp": 82,
            "goals": 15,
            "assists": 45,
            "points": 60,
            "plus_minus": 25,
            "pim": 20,
            "shots": 180,
            "shootpct": 8.3
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["predicted_cap_hit"] == 6500000.0
        
        # Verify defenseman model was used
        call_args = mock_predict.call_args
        assert call_args[1]["model_name"] == "defenseman_model"
    
    @patch('app.routers.ml.predict_single_player')
    def test_predict_defenseman_case_insensitive(self, mock_predict, client):
        """Test that defenseman position is case insensitive"""
        mock_predict.return_value = 6500000.0
        
        request_data = {
            "position": "Defenseman",
            "gp": 82,
            "goals": 15,
            "assists": 45,
            "points": 60,
            "plus_minus": 25,
            "pim": 20,
            "shots": 180,
            "shootpct": 8.3
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        
        call_args = mock_predict.call_args
        assert call_args[1]["model_name"] == "defenseman_model"
    
    @patch('app.routers.ml.predict_single_player')
    def test_predict_goalie_success(self, mock_predict, client):
        """Test successful prediction for a goalie"""
        mock_predict.return_value = 5000000.0
        
        request_data = {
            "position": "goalie",
            "gp": 60,
            "goals": 0,
            "assists": 2,
            "points": 2,
            "plus_minus": 0,
            "pim": 4,
            "shots": 0,
            "shootpct": 0.0
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["predicted_cap_hit"] == 5000000.0
        
        # Verify goalie model was used
        call_args = mock_predict.call_args
        assert call_args[1]["model_name"] == "goalie_model"
    
    @patch('app.routers.ml.predict_single_player')
    def test_predict_forward_default_position(self, mock_predict, client):
        """Test that forward is default when position is not defenseman or goalie"""
        mock_predict.return_value = 7500000.0
        
        request_data = {
            "position": "LW",
            "gp": 82,
            "goals": 30,
            "assists": 40,
            "points": 70,
            "plus_minus": 15,
            "pim": 25,
            "shots": 200,
            "shootpct": 15.0
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        
        call_args = mock_predict.call_args
        assert call_args[1]["model_name"] == "forward_model"
    
    def test_predict_missing_field(self, client):
        """Test prediction with missing required field"""
        request_data = {
            "position": "C",
            "gp": 82,
            "goals": 45,
            # Missing assists, points, etc.
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_predict_invalid_type(self, client):
        """Test prediction with invalid data type"""
        request_data = {
            "position": "C",
            "gp": "eighty-two",  # Should be int
            "goals": 45,
            "assists": 55,
            "points": 100,
            "plus_minus": 20,
            "pim": 30,
            "shots": 250,
            "shootpct": 18.0
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_predict_empty_request(self, client):
        """Test prediction with empty request body"""
        response = client.post("/api/ml/predict", json={})
        assert response.status_code == 422  # Validation error
    
    @patch('app.routers.ml.predict_single_player')
    def test_predict_model_not_found(self, mock_predict, client):
        """Test prediction when model file is not found"""
        mock_predict.side_effect = FileNotFoundError("Model file not found")
        
        request_data = {
            "position": "C",
            "gp": 82,
            "goals": 45,
            "assists": 55,
            "points": 100,
            "plus_minus": 20,
            "pim": 30,
            "shots": 250,
            "shootpct": 18.0
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 500
        assert "Model not found" in response.json()["detail"]
    
    @patch('app.routers.ml.predict_single_player')
    def test_predict_generic_error(self, mock_predict, client):
        """Test prediction when a generic error occurs"""
        mock_predict.side_effect = ValueError("Invalid input data")
        
        request_data = {
            "position": "C",
            "gp": 82,
            "goals": 45,
            "assists": 55,
            "points": 100,
            "plus_minus": 20,
            "pim": 30,
            "shots": 250,
            "shootpct": 18.0
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 500
        assert "Prediction error" in response.json()["detail"]
    
    @patch('app.routers.ml.predict_single_player')
    def test_predict_negative_values(self, mock_predict, client):
        """Test prediction with negative values (edge case)"""
        mock_predict.return_value = 1000000.0
        
        request_data = {
            "position": "C",
            "gp": 82,
            "goals": 45,
            "assists": 55,
            "points": 100,
            "plus_minus": -10,  # Negative value
            "pim": 30,
            "shots": 250,
            "shootpct": 18.0
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        # Should still work, just passes the values through
    
    @patch('app.routers.ml.predict_single_player')
    def test_predict_zero_values(self, mock_predict, client):
        """Test prediction with zero values (rookie player)"""
        mock_predict.return_value = 925000.0  # ELC contract
        
        request_data = {
            "position": "C",
            "gp": 0,
            "goals": 0,
            "assists": 0,
            "points": 0,
            "plus_minus": 0,
            "pim": 0,
            "shots": 0,
            "shootpct": 0.0
        }
        
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "predicted_cap_hit" in data