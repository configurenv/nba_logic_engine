# NBA Logic Engine

## About the Project
The NBA Logic Engine is an automated tracking and analysis system built to understand basketball games at a deeper level. It collects raw game data, processes player statistics, and applies custom logic rules to see how physical effort, game situations, and court locations affect player performance. The goal of this project is to turn basic box scores into a reliable, step-by-step system for analyzing how the game is actually played.

## Changelog & Additions

**August 1, 2026**
* initial data collection script to pull in raw play-by-play game information...

**Last Updated: August 2, 2026**

Run the following script sequence sequentially from your project root directory:

### Step 1: Ingest Raw Telemetry & Play-by-Play Data
Harvest baseline player box scores, advanced tracking splits, and play-by-play event logs into local storage:
```bash
python3 ingestion/extract_player_stats.py
python3 ingestion/extract_play_by_play.py
```
### Step 2: Refine Quantum Intel, Macro Context & Officiating Trackers
Process raw telemetry to stabilize feature variance, compile live game contexts, and dynamically sync referee pacing and whistle multipliers:
```bash
python3 process/prepare_quantum_intel.py
python3 process/macro_game_brain.py
python3 process/situational_moments_brain.py
python3 process/audit_league_forensics.py
python3 update_referee_tracker.py
```

Output Artifacts: Generates Logs/QUANTUM_STABILIZED_INTEL.csv, Models/macro_game_context.json, and Models/omega_situational_moments_brain.json,and synchronizes Logs/Referee_Tracker_V2.csv

### Step 3: Synchronize Metadata & Accumulate Training Labels
Harmonize spatial coordinates, play-by-play metadata, and lock down the multi-variable training ledger:

```bash
python3 Core/metadata_sync.py
python3 Core/update_train.py
```

Output Artifacts: Generates Logs/SENTINEL_ALPHA_MASTER_PBP.csv and locks records to Training_Data/V30_TRAINING_MASTER.csv.

### Step 4: Train ML Ensemble Sub-Brains
Run the gradient boosting trainer to output optimized vector prediction weight binaries:
```bash
python3 Core/ensemble.py
```

Output Artifacts: Exports trained sub-brain weights to Models/omega_actual_pts_brain.json, Models/omega_actual_ast_brain.json, and Models/omega_actual_reb_brain.json

### Step 5: Run Predictions & Generate Slates
Run your prediction script to simulate player props and write the results to your master slate file:
```bash
python3 Script/engine_sim.py
```
Output Artifacts: Generates Logs/Simulations/V41_MASTER_SLATE.csv.

### Step 6: Run Live Forensic Audits (Optional)
Run your audit tool to monitor live game quarters and check active parlay legs against real-time play-by-play data:
```bash
python3 utils/forensic_audit_tool.py
```
Output Artifacts: Prints real-time probability margins and portfolio statuses directly to your terminal.