"""Tests for app/routers/players.py (routes, contract predictions, and helpers)."""
from decimal import Decimal
from unittest.mock import patch

import pandas as pd
from sqlalchemy import text

from app.models import BasicPlayerStats, Contract, Player, PlayerSalary
from app.routers import players as players_router

from tests.factories import (
    advanced_goalie_row,
    advanced_skater_row,
    basic_goalie_row,
)


def _player_salary_row(
    player_id: int,
    contract_id: int,
    year: int,
    cap: str = "12500000",
    slide: bool = False,
) -> PlayerSalary:
    return PlayerSalary(
        player_id=player_id,
        contract_id=contract_id,
        year=year,
        cap_hit=Decimal(cap),
        cap_pct=Decimal("0.1000"),
        is_slide=slide,
    )


class TestGetPlayers:
    """Test GET /api/players endpoint"""

    def test_get_players_empty(self, client):
        """Test getting players when database is empty"""
        response = client.get("/api/players")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_players_single(self, client, db_session, sample_player_data):
        """Test getting a single player"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)

        response = client.get("/api/players")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["firstname"] == "Connor"
        assert data[0]["lastname"] == "McDavid"
        assert data[0]["team"] == "EDM"
        assert data[0]["position"] == "C"
        assert data[0]["age"] == 27

    def test_get_players_multiple(self, client, db_session, sample_players_data):
        """Test getting multiple players"""
        players = [Player(**data) for data in sample_players_data]
        db_session.add_all(players)
        db_session.commit()

        response = client.get("/api/players")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4


class TestGetPlayerById:
    """Test GET /api/players/{player_id} endpoint"""

    def test_get_player_by_id_success(self, client, db_session, sample_player_data):
        """Test getting a specific player by ID"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)

        response = client.get(f"/api/players/{player.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == player.id
        assert data["firstname"] == "Connor"
        assert data["lastname"] == "McDavid"

    def test_get_player_by_id_not_found(self, client):
        """Test getting a player that doesn't exist"""
        response = client.get("/api/players/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_player_by_id_invalid(self, client):
        """Test getting a player with invalid ID type"""
        response = client.get("/api/players/abc")
        assert response.status_code == 422  # Validation error


class TestSearchPlayers:
    """Test GET /api/players/search endpoint"""

    def test_search_by_name_firstname(self, client, db_session, sample_players_data):
        """Test searching players by first name"""
        players = [Player(**data) for data in sample_players_data]
        db_session.add_all(players)
        db_session.commit()

        response = client.get("/api/players/search?name=Connor")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["firstname"] == "Connor"

    def test_search_by_name_lastname(self, client, db_session, sample_players_data):
        """Test searching players by last name"""
        players = [Player(**data) for data in sample_players_data]
        db_session.add_all(players)
        db_session.commit()

        response = client.get("/api/players/search?name=Makar")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["lastname"] == "Makar"

    def test_search_by_name_case_insensitive(self, client, db_session, sample_player_data):
        """Test searching is case insensitive"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()

        response = client.get("/api/players/search?name=connor")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_search_by_name_partial_match(self, client, db_session, sample_players_data):
        """Test partial name matching"""
        players = [Player(**data) for data in sample_players_data]
        db_session.add_all(players)
        db_session.commit()

        response = client.get("/api/players/search?name=Mc")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "Mc" in data[0]["lastname"]

    def test_search_by_team(self, client, db_session, sample_players_data):
        """Test searching players by team"""
        players = [Player(**data) for data in sample_players_data]
        db_session.add_all(players)
        db_session.commit()

        response = client.get("/api/players/search?team=EDM")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(player["team"] == "EDM" for player in data)

    def test_search_by_position(self, client, db_session, sample_players_data):
        """Test searching players by position"""
        players = [Player(**data) for data in sample_players_data]
        db_session.add_all(players)
        db_session.commit()

        response = client.get("/api/players/search?position=D")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["position"] == "D"

    def test_search_multiple_filters(self, client, db_session, sample_players_data):
        """Test searching with multiple filters"""
        players = [Player(**data) for data in sample_players_data]
        db_session.add_all(players)
        db_session.commit()

        response = client.get("/api/players/search?team=EDM&position=C")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(player["team"] == "EDM" and player["position"] == "C" for player in data)

    def test_search_no_results(self, client, db_session, sample_players_data):
        """Test search with no matching results"""
        players = [Player(**data) for data in sample_players_data]
        db_session.add_all(players)
        db_session.commit()

        response = client.get("/api/players/search?name=NonExistent")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_search_team_and_name_intersection_empty(self, client, db_session, sample_players_data):
        players = [Player(**data) for data in sample_players_data]
        db_session.add_all(players)
        db_session.commit()

        r = client.get("/api/players/search?team=TOR&name=McDavid")
        assert r.status_code == 200
        assert r.json() == []

    def test_search_position_substring_matches_d(self, client, db_session, sample_players_data):
        """Position filter uses ilike %value% — 'D' matches stored 'D'."""
        players = [Player(**data) for data in sample_players_data]
        db_session.add_all(players)
        db_session.commit()

        r = client.get("/api/players/search?position=D")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["lastname"] == "Makar"


class TestGetPlayerContracts:
    """Test GET /api/players/{player_id}/contracts endpoint"""

    def test_get_player_contracts_success(self, client, db_session, sample_player_data, sample_contract_data):
        """Test getting contracts for a specific player"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)

        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()

        response = client.get(f"/api/players/{player.id}/contracts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["player_id"] == player.id
        assert float(data[0]["cap_hit"]) == 12500000.0

    def test_get_player_contracts_no_contracts(self, client, db_session, sample_player_data):
        """Test getting contracts for player with no contracts"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)

        response = client.get(f"/api/players/{player.id}/contracts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_get_player_contracts_player_not_found(self, client):
        """Test getting contracts for non-existent player"""
        response = client.get("/api/players/999/contracts")
        assert response.status_code == 404


class TestGetPlayerStats:
    """Test GET /api/players/{player_id}/stats endpoint"""

    def test_get_player_stats_success(self, client, db_session, sample_player_data, sample_contract_data, sample_stats_data):
        """Test getting stats for a specific player"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)

        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)

        stats_data = sample_stats_data.copy()
        stats_data["player_id"] = player.id
        stats_data["contract_id"] = contract.id
        stats = BasicPlayerStats(**stats_data)
        db_session.add(stats)
        db_session.commit()

        response = client.get(f"/api/players/{player.id}/stats")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["player_id"] == player.id
        assert data[0]["points"] == 153

    def test_get_player_stats_filter_by_season(self, client, db_session, sample_player_data, sample_contract_data, sample_stats_data):
        """Test filtering stats by season"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)

        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)

        stats_data = sample_stats_data.copy()
        stats_data["player_id"] = player.id
        stats_data["contract_id"] = contract.id

        stats1 = BasicPlayerStats(**stats_data)
        stats2_data = stats_data.copy()
        stats2_data["season"] = 2022
        stats2 = BasicPlayerStats(**stats2_data)
        db_session.add_all([stats1, stats2])
        db_session.commit()

        response = client.get(f"/api/players/{player.id}/stats?season=2023")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["season"] == 2023

    def test_get_player_stats_filter_by_playoff(self, client, db_session, sample_player_data, sample_contract_data, sample_stats_data):
        """Test filtering stats by playoff"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)

        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)

        stats_data = sample_stats_data.copy()
        stats_data["player_id"] = player.id
        stats_data["contract_id"] = contract.id

        stats1 = BasicPlayerStats(**stats_data)
        stats2_data = stats_data.copy()
        stats2_data["playoff"] = True
        stats2 = BasicPlayerStats(**stats2_data)
        db_session.add_all([stats1, stats2])
        db_session.commit()

        response = client.get(f"/api/players/{player.id}/stats?playoff=false")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["playoff"] is False

    def test_get_player_stats_filter_by_team(
        self, client, db_session, sample_player_data, sample_contract_data, sample_stats_data
    ):
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        contract = Contract(**{**sample_contract_data, "player_id": player.id})
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)

        s_edm = BasicPlayerStats(
            **{
                **sample_stats_data,
                "player_id": player.id,
                "contract_id": contract.id,
                "team": "EDM",
                "season": 2023,
            }
        )
        s_tor = BasicPlayerStats(
            **{
                **sample_stats_data,
                "player_id": player.id,
                "contract_id": contract.id,
                "team": "TOR",
                "season": 2023,
                "points": 50,
            }
        )
        db_session.add_all([s_edm, s_tor])
        db_session.commit()

        r = client.get(f"/api/players/{player.id}/stats?team=TOR")
        assert r.status_code == 200
        rows = r.json()
        assert len(rows) == 1
        assert rows[0]["team"] == "TOR"
        assert rows[0]["points"] == 50

    def test_get_player_stats_filter_team_case_insensitive(
        self, client, db_session, sample_player_data, sample_contract_data, sample_stats_data
    ):
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        contract = Contract(**{**sample_contract_data, "player_id": player.id})
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        stats = BasicPlayerStats(
            **{**sample_stats_data, "player_id": player.id, "contract_id": contract.id}
        )
        db_session.add(stats)
        db_session.commit()

        r = client.get(f"/api/players/{player.id}/stats?team=edm")
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_get_player_stats_combined_season_and_playoff(
        self, client, db_session, sample_player_data, sample_contract_data, sample_stats_data
    ):
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        contract = Contract(**{**sample_contract_data, "player_id": player.id})
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)

        reg = BasicPlayerStats(
            **{
                **sample_stats_data,
                "player_id": player.id,
                "contract_id": contract.id,
                "season": 2022,
                "playoff": False,
            }
        )
        po = BasicPlayerStats(
            **{
                **sample_stats_data,
                "player_id": player.id,
                "contract_id": contract.id,
                "season": 2022,
                "playoff": True,
                "points": 20,
            }
        )
        db_session.add_all([reg, po])
        db_session.commit()

        r = client.get(f"/api/players/{player.id}/stats?season=2022&playoff=true")
        assert r.status_code == 200
        rows = r.json()
        assert len(rows) == 1
        assert rows[0]["playoff"] is True
        assert rows[0]["points"] == 20

    def test_get_player_stats_player_not_found(self, client):
        """Test getting stats for non-existent player"""
        response = client.get("/api/players/999/stats")
        assert response.status_code == 404


