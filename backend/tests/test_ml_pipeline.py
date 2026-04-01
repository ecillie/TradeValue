"""Tests for app/ml/data/features.py, dataset_builder.py, and inference/predictor.py."""
import os
from unittest.mock import MagicMock, patch

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression

import app.ml.inference.predictor as predictor
from app.ml.data import dataset_builder as ds
from app.ml.data.features import goalie_data_to_features, skater_data_to_features


def _skater_df_row():
    return {
        "icetime": 400000.0,
        "cap_hit": 5_000_000.0,
        "i_f_goals": 40,
        "i_f_primary_assists": 30,
        "i_f_secondary_assists": 20,
        "i_f_points": 90,
        "i_f_x_goals": 42.0,
        "i_f_shots_on_goal": 200,
        "i_f_unblocked_shot_attempts": 260,
        "on_ice_x_goals_percentage": 0.52,
        "shots_blocked_by_player": 40,
        "i_f_takeaways": 30,
        "i_f_giveaways": 25,
        "i_f_penalties": 10,
        "penalties_drawn": 15,
        "i_f_o_zone_shift_starts": 400,
        "i_f_d_zone_shift_starts": 300,
        "i_f_neutral_zone_shift_starts": 350,
        "rfa": False,
        "age": 27,
        "duration": 7,
    }


def _goalie_df_row():
    return {
        "icetime": 400000.0,
        "cap_hit": 6_000_000.0,
        "x_goals": 120.0,
        "goals": 115.0,
        "unblocked_shot_attempts": 1500,
        "on_goal": 1400,
        "high_danger_goals": 20,
        "high_danger_shots": 400,
        "rebounds": 30,
        "x_rebounds": 28.0,
        "act_freeze": 40,
        "x_freeze": 38.0,
        "rfa": False,
        "age": 28,
        "duration": 6,
        "id": 1,
        "season": 2023,
        "team": "NYR",
        "playoff": False,
    }


class TestSkaterFeatures:
    def test_returns_none_or_empty_unchanged(self):
        assert skater_data_to_features(None) is None
        assert skater_data_to_features(pd.DataFrame()).empty

    def test_filters_low_icetime(self):
        df = pd.DataFrame([{**_skater_df_row(), "icetime": 1000.0}])
        out = skater_data_to_features(df)
        assert out.empty

    def test_drops_bad_cap_hit(self):
        df = pd.DataFrame(
            [
                {**_skater_df_row(), "cap_hit": np.nan},
                {**_skater_df_row(), "cap_hit": 0},
            ]
        )
        out = skater_data_to_features(df)
        assert out.empty

    def test_happy_path(self):
        df = pd.DataFrame([_skater_df_row()])
        out = skater_data_to_features(df)
        assert not out.empty
        assert "log_cap_hit" in out.columns


class TestGoalieFeatures:
    def test_returns_none_or_empty(self):
        assert goalie_data_to_features(None) is None
        assert goalie_data_to_features(pd.DataFrame()).empty

    def test_filters_and_transforms(self):
        df = pd.DataFrame([_goalie_df_row()])
        out = goalie_data_to_features(df)
        assert not out.empty
        assert "log_cap_hit" in out.columns


