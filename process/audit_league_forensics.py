import time
import os
import pandas as pd
import unicodedata
import re
from nba_api.stats.endpoints import playergamelogs, leaguedashteamstats
from requests.exceptions import ReadTimeout, ConnectionError

# --- PATH CONFIGURATION ---
BASE_DIR = os.getenv('BASE_DIR', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGS_DIR = os.path.join(BASE_DIR, "Logs")
GAME_LOGS_FILE = os.path.join(LOGS_DIR, "Forensic_Game_Logs.csv")
STATS_FILE = os.path.join(LOGS_DIR, "League_Advanced_Stats.csv")

# TARGETED 2026 POSTSEASON ROSTER
TARGET_TEAMS = [
    1610612752, # NYK
    1610612759, # SAS
    1610612760, # OKC
]

class NameSanitizer:
    """V35.5 Name Integrity Engine: Resolves encoding distortions and artifacts."""
    
    @staticmethod
    def clean(name):
        if not isinstance(name, str):
            return name
            
        # 1. Normalize Unicode (converts Vučević -> Vucevic)
        name = unicodedata.normalize('NFKD', name)
        name = name.encode('ascii', 'ignore').decode('ascii')
        
        # 2. Remove common harvest artifacts (e.g., "i12", "A me")
        # These patterns appear when UTF-8 bytes are misinterpreted as single characters
        name = name.replace("i12", "")
        name = name.replace("A me", "a") # Specific fix for Pacome Dadiet
        
        # 3. Final Regex Cleanup (Remove non-alphabetic noise but keep spaces/hyphens)
        name = re.sub(r'[^a-zA-Z\s\-]', '', name)
        
        return name.strip()

def run_harvest():
    if not os.path.exists(LOGS_DIR): 
        os.makedirs(LOGS_DIR)
    
    # 1. League Advanced Stats Update
    try:
        print("📊 Harvesting League Advanced Stats...")
        stats = leaguedashteamstats.LeagueDashTeamStats(
            season='2025-26',
            measure_type_detailed_defense='Advanced'
        ).get_data_frames()[0]
        stats.to_csv(STATS_FILE, index=False, encoding='utf-8-sig')
        print(f"✅ Advanced Stats Synced: {STATS_FILE}")
    except Exception as e: 
        print(f"⚠️ Team Stats Failed: {e}")

    # 2. Forensic Log Extraction
    all_logs = []
    for team_id in TARGET_TEAMS:
        success = False
        for attempt in range(3):
            try:
                print(f"📥 Harvesting Team {team_id} (Attempt {attempt+1})...")
                # Pulling Traditional Stats for Volume (PTS, AST, REB)
                logs = playergamelogs.PlayerGameLogs(
                    season_nullable='2025-26', 
                    team_id_nullable=team_id,
                    season_type_nullable='Playoffs'
                ).get_data_frames()[0]
                
                # Also pull Regular Season to fill gaps
                rs_logs = playergamelogs.PlayerGameLogs(
                    season_nullable='2025-26', 
                    team_id_nullable=team_id,
                    season_type_nullable='Regular Season'
                ).get_data_frames()[0]
                
                all_logs.extend([logs, rs_logs])
                success = True
                break
            except (ReadTimeout, ConnectionError):
                time.sleep(3)
        time.sleep(1.2)

    if all_logs:
        full_logs = pd.concat(all_logs).drop_duplicates(subset=['GAME_ID', 'PLAYER_ID'])
        
        # --- APPLY NAME INTEGRITY ENGINE ---
        print("🧬 Sanitizing Player Names...")
        full_logs['PLAYER_NAME'] = full_logs['PLAYER_NAME'].apply(NameSanitizer.clean)
        
        # Save with utf-8-sig to ensure Excel/WSL compatibility
        full_logs.to_csv(GAME_LOGS_FILE, index=False, encoding='utf-8-sig')
        print(f"✅ Forensic Logs Harvested & Sanitized: {GAME_LOGS_FILE}")
        
        # OPTIONAL: Synchronize QUANTUM_STABILIZED_INTEL.csv if it exists
        intel_path = os.path.join(LOGS_DIR, "QUANTUM_STABILIZED_INTEL.csv")
        if os.path.exists(intel_path):
            intel_df = pd.read_csv(intel_path)
            intel_df['PLAYER_NAME'] = intel_df['PLAYER_NAME'].apply(NameSanitizer.clean)
            intel_df.to_csv(intel_path, index=False, encoding='utf-8-sig')
            print("✅ Master Intel Names Sanitized.")

if __name__ == "__main__":
    run_harvest()