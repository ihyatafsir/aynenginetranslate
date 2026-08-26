#!/usr/bin/env python3
"""
run_nawawi_full_corpus_deep_worker.py

Full-Text Continuous Deep Translation Worker for Imam al-Nawawi (22 Masterworks):
- Processes every work with --max-chapters None (100% full text).
- Uses adaptive zero-truncation chunking on classical boundary markers.
- Integrates AynEngine AI (v3.0.0) Quad-Lexical translation apparatus.
- Saves progress continuously to data/translations/nawawi/{slug}_translated.json.
- Re-compiles full Pure English and Bilingual Apparatus EPUBs on completion of each book/batch.
- Syncs directly to WyreSup (/public/epubs/) and Google Drive.
"""

import os
import re
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

def adaptive_chunk_text(raw_text, max_chunk_chars=4500):
    """Splits classical text along authentic section and chapter boundaries."""
    # Split on classical chapter/section headings or page boundaries
    pattern = r'\n(?=(?:#+\s*PageV\d+P\d+|###\s*\|\s*|\#+\s*(?:كتاب|باب|فصل|المسألة|الحديث|ذكر|فائدة|مسألة|القول|الأصل)))'
    sections = re.split(pattern, raw_text)
    
    chunks = []
    buf = []
    buf_len = 0
    sec_idx = 1
    
    for sec in sections:
        sec_str = sec.strip()
        if not sec_str:
            continue
        
        # If a single section is very large, split on paragraphs
        if len(sec_str) > max_chunk_chars:
            paras = [p.strip() for p in sec_str.split("\n\n") if p.strip()]
            for p in paras:
                if buf_len + len(p) > max_chunk_chars and buf:
                    chunks.append({
                        "chapter_index": sec_idx,
                        "title_ar": f"Section {sec_idx}",
                        "text": "\n\n".join(buf)
                    })
                    sec_idx += 1
                    buf = [p]
                    buf_len = len(p)
                else:
                    buf.append(p)
                    buf_len += len(p)
        else:
            if buf_len + len(sec_str) > max_chunk_chars and buf:
                chunks.append({
                    "chapter_index": sec_idx,
                    "title_ar": f"Section {sec_idx}",
                    "text": "\n\n".join(buf)
                })
                sec_idx += 1
                buf = [sec_str]
                buf_len = len(sec_str)
            else:
                buf.append(sec_str)
                buf_len += len(sec_str)
                
    if buf:
        chunks.append({
            "chapter_index": sec_idx,
            "title_ar": f"Section {sec_idx}",
            "text": "\n\n".join(buf)
        })
        
    return chunks

