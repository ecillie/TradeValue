import sys
import os

from sqlalchemy.orm import Session
from decimal import Decimal
from app.database import SessionLocal, init_db
from app.models import Player, Contract, PlayerSalary

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) 

# Test using cd /Users/evancillie/Documents/GitHub/TradeValue/backend
# DB_HOST=localhost python3 -m app.ScriptingFiles.save_individual_contract_years


SALARY_CAP ={'2005' : Decimal('39000000'), '2006' : Decimal('44000000'), '2007' : Decimal('50300000'), '2008' : Decimal('56700000'), 
'2009' : Decimal('56800000'), '2010' : Decimal('59400000'), '2011' : Decimal('64300000'), '2012' : Decimal('70200000'), 
'2013' : Decimal('64300000'), '2014' : Decimal('69000000'), '2015' : Decimal('71400000'), '2016' : Decimal('73000000'),
'2017' : Decimal('75000000'), '2018' : Decimal('79500000'), '2019' : Decimal('81500000'), '2020' : Decimal('81500000'), 
'2021' : Decimal('81500000'), '2022' : Decimal('82500000'), '2023' : Decimal('82500000'), '2024' : Decimal('88000000'), '2025' : Decimal('95500000')}


def save_individual_contract_years():
    init_db()
    db: Session = SessionLocal()
    try:
        # Get all contracts at once
        all_contracts = db.query(Contract).all()
        
        salaries_created = 0
        salaries_skipped = 0
        
        for contract in all_contracts:
            # For each contract, create salary records for each year
            for year in range(contract.start_year, contract.end_year + 1):
                year_str = str(year)
                
                # Check if this salary record already exists
                existing = db.query(PlayerSalary).filter(
                    PlayerSalary.contract_id == contract.id,
                    PlayerSalary.year == year
                ).first()
                
                if existing:
                    salaries_skipped += 1
                    continue
                
                # Get the salary cap for this year
                if year_str not in SALARY_CAP:
                    continue  # Skip years without salary cap data
                
                salary_cap = SALARY_CAP[year_str]                
                
                cap_hit = contract.total_value / contract.duration if contract.total_value and contract.duration > 0 else Decimal('0')
                cap_pct = cap_hit / salary_cap if salary_cap > 0 else Decimal('0')

                player_salary = PlayerSalary(
                    player_id=contract.player_id,
                    contract_id=contract.id,
                    year=year,
                    cap_hit=cap_hit,
                    cap_pct=cap_pct,
                )
                db.add(player_salary)
                salaries_created += 1
            
            
            db.commit()
        
        print(f"Created {salaries_created} salary records, skipped {salaries_skipped} duplicates")
        
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    save_individual_contract_years()