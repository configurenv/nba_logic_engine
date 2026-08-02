#!/usr/bin/env python3
# =================================================================================================
# NBA LOGIC ENGINE — INGESTION LAYER
# FILE: ingestion/extract_play_by_play.py
# ROLE: Hardened Play-by-Play Event Stream Harvester
# =================================================================================================

import os
import time
import json
import random
import requests

# --- DYNAMIC ENVIRONMENT & PATH RESOLUTION ---
BASE_DIR = os.getenv('BASE_DIR', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGS_DIR = os.path.join(BASE_DIR, "Logs")
STAGING_FILE = os.path.join(LOGS_DIR, "ALL_PLAYS_RAW_STAGING.json")
ESPN_CORE = "https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba/events/{}/competitions/{}/plays?limit=1000"

# --- HISTORICAL GAME MASTER DICTIONARY ---
GAME_MAP = {
    "401871333": "0042500201", "401871334": "0042500202", "401871335": "0042500203",
    "401871336": "0042500204", "401871337": "0042500205", "401871154": "0042500233",
    "401871155": "0042500234", "401871156": "0042500235", "401871157": "0042500236",
    "401871338": "0042500206", "401871339": "0042500207", "401809838": "0022501230",
    "401810272": "0022500417", "401809239": "0022500010", "401810423": "0022500568",
    "401810585": "0022500730", "401873197": "0042500311", "401873341": "0042500301",
    "401873198": "0042500312", "401873342": "0042500302", "401873343": "0042500303",
    "401873200": "0042500314", "401873344": "0042500304", "401873201": "0042500315",
    "401873202": "0042500316", "401873203": "0042500317", "401859963": "0042500401",
    "401859964": "0042500402", "401859965": "0042500403", "401859966": "0042500404",
}

# --- ACTIVE LIVE SLATES ---
LIVE_SLATE_MAP = {
    "401859967": "0042500405",
}

def build_http_session():
    """Constructs a stateful session with standard HTTP headers for connection stability."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    })
    return session

def run_harvest():
    print("=================================================================")
    print("      NBA LOGIC ENGINE: PLAY-BY-PLAY EVENT STREAM HARVESTER      ")
    print("=================================================================")
    
    os.makedirs(LOGS_DIR, exist_ok=True)

    master_data = {}
    if os.path.exists(STAGING_FILE):
        try:
            with open(STAGING_FILE, "r", encoding="utf-8") as f:
                master_data = json.load(f)
            print(f"[INFO] Existing staging database loaded. Game records: {len(master_data)}")
        except Exception:
            master_data = {}

    full_target_map = {**GAME_MAP, **LIVE_SLATE_MAP}
    session = build_http_session()

    for espn_id, nba_id in full_target_map.items():
        if espn_id in master_data and espn_id not in LIVE_SLATE_MAP:
            continue

        if espn_id in LIVE_SLATE_MAP:
            print(f"🔄 [LIVE REFRESH] Querying event stream for NBA Game ID: {nba_id}...")
        else:
            print(f"📥 [HISTORICAL INGRESS] Pulling datasets for NBA Game ID: {nba_id}...")

        success = False
        for attempt in range(1, 4):
            try:
                time.sleep(random.uniform(1.2, 2.5))
                response = session.get(ESPN_CORE.format(espn_id, espn_id), timeout=20)
                
                if response.status_code == 200:
                    plays = response.json().get("items", [])
                    master_data[espn_id] = {
                        "nba_id": nba_id,
                        "plays": plays
                    }
                    print(f"✅ [SUCCESS] Captured {len(plays)} play events for Game ID: {nba_id}")
                    success = True
                    break
                elif response.status_code in [429, 503]:
                    time.sleep(4 * attempt)
            except Exception as e:
                print(f"⚠️ [WARNING] Attempt {attempt} failed for Game ID {nba_id}: {e}")
                time.sleep(2)
                
        if not success:
            print(f"❌ [ERROR] Abandoning fetch for ESPN Event ID: {espn_id}")

    try:
        with open(STAGING_FILE, "w", encoding="utf-8") as f:
            json.dump(master_data, f, indent=4, ensure_ascii=False)
        print("=================================================================")
        print(f"💾 [STAGING LOCKED] Payload successfully written to: {STAGING_FILE}")
        print("=================================================================")
    except Exception as e:
        print(f"❌ [CRITICAL] Failed to write staging file to disk: {e}")

if __name__ == "__main__":
    run_harvest()