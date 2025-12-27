from fastapi import APIRouter, HTTPException
from app.schemas import PredictionRequest, PredictionResponse
from app.ml.inference.predictor import predict

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
def predict_contract(request: PredictionRequest):
    """
    Predict contract value based on player advanced statistics
    """
    try:
        # Determine which model to use based on position
        model_name = 'forward_model'
        if request.position.lower() == 'defenseman':
            model_name = 'defenseman_model'
        elif request.position.lower() == 'goalie':
            model_name = 'goalie_model'
        
        # Convert request to dict, excluding None values
        player_stats = request.model_dump(exclude_none=True)
        
        # Convert to DataFrame for the predictor (which expects DataFrame input)
        import pandas as pd
        df = pd.DataFrame([player_stats])
        
        # Make prediction (returns DataFrame with predictions)
        result_df = predict(df, model_name=model_name)
        
        # Extract the predicted cap hit
        predicted_cap_hit = float(result_df['predicted_cap_hit'].iloc[0])
        
        return PredictionResponse(predicted_cap_hit=predicted_cap_hit)
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Model not found: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")