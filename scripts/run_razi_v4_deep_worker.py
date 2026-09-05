#!/usr/bin/env python3
"""
run_razi_v4_deep_worker.py

AynEngine AI v4.0 Sovereign Edition: Imam Fakhr al-Din al-Razi Worker
Dual-Pass Zero-Loss Active-RAG Execution:
- Ingests 18 classical masterworks of Imam Fakhr al-Din al-Razi (d. 606 AH).
- Incorporates prior translation drafts as reference baselines for harmonization.
- Queries active classical lexicons (Al-Mufradat, Asas al-Balaghah, Lisan al-Arab, Kitab al-Ayn).
- Zero-loss auto-continuation on token limits with sentence-safe boundary verification.
- Generates Dual-Edition EPUB3s (Pure Scholarly Reader + Bilingual Lexical Apparatus).
- Continuous atomic JSON checkpointing.
"""

import os
import sys
import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from core.lexicographical_engine import LexicographicalTranslationEngine
from core.epub_builder import AynEpubBuilder

DATA_DIR = BASE_DIR / "data"
RAZI_TEXTS = DATA_DIR / "texts" / "razi"
RAZI_TRANS = DATA_DIR / "translations" / "razi"
RAZI_EPUBS = DATA_DIR / "epubs" / "razi"

RAZI_TRANS.mkdir(parents=True, exist_ok=True)
RAZI_EPUBS.mkdir(parents=True, exist_ok=True)

CATALOG_PATH = RAZI_TEXTS / "catalog.json"

# Prior drafts search locations
PRIOR_SOURCES = [
    Path("/home/absolut7/Documents/news"),
    Path("/home/absolut7/.gemini/antigravity/scratch/imamrazi"),
    Path("/home/absolut7/aynengineai/data/translations/razi")
]

def find_prior_draft(slug, chunk_idx):
    """Searches archival stores for any prior translation of this chunk."""
    for p_dir in PRIOR_SOURCES:
        candidate_files = [
            p_dir / f"{slug}_translated.json",
            p_dir / f"{slug}_progress.json",
            p_dir / f"{slug}.json"
        ]
        for cf in candidate_files:
            if cf.exists():
                try:
                    data = json.loads(cf.read_text(encoding="utf-8"))
                    items = data if isinstance(data, list) else data.get("chapters", [])
                    for it in items:
                        if it.get("chapter_index") == chunk_idx:
                            tr = it.get("translation", "")
                            if len(tr.strip()) > 50 and not tr.startswith("[API Error"):
                                return tr.strip()
                except Exception:
                    pass
    return None

