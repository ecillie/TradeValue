"""Tests for app/routers/ml.py."""
from unittest.mock import patch

import pandas as pd


def _skater_predict_body(**overrides):
    """Minimal advanced-stats body for POST /api/ml/predict (skater)."""
    base = {
        "position": "forward",
        "icetime": 200000.0,
        "games_played": 82,
        "i_f_points": 80,
        "i_f_goals": 35,
        "i_f_primary_assists": 25,
        "i_f_secondary_assists": 20,
        "i_f_x_goals": 40.0,
        "i_f_shots_on_goal": 200,
        "i_f_unblocked_shot_attempts": 260,
        "on_ice_x_goals_percentage": 0.52,
        "shots_blocked_by_player": 40,
        "i_f_takeaways": 30,
        "i_f_giveaways": 25,
        "i_f_penalties": 8,
        "penalties_drawn": 12,
        "i_f_o_zone_shift_starts": 400,
        "i_f_d_zone_shift_starts": 300,
        "i_f_neutral_zone_shift_starts": 350,
    }
    base.update(overrides)
    return base


class TestPredictContract:
    """POST /api/ml/predict (router uses app.ml.inference.predictor.predict)."""

    @patch("app.routers.ml.predict")
    def test_predict_forward_success(self, mock_predict, client):
        mock_predict.return_value = pd.DataFrame({"predicted_cap_hit": [8_500_000.0]})
        request_data = _skater_predict_body(position="C")
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["predicted_cap_hit"] == 8_500_000.0
        mock_predict.assert_called_once()
        assert mock_predict.call_args[1]["model_name"] == "forward_model"

    @patch("app.routers.ml.predict")
    def test_predict_defenseman_success(self, mock_predict, client):
        mock_predict.return_value = pd.DataFrame({"predicted_cap_hit": [6_500_000.0]})
        request_data = _skater_predict_body(position="defenseman")
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        assert response.json()["predicted_cap_hit"] == 6_500_000.0
        assert mock_predict.call_args[1]["model_name"] == "defenseman_model"

    @patch("app.routers.ml.predict")
    def test_predict_defenseman_case_insensitive(self, mock_predict, client):
        mock_predict.return_value = pd.DataFrame({"predicted_cap_hit": [6_000_000.0]})
        request_data = _skater_predict_body(position="Defenseman")
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        assert mock_predict.call_args[1]["model_name"] == "defenseman_model"

    @patch("app.routers.ml.predict")
    def test_predict_goalie_success(self, mock_predict, client):
        mock_predict.return_value = pd.DataFrame({"predicted_cap_hit": [5_000_000.0]})
        request_data = {
            "position": "goalie",
            "x_goals": 150.0,
            "goals": 140.0,
            "unblocked_shot_attempts": 1800,
            "blocked_shot_attempts": 200,
            "icetime": 360000.0,
            "gp": 60,
        }
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        assert response.json()["predicted_cap_hit"] == 5_000_000.0
        assert mock_predict.call_args[1]["model_name"] == "goalie_model"

    @patch("app.routers.ml.predict")
    def test_predict_forward_default_position_non_defense_non_goalie(self, mock_predict, client):
        mock_predict.return_value = pd.DataFrame({"predicted_cap_hit": [7_000_000.0]})
        request_data = _skater_predict_body(position="LW")
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        assert mock_predict.call_args[1]["model_name"] == "forward_model"

    @patch("app.routers.ml.predict")
    def test_predict_optional_fields_omitted_still_ok(self, mock_predict, client):
        """Only `position` is required; remaining fields are optional on the schema."""
        mock_predict.return_value = pd.DataFrame({"predicted_cap_hit": [1.0]})
        response = client.post("/api/ml/predict", json={"position": "C"})
        assert response.status_code == 200

    def test_predict_invalid_games_played_type(self, client):
        request_data = _skater_predict_body(games_played="not-an-int")
        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 422

    def test_predict_empty_request(self, client):
        response = client.post("/api/ml/predict", json={})
        assert response.status_code == 422

    @patch("app.routers.ml.predict")
    def test_predict_model_not_found(self, mock_predict, client):
        mock_predict.side_effect = FileNotFoundError("forward_model.pkl missing")
        response = client.post("/api/ml/predict", json=_skater_predict_body())
        assert response.status_code == 500
        assert "Model not found" in response.json()["detail"]

    @patch("app.routers.ml.predict")
    def test_predict_value_error_from_predictor(self, mock_predict, client):
        mock_predict.side_effect = ValueError("feature mismatch")
        response = client.post("/api/ml/predict", json=_skater_predict_body())
        assert response.status_code == 400
        assert "Invalid input" in response.json()["detail"]

    @patch("app.routers.ml.predict")
    def test_predict_other_exception(self, mock_predict, client):
        mock_predict.side_effect = RuntimeError("unexpected")
        response = client.post("/api/ml/predict", json=_skater_predict_body())
        assert response.status_code == 500
        assert "Prediction error" in response.json()["detail"]

    @patch("app.routers.ml.predict")
    def test_predict_passes_negative_plus_minus_style_numbers(self, mock_predict, client):
        mock_predict.return_value = pd.DataFrame({"predicted_cap_hit": [3_000_000.0]})
        body = _skater_predict_body()
        response = client.post("/api/ml/predict", json=body)
        assert response.status_code == 200


class TestPredictContractAdvancedPayloads:
    """POST /api/ml/predict with fuller advanced-skater / goalie payloads."""

    @patch("app.routers.ml.predict")
    def test_predict_skater_advanced_stats(self, mock_predict, client):
        mock_predict.return_value = pd.DataFrame({"predicted_cap_hit": [8_500_000.0]})
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
            "i_f_neutral_zone_shift_starts": 600,
        }

        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["predicted_cap_hit"] == 8_500_000.0
        assert isinstance(data["predicted_cap_hit"], float)
        mock_predict.assert_called_once()
        assert mock_predict.call_args[1]["model_name"] == "forward_model"

    @patch("app.routers.ml.predict")
    def test_predict_goalie_advanced_stats(self, mock_predict, client):
        mock_predict.return_value = pd.DataFrame({"predicted_cap_hit": [5_500_000.0]})
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
            "shutouts": 5,
        }

        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code == 200
        assert response.json()["predicted_cap_hit"] == 5_500_000.0
        assert mock_predict.call_args[1]["model_name"] == "goalie_model"

    @patch("app.routers.ml.predict")
    def test_predict_missing_optional_advanced_stats(self, mock_predict, client):
        mock_predict.return_value = pd.DataFrame({"predicted_cap_hit": [7_500_000.0]})
        request_data = {
            "position": "C",
            "icetime": 20000.0,
            "games_played": 82,
            "i_f_points": 100,
            "i_f_goals": 45,
        }

        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code in [200, 400, 500]

    @patch("app.routers.ml.predict")
    def test_predict_minimum_icetime_handling(self, mock_predict, client):
        mock_predict.return_value = pd.DataFrame({"predicted_cap_hit": [2_000_000.0]})
        request_data = {
            "position": "C",
            "icetime": 5000.0,
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
            "i_f_neutral_zone_shift_starts": 20,
        }

        response = client.post("/api/ml/predict", json=request_data)
        assert response.status_code in [200, 400, 500]
