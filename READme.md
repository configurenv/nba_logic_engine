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

### **August 7, 2026**
* **Automated File Naming:** Prediction files are now automatically saved with the exact date and time they were generated so old files aren't overwritten.
* **Better Player Tracking:** The engine now understands player movement and workload on the court much better, making our points, assists, and rebounds predictions more accurate.
* **Realistic Odds & Overconfidence Fix:** Implemented mathematical safety limits (capping stacked modifiers and clamping maximum probability boundaries between 5.5% and 94.5%) so predictions no longer generate unrealistic 99.9% locks.
* **Clean Folder Structure:** Reorganized the entire project into four easy-to-use phases: data gathering, cleaning, model training, and final simulations. 
* **Backtesting Added:** Added new tools to run our models against full past seasons to see exactly how well our strategies would have performed historically.

**Updated Pipeline Order:**
Run the following script sequence sequentially from your project root directory:

# Step 1: Data Gathering (The Harvesters)
```bash
python3 ingestion/extract_player_stats.py
python3 ingestion/extract_play_by_play.py
python3 ingestion/generate_season_prop_master.py
```

# Step 2: Data Cleaning (The Refinery)
```bash

python3 process/audit_league_forensics.py
python3 process/macro_game_brain.py
python3 process/prepare_quantum_intel.py
python3 process/situational_moments_brain.py
python3 process/prop.py
python3 process/train_prop_models.py
```

# Step 3: Model Training (The Brains)
```bash
python3 Core/ensemble.py
python3 Core/metadata_sync.py
python3 Core/update_train.py
python3 Core/update_referee_tracker.py
```

# Step 4: Simulations & Backtesting (The Executioners)
```bash
python3 Scripts/engine_sim.py
python3 Scripts/full_season_backtest.py
```
