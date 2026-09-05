#!/usr/bin/env python3
import time
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
DATA_DIR = BASE_DIR / "data"
WYRESUP_EPUBS = Path("/home/absolut7/Documents/news/wyresup-mesh-app/public/epubs")

def sync_all():
    # 1. Copy newly created epubs to WyreSup
    for ep in (DATA_DIR / "epubs").rglob("*.epub"):
        target = WYRESUP_EPUBS / ep.name
        if not target.exists() or target.stat().st_mtime < ep.stat().st_mtime:
            subprocess.run(["cp", str(ep), str(target)], check=False)
            
    # 2. Rclone to Google Drive
    subprocess.run([
        "rclone", "copy",
        str(DATA_DIR / "epubs" / "razi"),
        "gdrive:aynengine_ai_classical_library/razi/epubs/"
    ], check=False)
    
    subprocess.run([
        "rclone", "copy",
        str(DATA_DIR / "epubs"),
        "gdrive:aynengine_ai_classical_library/all_epubs/"
    ], check=False)
    
    subprocess.run([
        "rclone", "copy",
        str(DATA_DIR / "translations" / "razi"),
        "gdrive:aynengine_ai_classical_library/razi/translations/"
    ], check=False)

if __name__ == "__main__":
    while True:
        try:
            sync_all()
        except Exception as e:
            print(f"[Sync Error]: {e}")
        time.sleep(300) # sync every 5 minutes
