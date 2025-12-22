from fastapi import APIRouter, HTTPException
from app.schemas import PredictionRequest, PredictionResponse
from app.ml.inference.predictor import predict_single_player

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
def predict_contract(request: PredictionRequest):
    """
    Predict contract value based on player statistics
    """
    try:
        # Determine which model to use based on position
        model_name = 'forward_model'  # default
        if request.position.lower() == 'defenseman':
            model_name = 'defenseman_model'
        elif request.position.lower() == 'goalie':
            # If you have a goalie model, use it
            model_name = 'goalie_model'
        
        # Convert request to dict for predictor
        player_stats = {
            'position': request.position,
            'gp': request.gp,
            'goals': request.goals,
            'assists': request.assists,
            'points': request.points,
            'plus_minus': request.plus_minus,
            'pim': request.pim,
            'shots': request.shots,
            'shootpct': request.shootpct,
        }
        
        # Make prediction
        predicted_pv = predict_single_player(player_stats, model_name=model_name)
        
        # The predictor returns pv (player value), but we want cap_hit
        # If your model predicts pv, you might need to convert it back to cap_hit
        # For now, assuming predicted_pv is what we want
        predicted_cap_hit = float(predicted_pv)
        
        return PredictionResponse(predicted_cap_hit=predicted_cap_hit)
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Model not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")