import pytest
from unittest.mock import patch, MagicMock
import os
from app.ml.inference.predictor import load_model


class TestModelLoading:
    """Test model loading functions"""
    
    @patch('joblib.load')
    @patch('os.path.exists')
    def test_load_model_success(self, mock_exists, mock_load):
        """Test successful model loading"""
        mock_exists.return_value = True
        mock_model = MagicMock()
        mock_feature_names = ['feature1', 'feature2', 'feature3']
        mock_load.side_effect = [mock_model, mock_feature_names]
        
        model, feature_names = load_model('forward_model')
        
        assert model == mock_model
        assert feature_names == mock_feature_names
        assert mock_load.call_count == 2
    
    @patch('os.path.exists')
    def test_load_model_file_not_found(self, mock_exists):
        """Test FileNotFoundError when model missing"""
        mock_exists.side_effect = lambda path: 'feature_names' in path
        
        with pytest.raises(FileNotFoundError):
            load_model('forward_model')
    
    @patch('joblib.load')
    @patch('os.path.exists')
    def test_load_model_feature_names_missing(self, mock_exists, mock_load):
        """Test error when feature names file missing"""
        mock_exists.side_effect = lambda path: 'forward_model.pkl' in path and 'feature_names' not in path
        
        with pytest.raises(FileNotFoundError):
            load_model('forward_model')
    
    @patch('joblib.load')
    @patch('os.path.exists')
    def test_load_model_different_model_names(self, mock_exists, mock_load):
        """Test loading different model types"""
        mock_exists.return_value = True
        mock_model = MagicMock()
        mock_feature_names = ['feature1', 'feature2']
        # Each load_model call makes 2 joblib.load calls (model and features)
        # So we need 6 returns total (2 per model * 3 models)
        mock_load.side_effect = [
            mock_model, mock_feature_names,  # forward_model
            mock_model, mock_feature_names,  # defenseman_model
            mock_model, mock_feature_names   # goalie_model
        ]
        
        # Test forward model
        model1, features1 = load_model('forward_model')
        assert model1 == mock_model
        
        # Test defenseman model
        model2, features2 = load_model('defenseman_model')
        assert model2 == mock_model
        
        # Test goalie model
        model3, features3 = load_model('goalie_model')
        assert model3 == mock_model


class TestPredictionPipeline:
    """Test end-to-end prediction pipeline"""
    
    @patch('app.ml.inference.predictor.load_model')
    def test_predict_feature_mismatch_error(self, mock_load):
        """Test ValueError when features don't match"""
        from app.ml.inference.predictor import predict
        import pandas as pd
        
        mock_model = MagicMock()
        # Load model will be called, but prepare_skater_features_for_prediction needs icetime
        mock_load.return_value = (mock_model, ['feature1', 'feature2', 'feature3'])
        
        # DataFrame with minimal required fields but missing features after preparation
        df = pd.DataFrame({
            'icetime': [20000.0],
            'games_played': [82],
            'i_f_points': [100],
            'i_f_goals': [45],
            'i_f_primary_assists': [40],
            'i_f_secondary_assists': [15],
            'i_f_x_goals': [40.0],
            'i_f_shots_on_goal': [250],
            'i_f_unblocked_shot_attempts': [280],
            'on_ice_x_goals_percentage': [0.55],
            'shots_blocked_by_player': [50],
            'i_f_takeaways': [30],
            'i_f_giveaways': [20],
            'i_f_penalties': [10],
            'penalties_drawn': [15],
            'i_f_o_zone_shift_starts': [400],
            'i_f_d_zone_shift_starts': [200],
            'i_f_neutral_zone_shift_starts': [300]
        })
        
        # The error should occur when trying to select features that don't exist after feature prep
        # prepare_skater_features_for_prediction will create features like goals_per_60, etc.
        # but the expected_features from load_model don't match, so we should get a ValueError
        # about missing features
        with pytest.raises(ValueError, match="Missing required features"):
            predict(df, model_name='forward_model')
        mock_load.assert_called_once()
    
    @patch('app.ml.inference.predictor.load_model')
    @patch('app.ml.inference.predictor.prepare_skater_features_for_prediction')
    def test_predict_log_transformation(self, mock_prepare, mock_load):
        """Test log1p transformation and expm1 inverse"""
        from app.ml.inference.predictor import predict
        import pandas as pd
        import numpy as np
        
        mock_model = MagicMock()
        # Model returns log_cap_hit
        mock_model.predict.return_value = np.array([np.log1p(5000000.0)])
        mock_load.return_value = (mock_model, ['feature1'])
        
        mock_prepare.return_value = pd.DataFrame({'feature1': [1.0]})
        
        df = pd.DataFrame({'dummy': [1]})
        result = predict(df, model_name='forward_model')
        
        # Check that predicted_cap_hit is transformed back
        assert 'predicted_cap_hit' in result.columns
        assert 'predicted_log_cap_hit' in result.columns
        # expm1(log1p(5000000)) should be approximately 5000000
        assert abs(result['predicted_cap_hit'].iloc[0] - 5000000.0) < 0.01

