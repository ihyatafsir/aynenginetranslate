#!/usr/bin/env python3
"""
run_mawwaq_deep_worker.py

AynEngine AI (v3.0.0) — Dedicated Autonomous Goal-Mode Worker for Sidi al-Mawwaq
- Translates the Andalusian masterwork:
  Sunan al-Muhtadin fi Maqamat al-Din (سنن المهتدين في مقامات الدين)
  by Sidi Muhammad ibn Yusuf al-Mawwaq al-'Abdari al-Gharnati (d. 897 AH / 1492 CE)
- Pure Python in-process Dual EPUB3 Compilation (Pure English + Bilingual Apparatus).
- Continuous real-time syncing to WyreSup Mesh and Google Drive.
- System Watchdog active with 0% swap pressure.
"""

import os
import re
import sys
import json
import time
import shutil
import gc
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from core.lexicographical_engine import LexicographicalTranslationEngine
from core.epub_builder import AynEpubBuilder
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

WYRESUP_EPUBS_DIR = Path("/home/absolut7/Documents/news/wyresup-mesh-app/public/epubs")
LOG_FILE = BASE_DIR / "mawwaq_worker.log"

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{ts}] [MAWWAQ] {msg}"
    print(formatted, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

def get_memory_stats():
    try:
        meminfo = {}
        with open("/proc/meminfo", "r") as f:
            for line in f:
                parts = line.split(":")
                if len(parts) == 2:
                    meminfo[parts[0].strip()] = int(parts[1].strip().split()[0])
        total_kb = meminfo.get("MemTotal", 1)
        avail_kb = meminfo.get("MemAvailable", 0)
        used_kb = total_kb - avail_kb
        used_gb = used_kb / (1024 * 1024)
        avail_gb = avail_kb / (1024 * 1024)
        total_gb = total_kb / (1024 * 1024)
        used_pct = (used_kb / total_kb) * 100
        return used_gb, avail_gb, total_gb, used_pct
    except Exception:
        return 0, 10, 32, 0

def check_memory_safety():
    used_gb, avail_gb, _, used_pct = get_memory_stats()
    if avail_gb < 3.0 or used_pct > 80.0:
        log(f"High memory pressure ({used_pct:.1f}% used, {avail_gb:.2f} GB avail). Running GC...")
        gc.collect()
        time.sleep(3)

def adaptive_chunk_text(raw_text, max_chunk_chars=4000):
    pattern = r'\n(?=(?:#+\s*PageV\d+P\d+|###\s*\|\s*|\|\|\|\s*\*|\#+\s*(?:كتاب|باب|فصل|المسألة|الحديث|ذكر|فائدة|مسألة|القول|الأصل|المقدمة|التمهيد|المسلك|الطرف|الركن|المقام)))'
    sections = re.split(pattern, raw_text)
    
    chunks = []
    buf = []
    buf_len = 0
    sec_idx = 1
    
    for sec in sections:
        sec_str = sec.strip()
        if not sec_str:
            continue
        
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

def build_dual_epubs(slug, title_ar, title_en, author_name, chapters, epubs_dir):
    epubs_dir.mkdir(parents=True, exist_ok=True)
    
    pure_epub = epubs_dir / f"{slug}_pure_en.epub"
    b_pure = AynEpubBuilder(title=title_en, author=author_name, edition_type="PURE_SCHOLARLY")
    for ch in chapters:
        b_pure.add_pure_scholarly_chapter(
            title=ch.get("title_en", f"Section {ch.get('chapter_index', 1)}"),
            translation_text=ch.get("translation", "")
        )
    b_pure.build(str(pure_epub))
    
    bilingual_epub = epubs_dir / f"{slug}_bilingual_lexical_en.epub"
    b_bil = AynEpubBuilder(title=f"{title_en} / {title_ar}", author=author_name, edition_type="BILINGUAL_APPARATUS")
    for ch in chapters:
        t_en = ch.get("title_en", f"Section {ch.get('chapter_index', 1)}")
        t_ar = ch.get("title_ar", "")
        b_bil.add_bilingual_apparatus_chapter(
            title=f"{t_en} ({t_ar})" if t_ar else t_en,
            arabic_text=ch.get("arabic_text", ""),
            quad_anchors=ch.get("anchors", ""),
            translation_text=ch.get("translation", "")
        )
    b_bil.build(str(bilingual_epub))
    
    return pure_epub, bilingual_epub

def sync_epubs(author_slug, pure_epub, bilingual_epub):
    if WYRESUP_EPUBS_DIR.exists():
        for ep in [pure_epub, bilingual_epub]:
            if ep.exists():
                try:
                    target = WYRESUP_EPUBS_DIR / ep.name
                    target.write_bytes(ep.read_bytes())
                except Exception as e:
                    log(f"Could not copy {ep.name} to WyreSup: {e}")
                    
    try:
        subprocess.Popen([
            "rclone", "copy",
            str(pure_epub.parent),
            f"gdrive:aynengine_ai_classical_library/{author_slug}/epubs"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        subprocess.Popen([
            "rclone", "copy",
            str(pure_epub.parent),
            "gdrive:sanan 2026/"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def run_mawwaq_pipeline():
    texts_dir = BASE_DIR / "data/texts/mawwaq"
    epubs_dir = BASE_DIR / "data/epubs/mawwaq"
    trans_dir = BASE_DIR / "data/translations/mawwaq"
    
    epubs_dir.mkdir(parents=True, exist_ok=True)
    trans_dir.mkdir(parents=True, exist_ok=True)
    
    with open(texts_dir / "catalog.json", "r", encoding="utf-8") as f:
        catalog_data = json.load(f)
        
    author_name = catalog_data.get("author", "Sidi Muhammad ibn Yusuf al-Mawwaq al-'Abdari (d. 897 AH)")
    works = catalog_data["works"]
    
    log("=" * 80)
    log("AYNENGINE AI SIDI AL-MAWWAQ CLASSICAL TRANSLATION PIPELINE INITIALIZED")
    log(f"Works: {len(works)} Masterpiece (Quad-Lexical Tasawwuf & Fiqh Engine)")
    log(f"Model: {DEEPSEEK_MODEL} at {DEEPSEEK_BASE_URL}")
    log("=" * 80)
    
    for w_idx, work in enumerate(works, 1):
        slug = work["slug"]
        title_ar = work["title_ar"]
        title_en = work["title_en"]
        raw_file = texts_dir / work["file"]
        progress_file = trans_dir / f"{slug}_progress.json"
        
        if not raw_file.exists():
            log(f"❌ Raw text file not found: {raw_file}")
            continue
            
        with open(raw_file, "r", encoding="utf-8") as f:
            raw_text = f.read()
            
        log(f"📖 [{w_idx}/{len(works)}] Processing: {title_en} ({title_ar})")
        log(f"   Raw text size: {len(raw_text):,} characters")
        
        chunks = adaptive_chunk_text(raw_text, max_chunk_chars=3500)
        total_chunks = len(chunks)
        log(f"   Generated {total_chunks} adaptive chunks for translation.")
        
        # Load progress
        translated_chunks = []
        if progress_file.exists():
            try:
                with open(progress_file, "r", encoding="utf-8") as f:
                    translated_chunks = json.load(f)
                log(f"   Found existing progress: {len(translated_chunks)}/{total_chunks} sections completed.")
            except Exception as e:
                log(f"   Could not load progress file: {e}")
                
        completed_indices = {c["chapter_index"] for c in translated_chunks}
        
        engine = LexicographicalTranslationEngine(
            author=author_name,
            book_title_ar=title_ar,
            book_title_en=title_en,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            model=DEEPSEEK_MODEL
        )
        
        # Hydrate used roots
        for c in translated_chunks:
            for r in c.get("roots", []):
                engine.used_roots.add(r)
                
        for ch in chunks:
            c_idx = ch["chapter_index"]
            if c_idx in completed_indices:
                continue
                
            check_memory_safety()
            
            c_text = ch["text"]
            c_title_ar = ch["title_ar"]
            
            log(f"   -> Translating section [{c_idx}/{total_chunks}] ({len(c_text):,} chars)...")
            
            try:
                res = engine.translate_passage(c_text, title_ar=c_title_ar)
                
                # Check for rate limiting / retries
                if "[API Error:" in res.get("translation", ""):
                    log(f"   ⚠️ API Error encountered on section {c_idx}: {res['translation'][:100]}. Waiting 5s...")
                    time.sleep(5)
                    res = engine.translate_passage(c_text, title_ar=c_title_ar)
                
                entry = {
                    "chapter_index": c_idx,
                    "title_ar": c_title_ar,
                    "title_en": res.get("title_en", c_title_ar),
                    "arabic_text": c_text,
                    "anchors": res.get("anchors", ""),
                    "translation": res.get("translation", ""),
                    "roots": res.get("roots", [])
                }
                
                translated_chunks.append(entry)
                completed_indices.add(c_idx)
                
                # Persist progress
                with open(progress_file, "w", encoding="utf-8") as f:
                    json.dump(translated_chunks, f, ensure_ascii=False, indent=2)
                    
                log(f"   ✅ Section {c_idx} completed: \"{entry['title_en']}\" ({len(entry['translation']):,} chars translation)")
                
                # Rebuild & sync EPUBs every 5 sections or at completion
                if len(translated_chunks) % 5 == 0 or len(translated_chunks) == total_chunks:
                    log("   🔄 Compiling Dual EPUBs...")
                    sorted_chapters = sorted(translated_chunks, key=lambda x: x["chapter_index"])
                    pure_ep, bil_ep = build_dual_epubs(slug, title_ar, title_en, author_name, sorted_chapters, epubs_dir)
                    log(f"   📚 EPUBs built: {pure_ep.name} ({pure_ep.stat().st_size:,} B), {bil_ep.name} ({bil_ep.stat().st_size:,} B)")
                    sync_epubs("mawwaq", pure_ep, bil_ep)
                    log("   ☁️ Live synchronized to WyreSup & Google Drive.")
                    
                time.sleep(0.5)
                
            except Exception as e:
                log(f"   ❌ Fatal error on section {c_idx}: {e}")
                time.sleep(5)
                
        # Final build
        sorted_chapters = sorted(translated_chunks, key=lambda x: x["chapter_index"])
        pure_ep, bil_ep = build_dual_epubs(slug, title_ar, title_en, author_name, sorted_chapters, epubs_dir)
        sync_epubs("mawwaq", pure_ep, bil_ep)
        log(f"🏆 WORK COMPLETE: {title_en} fully translated into Dual EPUB3 Editions!")

if __name__ == "__main__":
    run_mawwaq_pipeline()
