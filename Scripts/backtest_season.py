#!/usr/bin/env python3
# =================================================================================================
# NBA LOGIC ENGINE — BACKTESTING & FULL SEASON SIMULATION MODULE
# =================================================================================================

import os
import pandas as pd
import numpy as np
from scipy.stats import norm

def run_full_season_simulation():
    print("[*] Initializing Full-Season 2025-2026 Backtest Simulation...")
    
    # 1. Load historical forensic game logs (Actual player performances)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(base_dir, "Logs")
    game_logs_path = os.path.join(logs_dir, "Forensic_Game_Logs.csv")
    prop_master_path = os.path.join(base_dir, "Prop Master", "player_prop_master.csv")
    
    if not os.path.exists(game_logs_path) or not os.path.exists(prop_master_path):
        print("[ERROR] Required logs or prop master missing for full-season backtest.")
        return
        
    logs_df = pd.read_csv(game_logs_path, low_memory=False)
    props_df = pd.read_csv(prop_master_path)
    
    backtest_results = []
    
    # 2. Iterate through historical games and evaluate model accuracy vs actuals
    for _, prop in props_df.iterrows():
        player = prop['Player']
        market = prop['Prop_Type']
        milestone = float(prop['Milestone_Value'])
        
        # Filter actual game logs for this player
        player_games = logs_df[logs_df['PLAYER_NAME'].str.upper() == player.upper()]
        if player_games.empty:
            continue
            
        market_col_map = {'PTS': 'PTS', 'REB': 'REB', 'AST': 'AST', '3P_MADE': 'FG3M'}
        true_col = market_col_map.get(market, 'PTS')
        
        if true_col not in player_games.columns:
            continue
            
        # Simulate across games
        for _, game in player_games.iterrows():
            actual_val = float(game.get(true_col, 0))
            
            # Model expectation baseline
            mean_val = player_games[true_col].mean()
            std_val = player_games[true_col].std() if len(player_games) > 1 else 2.0
            std_val = max(1.0, std_val)
            
            # Probability calculation using skew-normal framework
            z_score = (milestone - 0.5 - mean_val) / std_val
            prob = round((1.0 - norm.cdf(z_score)) * 100, 2)
            
            hit = 1 if actual_val >= milestone else 0
            
            backtest_results.append({
                "Game_ID": game.get('GAME_ID', 'N/A'),
                "Player": player,
                "Market": market,
                "Milestone": milestone,
                "Actual_Value": actual_val,
                "Model_Probability": prob,
                "Hit_Status": hit
            })
            
    backtest_df = pd.DataFrame(backtest_results)
    output_report_path = os.path.join(logs_dir, "Full_Season_Backtest_Report.csv")
    backtest_df.to_csv(output_report_path, index=False, encoding='utf-8-sig')
    print(f"[SUCCESS] Full-season simulation complete. Report locked to: {output_report_path}")

if __name__ == "__main__":
    run_full_season_simulation()