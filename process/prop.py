#!/usr/bin/env python3
# =================================================================================================
# NBA LOGIC ENGINE — INGESTION LAYER
# FILE: ingestion/extract_odds_api_props.py
# ROLE: Live Odds API Player Prop Harvester with Quota Tracking & CSV Export
# =================================================================================================

import os
import requests
import pandas as pd

# --- PORTABLE PATH ARBITRATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) in ['Core', 'process', 'ingestion', 'utils', 'Script'] else script_dir

PROP_DIR = os.path.join(BASE_DIR, "Prop Master")
PROP_FILE = os.path.join(PROP_DIR, "player_prop_master.csv")

# Configuration: Replace with your actual key or load from environment variable
API_KEY = os.getenv("SPORTS_API_KEY", "931352bd88316b46304a1799f731494a")
SPORT_KEY = "basketball_nba"
REGIONS = "us"  # US region includes Caesars/William Hill
BOOKMAKERS = "williamhill,caesars"  # Target William Hill market keys
MARKETS = "player_points,player_rebounds,player_assists,player_threes"
ODDS_FORMAT = "america"

def fetch_and_parse_player_props():
    print("=================================================================")
    print("     THE ODDS API: NBA PLAYER PROP HARVESTER & QUOTA AUDIT       ")
    print("=================================================================")
    
    os.makedirs(PROP_DIR, exist_ok=True)
    
    # Corrected Base URL domain (api.the-odds-api.com instead of api.the-odds-api.v4)
    events_url = f"https://api.the-odds-api.com/v4/sports/{SPORT_KEY}/events"
    events_params = {"apiKey": API_KEY}
    
    try:
        print("[NETWORK] Fetching active NBA event schedules...")
        events_resp = requests.get(events_url, params=events_params, timeout=20)
        
        # Check and print remaining API quota headers
        remaining_calls = events_resp.headers.get('x-requests-remaining', 'N/A')
        used_calls = events_resp.headers.get('x-requests-used', 'N/A')
        print(f"📊 [API QUOTA STATUS] Remaining Calls: {remaining_calls} | Used Calls: {used_calls}")
        
        if events_resp.status_code != 200:
            print(f"[ERROR] Failed to fetch events. Status code: {events_resp.status_code}, Message: {events_resp.text}")
            return
            
        events = events_resp.json()
        if not events:
            print("[INFO] No active NBA events found matching current schedule.")
            return
            
        parsed_props = []
        
        # Iterate through upcoming games and pull player props (limiting batch size to conserve quota)
        for event in events[:2]:
            event_id = event['id']
            home_team = event['home_team']
            away_team = event['away_team']
            print(f"[FETCH] Pulling William Hill/Caesars props for: {away_team} @ {home_team}...")
            
            odds_url = f"https://api.the-odds-api.com/v4/sports/{SPORT_KEY}/events/{event_id}/odds"
            odds_params = {
                "apiKey": API_KEY,
                "regions": REGIONS,
                "bookmakers": BOOKMAKERS,
                "markets": MARKETS,
                "oddsFormat": ODDS_FORMAT
            }
            
            odds_resp = requests.get(odds_url, params=odds_params, timeout=25)
            
            # Print quota check after event odds query
            rem_odds = odds_resp.headers.get('x-requests-remaining', 'N/A')
            print(f"📊 [QUOTA UPDATE] Remaining API Calls: {rem_odds}")
            
            if odds_resp.status_code == 200:
                odds_data = odds_resp.json()
                bookmakers = odds_data.get('bookmakers', [])
                
                for bookmaker in bookmakers:
                    for market in bookmaker.get('markets', []):
                        m_key = market['key']
                        prop_type_map = {
                            'player_points': 'PTS',
                            'player_rebounds': 'REB',
                            'player_assists': 'AST',
                            'player_threes': '3PM'
                        }
                        p_type = prop_type_map.get(m_key)
                        if not p_type: continue
                        
                        for outcome in market.get('outcomes', []):
                            player_name = outcome.get('description')
                            point_milestone = outcome.get('point')
                            
                            if player_name and point_milestone is not None:
                                parsed_props.append({
                                    "Player": player_name.upper().strip(),
                                    "Prop_Type": p_type,
                                    "Milestone_Value": float(point_milestone)
                                })
            
        if parsed_props:
            df_props = pd.DataFrame(parsed_props).drop_duplicates()
            df_props.to_csv(PROP_FILE, index=False, encoding='utf-8-sig')
            print(f"=================================================================")
            print(f"✅ [SUCCESS] Prop Master updated successfully from API.")
            print(f"-> Destination: {PROP_FILE}")
            print(f"-> Total Harvested Prop Rows: {len(df_props)}")
            print(f"=================================================================")
        else:
            print("[INFO] No player prop lines returned for current game window. Check if games are currently active.")
            
    except Exception as e:
        print(f"[CRITICAL ERROR] Failed during Odds API ingestion loop: {e}")

if __name__ == "__main__":
    fetch_and_parse_player_props()