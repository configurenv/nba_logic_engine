#!/usr/bin/env python3
# =================================================================================================
# NBA Logic Engine — Utility Layer
# FILE: utils/forensic_audit_tool.py
# ARCHITECTURAL INTEGRATION: Non-Linear Rotation Expectancy Overlays & Live Copula Arrays
# =================================================================================================

import os
import json
import re
import numpy as np
from scipy.stats import norm

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

# --- PORTABLE PATH ARBITRATION ---
script_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(script_dir) if os.path.basename(script_dir) in ['Script', 'Core', 'process', 'ingestion', 'utils'] else script_dir

STAGING_FILE = os.path.join(BASE_DIR, "Logs", "ALL_PLAYS_RAW_STAGING.json")
SLIP_FILE = os.path.join(BASE_DIR, "active_slip.json")
GAME_ID = "401859965"  # Target Finals Game ID matching macro context

# High-Fidelity Base Projections (Pace Factor & Biomechanical Modulus Adjustments Applied)
BASE_PROJECTIONS = {
    "MILES MCBRIDE": {"PTS": 11.45, "std": 2.10},
    "LUKE KORNET": {"REB": 4.85, "std": 1.48},
    "KELDON JOHNSON": {"REB": 5.12, "std": 1.55},
    "DYLAN HARPER": {"AST": 3.75, "std": 1.28},
    "MITCHELL ROBINSON": {"REB": 5.72, "std": 1.62}
}

# Elite Rotation Calibration Maps (Percentage of expected total production distributed per quarter)
ROTATION_EXPECTANCY_CURVES = {
    "MILES MCBRIDE":    [0.05, 0.25, 0.35, 0.35], 
    "LUKE KORNET":      [0.20, 0.30, 0.20, 0.30], 
    "KELDON JOHNSON":   [0.15, 0.35, 0.25, 0.25], 
    "DYLAN HARPER":     [0.30, 0.20, 0.30, 0.20], 
    "MITCHELL ROBINSON": [0.35, 0.15, 0.35, 0.15]  
}

