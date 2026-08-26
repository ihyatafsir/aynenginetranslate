#!/usr/bin/env python3
"""
translate_ghazali_dual_edition_demo.py

Demonstration of Dual-Edition Publishing for Imam Abu Hamid al-Ghazali using AynEngine AI v3.0.0.
Compiles:
1. Pure English Scholarly Edition (_pure_en.epub)
2. Bilingual Scholarly Apparatus Edition (_bilingual_lexical_en.epub)
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from scripts.run_ghazali_dual_edition_pipeline import process_book, load_catalog

def main():
    print("==================================================================")
    print("🏛️ AYNENGINE AI v3.0.0: GHAZALI DUAL-EDITION DEMO")
    print("==================================================================")
    
    catalog = load_catalog()
    
    # Process Al-Munqidh min al-Dalal
    munqidh = next((w for w in catalog if w["slug"] == "al_munqidh_min_al_dalal"), None)
    if munqidh:
        print("\n🚀 1. Building Dual Edition for Deliverance from Error (المنقذ من الضلال)...")
        process_book(munqidh, max_chapters=3, dry_run=False)
        
    # Process Mishkat al-Anwar
    mishkat = next((w for w in catalog if w["slug"] == "mishkat_al_anwar"), None)
    if mishkat:
        print("\n🚀 2. Building Dual Edition for The Niche of Lights (مشكاة الأنوار)...")
        process_book(mishkat, max_chapters=3, dry_run=False)

if __name__ == "__main__":
    main()
