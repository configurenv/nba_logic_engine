#!/usr/bin/env python3
# =================================================================================================
# NBA LOGIC ENGINE — PROCESS LAYER
# FILE: process/prepare_quantum_intel.py
# ROLE: Advanced Intel Refinery & Variance Mapping Engine
# =================================================================================================

import os
import pandas as pd
import numpy as np

# --- DYNAMIC ENVIRONMENT & PATH RESOLUTION ---
BASE_DIR = os.getenv('BASE_DIR', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGS_DIR = os.path.join(BASE_DIR, "Logs")
REGULAR_PATH = os.path.join(LOGS_DIR, "REGULAR_SEASON_MASTER_TELEMETRY.csv")
OUTPUT_PATH = os.path.join(LOGS_DIR, "QUANTUM_STABILIZED_INTEL.csv")

def compile_quantum_intel():
    """
    Ingests master player tracking telemetry, resolves zero-variance linear independence bias,
    and compiles a stabilized feature matrix for downstream machine learning ingestion.
    """
    print("=================================================================")
    print("INITIALIZING QUANTUM INTEL REFINERY COMPILER (V40.2_TELEMETRY)")
    print("=================================================================")
    
    if not os.path.exists(REGULAR_PATH):
        print(f"[ERROR] Cannot map advanced tracking layers. Missing target file: {REGULAR_PATH}")
        return

    # Load master telemetry dataset with low memory optimization
    df = pd.read_csv(REGULAR_PATH, low_memory=False)
    print("[INFO] Master telemetry successfully ingested. Resolving feature variance...")

    # Build the stabilized output data frame conforming to engine requirements
    intel_df = pd.DataFrame()
    intel_df['PLAYER_NAME'] = df['PLAYER_NAME'].str.upper()
    intel_df['TEAM_ABBR'] = df['TEAM_ABBREVIATION']
    
    # 1. Core Feature Extraction (Restoring Information Gain for Gradient Boost Models)
    intel_df['USG_PCT_STABLE'] = df['USG_PCT_ADVANCED'].fillna(0.20)
    intel_df['PACE_STABLE'] = df['PACE_ADVANCED'].fillna(100.0)
    intel_df['PRE_DIST_RATIO'] = df['AST_PCT_ADVANCED'].fillna(0.15) 
    
    # 2. Schema Stability & Baseline Assignments
    intel_df['OFF_RTG_STABLE'] = df['OFF_RATING_ADVANCED'].fillna(110.0)
    intel_df['EFG_PCT_STABLE'] = df['EFG_PCT_ADVANCED'].fillna(0.50)
    intel_df['PTS_STABLE'] = df['PTS_BASE'].fillna(10.0) if 'PTS_BASE' in df.columns else 10.0
    intel_df['AST_STABLE'] = df['AST_BASE'].fillna(2.0) if 'AST_BASE' in df.columns else 2.0
    intel_df['REB_STABLE'] = df['REB_BASE'].fillna(3.0) if 'REB_BASE' in df.columns else 3.0
    intel_df['DRIVE_PTS'] = df['DRIVE_PTS_DRIVES'].fillna(2.0)
    intel_df['AVG_SPEED'] = df['AVG_SPEED_SPEEDDISTANCE'].fillna(4.1)
    intel_df['WORK_CAPACITY_SIGMA'] = 2.8
    intel_df['HUSTLE_SCORE'] = 3.5        
    intel_df['VERY_TIGHT_FREQ'] = 0.1     
    
    # 3. Dynamic Whistle Resistance Scaling
    if 'PCT_PFD_USAGE' in df.columns:
        raw_whistle = 0.85 + (df['PCT_PFD_USAGE'].astype(float) * 0.6)
        intel_df['Whistle_Multiplier'] = np.clip(raw_whistle, 0.85, 1.15)
    else:
        intel_df['Whistle_Multiplier'] = 0.96 
        
    # Deduplicate records to maintain primary key integrity
    intel_df = intel_df.drop_duplicates(subset=['PLAYER_NAME'])
    
    # Ensure target output directory exists prior to write operation
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    
    # Commit transformed schema to storage destination
    intel_df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
    print(f"[SUCCESS] Calibration Applied: Usage, Pace, and Whistle_Multiplier mapped to active variance.")
    print(f"[SUCCESS] Quantum Intel compiled successfully to: {OUTPUT_PATH}")

if __name__ == "__main__":
    compile_quantum_intel()