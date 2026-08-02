#!/usr/bin/env python3
# =================================================================================================
# NBA LOGIC ENGINE — CORE LAYER
# FILE: Core/metadata_sync.py
# ROLE: Spatial Coordinate & Play-by-Play Metadata Ingress Sync
# =================================================================================================

import json
import os
import glob
import pandas as pd

# --- PATH ARBITRATION RIG ---
script_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(script_dir) if os.path.basename(script_dir) == 'Core' else script_dir
LOGS_DIR = os.path.join(BASE_DIR, "Logs")
MASTER_PBP = os.path.join(LOGS_DIR, "SENTINEL_ALPHA_MASTER_PBP.csv")
STAGING_JSON = os.path.join(LOGS_DIR, "ALL_PLAYS_RAW_STAGING.json")

def run_sync():
    print("[METADATA] Initializing Safe Sync & Metadata Harmonization...")
    
    # Purge local metadata cache artifacts
    for art in glob.glob(os.path.join(BASE_DIR, "**/*.Identifier"), recursive=True):
        try:
            os.remove(art)
        except Exception:
            pass
    
    if not os.path.exists(STAGING_JSON):
        print(f"[ERROR] Staging payload missing at absolute path: {STAGING_JSON}")
        return

    master_df = (
        pd.read_csv(MASTER_PBP, dtype={'Player': str, 'Shot_Type': str}, low_memory=False) 
        if os.path.exists(MASTER_PBP) 
        else pd.DataFrame()
    )
    
    with open(STAGING_JSON, 'r', encoding='utf-8') as f: 
        data = json.load(f)
    
    new_records = []
    for g_id, g_data in data.items():
        for play in g_data.get('plays', []):
            coord = play.get('coordinate', {})
            new_records.append({
                "gameId": str(g_id),
                "play_id": play.get('id'),
                "text": play.get('text', ''),
                "x": coord.get('x', 0),
                "y": coord.get('y', 0)
            })
    
    new_df = pd.DataFrame(new_records)
    
    if not master_df.empty:
        master_df = master_df.drop_duplicates(subset=['gameId', 'play_id'])
        final_df = pd.concat([master_df, new_df], join='outer', ignore_index=True)
        final_df = final_df.drop_duplicates(subset=['gameId', 'play_id'], keep='last')
    else:
        final_df = new_df

    os.makedirs(LOGS_DIR, exist_ok=True)
    final_df.to_csv(MASTER_PBP, index=False, encoding='utf-8-sig')
    print(f"[SUCCESS] Synced {len(new_records)} records. Master schema preserved.")

if __name__ == "__main__":
    run_sync()