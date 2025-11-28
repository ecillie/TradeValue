import requests
import json
import re

headers = {
    "User-Agent": "EvanTradeValueProject/1.0 (contact: your_email@example.com)",
    "Accept": "text/html,application/json",
}

url = "https://capwages.com/players/active"
resp = requests.get(url, headers=headers)
print(f"Status code: {resp.status_code}")

try:
    html = resp.text
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)    
    if match:
        json_str = match.group(1)
        data = json.loads(json_str)
        # Extract players data
        if 'props' in data and 'pageProps' in data['props']:
            page_props = data['props']['pageProps']
            players_array = page_props.get('playersArray', [])
            players = []
            for player_data in players_array:
                if isinstance(player_data, list) and len(player_data) >= 4:
                    players.append({
                        'name': player_data[0] if len(player_data) > 0 else 'N/A',
                        'team': player_data[2] if len(player_data) > 2 else 'N/A',
                        'position': player_data[3] if len(player_data) > 3 else 'N/A',
                        'age': player_data[8] if len(player_data) > 8 else 'N/A',
                        
                    })
            with open('all_players.json', 'w') as f:
                json.dump(players, f, indent=2)
            with open('all_players.csv', 'w') as f:
                f.write("Name,Team,Position,Age\n")
                for player in players:
                    name = player['name'].replace(',', ';')
                    f.write(f"{name},{player['team']},{player['position']},{player['age']}\n")
    else:
        pass
    
except Exception as e:
    import traceback
    traceback.print_exc()