class TestDatasetBuilder:
    @patch.object(ds, "build_skater_advanced_dataset", return_value=pd.DataFrame({"x": [1]}))
    @patch.object(ds, "SessionLocal")
    @patch.object(ds, "init_db")
    def test_build_forward_dataset(self, mock_init, mock_slocal, mock_build):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.filter.return_value.all.return_value = [
            MagicMock()
        ]
        mock_slocal.return_value = mock_session
        out = ds.build_forward_dataset()
        assert not out.empty
        mock_init.assert_called()

    @patch.object(ds, "build_skater_advanced_dataset", return_value=pd.DataFrame())
    @patch.object(ds, "SessionLocal")
    @patch.object(ds, "init_db")
    def test_build_defenseman_dataset(self, mock_init, mock_slocal, mock_build):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = [MagicMock()]
        mock_slocal.return_value = mock_session
        ds.build_defenseman_dataset()
        mock_init.assert_called()

    @patch.object(ds, "goalie_advanced_dataset", return_value=pd.DataFrame({"g": [1]}))
    @patch.object(ds, "SessionLocal")
    @patch.object(ds, "init_db")
    def test_build_goalie_dataset(self, mock_init, mock_slocal, mock_goalie):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = [MagicMock()]
        mock_slocal.return_value = mock_session
        out = ds.build_goalie_dataset()
        assert not out.empty

    @patch("pandas.read_sql", side_effect=RuntimeError("boom"))
    @patch.object(ds, "SessionLocal")
    @patch.object(ds, "init_db")
    def test_build_skater_advanced_dataset_exception_returns_empty(
        self, mock_init, mock_slocal, mock_read_sql
    ):
        mock_session = MagicMock()
        mock_slocal.return_value = mock_session
        p = MagicMock()
        p.id = 1
        out = ds.build_skater_advanced_dataset([p])
        assert out.empty

    @patch("pandas.read_sql")
    @patch.object(ds, "SessionLocal")
    @patch.object(ds, "init_db")
    def test_build_skater_empty_players(self, mock_init, mock_slocal, mock_read_sql):
        mock_session = MagicMock()
        mock_slocal.return_value = mock_session
        assert ds.build_skater_advanced_dataset([]).empty

    @patch("pandas.read_sql")
    @patch.object(ds, "SessionLocal")
    @patch.object(ds, "init_db")
    def test_build_skater_dedupes_contract_id(self, mock_init, mock_slocal, mock_read_sql):
        mock_session = MagicMock()
        mock_slocal.return_value = mock_session
        mock_read_sql.return_value = pd.DataFrame(
            {"contract_id": [1, 1], "icetime": [400000.0, 400000.0], "cap_hit": [1e6, 1e6]}
        )
        p = MagicMock()
        p.id = 1
        out = ds.build_skater_advanced_dataset([p])
        assert len(out) == 1

    @patch("pandas.read_sql", side_effect=RuntimeError("boom"))
    @patch.object(ds, "SessionLocal")
    @patch.object(ds, "init_db")
    def test_goalie_advanced_dataset_exception(self, mock_init, mock_slocal, mock_read_sql):
        mock_session = MagicMock()
        mock_slocal.return_value = mock_session
        p = MagicMock()
        p.id = 1
        assert ds.goalie_advanced_dataset([p]).empty

    @patch("pandas.read_sql")
    @patch.object(ds, "SessionLocal")
    @patch.object(ds, "init_db")
    def test_goalie_advanced_empty_players(self, mock_init, mock_slocal, mock_read_sql):
        mock_session = MagicMock()
        mock_slocal.return_value = mock_session
        assert ds.goalie_advanced_dataset([]).empty

    @patch("pandas.read_sql")
    @patch.object(ds, "SessionLocal")
    @patch.object(ds, "init_db")
    def test_goalie_advanced_dedupes_contract_id(self, mock_init, mock_slocal, mock_read_sql):
        mock_session = MagicMock()
        mock_slocal.return_value = mock_session
        mock_read_sql.return_value = pd.DataFrame(
            {"contract_id": [2, 2], "cap_hit": [1e6, 1e6], "icetime": [400000.0, 400000.0]}
        )
        p = MagicMock()
        p.id = 1
        out = ds.goalie_advanced_dataset([p])
        assert len(out) == 1

    def test_player_salary_year_matches_start_expr(self):
        expr = ds._player_salary_year_matches_start()
        assert expr is not None


