#!/usr/bin/env python3
# =================================================================================================
# NBA LOGIC ENGINE — CORE PROCESSING & TRAINING LAYER
# FILE: Scripts/train_prop_models.py
# ROLE: XGBoost Neural Sub-Brain Trainer utilizing Stabilized Quantum Intel
# =================================================================================================

import os
import pandas as pd
import numpy as np

try:
    import xgboost as xgb
    XGB_TRAINING_AVAILABLE = True
except ImportError:
    XGB_TRAINING_AVAILABLE = False
    print("[WARNING] xgboost library not found. Please install via: pip install xgboost")

class PropModelTrainer:
    def __init__(self):
        # --- DYNAMIC ENVIRONMENT & PATH RESILIENCE ---
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.getenv('BASE_DIR', os.path.dirname(script_dir) if os.path.basename(script_dir) in ['Scripts', 'Core', 'process', 'ingestion', 'utils'] else script_dir)
        
        self.logs_dir = os.path.join(self.base_dir, "Logs")
        self.models_dir = os.path.join(self.base_dir, "Models")
        os.makedirs(self.models_dir, exist_ok=True)
        
        self.intel_path = os.path.join(self.logs_dir, "QUANTUM_STABILIZED_INTEL.csv")
        self.telemetry_path = os.path.join(self.logs_dir, "REGULAR_SEASON_MASTER_TELEMETRY.csv")

    def train_models(self):
        print("=================================================================")
        print("     NBA LOGIC ENGINE: PREDICTIVE MODEL TRAINING MODULE          ")
        print("=================================================================")
        
        if not XGB_TRAINING_AVAILABLE:
            print("[ERROR] XGBoost package required for training.")
            return
            
        if not os.path.exists(self.intel_path) or not os.path.exists(self.telemetry_path):
            print("[ERROR] Missing required feature intelligence or telemetry logs.")
            return

        intel_df = pd.read_csv(self.intel_path)
        tele_df = pd.read_csv(self.telemetry_path, low_memory=False)
        
        # Standardize ASCII headers
        intel_df.columns = [str(c).strip().upper() for c in intel_df.columns]
        tele_df.columns = [str(c).strip().upper() for c in tele_df.columns]
        
        print(f"[INFO] Ingested Intel: {intel_df.shape[0]} rows x {intel_df.shape[1]} cols | Telemetry: {tele_df.shape[0]} rows x {tele_df.shape[1]} cols")
        
        if 'PLAYER_NAME' in intel_df.columns:
            intel_df['PLAYER_NAME'] = intel_df['PLAYER_NAME'].astype(str).str.strip().str.upper()
        if 'PLAYER_NAME' in tele_df.columns:
            tele_df['PLAYER_NAME'] = tele_df['PLAYER_NAME'].astype(str).str.strip().str.upper()

        # Merge telemetry targets with quantum spatial features
        merged_df = pd.merge(intel_df, tele_df, on='PLAYER_NAME', how='inner', suffixes=('', '_tele'))
        
        print(f"[INFO] Merged Architecture: {merged_df.shape[0]} mapped entities ready for dimensional extraction.")
        
        if merged_df.empty:
            print("[DEBUG CRITICAL ERROR] Merged DataFrame is completely EMPTY! Check PLAYER_NAME key alignment.")
            return

        # Define dynamic feature matrix including rolling, spatial (QSQ), and kinematic (Sigma) parameters
        features = [
            'USG_PCT_STABLE', 
            'PACE_STABLE', 
            'PRE_DIST_RATIO', 
            'WHISTLE_MULTIPLIER', 
            'QSQ_DELTA',
            'WORK_CAPACITY_SIGMA'
        ]
        
        # Ensure all core features exist; instantiate to 0.0 if missing to prevent pipeline collapse
        for col in features:
            if col not in merged_df.columns:
                merged_df[col] = 0.0

        targets = {
            'PTS': next((c for c in ['PTS_STABLE', 'PTS_BASE', 'PTS'] if c in merged_df.columns), None),
            'AST': next((c for c in ['AST_STABLE', 'AST_BASE', 'AST'] if c in merged_df.columns), None),
            'REB': next((c for c in ['REB_STABLE', 'REB_BASE', 'REB'] if c in merged_df.columns), None)
        }
        
        for market, target_col in targets.items():
            if not target_col or target_col not in merged_df.columns:
                print(f"[WARNING] Target vector for {market} not found. Bypassing sub-brain training.")
                continue
                
            X = merged_df[features].fillna(0)
            y = merged_df[target_col].fillna(0)
            
            if y.nunique() <= 1 or y.max() == 0:
                print(f"[DEBUG CRITICAL ERROR] Target vector '{target_col}' has ZERO variance. Model flatline imminent.")
                continue

            print(f"[TRAINING] Compiling {market} Sub-Brain (Target: {target_col} | Mean: {round(float(y.mean()), 2)})...")
            
            dtrain = xgb.DMatrix(X, label=y)
            params = {
                'objective': 'reg:squarederror',
                'max_depth': 4,
                'eta': 0.05,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'seed': 42
            }
            
            bst = xgb.train(params, dtrain, num_boost_round=100)
            model_output_path = os.path.join(self.models_dir, f"omega_actual_{market.lower()}_brain.json")
            bst.save_model(model_output_path)
            
            print(f"  -> Locked to: Models/omega_actual_{market.lower()}_brain.json")

        print("=================================================================")
        print(" All predictive prop models successfully calibrated for execution. ")
        print("=================================================================")

if __name__ == "__main__":
    trainer = PropModelTrainer()
    trainer.train_models()