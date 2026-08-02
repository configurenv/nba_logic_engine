#!/usr/bin/env python3
# =================================================================================================
# NBA LOGIC ENGINE — CORE LAYER
# FILE: Core/ensemble.py
# ROLE: XGBoost Sub-Brain Vector Weight Trainer (Hardened & Environment-Resilient)
# =================================================================================================

import os
import numpy as np
import pandas as pd
import unicodedata

# Safe Dependency and Environment Arbitration
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

script_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(script_dir) if os.path.basename(script_dir) == 'Core' else script_dir

TRAIN_DATA_PATH = os.path.join(BASE_DIR, "Logs", "QUANTUM_STABILIZED_INTEL.csv")
MODEL_OUTPUT_DIR = os.path.join(BASE_DIR, "Models")

class NameResolver:
    MAPPING = {
        "BRON JAMES": "LEBRON JAMES", 
        "SHAI GILGEOUS": "SHAI GILGEOUS-ALEXANDER", 
        "ANTHONY TOWNS": "KARL-ANTHONY TOWNS",
        "KARL-ANTHONY TOWNS": "KARL-ANTHONY TOWNS",
        "DE'AARON FOX": "DEAARON FOX"
    }
    @classmethod
    def resolve(cls, name):
        if pd.isna(name): return ""
        norm = unicodedata.normalize('NFKD', str(name)).encode('ascii', 'ignore').decode('ascii')
        clean = norm.replace("'", "").replace("-", "").replace(".", "").strip().upper()
        return cls.MAPPING.get(clean, clean)

def train_array():
    print("=================================================================")
    print("       NBA LOGIC ENGINE: XGBOOST ENSEMBLE SUB-BRAIN TRAINER      ")
    print("=================================================================")

    if not XGB_AVAILABLE:
        print("[WARNING] XGBoost package not detected in active environment. Bypassing gradient boosting.")
        return

    if not os.path.exists(TRAIN_DATA_PATH):
        print(f"[ERROR] Structural training matrix missing at: {TRAIN_DATA_PATH}")
        return
        
    df = pd.read_csv(TRAIN_DATA_PATH)
    df['Player'] = df['PLAYER_NAME'].apply(NameResolver.resolve)

    potential_features = ['PRE_DIST_RATIO', 'USG_PCT_STABLE', 'PACE_STABLE', 'Whistle_Multiplier']
    active_features = [f for f in potential_features if f in df.columns]
    
    print(f"[SYNC] Active Training Features locked: {active_features}")
    
    sub_brains = [
        {'target': 'PTS_STABLE', 'filename': 'omega_actual_pts_brain.json'},
        {'target': 'AST_STABLE', 'filename': 'omega_actual_ast_brain.json'},
        {'target': 'REB_STABLE', 'filename': 'omega_actual_reb_brain.json'}
    ]

    os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)

    for brain in sub_brains:
        target_label = brain['target']
        if target_label not in df.columns: 
            print(f"[BYPASS] Target label '{target_label}' omitted from active tracking structures.")
            continue
            
        print(f"[TRAIN] Optimizing pathway for Target Node: {target_label}")
        X = df[active_features].apply(pd.to_numeric, errors='coerce').fillna(0.0)
        y = pd.to_numeric(df[target_label], errors='coerce').fillna(0.0)
        
        try:
            xgb_regressor = xgb.XGBRegressor(
                n_estimators=500, max_depth=5, learning_rate=0.05,
                subsample=0.8, colsample_bytree=0.8, random_state=42, tree_method='hist'
            )
            xgb_regressor.fit(X, y)
            target_brain_path = os.path.join(MODEL_OUTPUT_DIR, brain['filename'])
            xgb_regressor.get_booster().save_model(target_brain_path)
            print(f"[SUCCESS] Vector weights exported -> {target_brain_path}")
        except Exception as e:
            print(f"[ERROR] Training failed for node {target_label}: {e}")

if __name__ == "__main__":
    train_array()