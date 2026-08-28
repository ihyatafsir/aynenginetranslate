#!/usr/bin/env python3
"""
run_razi_deep_worker.py

AynEngine AI (v3.0.0) — Dedicated Autonomous Goal-Mode Worker for Imam Fakhr al-Din al-Razi
- Re-translates key theological and philosophical masterworks of Imam Fakhr al-Din al-Razi:
  1. I'tiqadat Firaq al-Muslimin wa'l-Mushrikin (7 complete sections)
  2. Kitab al-Jabr wa'l-Qadar / Al-Qada' wa'l-Qadar (119 complete sections)
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
LOG_FILE = BASE_DIR / "razi_worker.log"

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{ts}] [RAZI] {msg}"
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
    pattern = r'\n(?=(?:#+\s*PageV\d+P\d+|###\s*\|\s*|\|\|\|\s*\*|\#+\s*(?:كتاب|باب|فصل|المسألة|الحديث|ذكر|فائدة|مسألة|القول|الأصل|المقدمة|التمهيد|المسلك|الطرف|الركن|الفرقة)))'
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
            "gdrive:imamrazi/"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def run_razi_pipeline():
    texts_dir = BASE_DIR / "data/texts/razi"
    epubs_dir = BASE_DIR / "data/epubs/razi"
    trans_dir = BASE_DIR / "data/translations/razi"
    
    epubs_dir.mkdir(parents=True, exist_ok=True)
    trans_dir.mkdir(parents=True, exist_ok=True)
    
    with open(texts_dir / "catalog.json", "r", encoding="utf-8") as f:
        catalog_data = json.load(f)
        
    author_name = catalog_data.get("author", "Imam Fakhr al-Din al-Razi")
    works = catalog_data["works"]
    
    log("=" * 80)
    log("AYNENGINE AI IMAM RAZI THEOLOGICAL MASTERWORKS TRANSLATION PIPELINE INITIALIZED")
    log(f"Works: {len(works)} Masterpieces (Quad-Lexical Kalam Engine)")
    log("=" * 80)
    
    for w_idx, work in enumerate(works, 1):
        slug = work["slug"]
        title_ar = work["title_ar"]
        title_en = work["title_en"]
        
        fname = work.get("file_name") or f"{slug}.txt"
        txt_path = texts_dir / fname
        if not txt_path.exists():
            continue
            
        raw_text = txt_path.read_text(encoding="utf-8", errors="ignore")
        chunks = adaptive_chunk_text(raw_text, max_chunk_chars=4000)
        total_chunks = len(chunks)
        
        trans_file = trans_dir / f"{slug}_translated.json"
        trans_data = {"meta": work, "chapters": []}
        
        if trans_file.exists():
            try:
                with open(trans_file, "r", encoding="utf-8") as f:
                    trans_data = json.load(f)
            except Exception:
                trans_data = {"meta": work, "chapters": []}
                
        completed_indices = {c.get("chapter_index") or c.get("chapter_num") for c in trans_data.get("chapters", [])}
        
        used_gb, avail_gb, _, used_pct = get_memory_stats()
        log(f"\n[{w_idx}/{len(works)}] Book: {title_en} ({title_ar})")
        log(f"   Progress: {len(completed_indices)}/{total_chunks} sections completed | RAM: {used_gb:.1f}GB used, {avail_gb:.1f}GB avail")
        
        if len(completed_indices) >= total_chunks and total_chunks > 0:
            pure_ep = epubs_dir / f"{slug}_pure_en.epub"
            bil_ep = epubs_dir / f"{slug}_bilingual_lexical_en.epub"
            if not pure_ep.exists() or not bil_ep.exists():
                pure_ep, bil_ep = build_dual_epubs(slug, title_ar, title_en, author_name, trans_data["chapters"], epubs_dir)
                sync_epubs("razi", pure_ep, bil_ep)
            continue
            
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
            if idx in completed_indices:
                continue
                
            check_memory_safety()
            
            used_gb, avail_gb, _, _ = get_memory_stats()
            print(f"   [{idx}/{total_chunks}] Translating '{chunk['title_ar']}' (RAM: {avail_gb:.1f}GB avail)...", end="", flush=True)
            
            retry_count = 0
            success = False
            while retry_count < 3 and not success:
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
                    
                    tmp_trans_file = trans_file.with_suffix(".tmp")
                    with open(tmp_trans_file, "w", encoding="utf-8") as f:
                        json.dump(trans_data, f, ensure_ascii=False, indent=2)
                    shutil.move(tmp_trans_file, trans_file)
                    
                    print(" Done.")
                    modified = True
                    success = True
                    time.sleep(0.5)
                except Exception as e:
                    retry_count += 1
                    print(f" Error: {e}. Retrying ({retry_count}/3)...", flush=True)
                    time.sleep(3 * retry_count)
                    
            if idx % 5 == 0 or idx == total_chunks:
                pure_ep, bil_ep = build_dual_epubs(slug, title_ar, title_en, author_name, trans_data["chapters"], epubs_dir)
                sync_epubs("razi", pure_ep, bil_ep)
                log(f"   Incremental Sync: {pure_ep.name} ({pure_ep.stat().st_size/1024:.1f} KB) & {bil_ep.name} ({bil_ep.stat().st_size/1024:.1f} KB)")
                gc.collect()

        if modified:
            pure_ep, bil_ep = build_dual_epubs(slug, title_ar, title_en, author_name, trans_data["chapters"], epubs_dir)
            sync_epubs("razi", pure_ep, bil_ep)
            log(f"   FULL EDITION COMPLETED: {slug} (Pure: {pure_ep.stat().st_size/1024:.1f} KB, Bil: {bil_ep.stat().st_size/1024:.1f} KB)")
            gc.collect()

if __name__ == "__main__":
    run_razi_pipeline()
