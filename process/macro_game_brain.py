#!/usr/bin/env python3
# =================================================================================================
# NBA LOGIC ENGINE — PROCESS LAYER
# FILE: process/macro_game_brain.py
# ROLE: Real-Time Odds Ingress & Macro Game Context Compiler
# =================================================================================================

import os
import json
import datetime
import urllib.request

def run_macro_game_brain_compiler():
    print("[+] Launching Macro Game Context Compiler...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir) if os.path.basename(script_dir) in ['Core', 'process'] else script_dir
        
    models_dir = os.path.join(base_dir, "Models")
    output_context_path = os.path.join(models_dir, "macro_game_context.json")
    
    target_day = datetime.date(2026, 6, 13)
    current_date_str = target_day.strftime("%Y-%m-%d")
    
    target_espn_id = "401859967"
    target_nba_id = "0042500405"
    
    active_matchup = "NYK @ SAS"
    away_team = "NYK"
    home_team = "SAS"
    vegas_total = 209.6
    spread_margin = 0.5
    favorite_team = "SAS"
    
    assigned_referee = "SCOTT FOSTER"
    ref_pace_factor = 95.8
    scenario_mult = 1.04
    adjusted_target_pace = 95.8

    if favorite_team == home_team:
        predicted_score_home = (vegas_total + spread_margin) / 2.0
        predicted_score_away = vegas_total - predicted_score_home
    else:
        predicted_score_away = (vegas_total + spread_margin) / 2.0
        predicted_score_home = vegas_total - predicted_score_away

    context_payload = {
        "target_date": current_date_str,
        "matchup": active_matchup,
        "espn_game_id": target_espn_id,
        "nba_game_id": target_nba_id,
        "assigned_referee": assigned_referee,
        "referee_pace_factor": ref_pace_factor,
        "adjusted_target_pace": adjusted_target_pace,
        "whistle_multiplier": scenario_mult,
        "alpha_count": 3,
        "predicted_score": {
            away_team: round(predicted_score_away, 1),
            home_team: round(predicted_score_home, 1)
        },
        "quantum_total": vegas_total,
        "quantum_spread_margin": spread_margin,
        "favorite_side": favorite_team,
        "defensive_efficiency_multiplier": {
            away_team: 0.94,
            home_team: 0.93
        },
        "bench_minutes_contractor": 0.50,
        "lineup_context": "STANDARD_HEAVY"
    }
    
    os.makedirs(models_dir, exist_ok=True)
    with open(output_context_path, 'w', encoding='utf-8') as json_file:
        json.dump(context_payload, json_file, indent=4)
    print(f"[SUCCESS] Macro Game Context Matrix compiled -> {output_context_path}")

if __name__ == "__main__":
    run_macro_game_brain_compiler()