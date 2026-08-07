#!/usr/bin/env python3
# =================================================================================================
# NBA LOGIC ENGINE — PROCESS LAYER
# FILE: process/prepare_quantum_intel.py
# ROLE: Dynamic Intel Refinery, Spatial qSQ Delta, and Kinematic Work-Rate Compiler
# =================================================================================================
import os
import pandas as pd
import numpy as np

# --- DYNAMIC ENVIRONMENT & PATH RESILIENCE ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.getenv('BASE_DIR', os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) in ['Script', 'Core', 'process', 'ingestion', 'utils'] else SCRIPT_DIR)

LOGS_DIR = os.path.join(BASE_DIR, "Logs")
os.makedirs(LOGS_DIR, exist_ok=True)

REGULAR_PATH = os.path.join(LOGS_DIR, "REGULAR_SEASON_MASTER_TELEMETRY.csv")
PBP_PATH = os.path.join(LOGS_DIR, "SENTINEL_ALPHA_MASTER_PBP.csv")
OUTPUT_PATH = os.path.join(LOGS_DIR, "QUANTUM_STABILIZED_INTEL.csv")

def compute_dynamic_spatial_metrics(pbp_path):
    """
    Dynamically computes Quantified Shot Quality (qSQ) Delta and Kinematic Work-Rate (Sigma)
    from spatial play-by-play coordinate data.
    """
    qsq_dict = {}
    work_cap_dict = {}
    
    if os.path.exists(pbp_path):
        try:
            pbp_df = pd.read_csv(pbp_path, low_memory=False)
            # Standardize ASCII headers
            pbp_df.columns = [str(c).strip().upper() for c in pbp_df.columns]
            
            if all(col in pbp_df.columns for col in ['LOC_X', 'LOC_Y', 'PLAYER_NAME']):
                # Calculate Euclidean distance from origin (rim) using powers
                pbp_df['DIST'] = np.sqrt(pbp_df['LOC_X']**2 + pbp_df['LOC_Y']**2) / 10.0
                pbp_df['EXP_EFG'] = np.maximum(0.30, 0.72 - (0.025 * pbp_df['DIST']))
                pbp_df['ACT_EFG'] = np.where(pbp_df['EVENT_TYPE'] == 'Made Shot', 1.0, 0.0)
                
                # Group by standard ASCII player name
                grouped = pbp_df.groupby('PLAYER_NAME').agg(
                    ACT_EFG=('ACT_EFG', 'mean'),
                    EXP_EFG=('EXP_EFG', 'mean'),
                    DIST_STD=('DIST', 'std')
                )
                
                grouped['QSQ_DELTA'] = grouped['ACT_EFG'] - grouped['EXP_EFG']
                # Kinematic fatigue volatility modeled as the spatial distribution spread of their actions
                grouped['WORK_CAP_SIGMA'] = grouped['DIST_STD'].fillna(2.0) * 1.5
                
                qsq_dict = grouped['QSQ_DELTA'].to_dict()
                work_cap_dict = grouped['WORK_CAP_SIGMA'].to_dict()
                print("[INFO] Spatial telemetry matrix successfully parsed and metrics calculated.")
        except Exception as e:
            print(f"[WARNING] Spatial PBP calculation bypassed due to error: {e}")
    else:
        print(f"[WARNING] PBP file not found at {pbp_path}. Falling back to default baseline matrices.")
        
    return qsq_dict, work_cap_dict

def compile_quantum_intel():
    print("====================================================================================================")
    print("                     NBA LOGIC ENGINE: DYNAMIC INTEL REFINERY                                       ")
    print("====================================================================================================")
    
    if not os.path.exists(REGULAR_PATH):
        print(f"[ERROR] Cannot map tracking layers. Missing target file: {REGULAR_PATH}")
        return

    df = pd.read_csv(REGULAR_PATH, low_memory=False)
    df.columns = [str(c).strip().upper() for c in df.columns]
    print(f"[INFO] Master telemetry successfully ingested ({len(df)} records). Resolving feature variance...")
    
    qsq_spatial_db, work_cap_db = compute_dynamic_spatial_metrics(PBP_PATH)
    
    intel_df = pd.DataFrame()
    intel_df['PLAYER_NAME'] = df['PLAYER_NAME'].astype(str).str.upper().str.strip()
    intel_df['TEAM_ABBR'] = df['TEAM_ABBREVIATION'] if 'TEAM_ABBREVIATION' in df.columns else 'UNK'
    
    # Core Stability Features
    intel_df['USG_PCT_STABLE'] = df['USG_PCT_ADVANCED'].fillna(0.20) if 'USG_PCT_ADVANCED' in df.columns else 0.20
    intel_df['PACE_STABLE'] = df['PACE_ADVANCED'].fillna(100.0) if 'PACE_ADVANCED' in df.columns else 100.0
    intel_df['PRE_DIST_RATIO'] = df['AST_PCT_ADVANCED'].fillna(0.15) if 'AST_PCT_ADVANCED' in df.columns else 0.15
    intel_df['OFF_RTG_STABLE'] = df['OFF_RATING_ADVANCED'].fillna(110.0) if 'OFF_RATING_ADVANCED' in df.columns else 110.0
    intel_df['EFG_PCT_STABLE'] = df['EFG_PCT_ADVANCED'].fillna(0.50) if 'EFG_PCT_ADVANCED' in df.columns else 0.50
    
    # Base Box Scores
    intel_df['PTS_STABLE'] = df['PTS_BASE'].fillna(10.0) if 'PTS_BASE' in df.columns else 10.0
    intel_df['AST_STABLE'] = df['AST_BASE'].fillna(2.0) if 'AST_BASE' in df.columns else 2.0
    intel_df['REB_STABLE'] = df['REB_BASE'].fillna(3.0) if 'REB_BASE' in df.columns else 3.0
    
    # Dynamic Spatial Integration
    intel_df['QSQ_DELTA'] = intel_df['PLAYER_NAME'].map(qsq_spatial_db).fillna(0.03)
    intel_df['WORK_CAPACITY_SIGMA'] = intel_df['PLAYER_NAME'].map(work_cap_db).fillna(8.2)
    
    # Dynamic Whistle Resistance
    if 'PCT_PFD_USAGE' in df.columns:
        raw_whistle = 0.85 + (df['PCT_PFD_USAGE'].astype(float) * 0.6)
        intel_df['WHISTLE_MULTIPLIER'] = np.clip(raw_whistle, 0.85, 1.15)
    else:
        intel_df['WHISTLE_MULTIPLIER'] = 0.96 
        
    # Standardize data structure and purge duplicate player entries
    intel_df = intel_df.drop_duplicates(subset=['PLAYER_NAME'])
    
    intel_df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
    print(f"[SUCCESS] Quantum Intel compiled successfully to: {OUTPUT_PATH}")

if __name__ == "__main__":
    compile_quantum_intel()