#!/usr/bin/env python3
# =================================================================================================
# NBA Logic Engine — Production Inference Script
# PIPELINE EVOLUTION: XGBOOST NEURAL SUB-BRAIN ACTIVATION & SKEW-NORMAL ARCHITECTURE
# =================================================================================================

import os
import json
import re
import numpy as np
import pandas as pd
from scipy.stats import norm

# Safe XGBoost initialization
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False
    print("[⚠️ WARNING] xgboost library not found in environment. Defaulting to Tier 2 Telemetry Fallback.")

class HighFidelityNameSanitizer:
    @staticmethod
    def sanitize(name_obj):
        if pd.isna(name_obj): return ""
        clean = str(name_obj).upper().strip()
        clean = re.sub(r"[.\s'\-]+", "", clean)
        return clean

class Sentinel_Production_Apex:
    def __init__(self):
        # PORTABLE PATH ARBITRATION (Works on any machine or WSL2 environment)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.dirname(script_dir) if os.path.basename(script_dir) in ['Script', 'Core', 'process', 'ingestion'] else script_dir
        
        self.props_path = os.path.join(self.base_dir, "Prop Master/player_prop_master.csv")
        self.slate_path = os.path.join(self.base_dir, "Logs/Simulations/V41_MASTER_SLATE.csv")
        self.context_path = os.path.join(self.base_dir, "Models/macro_game_context.json")
        self.intel_path = os.path.join(self.base_dir, "Logs/QUANTUM_STABILIZED_INTEL.csv")
        self.playoff_telemetry_path = os.path.join(self.base_dir, "Logs/PLAYOFFS_MASTER_TELEMETRY.csv")
        self.injury_path = os.path.join(self.base_dir, "Logs/Injury_report.csv")
        self.referee_path = os.path.join(self.base_dir, "Logs/Referee_Tracker_V2.csv")
        
        self.brain_paths = {
            'PTS': os.path.join(self.base_dir, "Models/omega_actual_pts_brain.json"),
            'AST': os.path.join(self.base_dir, "Models/omega_actual_ast_brain.json"),
            'REB': os.path.join(self.base_dir, "Models/omega_actual_reb_brain.json"),
            '3P_MADE': os.path.join(self.base_dir, "Models/omega_actual_3pm_brain.json")
        }
        
        self.scratched_keys = set()
        self.biomechanical_penalties = {}
        self.telemetry_fallback_db = {}
        self.playoff_telemetry_db = {}
        self.xgb_models = {}
        self.macro_context = {}
        self.referee_modifiers = {}

        self.MATCHUP_ROTATION_PROFILES = {
            "SMALL_BALL": {"MILES MCBRIDE": 1.25, "LUKE KORNET": 0.60, "KELDON JOHNSON": 1.15, "DYLAN HARPER": 1.00, "MITCHELL ROBINSON": 0.70},
            "STANDARD_HEAVY": {"MILES MCBRIDE": 0.90, "LUKE KORNET": 1.10, "KELDON JOHNSON": 0.95, "DYLAN HARPER": 1.05, "MITCHELL ROBINSON": 1.20}
        }

    def initialize_workspace_telemetry(self):
        print("[*] Initiating Full-Spectrum XGBoost Predictive Ingress Protocol...")
        
        if os.path.exists(self.context_path):
            with open(self.context_path, 'r', encoding='utf-8') as f:
                self.macro_context = json.load(f)
                
        if os.path.exists(self.injury_path):
            inj_df = pd.read_csv(self.injury_path)
            for _, row in inj_df.iterrows():
                p_name = HighFidelityNameSanitizer.sanitize(row.get('PLAYER_NAME', ''))
                status = str(row.get('STATUS', '')).upper()
                reason = str(row.get('REASON', '')).upper()
                if 'OUT' in status or 'SCRATCH' in status:
                    self.scratched_keys.add(p_name)
                elif "FRACTURED" in reason or "ILLNESS" in reason:
                    self.biomechanical_penalties[p_name] = 0.65 

        if os.path.exists(self.referee_path):
            ref_df = pd.read_csv(self.referee_path)
            for _, row in ref_df.iterrows():
                ref_name = str(row.get('Referee', row.get('Crew Chief', ''))).upper().strip()
                self.referee_modifiers[ref_name] = {
                    'PTS': float(row.get('PTS_Modifier', 1.0)), 'AST': float(row.get('AST_Modifier', 1.0)),
                    'REB': float(row.get('REB_Modifier', 1.0)), '3P_MADE': float(row.get('3PM_Modifier', 1.0))
                }

        if os.path.exists(self.intel_path):
            intel_df = pd.read_csv(self.intel_path)
            intel_df.columns = [c.strip().upper() for c in intel_df.columns]
            name_col = next((c for c in ['PLAYER_NAME', 'PLAYER', 'NAME'] if c in intel_df.columns), 'PLAYER_NAME')
            for _, row in intel_df.iterrows():
                p_name = HighFidelityNameSanitizer.sanitize(row[name_col])
                self.telemetry_fallback_db[p_name] = {
                    'PTS': float(row.get('PTS_STABLE', 10.0)),
                    'AST': float(row.get('AST_STABLE', 3.0)),
                    'REB': float(row.get('REB_STABLE', 4.0)),
                    'USG': float(row.get('USG_PCT_STABLE', 0.20)),
                    'PRE_DIST_RATIO': float(row.get('PRE_DIST_RATIO', 1.0)),
                    'PACE_STABLE': float(row.get('PACE_STABLE', 96.0)),
                    'WHISTLE_RESISTANCE': float(row.get('WHISTLE_RESISTANCE', row.get('WHISTLE_MULTIPLIER', 1.0)))
                }

        if os.path.exists(self.playoff_telemetry_path):
            playoff_df = pd.read_csv(self.playoff_telemetry_path)
            playoff_df.columns = [c.strip().upper() for c in playoff_df.columns]
            for _, row in playoff_df.iterrows():
                p_name = HighFidelityNameSanitizer.sanitize(row.get('PLAYER_NAME', ''))
                self.playoff_telemetry_db[p_name] = {
                    'PTS': float(row.get('PTS_BASE', 0.0)), 'AST': float(row.get('AST_BASE', 0.0)),
                    'REB': float(row.get('REB_BASE', 0.0)), '3P_MADE': float(row.get('FG3M_BASE', 0.0))
                }

        if XGB_AVAILABLE:
            for market, path in self.brain_paths.items():
                if os.path.exists(path):
                    try:
                        bst = xgb.Booster()
                        bst.load_model(path)
                        self.xgb_models[market] = bst
                        print(f"[+] Loaded XGBoost Brain Node for {market}")
                    except Exception as e:
                        print(f"[-] Sub-Brain abort for {market}: {e}")

    def skew_normal_cdf(self, x, mean, std, skew):
        z = (x - mean) / std
        return norm.cdf(z) - 2 * (0.5 * norm.cdf(z) * (1.0 - norm.cdf(skew * z)))

    def run_high_fidelity_simulation(self):
        if not os.path.exists(self.props_path): 
            print(f"[WARNING] Props master database not found at: {self.props_path}")
            return
            
        props_df = pd.read_csv(self.props_path)
        sim_results = []
        
        pace_factor = float(self.macro_context.get("referee_pace_factor", 96.2))
        pace_modifier = pace_factor / 98.2
        coaching_context = self.macro_context.get("lineup_context", "STANDARD_HEAVY")
        assigned_ref = str(self.macro_context.get("assigned_referee", "")).upper().strip()
        
        for _, row in props_df.iterrows():
            raw_name = row['Player']
            market_raw = row['Prop_Type']
            milestone = float(row['Milestone_Value'])
            p_clean = HighFidelityNameSanitizer.sanitize(raw_name)
            m_clean = str(market_raw).upper().strip().replace('3PM', '3P_MADE')
            
            if p_clean in self.scratched_keys:
                sim_results.append({"Player": raw_name, "Market": market_raw, "Milestone": milestone, "Omega_ %": 0.0, "Action": "PASS"})
                continue
                
            mean_val, brain_matched = None, False
            base_profile = self.telemetry_fallback_db.get(p_clean, {'PTS': 10.0, 'AST': 3.0, 'REB': 4.0, 'USG': 0.20, 'PRE_DIST_RATIO': 1.0, 'PACE_STABLE': 96.0, 'WHISTLE_RESISTANCE': 1.0})
            player_usage = base_profile.get('USG', 0.20)
            
            std_map = {'PTS': 4.5, 'AST': 1.8, 'REB': 2.5, '3P_MADE': 0.8}
            std_val = std_map.get(m_clean, 2.0)

            if XGB_AVAILABLE and m_clean in self.xgb_models and p_clean in self.telemetry_fallback_db:
                try:
                    bst = self.xgb_models[m_clean]
                    features = np.array([[base_profile['PRE_DIST_RATIO'], base_profile['USG'], base_profile['PACE_STABLE'], base_profile['WHISTLE_RESISTANCE']]])
                    dmatrix = xgb.DMatrix(features)
                    mean_val = float(bst.predict(dmatrix)[0])
                    brain_matched = True
                except Exception:
                    pass

            if not brain_matched or mean_val is None:
                if p_clean in self.playoff_telemetry_db and m_clean in self.playoff_telemetry_db[p_clean]:
                    mean_val = self.playoff_telemetry_db[p_clean][m_clean] * 0.94
                else:
                    mean_val = base_profile.get(m_clean if m_clean != '3P_MADE' else 'PTS', 5.0)
            
            skew_val = 1.5 if m_clean in ['PTS', 'AST'] else 0.5
            mean_val *= pace_modifier
            
            if assigned_ref in self.referee_modifiers and m_clean in self.referee_modifiers[assigned_ref]:
                ref_mod = self.referee_modifiers[assigned_ref][m_clean]
                mean_val *= ref_mod
                std_val *= (1.05 if ref_mod > 1.0 else 0.98) 
            
            if player_usage < 0.21:
                rotation_contractor = float(self.macro_context.get("bench_minutes_contractor", 0.50))
                mean_val *= rotation_contractor
                std_val *= 1.35 
                
            if p_clean in self.biomechanical_penalties:
                mean_val *= self.biomechanical_penalties[p_clean]
                std_val *= 1.15
                
            if coaching_context in self.MATCHUP_ROTATION_PROFILES and raw_name.upper().strip() in self.MATCHUP_ROTATION_PROFILES[coaching_context]:
                mean_val *= self.MATCHUP_ROTATION_PROFILES[coaching_context][raw_name.upper().strip()]

            prob_raw = (1.0 - self.skew_normal_cdf(milestone - 0.5, mean_val, std_val, skew_val)) * 100
            prob = round(max(0.01, min(99.99, prob_raw)), 2)
            
            action = "BUY" if prob >= 65.0 else "PASS"
            sim_results.append({"Player": raw_name, "Market": market_raw, "Milestone": milestone, "Omega_ %": prob, "Action": action})
            
        output_df = pd.DataFrame(sim_results)
        os.makedirs(os.path.dirname(self.slate_path), exist_ok=True)
        output_df.to_csv(self.slate_path, index=False)
        print(f"✅ Master simulation complete. Highly successful slates written to: {self.slate_path}")

if __name__ == "__main__":
    engine = Sentinel_Production_Apex()
    engine.initialize_workspace_telemetry()
    engine.run_high_fidelity_simulation()