class TestGetAllContracts:
    """Test GET /api/players/contracts endpoint"""

    def test_get_all_contracts_empty(self, client):
        """Test getting all contracts when database is empty"""
        response = client.get("/api/players/contracts")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_contracts_success(self, client, db_session, sample_player_data, sample_contract_data):
        """Test getting all contracts"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)

        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()

        response = client.get("/api/players/contracts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["player_id"] == player.id


class TestGetContractById:
    """Test GET /api/players/contracts/{contract_id} endpoint"""

    def test_get_contract_by_id_success(self, client, db_session, sample_player_data, sample_contract_data):
        """Test getting a specific contract by ID"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)

        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)

        response = client.get(f"/api/players/contracts/{contract.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == contract.id
        assert data["player_id"] == player.id
        assert float(data["cap_hit"]) == 12500000.0

    def test_get_contract_by_id_not_found(self, client):
        """Test getting a contract that doesn't exist"""
        response = client.get("/api/players/contracts/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestGetPlayerContractPredictions:
    """GET /api/players/{player_id}/contract-predictions"""

    def test_player_not_found(self, client):
        response = client.get("/api/players/99999/contract-predictions")
        assert response.status_code == 404

    def test_no_contracts_returns_empty(self, client, db_session, sample_player_data):
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        response = client.get(f"/api/players/{player.id}/contract-predictions")
        assert response.status_code == 200
        assert response.json() == []

    def test_contracts_but_no_salary_rows_returns_empty(
        self, client, db_session, sample_player_data, sample_contract_data
    ):
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()
        response = client.get(f"/api/players/{player.id}/contract-predictions")
        assert response.status_code == 200
        assert response.json() == []

    @patch("app.routers.players.predict")
    def test_predicted_cap_hit_per_salary_year(
        self,
        mock_predict,
        client,
        db_session,
        sample_player_data,
        sample_contract_data,
        sample_player_salary_data,
    ):
        """With advanced stats for the salary year, expected_cap_hit comes from mocked predict."""
        mock_predict.return_value = pd.DataFrame({"predicted_cap_hit": [7_000_000.0]})
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)

        salary_data = sample_player_salary_data.copy()
        salary_data["player_id"] = player.id
        salary_data["contract_id"] = contract.id
        db_session.add(PlayerSalary(**salary_data))
        db_session.add(advanced_skater_row(player.id, contract.id, season=contract.start_year))
        db_session.commit()

        response = client.get(f"/api/players/{player.id}/contract-predictions")
        assert response.status_code == 200
        rows = response.json()
        assert len(rows) == 1
        assert rows[0]["year"] == 2023
        assert float(rows[0]["actual_cap_hit"]) == 12_500_000.0
        assert rows[0]["expected_cap_hit"] == 7_000_000.0
        assert rows[0]["contract_id"] == contract.id
        assert rows[0]["is_slide"] is False
        assert mock_predict.call_count >= 1

    @patch("app.routers.players.predict")
    def test_slide_year_expected_zero(
        self,
        mock_predict,
        client,
        db_session,
        sample_player_data,
        sample_contract_data,
        sample_player_salary_data,
    ):
        mock_predict.return_value = pd.DataFrame({"predicted_cap_hit": [7_000_000.0]})
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)

        salary_data = sample_player_salary_data.copy()
        salary_data["player_id"] = player.id
        salary_data["contract_id"] = contract.id
        salary_data["is_slide"] = True
        db_session.add(PlayerSalary(**salary_data))
        db_session.add(advanced_skater_row(player.id, contract.id, season=contract.start_year))
        db_session.commit()

        response = client.get(f"/api/players/{player.id}/contract-predictions")
        assert response.status_code == 200
        rows = response.json()
        assert len(rows) == 1
        assert rows[0]["expected_cap_hit"] == 0.0


