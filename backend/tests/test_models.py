import pytest
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from app.models import Player, Contract, BasicPlayerStats, AdvancedSkaterStats, AdvancedGoalieStats, BasicGoalieStats


class TestDatabaseModels:
    """Test database model relationships and constraints"""
    
    def test_player_contract_relationship(self, db_session):
        """Test foreign key relationship"""
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
            cap_hit=Decimal("5000000"),
            rfa=False,
            elc=False,
            cap_pct=Decimal("0.06"),
            total_value=Decimal("15000000")
        )
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        
        assert contract.player_id == player.id
        assert contract.id is not None
    
    def test_cascade_delete_player(self, db_session):
        """Test cascading deletes"""
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
            cap_hit=Decimal("5000000"),
            rfa=False,
            elc=False,
            cap_pct=Decimal("0.06"),
            total_value=Decimal("15000000")
        )
        db_session.add(contract)
        db_session.commit()
        contract_id = contract.id
        
        # Delete player
        db_session.delete(player)
        db_session.commit()
        
        # Contract should be deleted
        deleted_contract = db_session.query(Contract).filter(Contract.id == contract_id).first()
        assert deleted_contract is None
    
    def test_contract_stats_relationship(self, db_session):
        """Test contract to stats relationship"""
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
            cap_hit=Decimal("5000000"),
            rfa=False,
            elc=False,
            cap_pct=Decimal("0.06"),
            total_value=Decimal("15000000")
        )
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        
        stats = BasicPlayerStats(
            player_id=player.id,
            contract_id=contract.id,
            season=2023,
            playoff=False,
            team="EDM",
            gp=82,
            goals=40,
            assists=60,
            points=100,
            plus_minus=20,
            pim=30,
            shots=250,
            shootpct=Decimal("16.0")
        )
        db_session.add(stats)
        db_session.commit()
        db_session.refresh(stats)
        
        assert stats.contract_id == contract.id
        assert stats.player_id == player.id
    
    def test_advanced_stats_constraints(self, db_session):
        """Test NOT NULL constraints and validations"""
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
            cap_hit=Decimal("5000000"),
            rfa=False,
            elc=False,
            cap_pct=Decimal("0.06"),
            total_value=Decimal("15000000")
        )
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        
        # Try to create stats without required fields
        stats = AdvancedSkaterStats(
            player_id=player.id,
            contract_id=contract.id,
            # Missing required fields: season, playoff, team, situation
        )
        
        db_session.add(stats)
        with pytest.raises((IntegrityError, Exception)):
            db_session.commit()
    
    def test_player_unique_constraints(self, db_session):
        """Test that players can have the same name (no unique constraint)"""
        player1 = Player(
            firstname="John",
            lastname="Smith",
            team="EDM",
            position="C",
            age=25
        )
        player2 = Player(
            firstname="John",
            lastname="Smith",
            team="TOR",
            position="D",
            age=27
        )
        
        db_session.add_all([player1, player2])
        db_session.commit()
        
        # Both should be saved (no unique constraint on name)
        assert player1.id is not None
        assert player2.id is not None
        assert player1.id != player2.id