def translate_razi_work(work_meta):
    slug = work_meta["slug"]
    title_ar = work_meta["title_ar"]
    title_en = work_meta["title_en"]
    source_path = Path(work_meta["file_path"])
    
    trans_file = RAZI_TRANS / f"{slug}_v4_translated.json"
    epub_pure = RAZI_EPUBS / f"{slug}_pure_en.epub"
    epub_bilingual = RAZI_EPUBS / f"{slug}_bilingual_lexical_en.epub"
    
    print("\n" + "=" * 80)
    print(f"📖 STARTING IMAM RAZI WORK: {title_ar}")
    print(f"English: {title_en}")
    print(f"Slug: {slug} | Source: {source_path.name} ({work_meta['size_kb']} KB)")
    print("=" * 80)
    
    if not source_path.exists():
        print(f"❌ Error: Source file not found at {source_path}")
        return
        
    raw_text = source_path.read_text(encoding="utf-8")
    
    engine = LexicographicalTranslationEngine(
        author="Imam Fakhr al-Din al-Razi (d. 606 AH)",
        book_title_ar=title_ar,
        book_title_en=title_en,
        max_chunk_chars=3200
    )
    
    chunks = engine.chunk_manuscript(raw_text)
    total_chunks = len(chunks)
    print(f"🧩 Partitioned into {total_chunks} sentence-safe chunks (Zero-Loss standard).")
    
    progress = []
    if trans_file.exists():
        try:
            progress = json.loads(trans_file.read_text(encoding="utf-8"))
            print(f"⚡ Resuming from checkpoint: {len(progress)}/{total_chunks} sections already completed.")
        except Exception:
            progress = []
            
    completed_indices = {item["chapter_index"] for item in progress if not item.get("translation", "").startswith("[API Error")}
    
    for i, chunk in enumerate(chunks, 1):
        idx = chunk["chapter_index"]
        if idx in completed_indices:
            continue
            
        prior_draft = find_prior_draft(slug, idx)
        draft_note = " (using prior draft as reference baseline)" if prior_draft else ""
        print(f"\n⏳ [{i}/{total_chunks}] Translating Section {idx} ({len(chunk['text'])} chars){draft_note}...")
        t0 = time.time()
        
        try:
            res = engine.translate_passage(chunk["text"], title_ar=f"Section {idx}", prior_draft=prior_draft)
            elapsed = time.time() - t0
            
            item = {
                "chapter_index": idx,
                "title_ar": res["title_ar"],
                "title_en": res["title_en"],
                "anchors": res["anchors"],
                "arabic_text": res["arabic_text"],
                "translation": res["translation"],
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "duration_seconds": round(elapsed, 2)
            }
            
            progress.append(item)
            trans_file.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8")
            
            ar_words = len(chunk["text"].split())
            en_words = len(res["translation"].split())
            ratio = round(en_words / max(1, ar_words), 2)
            print(f"  ✅ Section {idx} done in {elapsed:.1f}s | {ar_words} ar words -> {en_words} en words (ratio: {ratio}x)")
            
        except Exception as e:
            print(f"  ❌ Error on Section {idx}: {e}")
            time.sleep(5)
            
    print(f"\n📚 Translation complete for {slug}! Building Dual-Edition EPUBs...")
    
    # 1. Pure English
    b_pure = AynEpubBuilder(title=title_en, author="Imam Fakhr al-Din al-Razi (d. 606 AH)", edition_type="PURE_SCHOLARLY")
    for item in sorted(progress, key=lambda x: x["chapter_index"]):
        b_pure.add_pure_scholarly_chapter(
            title=item.get("title_en", f"Section {item.get('chapter_index', 1)}"),
            translation_text=item.get("translation", "")
        )
    b_pure.build(str(epub_pure))
    print(f"  📗 Generated Pure Edition: {epub_pure.name} ({epub_pure.stat().st_size / 1024:.1f} KB)")
    
    # 2. Bilingual Apparatus
    b_bil = AynEpubBuilder(title=f"{title_en} / {title_ar}", author="Imam Fakhr al-Din al-Razi (d. 606 AH)", edition_type="BILINGUAL_APPARATUS")
    for item in sorted(progress, key=lambda x: x["chapter_index"]):
        t_en = item.get("title_en", f"Section {item.get('chapter_index', 1)}")
        t_ar = item.get("title_ar", "")
        b_bil.add_bilingual_apparatus_chapter(
            title=f"{t_en} ({t_ar})" if t_ar else t_en,
            arabic_text=item.get("arabic_text", ""),
            quad_anchors=item.get("anchors", ""),
            translation_text=item.get("translation", "")
        )
    b_bil.build(str(epub_bilingual))
    print(f"  📘 Generated Bilingual Edition: {epub_bilingual.name} ({epub_bilingual.stat().st_size / 1024:.1f} KB)")

def main():
    print("=" * 80)
    print("🌟 AYNENGINE AI v4.0: IMAM FAKHR AL-DIN AL-RAZI RE-TRANSLATION PIPELINE")
    print("=" * 80)
    
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)
        
    works = catalog.get("works", [])
    print(f"Loaded {len(works)} classical works for Imam Fakhr al-Din al-Razi.\n")
    
    # Execution Order: Foundational theological & philosophical treatises first
    priority = [
        "al_qada_wal_qadar",           # On Divine Decree, Predestination & Justice
        "itiqadat_firaq_al_muslimin",  # Heresiology & Doctrines of Sects
        "razi_asas",                   # Asas al-Taqdis (The Foundation of Divine Sanctification)
        "razi_lawami",                 # Lawami al-Bayyinat (Divine Names & Attributes)
        "matalib_vol_01",              # Matalib Vol 1 (Divine Unity)
        "matalib_vol_02",              # Matalib Vol 2 (Attributes)
        "matalib_vol_03",              # Matalib Vol 3 (Origination & Time)
        "matalib_vol_04",              # Matalib Vol 4 (Space & Void)
        "matalib_vol_05",              # Matalib Vol 5 (Atomism)
        "matalib_vol_06",              # Matalib Vol 6 (Prime Matter & Form)
        "matalib_vol_07",              # Matalib Vol 7 (Rational Soul)
        "matalib_vol_08",              # Matalib Vol 8 (Prophethood)
        "matalib_vol_09",              # Matalib Vol 9 (Eschatology)
        "razi_ismat_anbiya",           # Infallibility of Prophets
        "razi_asrar_tanzil",           # Secrets of Revelation
        "razi_mahsul",                 # Al-Mahsul (Usul al-Fiqh)
        "razi_arbain",                 # Forty Inquiries
        "razi_tafsir_kabir"            # Tafsir al-Kabir
    ]
    
    sorted_works = sorted(works, key=lambda w: priority.index(w["slug"]) if w["slug"] in priority else 99)
    
    for w in sorted_works:
        translate_razi_work(w)

if __name__ == "__main__":
    main()
