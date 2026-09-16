#!/usr/bin/env python3
import time
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
DATA_DIR = BASE_DIR / "data"
WYRESUP_EPUBS = Path("/home/absolut7/Documents/news/wyresup-mesh-app/public/epubs")

AUTHORS = ["ghazali", "razi", "raghib", "nawawi", "mawwaq"]

def sync_all():
    print("[Sync] Starting full synchronization cycle...")
    
    # 1. Copy newly created epubs to WyreSup Mesh public distribution
    if (DATA_DIR / "epubs").exists():
        for ep in (DATA_DIR / "epubs").rglob("*.epub"):
            target = WYRESUP_EPUBS / ep.name
            if not target.exists() or target.stat().st_mtime < ep.stat().st_mtime:
                subprocess.run(["cp", str(ep), str(target)], check=False)
                
    # 2. Sync all authors' translations to Google Drive
    for author in AUTHORS:
        local_tr = DATA_DIR / "translations" / author
        if local_tr.exists():
            subprocess.run([
                "rclone", "copy",
                str(local_tr),
                f"gdrive:aynengine_ai_classical_library/{author}/translations/"
            ], check=False)

    # 3. Sync all authors' epubs to Google Drive
    for author in AUTHORS:
        local_ep = DATA_DIR / "epubs" / author
        if local_ep.exists():
            subprocess.run([
                "rclone", "copy",
                str(local_ep),
                f"gdrive:aynengine_ai_classical_library/{author}/epubs/"
            ], check=False)

    # 4. Sync consolidated all_epubs to Google Drive
    if (DATA_DIR / "epubs").exists():
        subprocess.run([
            "rclone", "copy",
            str(DATA_DIR / "epubs"),
            "gdrive:aynengine_ai_classical_library/all_epubs/"
        ], check=False)
        
    print("[Sync] Full sync cycle completed successfully.")

if __name__ == "__main__":
    while True:
        try:
            sync_all()
        except Exception as e:
            print(f"[Sync Error]: {e}")
        time.sleep(300) # sync every 5 minutes