class TestPredictor:
    def test_load_model_missing_file(self):
        with pytest.raises(FileNotFoundError):
            predictor.load_model("nonexistent_model_xyz")

    def test_prepare_skater_branches(self):
        df = pd.DataFrame([_skater_df_row()])
        df_no_rfa = df.drop(columns=["rfa"])
        out = predictor.prepare_skater_features_for_prediction(df_no_rfa)
        assert "rfa_flag" in out.columns

        df_no_age = df.drop(columns=["age"])
        out2 = predictor.prepare_skater_features_for_prediction(df_no_age)
        assert (out2["age"] == 0).all()

        df_no_dur = df.drop(columns=["duration"])
        out3 = predictor.prepare_skater_features_for_prediction(df_no_dur)
        assert (out3["duration"] == 0).all()

    def test_prepare_goalie_branches(self):
        row = _goalie_df_row()
        df = pd.DataFrame([row])
        df_no_rfa = df.drop(columns=["rfa"])
        out = predictor.prepare_goalie_features_for_prediction(df_no_rfa)
        assert "rfa_flag" in out.columns

        df_no_age = df.drop(columns=["age"])
        out2 = predictor.prepare_goalie_features_for_prediction(df_no_age)
        assert (out2["age"] == 0).all()

        df_no_dur = df.drop(columns=["duration"])
        out3 = predictor.prepare_goalie_features_for_prediction(df_no_dur)
        assert (out3["duration"] == 0).all()

    def test_predict_and_predict_single_player(self, tmp_path):
        df = pd.DataFrame([_skater_df_row()])
        feat = predictor.prepare_skater_features_for_prediction(df)
        names = list(feat.columns)
        model = LinearRegression()
        model.fit(feat.values, np.array([15.0]))
        joblib.dump(model, tmp_path / "forward_model.pkl")
        joblib.dump(names, tmp_path / "forward_model_feature_names.pkl")

        with patch.object(predictor, "ARTIFACTS_DIR", str(tmp_path)):
            out = predictor.predict(df, "forward_model")
            assert "predicted_cap_hit" in out.columns
            single = predictor.predict_single_player(_skater_df_row(), "forward_model")
            assert "predicted_cap_hit" in single

    def test_predict_goalie_model_branch(self, tmp_path):
        df = pd.DataFrame([_goalie_df_row()])
        feat = predictor.prepare_goalie_features_for_prediction(df)
        names = list(feat.columns)
        model = LinearRegression()
        model.fit(feat.values, np.array([16.0]))
        joblib.dump(model, tmp_path / "goalie_model.pkl")
        joblib.dump(names, tmp_path / "goalie_model_feature_names.pkl")

        with patch.object(predictor, "ARTIFACTS_DIR", str(tmp_path)):
            out = predictor.predict(df, "goalie_model")
            assert "predicted_cap_hit" in out.columns

    def test_predict_missing_features_raises(self, tmp_path):
        df = pd.DataFrame([_skater_df_row()])
        feat = predictor.prepare_skater_features_for_prediction(df)
        model = LinearRegression()
        model.fit(feat.values, np.array([15.0]))
        joblib.dump(model, tmp_path / "forward_model.pkl")
        # Artifact lists a column that prepare_skater_features_for_prediction never produces
        joblib.dump(list(feat.columns) + ["__required_but_missing__"], tmp_path / "forward_model_feature_names.pkl")

        with patch.object(predictor, "ARTIFACTS_DIR", str(tmp_path)):
            with pytest.raises(ValueError, match="Missing required features"):
                predictor.predict(df, "forward_model")

    def test_load_model_missing_feature_names_file(self, tmp_path):
        df = pd.DataFrame([_skater_df_row()])
        feat = predictor.prepare_skater_features_for_prediction(df)
        model = LinearRegression()
        model.fit(feat.values, np.array([15.0]))
        joblib.dump(model, tmp_path / "forward_model.pkl")
        with patch.object(predictor, "ARTIFACTS_DIR", str(tmp_path)):
            with pytest.raises(FileNotFoundError, match="Feature names"):
                predictor.load_model("forward_model")
