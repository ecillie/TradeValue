import pytest
from decimal import Decimal
from app.routers.players import YearPrediction
from app.schemas import PredictionRequest, PredictionResponse
from pydantic import ValidationError


class TestDataValidation:
    """Test data validation in schemas and endpoints"""
    
    def test_contract_prediction_schema_validation(self):
        """Test YearPrediction schema"""
        # Valid prediction
        prediction = YearPrediction(
            year=2023,
            actual_cap_hit=5000000.0,
            expected_cap_hit=5500000.0
        )
        
        assert prediction.year == 2023
        assert prediction.actual_cap_hit == 5000000.0
        assert prediction.expected_cap_hit == 5500000.0
        
        # Invalid: missing fields
        with pytest.raises(ValidationError):
            YearPrediction(year=2023)
    
    def test_prediction_request_schema_validation(self):
        """Test PredictionRequest schema validation"""
        # Valid request with position
        request = PredictionRequest(position="C")
        assert request.position == "C"
        
        # Invalid: missing required position
        with pytest.raises(ValidationError):
            PredictionRequest()
        
        # Valid with optional fields
        request_full = PredictionRequest(
            position="C",
            icetime=20000.0,
            games_played=82,
            i_f_points=100
        )
        assert request_full.position == "C"
        assert request_full.icetime == 20000.0
        assert request_full.games_played == 82
    
    def test_prediction_response_schema_validation(self):
        """Test PredictionResponse schema"""
        response = PredictionResponse(predicted_cap_hit=5000000.0)
        assert response.predicted_cap_hit == 5000000.0
        assert isinstance(response.predicted_cap_hit, float)
        
        # Invalid: missing field
        with pytest.raises(ValidationError):
            PredictionResponse()
    
    def test_decimal_precision_handling(self, client, db_session):
        """Test Decimal type handling in responses"""
        from app.models import Player, Contract
        
        player = Player(
            firstname="Test",
            lastname="Player",
            team="EDM",
            position="C",
            age=25
        )
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        contract = Contract(
            player_id=player.id,
            team="EDM",
            start_year=2023,
            end_year=2025,
            duration=3,
            cap_hit=Decimal("1234567.89"),
            rfa=False,
            elc=False,
            cap_pct=Decimal("0.0149"),
            total_value=Decimal("3703703.67")
        )
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        
        response = client.get(f"/api/players/{player.id}/contracts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        # Decimal is serialized as Decimal in Pydantic, which FastAPI converts to string
        # to preserve precision in JSON. The schema uses Decimal type.
        cap_hit = data[0]["cap_hit"]
        # FastAPI/Pydantic serializes Decimal as string in JSON
        assert isinstance(cap_hit, str)
        # Verify it's a valid number string
        assert float(cap_hit) > 0
    
    def test_date_range_validation(self, db_session):
        """Test contract date ranges (start_year <= end_year)"""
        from app.models import Player, Contract
        
        player = Player(
            firstname="Test",
            lastname="Player",
            team="EDM",
            position="C",
            age=25
        )
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        # Valid: start_year < end_year
        contract1 = Contract(
            player_id=player.id,
            team="EDM",
            start_year=2023,
            end_year=2025,
            duration=3,
            cap_hit=Decimal("5000000"),
            rfa=False,
            elc=False,
            cap_pct=Decimal("0.06"),
            total_value=Decimal("15000000")
        )
        db_session.add(contract1)
        db_session.commit()
        assert contract1.id is not None
        
        # Valid: start_year == end_year (1 year contract)
        contract2 = Contract(
            player_id=player.id,
            team="EDM",
            start_year=2026,
            end_year=2026,
            duration=1,
            cap_hit=Decimal("3000000"),
            rfa=False,
            elc=False,
            cap_pct=Decimal("0.036"),
            total_value=Decimal("3000000")
        )
        db_session.add(contract2)
        db_session.commit()
        assert contract2.id is not None
        
        # Note: Database doesn't enforce start_year <= end_year,
        # but application logic should handle this

