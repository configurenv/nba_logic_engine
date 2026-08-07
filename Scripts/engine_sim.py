#!/usr/bin/env python3
# =================================================================================================
# NBA LOGIC ENGINE — SIMULATION & EXECUTION LAYER
# FILE: Scripts/engine_sim.py
# ROLE: Production Inference Core (XGBoost 6-Dim Feature Mapping & Skew-Normal Engine)
# =================================================================================================

import os
import json
import re
import numpy as np
import pandas as pd
from scipy.stats import norm
from datetime import datetime

try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False
    print("[WARNING] xgboost library not found. Defaulting to Tier 2 Telemetry Fallback.")

class HighFidelityNameSanitizer:
    @staticmethod
    def sanitize(name_obj):
        if pd.isna(name_obj): return ""
        clean = str(name_obj).upper().strip()
        clean = re.sub(r"[.\s'\-]+", "", clean)
        return clean

class Sentinel_Production_Apex:
    def __init__(self):
        # --- DYNAMIC ENVIRONMENT & PATH RESILIENCE ---
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.getenv('BASE_DIR', os.path.dirname(script_dir) if os.path.basename(script_dir) in ['Scripts', 'Script', 'Core', 'process', 'ingestion'] else script_dir)
        
        self.props_path = os.path.join(self.base_dir, "Prop Master", "player_prop_master.csv")
        
        # --- DYNAMIC TIMESTAMP FILE NAMING ---
        current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.slate_path = os.path.join(self.base_dir, "Logs", "Simulations", f"sim_{current_timestamp}.csv")
        
        self.context_path = os.path.join(self.base_dir, "Models", "macro_game_context.json")
        self.intel_path = os.path.join(self.base_dir, "Logs", "QUANTUM_STABILIZED_INTEL.csv")
        self.injury_path = os.path.join(self.base_dir, "Logs", "Injury_report.csv")
        
        self.brain_paths = {
            'PTS': os.path.join(self.base_dir, "Models", "omega_actual_pts_brain.json"),
            'AST': os.path.join(self.base_dir, "Models", "omega_actual_ast_brain.json"),
            'REB': os.path.join(self.base_dir, "Models", "omega_actual_reb_brain.json")
        }
        
        self.scratched_keys = set()
        self.biomechanical_penalties = {}
        self.quantum_intel_db = {}
        self.xgb_models = {}
        self.macro_context = {}

        self.MATCHUP_ROTATION_PROFILES = {
            "SMALL_BALL": {"MILES MCBRIDE": 1.25, "LUKE KORNET": 0.60, "KELDON JOHNSON": 1.15},
            "STANDARD_HEAVY": {"MILES MCBRIDE": 0.90, "LUKE KORNET": 1.10, "KELDON JOHNSON": 0.95}
        }

    def initialize_workspace_telemetry(self):
        print("[*] Initializing Sentinel Apex Telemetry Maps...")
        
        # 1. Ingest Macro Game Context
        if os.path.exists(self.context_path):
            with open(self.context_path, 'r') as f:
                self.macro_context = json.load(f)
            print("[+] Macro Game Context Synced.")
        else:
            print("[-] Macro Context missing. Resorting to neutral baseline.")

        # 2. Ingest Injury Ledger (Scratches & Minutes Restrictions)
        if os.path.exists(self.injury_path):
            inj_df = pd.read_csv(self.injury_path)
            for _, row in inj_df.iterrows():
                p_clean = HighFidelityNameSanitizer.sanitize(row.get('PLAYER_NAME', ''))
                status = str(row.get('STATUS', '')).upper()
                if status == 'OUT':
                    self.scratched_keys.add(p_clean)
                elif status in ['QUESTIONABLE', 'MINUTES_RESTRICTION']:
                    self.biomechanical_penalties[p_clean] = 0.85 

        # 3. Ingest 6-Dim Quantum Intelligence
        if os.path.exists(self.intel_path):
            intel_df = pd.read_csv(self.intel_path)
            intel_df.columns = [str(c).strip().upper() for c in intel_df.columns]
            for _, row in intel_df.iterrows():
                p_name = HighFidelityNameSanitizer.sanitize(row.get('PLAYER_NAME', ''))
                self.quantum_intel_db[p_name] = {
                    'USG_PCT_STABLE': float(row.get('USG_PCT_STABLE', 0.20)),
                    'PACE_STABLE': float(row.get('PACE_STABLE', 100.0)),
                    'PRE_DIST_RATIO': float(row.get('PRE_DIST_RATIO', 0.15)),
                    'WHISTLE_MULTIPLIER': float(row.get('WHISTLE_MULTIPLIER', 1.0)),
                    'QSQ_DELTA': float(row.get('QSQ_DELTA', 0.03)),
                    'WORK_CAPACITY_SIGMA': float(row.get('WORK_CAPACITY_SIGMA', 8.2)),
                    'TEAM_ABBR': str(row.get('TEAM_ABBR', 'UNK')).upper()
                }

        # 4. Mount XGBoost Sub-Brains
        if XGB_AVAILABLE:
            for market, path in self.brain_paths.items():
                if os.path.exists(path):
                    try:
                        bst = xgb.Booster()
                        bst.load_model(path)
                        self.xgb_models[market] = bst
                        print(f"[+] Mounted Neural Sub-Brain: {market}")
                    except Exception as e:
                        print(f"[-] Sub-Brain abort for {market}: {e}")

    def skew_normal_cdf(self, target, mean, std, skew):
        """Calculates cumulative probability mapping standard normal against skew drift."""
        z = (target - mean) / max(0.1, std)
        return norm.cdf(z) - 2 * (0.5 * norm.cdf(z) * (1.0 - norm.cdf(skew * z)))

    def run_high_fidelity_simulation(self):
        if not os.path.exists(self.props_path): 
            print(f"[ERROR] Props master database not found at: {self.props_path}")
            return
            
        props_df = pd.read_csv(self.props_path)
        sim_results = []
        
        coaching_context = self.macro_context.get("lineup_context", "STANDARD_HEAVY")
        defensive_multipliers = self.macro_context.get("defensive_efficiency_multiplier", {})
        
        for _, row in props_df.iterrows():
            raw_name = str(row.get('Player', ''))
            p_clean = HighFidelityNameSanitizer.sanitize(raw_name)
            market_raw = str(row.get('Prop_Type', '')).upper().strip()
            
            # Map standard sportsbook terms or direct internal models
            m_clean = 'PTS' if any(x in market_raw for x in ['POINT', 'PTS']) else \
                      'AST' if any(x in market_raw for x in ['ASSIST', 'AST']) else \
                      'REB' if any(x in market_raw for x in ['REBOUND', 'REB']) else None
                      
            if p_clean in self.scratched_keys or not m_clean: continue
            
            try:
                milestone = float(row.get('Milestone_Value', 0.0))
            except ValueError:
                continue

            base_profile = self.quantum_intel_db.get(p_clean, None)
            if not base_profile: continue

            mean_val = None
            brain_matched = False
            
            # --- [XGBOOST 6-DIMENSIONAL EXECUTION] ---
            if m_clean in self.xgb_models:
                try:
                    bst = self.xgb_models[m_clean]
                    features = [
                        base_profile['USG_PCT_STABLE'],
                        base_profile['PACE_STABLE'],
                        base_profile['PRE_DIST_RATIO'],
                        base_profile['WHISTLE_MULTIPLIER'],
                        base_profile['QSQ_DELTA'],
                        base_profile['WORK_CAPACITY_SIGMA']
                    ]
                    
                    feature_array = np.array([features])
                    dmatrix = xgb.DMatrix(feature_array, feature_names=['USG_PCT_STABLE', 'PACE_STABLE', 'PRE_DIST_RATIO', 'WHISTLE_MULTIPLIER', 'QSQ_DELTA', 'WORK_CAPACITY_SIGMA'])
                    
                    mean_val = float(bst.predict(dmatrix)[0])
                    brain_matched = True
                except Exception:
                    pass

            if not brain_matched or mean_val is None:
                continue

            # Target Variance Mapping
            std_val = max(1.5, mean_val * 0.25)
            skew_val = 0.5 

            # Apply Macro Environment Defensive Taxes
            opposing_defense = defensive_multipliers.get(base_profile['TEAM_ABBR'], 1.0)
            mean_val *= opposing_defense

            # Usage Vacuum & Biomechanical Adjustments
            if base_profile['USG_PCT_STABLE'] < 0.21:
                rotation_contractor = float(self.macro_context.get("bench_minutes_contractor", 0.50))
                mean_val *= rotation_contractor
                std_val *= 1.35 
                
            if p_clean in self.biomechanical_penalties:
                mean_val *= self.biomechanical_penalties[p_clean]
                std_val *= 1.15
                
            if coaching_context in self.MATCHUP_ROTATION_PROFILES and raw_name.upper().strip() in self.MATCHUP_ROTATION_PROFILES[coaching_context]:
                mean_val *= self.MATCHUP_ROTATION_PROFILES[coaching_context][raw_name.upper().strip()]

            # Execute Probability Calculation
            prob_raw = (1.0 - self.skew_normal_cdf(milestone - 0.5, mean_val, std_val, skew_val)) * 100
            prob = round(max(0.01, min(99.99, prob_raw)), 2)
            
            action = "BUY OVER" if prob >= 65.0 else ("BUY UNDER" if prob <= 35.0 else "PASS")
            
            sim_results.append({
                "Player": raw_name, 
                "Market": market_raw, 
                "Milestone": milestone, 
                "Expected_Target": round(mean_val, 2),
                "Omega_Probability_%": prob, 
                "Action": action
            })
            
        output_df = pd.DataFrame(sim_results)
        os.makedirs(os.path.dirname(self.slate_path), exist_ok=True)
        
        if not output_df.empty:
            output_df = output_df.sort_values(by="Omega_Probability_%", ascending=False)
            output_df.to_csv(self.slate_path, index=False, encoding='utf-8-sig')
            
            print("=================================================================")
            print(f"[SUCCESS] Apex Simulation Execution Complete.")
            print(f"-> Generated {len(output_df)} calibrated predictions.")
            print(f"-> Exported to: {self.slate_path}")
            print("=================================================================")
        else:
            print("[WARNING] Simulation returned zero valid permutations. Check player names in prop master vs intel dataset.")

if __name__ == "__main__":
    apex = Sentinel_Production_Apex()
    apex.initialize_workspace_telemetry()
    apex.run_high_fidelity_simulation()