class TestContractPredictionsFallback:
    """Fallback and missing-data behaviour for contract-predictions."""

    @patch("app.routers.players.predict")
    def test_no_advanced_stats_anywhere_expected_zero(
        self, mock_predict, client, db_session, sample_player_data, sample_contract_data
    ):
        mock_predict.return_value = pd.DataFrame({"predicted_cap_hit": [9_000_000.0]})
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        contract = Contract(**{**sample_contract_data, "player_id": player.id})
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        db_session.add(_player_salary_row(player.id, contract.id, 2023))
        db_session.commit()

        r = client.get(f"/api/players/{player.id}/contract-predictions")
        assert r.status_code == 200
        row = r.json()[0]
        assert row["expected_cap_hit"] == 0.0
        mock_predict.assert_not_called()

    @patch("app.routers.players.predict")
    def test_salary_year_without_advanced_stats_uses_signing_fallback(
        self, mock_predict, client, db_session, sample_player_data, sample_contract_data
    ):
        """Salary row for 2024 but only advanced row for start_year 2023 — one predict (fallback)."""
        mock_predict.return_value = pd.DataFrame({"predicted_cap_hit": [4_000_000.0]})
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        contract = Contract(**{**sample_contract_data, "player_id": player.id})
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        db_session.add(advanced_skater_row(player.id, contract.id, season=contract.start_year))
        db_session.add(_player_salary_row(player.id, contract.id, year=2024, cap="8000000"))
        db_session.commit()

        r = client.get(f"/api/players/{player.id}/contract-predictions")
        assert r.status_code == 200
        row = r.json()[0]
        assert row["year"] == 2024
        assert row["expected_cap_hit"] == 4_000_000.0
        assert mock_predict.call_count == 1

    @patch("app.routers.players.predict")
    def test_per_year_predict_failure_falls_back(
        self, mock_predict, client, db_session, sample_player_data, sample_contract_data
    ):
        mock_predict.side_effect = [
            pd.DataFrame({"predicted_cap_hit": [5_000_000.0]}),
            RuntimeError("filtered empty"),
        ]
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        contract = Contract(**{**sample_contract_data, "player_id": player.id})
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        db_session.add(advanced_skater_row(player.id, contract.id, season=2023))
        db_session.add(advanced_skater_row(player.id, contract.id, season=2024))
        db_session.add(_player_salary_row(player.id, contract.id, year=2024))
        db_session.commit()

        r = client.get(f"/api/players/{player.id}/contract-predictions")
        assert r.status_code == 200
        assert r.json()[0]["expected_cap_hit"] == 5_000_000.0
        assert mock_predict.call_count == 2


