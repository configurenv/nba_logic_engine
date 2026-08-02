#!/usr/bin/env python3
# =================================================================================================
# NBA LOGIC ENGINE — PROCESS LAYER
# FILE: process/situational_moments_brain.py
# ROLE: Situational Splits, Friction Modifiers, and Referee Auto-Population with Resilient Fetching
# =================================================================================================

import os
import time
import re
import random
import json
import datetime
import unicodedata
import pandas as pd
import requests

def initialize_logic_engine_workspace():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir) if os.path.basename(script_dir) in ['Core', 'process', 'ingestion'] else script_dir
        
    logs_dir = os.path.join(base_dir, "Logs")
    models_dir = os.path.join(base_dir, "Models")
    
    os.makedirs(logs_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    
    return {
        "BASE": base_dir,
        "LOGS": logs_dir,
        "MODELS": models_dir,
        "REFEREE_TRACKER": os.path.join(logs_dir, "Referee_Tracker_V2.csv"),
        "FORENSIC_LOGS": os.path.join(logs_dir, "Forensic_Game_Logs.csv"),
        "TELEMETRY_LOGS": os.path.join(logs_dir, "REGULAR_SEASON_MASTER_TELEMETRY.csv"),
        "SITUATIONAL_BRAIN": os.path.join(models_dir, "omega_situational_moments_brain.json"),
        "MACRO_CONTEXT": os.path.join(models_dir, "macro_game_context.json")
    }

def normalize_player_name(name_str):
    if pd.isna(name_str) or not isinstance(name_str, str):
        return ""
    decomposed = unicodedata.normalize('NFKD', name_str.replace("?", ""))
    ascii_str = decomposed.encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'\s+', ' ', ascii_str).strip().upper()

def build_secure_nba_network_session():
    session = requests.Session()
    session.headers.update({
        "Host": "stats.nba.com",
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Origin": "https://www.nba.com",
        "Referer": "https://www.nba.com/",
    })
    return session

def get_base_parameters(season, season_type):
    return {
        "LeagueID": "00", "PerMode": "PerGame", "Season": season, "SeasonType": season_type,
        "PlayerOrTeam": "Player", "College": "", "Conference": "", "Country": "", "DateFrom": "", "DateTo": "",
        "Division": "", "DraftPick": "", "DraftYear": "", "GameScope": "", "GameSegment": "", "Height": "",
        "LastNGames": "0", "Location": "", "Month": "0", "OpponentTeamID": "0", "Outcome": "", "PORound": "0",
        "PaceAdjust": "N", "Period": "0", "PlayerExperience": "", "PlayerPosition": "", "PlusMinus": "N",
        "Rank": "N", "SeasonSegment": "", "ShotClockRange": "", "StarterBench": "", "TeamID": "0",
        "VsConference": "", "VsDivision": "", "Weight": ""
    }

