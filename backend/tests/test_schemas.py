"""Tests for app/schemas.py (Pydantic models)."""
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas import BasicPlayerStats, Contract, Player, PredictionRequest, PredictionResponse


class TestPlayerSchema:
    def test_valid_player(self):
        p = Player(
            id=1,
            firstname="A",
            lastname="B",
            team="EDM",
            position="C",
            age=25,
        )
        assert p.model_dump()["firstname"] == "A"

    def test_player_requires_fields(self):
        with pytest.raises(ValidationError):
            Player(id=1, firstname="A", lastname="B", team="EDM", position="C")  # type: ignore[call-arg]


class TestContractSchema:
    def test_contract_optional_total_value(self):
        c = Contract(
            id=1,
            player_id=2,
            team="EDM",
            start_year=2023,
            end_year=2030,
            duration=7,
            cap_hit=Decimal("9000000"),
            rfa=False,
            elc=False,
        )
        assert c.total_value is None

    def test_contract_with_total_value(self):
        c = Contract(
            id=1,
            player_id=2,
            team="EDM",
            start_year=2023,
            end_year=2030,
            duration=7,
            cap_hit=Decimal("9000000"),
            rfa=False,
            elc=False,
            total_value=Decimal("63000000"),
        )
        assert c.total_value == Decimal("63000000")


class TestBasicPlayerStatsSchema:
    def test_roundtrip(self):
        s = BasicPlayerStats(
            id=10,
            player_id=1,
            contract_id=2,
            season=2024,
            playoff=False,
            team="TOR",
            gp=82,
            goals=40,
            assists=50,
            points=90,
            plus_minus=12,
            pim=20,
            shots=200,
            shootpct=Decimal("15.5"),
        )
        d = s.model_dump()
        assert d["points"] == 90
        assert d["shootpct"] == Decimal("15.5")


class TestPredictionRequest:
    def test_position_only(self):
        r = PredictionRequest(position="forward")
        assert r.position == "forward"
        assert r.icetime is None
        assert r.i_f_points is None

    def test_skater_and_goalie_fields_coexist(self):
        r = PredictionRequest(
            position="goalie",
            icetime=1000.0,
            i_f_points=50,
            x_goals=100.0,
            gp=60,
        )
        assert r.x_goals == 100.0
        assert r.i_f_points == 50


class TestPredictionResponse:
    def test_response(self):
        r = PredictionResponse(predicted_cap_hit=5_500_000.0)
        assert r.predicted_cap_hit == 5_500_000.0