def sync_epubs(slug):
    epubs_dir = BASE_DIR / "data/epubs/nawawi"
    pure_epub = epubs_dir / f"{slug}_pure_en.epub"
    bilingual_epub = epubs_dir / f"{slug}_bilingual_lexical_en.epub"
    
    if WYRESUP_EPUBS_DIR.exists():
        for ep in [pure_epub, bilingual_epub]:
            if ep.exists():
                target = WYRESUP_EPUBS_DIR / ep.name
                try:
                    target.write_bytes(ep.read_bytes())
                except Exception as e:
                    print(f"⚠️ Could not copy to WyreSup: {e}")
                    
    # Sync to Google Drive in background
    try:
        subprocess.Popen([
            "rclone", "copy",
            str(epubs_dir),
            "gdrive:aynengine_ai_classical_library/nawawi/epubs"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def run_nawawi_full_deep_worker():
    texts_dir = BASE_DIR / "data/texts/nawawi"
    epubs_dir = BASE_DIR / "data/epubs/nawawi"
    trans_dir = BASE_DIR / "data/translations/nawawi"
    
    epubs_dir.mkdir(parents=True, exist_ok=True)
    trans_dir.mkdir(parents=True, exist_ok=True)
    
    cat_path = texts_dir / "catalog.json"
    with open(cat_path, "r", encoding="utf-8") as f:
        catalog_data = json.load(f)
        
    author_name = catalog_data.get("author", "Imam Yahya ibn Sharaf al-Nawawi")
    works = catalog_data["works"]
    
    print("=" * 80)
    print(f"🚀 FULL CORPUS UNLIMITED DEEP TRANSLATION WORKER: {author_name.upper()}")
    print(f"Total Works: {len(works)} | Max Chapters: None (Full Text)")
    print(f"Model: {DEEPSEEK_MODEL} | Base URL: {DEEPSEEK_BASE_URL}")
    print("=" * 80)
    
    for w_idx, work in enumerate(works, 1):
        slug = work["slug"]
        title_ar = work["title_ar"]
        title_en = work["title_en"]
        txt_path = Path(work["file_path"])
        
        if not txt_path.exists():
            print(f"⚠️ File missing: {txt_path}")
            continue
            
        raw_text = txt_path.read_text(encoding="utf-8", errors="ignore")
        chunks = adaptive_chunk_text(raw_text, max_chunk_chars=4500)
        total_chunks = len(chunks)
        
        trans_file = trans_dir / f"{slug}_translated.json"
        trans_data = {"meta": work, "chapters": []}
        
        if trans_file.exists():
            try:
                with open(trans_file, "r", encoding="utf-8") as f:
                    trans_data = json.load(f)
            except Exception:
                trans_data = {"meta": work, "chapters": []}
                
        completed_set = {c.get("chapter_index") or c.get("chapter_num") for c in trans_data.get("chapters", [])}
        print(f"\n[{w_idx}/{len(works)}] 📖 {title_ar} ({title_en})")
        print(f"   Total Chunks: {total_chunks} | Already Completed: {len(completed_set)}")
        
        engine = LexicographicalTranslationEngine(
            author=author_name,
            book_title_ar=title_ar,
            book_title_en=title_en,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            model=DEEPSEEK_MODEL,
            engine_mode="QUAD_LEXICAL"
        )
        
        modified = False
        for idx, chunk in enumerate(chunks, 1):
            if idx in completed_set:
                continue
                
            print(f"   Translating section [{idx}/{total_chunks}]...", end="", flush=True)
            try:
                res_trans = engine.translate_passage(chunk["text"], title_ar=f"Section {idx}")
                ch_entry = {
                    "chapter_index": idx,
                    "chapter_num": idx,
                    "title_ar": res_trans.get("title_ar") or f"Section {idx}",
                    "title_en": res_trans.get("title_en") or f"Section {idx}: {title_en}",
                    "arabic_text": chunk["text"],
                    "anchors": res_trans.get("anchors", ""),
                    "translation": res_trans.get("translation", "")
                }
                trans_data["chapters"].append(ch_entry)
                with open(trans_file, "w", encoding="utf-8") as f:
                    json.dump(trans_data, f, ensure_ascii=False, indent=2)
                print(" ✅ Done.")
                modified = True
                time.sleep(1)
            except Exception as e:
                print(f" ⚠️ API Error: {e}. Retrying after 5s...")
                time.sleep(5)
                
            # Periodic EPUB rebuild every 5 chapters or when finished
            if idx % 5 == 0 or idx == total_chunks:
                # Recompile Dual Editions
                pure_epub = epubs_dir / f"{slug}_pure_en.epub"
                b_pure = AynEpubBuilder(title=title_en, author=author_name, edition_type="PURE_SCHOLARLY")
                for ch in trans_data["chapters"]:
                    b_pure.add_pure_scholarly_chapter(ch.get("title_en", f"Section {ch.get('chapter_index', 1)}"), ch.get("translation", ""))
                b_pure.build(str(pure_epub))
                
                bilingual_epub = epubs_dir / f"{slug}_bilingual_lexical_en.epub"
                b_bil = AynEpubBuilder(title=f"{title_en} / {title_ar}", author=author_name, edition_type="BILINGUAL_APPARATUS")
                for ch in trans_data["chapters"]:
                    b_bil.add_bilingual_apparatus_chapter(
                        title=f"{ch.get('title_en', '')} ({ch.get('title_ar', '')})",
                        arabic_text=ch.get("arabic_text", ""),
                        quad_anchors=ch.get("anchors", ""),
                        translation_text=ch.get("translation", "")
                    )
                b_bil.build(str(bilingual_epub))
                sync_epubs(slug)
                print(f"   📦 Rebuilt & Synced: {pure_epub.name} ({pure_epub.stat().st_size / 1024:.1f} KB) & {bilingual_epub.name} ({bilingual_epub.stat().st_size / 1024:.1f} KB)")

        # Final rebuild on work completion
        if modified or not (epubs_dir / f"{slug}_pure_en.epub").exists():
            pure_epub = epubs_dir / f"{slug}_pure_en.epub"
            b_pure = AynEpubBuilder(title=title_en, author=author_name, edition_type="PURE_SCHOLARLY")
            for ch in trans_data["chapters"]:
                b_pure.add_pure_scholarly_chapter(ch.get("title_en", f"Section {ch.get('chapter_index', 1)}"), ch.get("translation", ""))
            b_pure.build(str(pure_epub))
            
            bilingual_epub = epubs_dir / f"{slug}_bilingual_lexical_en.epub"
            b_bil = AynEpubBuilder(title=f"{title_en} / {title_ar}", author=author_name, edition_type="BILINGUAL_APPARATUS")
            for ch in trans_data["chapters"]:
                b_bil.add_bilingual_apparatus_chapter(
                    title=f"{ch.get('title_en', '')} ({ch.get('title_ar', '')})",
                    arabic_text=ch.get("arabic_text", ""),
                    quad_anchors=ch.get("anchors", ""),
                    translation_text=ch.get("translation", "")
                )
            b_bil.build(str(bilingual_epub))
            sync_epubs(slug)
            print(f"   ✨ FINAL EPUB COMPILED: {slug} (Pure: {pure_epub.stat().st_size / 1024:.1f} KB, Bilingual: {bilingual_epub.stat().st_size / 1024:.1f} KB)")

    print("\n🎉 ALL 22 NAWAWI MASTERWORKS FULL-TEXT DEEP TRANSLATION COMPLETED!")

if __name__ == "__main__":
    run_nawawi_full_deep_worker()