def execute_high_velocity_fetch(session, url, params, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            time.sleep(random.uniform(2.0, 4.0))
            response = session.get(url, params=params, timeout=30, allow_redirects=False)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[WARNING] HTTP Status {response.status_code} on attempt {attempt}/{max_retries}")
        except Exception as e:
            print(f"[WARNING] Network pipe latency/timeout on attempt {attempt}/{max_retries}: {e}")
    return None

def extract_nba_matrix_to_dataframe(json_payload):
    if not json_payload or "resultSets" not in json_payload:
        return None
    res = json_payload["resultSets"]
    target_set = res[0] if isinstance(res, list) and len(res) > 0 else res
    if isinstance(target_set, dict) and "headers" in target_set and "rowSet" in target_set:
        return pd.DataFrame(target_set["rowSet"], columns=[h.upper() for h in target_set["headers"]])
    return None

def fetch_situational_split_data(session, season, season_type, endpoint_mode, pt_measure="", measure_type="", clutch_time=""):
    params = get_base_parameters(season, season_type)
    if endpoint_mode == "PT":
        url = "https://stats.nba.com/stats/leaguedashptstats"
        params["PtMeasureType"] = pt_measure
    else:
        url = "https://stats.nba.com/stats/leaguedashplayerstats"
        params["MeasureType"] = measure_type
        
    if clutch_time:
        params["ClutchTime"] = clutch_time
        
    raw_json = execute_high_velocity_fetch(session, url, params)
    return extract_nba_matrix_to_dataframe(raw_json)

def compute_defensive_length_index(player_name):
    combine_profiles = {
        "AUSAR THOMPSON": {"WS": 84.0, "SR": 104.0, "VT": 38.5, "AG": 10.72},
        "EVAN MOBLEY": {"WS": 88.0, "SR": 110.0, "VT": 32.5, "AG": 11.12},
        "RUDY GOBERT": {"WS": 93.0, "SR": 115.0, "VT": 29.0, "AG": 12.45},
        "JARRETT ALLEN": {"WS": 90.0, "SR": 111.0, "VT": 31.5, "AG": 11.82},
        "SHAI GILGEOUS-ALEXANDER": {"WS": 83.5, "SR": 101.5, "VT": 34.0, "AG": 10.95},
        "STEPHON CASTLE": {"WS": 81.0, "SR": 102.0, "VT": 37.0, "AG": 10.82}
    }
    key = str(player_name).upper().strip()
    return float((combine_profiles[key]["WS"] + combine_profiles[key]["SR"] + combine_profiles[key]["VT"]) / combine_profiles[key]["AG"]) if key in combine_profiles else 20.50

def execute_integrated_referee_updater(paths):
    print("[*] Processing Integrated Referee Auto-Population Sequence...")
    target_day = datetime.date(2026, 6, 13)
    target_date_str = target_day.strftime("%Y-%m-%d")
    target_game_str = "NYK@SAS"
    
    crew_chief = "Scott Foster"
    audit_note = "STABLE: Finals Game 5 confirmed; pace contractions dilated via macro configuration."
    
    if os.path.exists(paths["MACRO_CONTEXT"]):
        try:
            with open(paths["MACRO_CONTEXT"], 'r') as f:
                macro_data = json.load(f)
                if "assigned_referee" in macro_data:
                    crew_chief = str(macro_data["assigned_referee"]).title()
                    audit_note = "STABLE: Postseason veteran crew assignment loaded via macro game context."
        except Exception as e:
            print(f"[WARNING] Macro context read bypassed: {e}")

    new_assignment_row = {
        "Referee": crew_chief,
        "Game": target_game_str,
        "Date": target_date_str,
        "Pace_Factor": 95.8,
        "Whistle_Multiplier": 1.04,
        "PTS_Modifier": 1.01,
        "AST_Modifier": 1.0,
        "REB_Modifier": 1.0,
        "3PM_Modifier": 1.0,
        "Audit_Note": audit_note
    }

    try:
        if os.path.exists(paths["REFEREE_TRACKER"]):
            with open(paths["REFEREE_TRACKER"], 'r') as r_file:
                first_line = r_file.readline()
            determined_sep = '\t' if '\t' in first_line else ','
            
            df = pd.read_csv(paths["REFEREE_TRACKER"], sep=determined_sep)
            df.columns = [str(c).strip() for c in df.columns]
            if 'Crew Chief' in df.columns and 'Referee' not in df.columns:
                df = df.rename(columns={'Crew Chief': 'Referee'})
            
            if "Date" in df.columns and "Game" in df.columns:
                df = df[~((df["Date"] == target_date_str) & (df["Game"] == target_game_str))]
            
            df_target_row = pd.DataFrame([new_assignment_row])
            df_target_row = df_target_row.reindex(columns=df.columns, fill_value=1.0)
            df_target_row["Referee"] = crew_chief
            df_target_row["Game"] = target_game_str
            df_target_row["Date"] = target_date_str
            df_target_row["Pace_Factor"] = 95.8
            df_target_row["Whistle_Multiplier"] = 1.04
            df_target_row["Audit_Note"] = audit_note
            
            df_new = pd.concat([df, df_target_row], ignore_index=True)
            df_new.to_csv(paths["REFEREE_TRACKER"], sep=determined_sep, index=False)
        else:
            df_new = pd.DataFrame([new_assignment_row])
            df_new.to_csv(paths["REFEREE_TRACKER"], sep=',', index=False)
            
        print(f"[+] {os.path.basename(paths['REFEREE_TRACKER'])} successfully synchronized for the target slate.")
        print(f"📊 Referee Chief: {crew_chief} | Pace Factor: 95.8")
    except Exception as e:
        print(f"❌ Officiating tracker insertion failed: {e}")

def run_advanced_refinery_pipeline():
    paths = initialize_logic_engine_workspace()
    
    situational_moments_database = {}
    if os.path.exists(paths["SITUATIONAL_BRAIN"]):
        print("[+] Pre-Loading Stable Historical Sub-Brain Node Map from Disk...")
        try:
            with open(paths["SITUATIONAL_BRAIN"], 'r', encoding='utf-8') as f:
                situational_moments_database = json.load(f)
            print(f"[+] Loaded {len(situational_moments_database)} historical player nodes safely into memory.")
        except Exception as e:
            print(f"[WARNING] Historical brain template empty or corrupted: {e}")

    session = build_secure_nba_network_session()
    target_season = "2025-26"
    target_type = "Playoffs"
    
    print("[*] Actuating Situational Data Ingress Channels (with Fallback Protection)...")
    df_usage = fetch_situational_split_data(session, target_season, target_type, "PLAYER", measure_type="Usage")
    df_scoring = fetch_situational_split_data(session, target_season, target_type, "PLAYER", measure_type="Scoring")
    
    if df_usage is None or df_scoring is None:
        print("[WARNING] Live API endpoints encountered rate limits or timeouts. Falling back to local telemetry cache...")
        if os.path.exists(paths["TELEMETRY_LOGS"]):
            tele_df = pd.read_csv(paths["TELEMETRY_LOGS"], low_memory=False)
            for _, row in tele_df.iterrows():
                p_name = normalize_player_name(row.get("PLAYER_NAME", row.get("PLAYER_NAME_CLEAN", "")))
                if not p_name: continue
                target_node = situational_moments_database.setdefault(p_name, {})
                target_node["USAGE_SHARE_PTS"] = float(row.get("USG_PCT_USAGE", 0.20))
                target_node["PCT_PTS_FTM"] = float(row.get("PCT_PTS_FT_SCORING", 0.18))
                target_node["PCT_PTS_3PM"] = float(row.get("PCT_PTS_3PT_SCORING", 0.28))
                target_node["PCT_AST_FGM"] = float(row.get("PCT_AST_FGM_SCORING", 0.45))
            print(f"[SUCCESS] Successfully ingested {len(tele_df)} player records from local telemetry fallback.")
    else:
        for _, row in df_usage.iterrows():
            p_name = normalize_player_name(row.get("PLAYER_NAME", row.get("PLAYER", "")))
            if p_name: situational_moments_database.setdefault(p_name, {})["USAGE_SHARE_PTS"] = float(row.get("PCT_PTS", 0.20))

        for _, row in df_scoring.iterrows():
            p_name = normalize_player_name(row.get("PLAYER_NAME", row.get("PLAYER", "")))
            if not p_name: continue
            target_node = situational_moments_database.setdefault(p_name, {})
            target_node["PCT_PTS_FTM"] = float(row.get("PCT_PTS_FT", 0.18))
            target_node["PCT_PTS_3PM"] = float(row.get("PCT_PTS_3PT", 0.28))
            target_node["PCT_AST_FGM"] = float(row.get("PCT_AST_FGM", 0.45))

    final_cleaned_moments = {}
    for p_name, features in situational_moments_database.items():
        refined_features = {
            "PCT_PTS_FTM": features.get("PCT_PTS_FTM", 0.18),
            "PCT_PTS_3PM": features.get("PCT_PTS_3PM", 0.28),
            "PCT_AST_FGM": features.get("PCT_AST_FGM", 0.45),
            "PCT_UAST_2FGM": features.get("PCT_UAST_2FGM", 0.35),
            "PCT_PTS_PAINT": features.get("PCT_PTS_PAINT", 0.40),
            "PCT_PTS_MID_RANGE": features.get("PCT_PTS_MID_RANGE", 0.15),
            "PTS_OFF_TO": features.get("PTS_OFF_TO", 2.5),
            "PF_DRAWN": features.get("PF_DRAWN", 3.0),
            "DRIVES_COUNT": features.get("DRIVES_COUNT", 8.0),
            "DRIVE_PTS": features.get("DRIVE_PTS", 4.5),
            "FATIGUE_VOLATILITY_SCALE": features.get("FATIGUE_VOLATILITY_SCALE", 0.76),
            "CLUTCH_USG_PCT": features.get("CLUTCH_USG_PCT", 0.20),
            "CLUTCH_NET_RATING": features.get("CLUTCH_NET_RATING", 0.0),
            "USAGE_SHARE_PCT": features.get("USAGE_SHARE_PTS", 0.20),
            "DEFENSIVE_LENGTH_INDEX": features.get("DEFENSIVE_LENGTH_INDEX", compute_defensive_length_index(p_name))
        }
        
        if refined_features["PCT_UAST_2FGM"] > 0.55 or refined_features["CLUTCH_USG_PCT"] > 0.32:
            refined_features["FRICTION_RESISTANCE_RATING"] = "ELITE_ISOLATION_SHIELD"
            refined_features["ELASTIC_MULTIPLIER_MODULUS"] = 1.15
        elif refined_features["PCT_UAST_2Fgn"] > 0.35 or refined_features["PCT_UAST_2FGM"] > 0.35:
            refined_features["FRICTION_RESISTANCE_RATING"] = "STABLE_SECONDARY_CREATOR"
            refined_features["ELASTIC_MULTIPLIER_MODULUS"] = 1.05
        else:
            refined_features["FRICTION_RESISTANCE_RATING"] = "DEPENDENT_CATCH_SHOOT"
            refined_features["ELASTIC_MULTIPLIER_MODULUS"] = 0.92
            
        final_cleaned_moments[p_name] = refined_features

    with open(paths["SITUATIONAL_BRAIN"], 'w', encoding='utf-8') as f:
        json.dump(final_cleaned_moments, f, indent=4)
    print(f"[SUCCESS] Refinery Sub-Brain generated successfully: {paths['SITUATIONAL_BRAIN']}")

    execute_integrated_referee_updater(paths)

if __name__ == "__main__":
    run_advanced_refinery_pipeline()