def parse_live_pbp_stream():
    stats = {p: {"PTS": 0, "REB": 0, "AST": 0} for p in BASE_PROJECTIONS.keys()}
    game_clock_seconds_remaining = 2880  # 48 minutes baseline
    
    if not os.path.exists(STAGING_FILE):
        return stats, game_clock_seconds_remaining
        
    with open(STAGING_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception:
            return stats, game_clock_seconds_remaining

    game_data = data.get(GAME_ID, {})
    plays = game_data.get("plays", [])
    
    for play in plays:
        text = play.get('text', play.get('description', ''))
        if not text:
            continue
        text_upper = text.upper()
        
        raw_period = play.get('period', 1)
        if isinstance(raw_period, dict):
            period = int(raw_period.get('number', 1))
        else:
            try:
                period = int(raw_period)
            except (TypeError, ValueError):
                period = 1
                
        raw_clock = play.get('clock', {})
        if isinstance(raw_clock, dict):
            clock_str = raw_clock.get('displayValue', '12:00')
        else:
            clock_str = play.get('clock', '12:00')
            
        time_match = re.search(r"(\d+):(\d+)", str(clock_str))
        if time_match:
            mins, secs = map(int, time_match.groups())
            current_quarter_seconds_left = (mins * 60) + secs
            
            if period <= 4:
                game_clock_seconds_remaining = ((4 - period) * 720) + current_quarter_seconds_left
            else:
                game_clock_seconds_remaining = max(0, current_quarter_seconds_left)

        for player in stats.keys():
            last_name = player.split()[-1].upper()
            
            if last_name in text_upper:
                if "MAKES" in text_upper or "SINKS" in text_upper:
                    if "THREE-POINT" in text_upper or "3-POINTER" in text_upper:
                        if last_name in text_upper.split("MAKES")[0] or last_name in text_upper.split("SINKS")[0]:
                            stats[player]["PTS"] += 3
                    elif "FREE THROW" in text_upper:
                        if last_name in text_upper.split("MAKES")[0] or last_name in text_upper.split("SINKS")[0]:
                            stats[player]["PTS"] += 1
                    else:
                        if last_name in text_upper.split("MAKES")[0] or last_name in text_upper.split("SINKS")[0]:
                            stats[player]["PTS"] += 2
                            
                assist_match = re.search(rf"\({last_name}\s+ASSIST[S]?\)", text_upper)
                if assist_match or f"ASSIST BY {last_name}" in text_upper:
                    stats[player]["AST"] += 1
                        
                if "REBOUND" in text_upper:
                    if "TEAM REBOUND" not in text_upper:
                        if f"{last_name} DEFENSIVE" in text_upper or f"{last_name} OFFENSIVE" in text_upper or f"{last_name} REBOUND" in text_upper:
                            stats[player]["REB"] += 1
                        elif "DEFENSIVE REBOUND" in text_upper or "OFFENSIVE REBOUND" in text_upper:
                            stats[player]["REB"] += 1
                            
    return stats, game_clock_seconds_remaining

def compute_live_success_rate():
    if not os.path.exists(SLIP_FILE):
        print(f"{Colors.YELLOW}⚠️ NOTICE: active_slip.json manifest missing at {SLIP_FILE}.{Colors.RESET}")
        print(f"ℹ️ Create an active_slip.json file in your project root to audit live parlay legs.")
        return
        
    with open(SLIP_FILE, 'r', encoding='utf-8') as f:
        slip = json.load(f)
        
    current_stats, seconds_left = parse_live_pbp_stream()
    
    if seconds_left > 2160: current_quarter = 1
    elif seconds_left > 1440: current_quarter = 2
    elif seconds_left > 720: current_quarter = 3
    else: current_quarter = 4
    
    quarter_elapsed_seconds = 720 - (seconds_left % 720 if seconds_left % 720 != 0 else 720)
    quarter_time_remaining_ratio = (720 - quarter_elapsed_seconds) / 720
    
    print(f"\n{Colors.CYAN}{'='*120}")
    print(f" LIVE FINALS MULTI-VARIABLE PARLAY AUDIT CORE: NON-LINEAR ROTATION PATTERN MATCHING")
    print(f" TIME LOGIC PROGRESSION: {int(seconds_left // 60)}m {int(seconds_left % 60)}s SECONDS REMAINING | ACTIVE PERIOD: Q{current_quarter}")
    print(f"{'='*120}{Colors.RESET}")
    print(f"{'PLAYER NAME':<22} | {'MARKET':<6} | {'TARGET':<8} | {'CURRENT':<8} | {'CALIBRATED REM':<15} | {'LIVE Ω %':<10} | {'STATUS'}")
    print("-" * 120)
    
    individual_probabilities = []
    
    for player, config in slip.items():
        market = config["market"]
        target = config["milestone"]
        current = current_stats.get(player, {}).get(market, 0)
        
        base_mean = BASE_PROJECTIONS.get(player, {}).get(market, 10.0)
        base_std = BASE_PROJECTIONS.get(player, {}).get("std", 2.0)
        
        distribution_curve = ROTATION_EXPECTANCY_CURVES.get(player, [0.25, 0.25, 0.25, 0.25])
        
        remaining_volume_weight = 0.0
        for q_idx in range(current_quarter - 1, 4):
            if q_idx == current_quarter - 1:
                remaining_volume_weight += distribution_curve[q_idx] * quarter_time_remaining_ratio
            else:
                remaining_volume_weight += distribution_curve[q_idx]
                
        live_projected_remaining_mean = base_mean * remaining_volume_weight
        live_projected_remaining_std = base_std * np.sqrt(max(0.05, remaining_volume_weight))
        
        live_total_expected_mean = current + live_projected_remaining_mean
        
        if current >= target:
            live_prob = 100.0
            status = f"{Colors.GREEN}✅ LEG COVERED{Colors.RESET}"
        elif seconds_left <= 0:
            live_prob = 0.0
            status = f"{Colors.RED}❌ FAILED{Colors.RESET}"
        else:
            z_score = (target - 0.5 - live_total_expected_mean) / max(0.1, live_projected_remaining_std)
            raw_prob = (1.0 - norm.cdf(z_score)) * 100
            
            if raw_prob > 99.0: live_prob = 99.0
            elif raw_prob < 1.0: live_prob = 1.0
            else: live_prob = round(raw_prob, 2)
            
            if live_prob >= 75.0: status = f"{Colors.GREEN}📈 STABLE BUY{Colors.RESET}"
            elif live_prob >= 40.0: status = f"{Colors.YELLOW}⏳ TRACKING{Colors.RESET}"
            else: status = f"{Colors.RED}📉 RISK VECTOR{Colors.RESET}"
            
        individual_probabilities.append(live_prob / 100.0)
        print(f"{player:<22} | {market:<6} | {target:<8.1f} | {current:<8.1f} | {live_projected_remaining_mean:<15.2f} | {str(live_prob)+' %':<10} | {status}")
        
    print("-" * 120)
    
    if individual_probabilities:
        joint_success_rate = np.prod(individual_probabilities) * 100
    else:
        joint_success_rate = 0.0
    
    if joint_success_rate >= 62.0:
        portfolio_status = f"{Colors.GREEN}🟢 HIGH INTEGRITY MATRIX ({joint_success_rate:.2f}% JOINT EXPECTANCY){Colors.RESET}"
    elif joint_success_rate >= 35.0:
        portfolio_status = f"{Colors.YELLOW}🟡 LIVE MARGIN TRACKING ({joint_success_rate:.2f}% JOINT EXPECTANCY){Colors.RESET}"
    else:
        portfolio_status = f"{Colors.RED}🔴 CRITICAL SKEW DETECTED ({joint_success_rate:.2f}% JOINT EXPECTANCY){Colors.RESET}"
        
    print(f"🎯 PORTFOLIO MANAGEMENT SYSTEM STATUS: {portfolio_status}")
    print(f"{Colors.CYAN}{'='*120}{Colors.RESET}\n")

if __name__ == "__main__":
    compute_live_success_rate()