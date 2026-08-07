#!/usr/bin/env python3
# =================================================================================================
# NBA LOGIC ENGINE — INGESTION LAYER
# FILE: ingestion/injury_report.py
# ROLE: Live Injury Report PDF Ingress & Roster Vacuum Context
# =================================================================================================

import os
import re
import io
import urllib.request
import pandas as pd

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("[WARNING] pdfplumber library not found. Please install via: pip install pdfplumber")

class HighFidelityNameSanitizer:
    @staticmethod
    def sanitize(name_obj):
        if pd.isna(name_obj): return ""
        s = str(name_obj).upper().strip()
        anomalies = [".", "-", "'", "’", ",", " JR", " III", " II", "IV", "V"]
        for element in anomalies:
            s = s.replace(element, "")
        return " ".join(s.split())

class InjuryReportIngressor:
    def __init__(self):
        # --- DYNAMIC ENVIRONMENT & PATH RESILIENCE ---
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.getenv('BASE_DIR', os.path.dirname(script_dir) if os.path.basename(script_dir) in ['Scripts', 'Script', 'Core', 'process', 'ingestion', 'utils'] else script_dir)
        
        self.logs_dir = os.path.join(self.base_dir, "Logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        
        self.output_csv_path = os.path.join(self.logs_dir, "Injury_report.csv")
        self.index_url = "https://official.nba.com/nba-injury-report-2026-27-season/"
        
        # --- SANITIZED HEADERS FOR PUBLIC GITHUB ---
        # Note: Active session cookies removed for repository security. 
        # Inject fresh Akamai tokens locally during live season runs if temporarily blocked.
        self.request_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/pdf,*/*;q=0.8',
            'Connection': 'keep-alive',
        }

    def run_ingress(self):
        print("=================================================================")
        print("     NBA LOGIC ENGINE: LIVE INJURY REPORT INGRESS CORE           ")
        print("=================================================================")
        
        if not PDF_AVAILABLE:
            print("[ERROR] PDF Parsing Engine offline. Aborting extraction.")
            return

        latest_pdf_url = None
        parsed_entries = []

        try:
            print("[*] Connecting to Official Index to trace latest report iterations...")
            req = urllib.request.Request(self.index_url, headers=self.request_headers)
            with urllib.request.urlopen(req, timeout=12) as response:
                html_str = response.read().decode('utf-8', errors='ignore')
            
            pdf_patterns = re.findall(r'href="(https://ak-static.cms.nba.com/referee/injury/Injury-Report_[^"]+\.pdf)"', html_str)
            
            if pdf_patterns:
                latest_pdf_url = pdf_patterns[-1]
                print(f"[+] Isolated Active Live PDF Target: {os.path.basename(latest_pdf_url)}")
            else:
                raise ValueError("No valid PDF URLs extracted from index.")
                
        except Exception as e:
            print(f"[WARNING] Primary Index Parsing Denied or Offline ({e}).")
            print("[*] Engaging Off-Season / Structural Baseline Fallback...")

        if latest_pdf_url:
            try:
                print(f"[*] Extracting payload blocks from: {latest_pdf_url}")
                pdf_req = urllib.request.Request(latest_pdf_url, headers=self.request_headers)
                with urllib.request.urlopen(pdf_req, timeout=15) as pdf_response:
                    pdf_memory_file = io.BytesIO(pdf_response.read())
                    
                with pdfplumber.open(pdf_memory_file) as pdf:
                    print(f"[+] Processing {len(pdf.pages)} PDF source page layers...")
                    for page in pdf.pages:
                        text_layer = page.extract_text()
                        if not text_layer: continue
                        
                        for line in text_layer.split("\n"):
                            match = re.search(r'^(?P<Team>[A-Za-z0-9\s]+)\s+(?P<Player>[A-Za-z\s,\.\'-]+)\s+(?P<Status>Available|Out|Questionable|Probable|Doubtful)\s+(?P<Reason>.*)$', line.strip())
                            if match:
                                data = match.groupdict()
                                parsed_entries.append({
                                    "PLAYER_NAME": HighFidelityNameSanitizer.sanitize(data["Player"]),
                                    "TEAM": data["Team"].strip().upper(),
                                    "STATUS": data["Status"].upper().strip(),
                                    "ROTATION_VACUUM_IMPACT": 0.5 if data["Status"].upper() == "QUESTIONABLE" else 1.0,
                                    "RESTRICTION_LIMIT_MIN": 0.0
                                })
            except Exception as e:
                print(f"[ERROR] PDF Extraction Sequence Failed: {e}")

        # --- OFF-SEASON NEUTRAL BASELINE ---
        if not parsed_entries:
            print("[INFO] Active parsing filter empty (Off-Season / Idle). Injecting neutral baseline roster details.")
            parsed_entries = [
                {"PLAYER_NAME": "SYNTHETIC FALLBACK", "TEAM": "NBA", "STATUS": "AVAILABLE", "ROTATION_VACUUM_IMPACT": 0.0, "RESTRICTION_LIMIT_MIN": 0.0}
            ]

        final_df = pd.DataFrame(parsed_entries)
        final_df.to_csv(self.output_csv_path, index=False)
        print(f"[SUCCESS] Ingress Complete. Clean sheet synchronized to storage: {self.output_csv_path}")
        print("=================================================================")

if __name__ == "__main__":
    ingressor = InjuryReportIngressor()
    ingressor.run_ingress()