class TestContractPredictionsMultiYear:
    @patch("app.routers.players.predict")
    def test_two_years_ordered_by_year_then_contract_id(
        self, mock_predict, client, db_session, sample_player_data, sample_contract_data
    ):
        mock_predict.return_value = pd.DataFrame({"predicted_cap_hit": [6_000_000.0]})
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        contract = Contract(**{**sample_contract_data, "player_id": player.id})
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        for season in (2023, 2024):
            db_session.add(advanced_skater_row(player.id, contract.id, season=season))
        db_session.add(_player_salary_row(player.id, contract.id, year=2024))
        db_session.add(_player_salary_row(player.id, contract.id, year=2023, cap="11000000"))
        db_session.commit()

        r = client.get(f"/api/players/{player.id}/contract-predictions")
        assert r.status_code == 200
        rows = r.json()
        assert [x["year"] for x in rows] == [2023, 2024]
        assert float(rows[0]["actual_cap_hit"]) == 11_000_000.0
        assert float(rows[1]["actual_cap_hit"]) == 12_500_000.0


class TestContractPredictionsDefensemanGoalie:
    @patch("app.routers.players.predict")
    def test_defenseman_selects_defenseman_model(
        self, mock_predict, client, db_session, sample_defenseman_player_data, sample_contract_data
    ):
        mock_predict.return_value = pd.DataFrame({"predicted_cap_hit": [8_000_000.0]})
        player = Player(**sample_defenseman_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        contract = Contract(**{**sample_contract_data, "player_id": player.id})
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        db_session.add(advanced_skater_row(player.id, contract.id, season=contract.start_year))
        db_session.add(_player_salary_row(player.id, contract.id, year=2023))
        db_session.commit()

        r = client.get(f"/api/players/{player.id}/contract-predictions")
        assert r.status_code == 200
        assert mock_predict.call_count >= 1
        for call in mock_predict.call_args_list:
            assert call.kwargs["model_name"] == "defenseman_model"

    @patch("app.routers.players.predict")
    def test_goalie_selects_goalie_model(
        self, mock_predict, client, db_session, sample_goalie_player_data, sample_contract_data
    ):
        mock_predict.return_value = pd.DataFrame({"predicted_cap_hit": [6_500_000.0]})
        player = Player(**sample_goalie_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        contract = Contract(**{**sample_contract_data, "player_id": player.id})
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        db_session.add(advanced_goalie_row(player.id, contract.id, season=contract.start_year))
        db_session.add(basic_goalie_row(player.id, contract.id, season=contract.start_year))
        db_session.add(_player_salary_row(player.id, contract.id, year=2023))
        db_session.commit()

        r = client.get(f"/api/players/{player.id}/contract-predictions")
        assert r.status_code == 200
        assert r.json()[0]["expected_cap_hit"] == 6_500_000.0
        for call in mock_predict.call_args_list:
            assert call.kwargs["model_name"] == "goalie_model"


class TestStatsDictForContractSeason:
    """Unit tests for _stats_dict_for_contract_season."""

    def test_skater_returns_none_when_no_advanced_row(
        self, db_session, sample_player_data, sample_contract_data
    ):
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        contract = Contract(**{**sample_contract_data, "player_id": player.id})
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)

        out = players_router._stats_dict_for_contract_season(
            db_session, contract, player, "forward_model", season=2023
        )
        assert out is None

    def test_skater_returns_dict_with_expected_keys(
        self, db_session, sample_player_data, sample_contract_data
    ):
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        contract = Contract(**{**sample_contract_data, "player_id": player.id})
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        db_session.add(advanced_skater_row(player.id, contract.id, season=2023))
        db_session.commit()

        out = players_router._stats_dict_for_contract_season(
            db_session, contract, player, "forward_model", season=2023
        )
        assert out is not None
        assert "icetime" in out
        assert "i_f_points" in out
        assert out["rfa"] is False
        assert out["duration"] == contract.duration

    def test_goalie_includes_basic_goalie_when_present(
        self, db_session, sample_goalie_player_data, sample_contract_data
    ):
        player = Player(**sample_goalie_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        contract = Contract(**{**sample_contract_data, "player_id": player.id})
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        db_session.add(advanced_goalie_row(player.id, contract.id, season=2023))
        db_session.add(basic_goalie_row(player.id, contract.id, season=2023))
        db_session.commit()

        out = players_router._stats_dict_for_contract_season(
            db_session, contract, player, "goalie_model", season=2023
        )
        assert out is not None
        assert out["gp"] == 55
        assert "x_goals" in out

    def test_goalie_returns_none_without_advanced_row(
        self, db_session, sample_goalie_player_data, sample_contract_data
    ):
        player = Player(**sample_goalie_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        contract = Contract(**{**sample_contract_data, "player_id": player.id})
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        assert (
            players_router._stats_dict_for_contract_season(
                db_session, contract, player, "goalie_model", season=2023
            )
            is None
        )

    def test_goalie_without_basic_stats_sets_zeros(
        self, db_session, sample_goalie_player_data, sample_contract_data
    ):
        player = Player(**sample_goalie_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        contract = Contract(**{**sample_contract_data, "player_id": player.id})
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        db_session.add(advanced_goalie_row(player.id, contract.id, season=2023))
        db_session.commit()

        out = players_router._stats_dict_for_contract_season(
            db_session, contract, player, "goalie_model", season=2023
        )
        assert out is not None
        assert out["gp"] == 0
        assert out["wins"] == 0


class TestContractPredictionsEdgeCases:
    """Branches in get_player_contract_predictions (invalid year, fallback failure)."""

    @patch("app.routers.players._predict_cap_hit_from_stats_dict")
    def test_fallback_predict_failure_skips_contract(
        self, mock_pred, client, db_session, sample_player_data, sample_contract_data, sample_player_salary_data
    ):
        mock_pred.side_effect = [RuntimeError("fallback fail"), 4_000_000.0]
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        contract = Contract(**{**sample_contract_data, "player_id": player.id})
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        db_session.add(advanced_skater_row(player.id, contract.id, season=contract.start_year))
        db_session.add(advanced_skater_row(player.id, contract.id, season=2024))
        sal = sample_player_salary_data.copy()
        sal["player_id"] = player.id
        sal["contract_id"] = contract.id
        sal["year"] = 2024
        db_session.add(PlayerSalary(**sal))
        db_session.commit()

        r = client.get(f"/api/players/{player.id}/contract-predictions")
        assert r.status_code == 200
        row = r.json()[0]
        assert row["year"] == 2024
        assert row["expected_cap_hit"] == 4_000_000.0
        assert mock_pred.call_count == 2

    @patch("app.routers.players.predict")
    def test_invalid_salary_year_string_skipped_in_loops(
        self, mock_predict, client, db_session, sample_player_data, sample_contract_data, sample_player_salary_data
    ):
        mock_predict.return_value = pd.DataFrame({"predicted_cap_hit": [1.0]})
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        contract = Contract(**{**sample_contract_data, "player_id": player.id})
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        db_session.add(advanced_skater_row(player.id, contract.id, season=2023))
        sal = sample_player_salary_data.copy()
        sal["player_id"] = player.id
        sal["contract_id"] = contract.id
        db_session.add(PlayerSalary(**sal))
        db_session.commit()
        sid = db_session.query(PlayerSalary).first().id
        db_session.execute(text("UPDATE player_salaries SET year = 'not_a_year' WHERE id = :id"), {"id": sid})
        db_session.commit()

        r = client.get(f"/api/players/{player.id}/contract-predictions")
        assert r.status_code == 200
        assert r.json() == []

    @patch("app.routers.players.predict")
    def test_salary_with_unknown_contract_id_skipped(
        self, mock_predict, client, db_session, sample_player_data, sample_contract_data, sample_player_salary_data
    ):
        mock_predict.return_value = pd.DataFrame({"predicted_cap_hit": [3.0]})
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        contract = Contract(**{**sample_contract_data, "player_id": player.id})
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        db_session.add(advanced_skater_row(player.id, contract.id, season=2023))
        sal = sample_player_salary_data.copy()
        sal["player_id"] = player.id
        sal["contract_id"] = contract.id
        db_session.add(PlayerSalary(**sal))
        db_session.commit()
        sid = db_session.query(PlayerSalary).first().id
        db_session.execute(text("PRAGMA foreign_keys = OFF"))
        db_session.execute(
            text("UPDATE player_salaries SET contract_id = 999999 WHERE id = :id"), {"id": sid}
        )
        db_session.commit()

        r = client.get(f"/api/players/{player.id}/contract-predictions")
        assert r.status_code == 200
        assert r.json()[0]["expected_cap_hit"] == 0.0


class TestPredictCapHitFromStatsDict:
    """Unit tests for _predict_cap_hit_from_stats_dict."""

    @patch("app.routers.players.predict")
    def test_calls_predict_and_returns_float(self, mock_predict):
        mock_predict.return_value = pd.DataFrame({"predicted_cap_hit": [3_333_333.0]})
        stats = {"icetime": 500000.0, "i_f_points": 1}
        v = players_router._predict_cap_hit_from_stats_dict(stats, "forward_model")
        assert v == 3_333_333.0
        mock_predict.assert_called_once()
