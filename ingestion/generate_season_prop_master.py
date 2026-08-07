#!/usr/bin/env python3
# =================================================================================================
# NBA LOGIC ENGINE — COMPREHENSIVE PROP MASTER GENERATOR
# FILE: Script/generate_season_prop_master.py
# =================================================================================================

import os
import pandas as pd
import numpy as np

def generate_season_prop_master():
    print("=================================================================")
    print("     NBA LOGIC ENGINE: FULL SEASON PROP MASTER GENERATOR         ")
    print("=================================================================")
    
    # Portable path arbitration ensuring output lands in /nba_logic_engine/Prop Master/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir) if os.path.basename(script_dir) in ['Script', 'Core', 'process', 'ingestion', 'utils'] else script_dir
    
    prop_dir = os.path.join(base_dir, "Prop Master")
    prop_file_path = os.path.join(prop_dir, "player_prop_master.csv")
    telemetry_path = os.path.join(base_dir, "Logs", "REGULAR_SEASON_MASTER_TELEMETRY.csv")
    
    os.makedirs(prop_dir, exist_ok=True)
    
    prop_records = []
    
    if os.path.exists(telemetry_path):
        print(f"[INGRESS] Parsing master telemetry from: {telemetry_path}")
        tele_df = pd.read_csv(telemetry_path, low_memory=False)
        tele_df.columns = [c.strip().upper() for c in tele_df.columns]
        
        name_col = next((c for c in ['PLAYER_NAME', 'PLAYER', 'NAME'] if c in tele_df.columns), 'PLAYER_NAME')
        pts_col = next((c for c in ['PTS_STABLE', 'PTS', 'PTS_BASE'] if c in tele_df.columns), None)
        reb_col = next((c for c in ['REB_STABLE', 'REB', 'REB_BASE'] if c in tele_df.columns), None)
        ast_col = next((c for c in ['AST_STABLE', 'AST', 'AST_BASE'] if c in tele_df.columns), None)
        
        # Season segments to simulate performance variance over time
        season_segments = ["EARLY_SEASON", "ALL_STAR_BREAK", "LATE_SEASON"]
        
        for _, row in tele_df.iterrows():
            player_name = str(row.get(name_col, "")).strip().upper()
            if not player_name or player_name == "NAN":
                continue
                
            base_pts = float(row.get(pts_col, 10.0)) if pts_col and pd.notna(row.get(pts_col)) else 10.0
            base_reb = float(row.get(reb_col, 3.0)) if reb_col and pd.notna(row.get(reb_col)) else 3.0
            base_ast = float(row.get(ast_col, 2.0)) if ast_col and pd.notna(row.get(ast_col)) else 2.0
            
            # Generate multi-segment milestones and varying odds for simulation storytelling
            for segment in season_segments:
                # Add slight variance per segment to model hot/cold streaks and odds adjustments
                segment_multiplier = 1.05 if segment == "LATE_SEASON" else (0.95 if segment == "EARLY_SEASON" else 1.0)
                
                pts_milestone = round((base_pts * segment_multiplier) * 2) / 2
                reb_milestone = round((base_reb * segment_multiplier) * 2) / 2
                ast_milestone = round((base_ast * segment_multiplier) * 2) / 2
                
                prop_records.append({"Player": player_name, "Prop_Type": "PTS", "Milestone_Value": max(4.5, pts_milestone), "Season_Segment": segment})
                prop_records.append({"Player": player_name, "Prop_Type": "REB", "Milestone_Value": max(1.5, reb_milestone), "Season_Segment": segment})
                prop_records.append({"Player": player_name, "Prop_Type": "AST", "Milestone_Value": max(0.5, ast_milestone), "Season_Segment": segment})
    else:
        print("[WARNING] Telemetry master not found. Generating default fallback roster.")
        prop_records = [
            {"Player": "MILES MCBRIDE", "Prop_Type": "PTS", "Milestone_Value": 11.5, "Season_Segment": "LATE_SEASON"},
            {"Player": "LUKE KORNET", "Prop_Type": "REB", "Milestone_Value": 4.5, "Season_Segment": "LATE_SEASON"},
            {"Player": "KELDON JOHNSON", "Prop_Type": "REB", "Milestone_Value": 5.5, "Season_Segment": "LATE_SEASON"},
            {"Player": "DYLAN HARPER", "Prop_Type": "AST", "Milestone_Value": 3.5, "Season_Segment": "LATE_SEASON"},
            {"Player": "MITCHELL ROBINSON", "Prop_Type": "REB", "Milestone_Value": 5.5, "Season_Segment": "LATE_SEASON"}
        ]

    master_props_df = pd.DataFrame(prop_records).drop_duplicates()
    master_props_df.to_csv(prop_file_path, index=False, encoding='utf-8-sig')
    
    print("=================================================================")
    print(f"✅ Full Season Prop Master generated successfully.")
    print(f"-> Destination: {prop_file_path}")
    print(f"-> Total Multi-Segment Milestone Entries: {len(master_props_df)}")
    print("=================================================================")

if __name__ == "__main__":
    generate_season_prop_master()