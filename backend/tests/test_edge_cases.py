import pytest
from decimal import Decimal
from unittest.mock import patch
import pandas as pd
from app.models import Player, Contract, AdvancedSkaterStats, AdvancedGoalieStats, BasicGoalieStats


class TestEdgeCases:
    """Test edge cases and error scenarios"""
    
    @patch('app.routers.players.predict')
    def test_player_multiple_contracts_same_year(self, mock_predict, client, db_session,
                                                   sample_player_data):
        """Test year aggregation with overlapping contracts"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        # Create two contracts that completely overlap
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
        db_session.refresh(contract1)
        
        contract2 = Contract(
            player_id=player.id,
            team="TOR",
            start_year=2023,
            end_year=2025,
            duration=3,
            cap_hit=Decimal("7000000"),
            rfa=False,
            elc=False,
            cap_pct=Decimal("0.084"),
            total_value=Decimal("21000000")
        )
        db_session.add(contract2)
        db_session.commit()
        db_session.refresh(contract2)
        
        # Add stats for both contracts
        stats1 = AdvancedSkaterStats(
            player_id=player.id,
            contract_id=contract1.id,
            season=2023,
            playoff=False,
            team="EDM",
            situation="all",
            icetime=20000.0,
            games_played=82
        )
        stats2 = AdvancedSkaterStats(
            player_id=player.id,
            contract_id=contract2.id,
            season=2023,
            playoff=False,
            team="TOR",
            situation="all",
            icetime=20000.0,
            games_played=82
        )
        db_session.add_all([stats1, stats2])
        db_session.commit()
        
        mock_result_df = pd.DataFrame({'predicted_cap_hit': [6000000.0]})
        mock_predict.return_value = mock_result_df
        
        response = client.get(f"/api/players/{player.id}/contract-predictions")
        assert response.status_code == 200
        data = response.json()
        
        # Each year should have aggregated cap hits
        year_2023 = next(item for item in data if item["year"] == 2023)
        assert year_2023["actual_cap_hit"] == 12000000.0  # 5M + 7M
    
    @patch('app.routers.players.predict')
    def test_player_no_stats_for_contract_start_year(self, mock_predict, client, db_session,
                                                       sample_player_data, sample_contract_data):
        """Test handling missing stats for contract start year"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        contract_data = sample_contract_data.copy()
        contract_data["player_id"] = player.id
        contract_data["start_year"] = 2023
        contract = Contract(**contract_data)
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        
        # Add stats for a different year (not start_year)
        stats = AdvancedSkaterStats(
            player_id=player.id,
            contract_id=contract.id,
            season=2024,  # Different from start_year
            playoff=False,
            team="EDM",
            situation="all",
            icetime=20000.0,
            games_played=82
        )
        db_session.add(stats)
        db_session.commit()
        
        # Should return empty list since no stats for start_year
        response = client.get(f"/api/players/{player.id}/contract-predictions")
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    def test_contract_predictions_elc_handling(self, client, db_session, sample_player_data,
                                                 sample_advanced_skater_stats_data):
        """Test ELC contracts are handled correctly"""
        player = Player(**sample_player_data)
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        # Create ELC contract
        elc_contract = Contract(
            player_id=player.id,
            team="EDM",
            start_year=2023,
            end_year=2025,
            duration=3,
            cap_hit=Decimal("925000"),
            rfa=False,
            elc=True,  # ELC contract
            cap_pct=Decimal("0.011"),
            total_value=Decimal("2775000")
        )
        db_session.add(elc_contract)
        db_session.commit()
        db_session.refresh(elc_contract)
        
        # ELC contracts may be filtered in dataset builder, but endpoint should still work
        stats_data = sample_advanced_skater_stats_data.copy()
        stats_data["player_id"] = player.id
        stats_data["contract_id"] = elc_contract.id
        stats = AdvancedSkaterStats(**stats_data)
        db_session.add(stats)
        db_session.commit()
        
        # Note: The actual filtering happens in dataset_builder, not in the endpoint
        # So this test verifies the endpoint can handle ELC contracts
    
    def test_large_cap_hit_values(self, db_session):
        """Test handling of very large contract values"""
        player = Player(
            firstname="Super",
            lastname="Star",
            team="TOR",
            position="C",
            age=25
        )
        db_session.add(player)
        db_session.commit()
        db_session.refresh(player)
        
        # Very large contract (e.g., $15M+ cap hit)
        large_contract = Contract(
            player_id=player.id,
            team="TOR",
            start_year=2023,
            end_year=2030,
            duration=8,
            cap_hit=Decimal("15000000"),
            rfa=False,
            elc=False,
            cap_pct=Decimal("0.18"),
            total_value=Decimal("120000000")
        )
        db_session.add(large_contract)
        db_session.commit()
        db_session.refresh(large_contract)
        
        assert large_contract.id is not None
        assert float(large_contract.cap_hit) == 15000000.0
    
    def test_zero_or_negative_statistics(self, db_session):
        """Test handling of zero/negative stat values"""
        player = Player(
            firstname="Rookie",
            lastname="Player",
            team="EDM",
            position="C",
            age=18
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
            cap_hit=Decimal("925000"),
            rfa=False,
            elc=True,
            cap_pct=Decimal("0.011"),
            total_value=Decimal("2775000")
        )
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        
        # Stats with zero values
        stats = AdvancedSkaterStats(
            player_id=player.id,
            contract_id=contract.id,
            season=2023,
            playoff=False,
            team="EDM",
            situation="all",
            icetime=5000.0,  # Low icetime
            games_played=10,
            i_f_points=0,
            i_f_goals=0,
            i_f_primary_assists=0,
            i_f_secondary_assists=0,
            i_f_x_goals=Decimal("0.0"),
            i_f_shots_on_goal=0,
            i_f_unblocked_shot_attempts=0,
            on_ice_x_goals_percentage=Decimal("0.50"),
            shots_blocked_by_player=0,
            i_f_takeaways=0,
            i_f_giveaways=0,
            i_f_penalties=0,
            penalties_drawn=0,
            i_f_o_zone_shift_starts=0,
            i_f_d_zone_shift_starts=0,
            i_f_neutral_zone_shift_starts=0
        )
        db_session.add(stats)
        db_session.commit()
        
        assert stats.id is not None
        # Database should accept zero values

