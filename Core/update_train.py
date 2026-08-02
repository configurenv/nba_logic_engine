#!/usr/bin/env python3
# =================================================================================================
# NBA LOGIC ENGINE — CORE LAYER
# FILE: update_train.py
# ROLE: High-Velocity Game-by-Game Label Accumulator & Feature Bridge
# =================================================================================================

import pandas as pd
import numpy as np
import os
import unicodedata

# --- PORTABLE PATH ARBITRATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Handles execution whether run from root or Core/ subdirectory
BASE_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == 'Core' else SCRIPT_DIR

TRAIN_DIR = os.path.join(BASE_DIR, "Training_Data")
LOGS_DIR = os.path.join(BASE_DIR, "Logs")

TRAIN_PATH = os.path.join(TRAIN_DIR, "V30_TRAINING_MASTER.csv")
ACTUALS_PATH = os.path.join(LOGS_DIR, "Forensic_Game_Logs.csv")
INTEL_PATH = os.path.join(LOGS_DIR, "QUANTUM_STABILIZED_INTEL.csv")

class NameResolver:
    MAPPING = {
        "BRON JAMES": "LEBRON JAMES", 
        "SHAI GILGEOUS": "SHAI GILGEOUS-ALEXANDER", 
        "ANTHONY TOWNS": "KARL-ANTHONY TOWNS",
        "DEAARON FOX": "DE'AARON FOX",
        "TERRENCE SHANNON JR": "TERRENCE SHANNON JR.",
        "NICK SMITH JR": "NICK SMITH JR.",
        "V J EDGECOMBE": "VJ EDGECOMBE"
    }
    @classmethod
    def resolve(cls, name):
        if pd.isna(name): return ""
        norm = unicodedata.normalize('NFKD', str(name)).encode('ascii', 'ignore').decode('ascii')
        clean = norm.strip().upper()
        return cls.MAPPING.get(clean, clean)

def run_update():
    print("[TRAINING] Actuating Multi-Variable Data Ledger Engine...")
    
    # Ensure directories exist
    os.makedirs(TRAIN_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

    if not os.path.exists(ACTUALS_PATH):
        print(f"[ERROR] Required actuals database missing at: {ACTUALS_PATH}")
        return

    forensic_df = pd.read_csv(ACTUALS_PATH, low_memory=False)

    # Bootstrap training master if it doesn't exist for fresh repository clones
    if not os.path.exists(TRAIN_PATH):
        print(f"[INFO] Training master not found. Bootstrapping initial template at {TRAIN_PATH}...")
        initial_df = pd.DataFrame({
            'Game_ID': forensic_df['GAME_ID'],
            'Player': forensic_df['PLAYER_NAME'].apply(NameResolver.resolve),
            'ACTUAL_PTS': forensic_df['PTS'],
            'ACTUAL_AST': forensic_df['AST'],
            'ACTUAL_REB': forensic_df['REB'],
            'ACTUAL_3PM': forensic_df['FG3M']
        })
        initial_df.to_csv(TRAIN_PATH, index=False, encoding='utf-8-sig')

    train_df = pd.read_csv(TRAIN_PATH)
    
    # 1. INGEST ADVANCED INTEL (Node A)
    if not os.path.exists(INTEL_PATH):
        print(f"[ERROR] Cannot map advanced features. Intel file missing at {INTEL_PATH}")
        return
        
    print("[TRAINING] Sourcing Advanced Multi-Variable Features...")
    intel_df = pd.read_csv(INTEL_PATH)
    
    # DYNAMIC MAPPING: Rename upstream column to match ML array expectations
    if 'Whistle_Multiplier' in intel_df.columns:
        intel_df.rename(columns={'Whistle_Multiplier': 'WHISTLE_RESISTANCE'}, inplace=True)
    elif 'WHISTLE_RESISTANCE' not in intel_df.columns:
         print("[ERROR] Neither 'Whistle_Multiplier' nor 'WHISTLE_RESISTANCE' found in Intel file.")
         return
         
    intel_df['Player'] = intel_df['PLAYER_NAME'].apply(NameResolver.resolve)
    
    # Isolate required feature set
    advanced_features = intel_df[['Player', 'USG_PCT_STABLE', 'PACE_STABLE', 'WHISTLE_RESISTANCE', 'PRE_DIST_RATIO']].copy()

    # 2. PROCESS RAW ACTUALS (Node B)
    forensic_df['Player'] = forensic_df['PLAYER_NAME'].apply(NameResolver.resolve)
    actuals = forensic_df[['GAME_ID', 'Player', 'PTS', 'AST', 'REB', 'FG3M']].copy()
    actuals.rename(columns={
        'GAME_ID': 'Game_ID',
        'PTS': 'ACTUAL_PTS',
        'AST': 'ACTUAL_AST',
        'REB': 'ACTUAL_REB',
        'FG3M': 'ACTUAL_3PM'
    }, inplace=True)
    actuals['gameId'] = actuals['Game_ID']

    # 3. THE BRIDGE (Node C)
    actuals = actuals.merge(advanced_features, on='Player', how='left')

    print("[TRAINING] Commencing combine_first() overlay...")
    
    # Set Indices to map data perfectly
    train_df.set_index(['Game_ID', 'Player'], inplace=True)
    actuals.set_index(['Game_ID', 'Player'], inplace=True)
    
    # 4. COMMIT TO LEDGER (Node D)
    updated = train_df.combine_first(actuals).reset_index()
    
    # Scrub remaining artifacts
    updated = updated.fillna(0.0)
    updated.to_csv(TRAIN_PATH, index=False, encoding='utf-8-sig')
    
    print(f"[SUCCESS] Ledger Locked. Advanced features successfully mapped to {len(updated)} records.")

if __name__ == "__main__":
    run_update()