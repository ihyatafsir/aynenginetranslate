#!/usr/bin/env python3
"""
run_continuous_deep_translation_worker.py

Continuous Autonomous Scholarly Translation Worker:
- Sequentially processes all 26 works of Imam al-Ghazali and 22 works of Imam al-Nawawi.
- Translates every chapter using AynEngine AI Quad-Lexical DeepSeek inference.
- Re-compiles Pure English and Bilingual Apparatus EPUBs on each step.
- Automatically copies new EPUBs to WyreSup and syncs to Google Drive.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from core.lexicographical_engine import LexicographicalTranslationEngine
from core.epub_builder import AynEpubBuilder
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

WYRESUP_EPUBS_DIR = Path("/home/absolut7/Documents/news/wyresup-mesh-app/public/epubs")

def sync_to_drive_and_wyresup(author_slug):
    epubs_dir = BASE_DIR / f"data/epubs/{author_slug}"
    trans_dir = BASE_DIR / f"data/translations/{author_slug}"
    
    # 1. Copy to WyreSup
    if WYRESUP_EPUBS_DIR.exists():
        for epub in epubs_dir.glob("*.epub"):
            target = WYRESUP_EPUBS_DIR / epub.name
            try:
                target.write_bytes(epub.read_bytes())
            except Exception:
                pass

    # 2. Sync to Google Drive
    try:
        subprocess.run(["rclone", "copy", str(epubs_dir), f"gdrive:aynengine_ai_classical_library/{author_slug}/epubs"], check=False)
        subprocess.run(["rclone", "copy", str(trans_dir), f"gdrive:aynengine_ai_classical_library/{author_slug}/translations"], check=False)
    except Exception:
        pass

def run_continuous_pipeline():
    print("=" * 80)
    print("🚀 AYNENGINE AI CONTINUOUS TRANSLATION WORKER STARTED")
    print(f"Model: {DEEPSEEK_MODEL} | Base URL: {DEEPSEEK_BASE_URL}")
    print("=" * 80)

    authors = ["ghazali", "nawawi"]
    
    for author_slug in authors:
        texts_dir = BASE_DIR / f"data/texts/{author_slug}"
        epubs_dir = BASE_DIR / f"data/epubs/{author_slug}"
        trans_dir = BASE_DIR / f"data/translations/{author_slug}"
        
        epubs_dir.mkdir(parents=True, exist_ok=True)
        trans_dir.mkdir(parents=True, exist_ok=True)
        
        cat_path = texts_dir / "catalog.json"
        if not cat_path.exists():
            continue
            
        with open(cat_path, "r", encoding="utf-8") as f:
            catalog_data = json.load(f)
            
        author_name = catalog_data.get("author", "Classical Scholar")
        works = catalog_data["works"]
        
        print(f"\n🏛️ Corpus: {author_name} ({len(works)} Works)")
        
        for idx, work in enumerate(works, 1):
            slug = work["slug"]
            title_ar = work["title_ar"]
            title_en = work["title_en"]
            fname = work.get("file_name", work.get("filename", f"{slug}.txt"))
            txt_file = texts_dir / fname
            
            if not txt_file.exists():
                txt_file = texts_dir / f"{slug}.txt"
            if not txt_file.exists():
                continue
                
            trans_file = trans_dir / f"{slug}_translated.json"
            existing_data = {"chapters": []}
            if trans_file.exists():
                try:
                    with open(trans_file, "r", encoding="utf-8") as f:
                        existing_data = json.load(f)
                except Exception:
                    existing_data = {"chapters": []}
                    
            existing_count = len(existing_data.get("chapters", []))
            
            raw_text = txt_file.read_text(encoding="utf-8", errors="ignore")
            # Split sections
            sections = [s.strip() for s in raw_text.split("### |") if s.strip()]
            if len(sections) <= 1:
                paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
                sections = []
                chunk_buf = []
                chunk_words = 0
                for p in paragraphs:
                    w = len(p.split())
                    chunk_buf.append(p)
                    chunk_words += w
                    if chunk_words >= 500:
                        sections.append("\n\n".join(chunk_buf))
                        chunk_buf = []
                        chunk_words = 0
                if chunk_buf:
                    sections.append("\n\n".join(chunk_buf))
                    
            total_sections = len(sections)
            print(f"\n[{idx}/{len(works)}] 📖 {title_ar} ({title_en})")
            print(f"   Progress: {existing_count}/{total_sections} chapters completed.")
            
            engine = LexicographicalTranslationEngine(
                author=author_name,
                book_title_ar=title_ar,
                book_title_en=title_en,
                api_key=DEEPSEEK_API_KEY,
                base_url=DEEPSEEK_BASE_URL,
                model=DEEPSEEK_MODEL,
                engine_mode="QUAD_LEXICAL"
            )
            
            new_translations = False
            for sec_idx in range(existing_count, total_sections):
                sec_text = sections[sec_idx]
                sec_title = f"Section {sec_idx + 1}"
                print(f"   Translating [{sec_idx + 1}/{total_sections}]...", end="", flush=True)
                
                try:
                    res = engine.translate_passage(sec_text, title_ar=sec_title)
                    existing_data["chapters"].append({
                        "chapter_num": sec_idx + 1,
                        "title_ar": sec_title,
                        "title_en": res.get("title_en", sec_title),
                        "arabic_text": sec_text[:4000],
                        "anchors": res.get("anchors", ""),
                        "translation": res.get("translation", "")
                    })
                    with open(trans_file, "w", encoding="utf-8") as f:
                        json.dump(existing_data, f, ensure_ascii=False, indent=2)
                    print(f" ✅ Done.")
                    new_translations = True
                    time.sleep(1)
                except Exception as e:
                    print(f" ⚠️ API Error: {e}. Pausing for 5s...")
                    time.sleep(5)
                    break
                    
            if new_translations:
                # Recompile EPUBs
                builder = AynEpubBuilder(author_name, title_ar, title_en, slug=slug)
                for ch in existing_data["chapters"]:
                    builder.add_chapter(
                        ch["title_ar"],
                        ch["title_en"],
                        ch["arabic_text"],
                        ch["translation"],
                        ch["anchors"]
                    )
                pure_epub = epubs_dir / f"{slug}_pure_en.epub"
                bilingual_epub = epubs_dir / f"{slug}_bilingual_lexical_en.epub"
                builder.build(pure_epub, edition_type="PURE_SCHOLARLY")
                builder.build(bilingual_epub, edition_type="BILINGUAL_APPARATUS")
                
                sync_to_drive_and_wyresup(author_slug)

    print("\n🎉 ALL CLASSICAL WORKS TRANSLATION PASS COMPLETED!")

if __name__ == "__main__":
    run_continuous_pipeline()
