from app.ScriptingFiles.save_basic_player_stats import main as save_basic_player_stats
from app.ScriptingFiles.save_contracts_to_db import main as save_contracts_to_db
from app.ScriptingFiles.save_goalie_advanced_stats import main as save_goalie_advanced_stats
from app.ScriptingFiles.save_players_to_db import main as save_players_to_db
from app.ScriptingFiles.save_skater_advanced_stats import main as save_skater_advanced_stats
from app.ScriptingFiles.save_individual_contract_years import main as save_individual_contract_years

def main():
    #save_players_to_db()
    save_basic_player_stats()
   # save_contracts_to_db()
   # save_goalie_advanced_stats()
   # save_skater_advanced_stats()
    save_individual_contract_years()

if __name__ == "__main__":
    main()