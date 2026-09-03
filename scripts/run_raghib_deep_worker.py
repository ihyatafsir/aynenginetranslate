#!/usr/bin/env python3
"""
run_raghib_deep_worker.py

AynEngine AI v4.0.0 Sovereign Edition: Al-Raghib al-Isfahani Deep Translation Worker
Zero-Loss Active-RAG Execution:
- Ingests all 6 classical works of Al-Raghib al-Isfahani (d. 502 AH).
- Sentence-safe chunking (~3,200 chars).
- Active Lexicon Grounding from Al-Mufradat, Asas al-Balaghah, Lisan al-Arab, Kitab al-Ayn.
- Zero-loss auto-continuation on token limits.
- Dual-Edition EPUB3 Generation (Pure English Reader + Bilingual Lexical Apparatus).
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
TEXTS_DIR = DATA_DIR / "texts" / "raghib"
TRANS_DIR = DATA_DIR / "translations" / "raghib"
EPUBS_DIR = DATA_DIR / "epubs" / "raghib"

TRANS_DIR.mkdir(parents=True, exist_ok=True)
EPUBS_DIR.mkdir(parents=True, exist_ok=True)

CATALOG_PATH = TEXTS_DIR / "catalog.json"

def translate_work(work_meta):
    slug = work_meta["slug"]
    title_ar = work_meta["title_ar"]
    title_en = work_meta["title_en"]
    source_path = Path(work_meta["file_path"])
    
    trans_file = TRANS_DIR / f"{slug}_translated.json"
    epub_pure = EPUBS_DIR / f"{slug}_pure_en.epub"
    epub_bilingual = EPUBS_DIR / f"{slug}_bilingual_lexical_en.epub"
    
    print("\n" + "=" * 80)
    print(f"📖 STARTING WORK: {title_ar} ({title_en})")
    print(f"Slug: {slug} | Source: {source_path.name} ({work_meta['size_kb']} KB)")
    print("=" * 80)
    
    if not source_path.exists():
        print(f"❌ Error: Source file not found at {source_path}")
        return
        
    raw_text = source_path.read_text(encoding="utf-8")
    
    engine = LexicographicalTranslationEngine(
        author="Al-Rāghib al-Iṣfahānī (d. 502 AH)",
        book_title_ar=title_ar,
        book_title_en=title_en,
        max_chunk_chars=3200
    )
    
    chunks = engine.chunk_manuscript(raw_text)
    total_chunks = len(chunks)
    print(f"🧩 Manuscript partitioned into {total_chunks} sentence-safe chunks (Zero-Loss standard).")
    
    # Load existing progress checkpoint
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
            
        print(f"\n⏳ [{i}/{total_chunks}] Translating Section {idx} ({len(chunk['text'])} chars)...")
        t0 = time.time()
        
        try:
            res = engine.translate_passage(chunk["text"], title_ar=f"Section {idx}")
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
            
            # Atomic update
            progress.append(item)
            trans_file.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8")
            
            ar_words = len(chunk["text"].split())
            en_words = len(res["translation"].split())
            ratio = round(en_words / max(1, ar_words), 2)
            print(f"  ✅ Completed in {elapsed:.1f}s | {ar_words} ar words -> {en_words} en words (ratio: {ratio}x)")
            
        except Exception as e:
            print(f"  ❌ Error translating section {idx}: {e}")
            time.sleep(5)
            
    print(f"\n📚 Translation complete for {slug}! Building Dual-Edition EPUBs...")
    
    # 1. Pure English Reader Edition
    builder_pure = AynEpubBuilder(title=title_en, author="Al-Rāghib al-Iṣfahānī", edition_type="PURE_SCHOLARLY")
    for item in sorted(progress, key=lambda x: x["chapter_index"]):
        body = f"<div class='section-ar-meta'><strong>{item['title_ar']}</strong></div>\n\n{item['translation']}"
        builder_pure.add_chapter(item["title_en"], body, chapter_index=item["chapter_index"])
    builder_pure.build(epub_pure)
    print(f"  📗 Generated Pure Edition: {epub_pure.name} ({epub_pure.stat().st_size / 1024:.1f} KB)")
    
    # 2. Bilingual Apparatus Edition
    builder_bilingual = AynEpubBuilder(title=title_en, author="Al-Rāghib al-Iṣfahānī", edition_type="BILINGUAL_LEXICAL")
    for item in sorted(progress, key=lambda x: x["chapter_index"]):
        body = f"""
        <div class="scholarly-apparatus">
            <h3>Classical Arabic Apparatus & Lexicographical Anchors</h3>
            <pre class="anchors-block">{item['anchors']}</pre>
        </div>
        <div class="arabic-source" dir="rtl" lang="ar">
            <h4>النص العربي الأصيل</h4>
            <p>{item['arabic_text']}</p>
        </div>
        <hr class="apparatus-separator"/>
        <div class="english-translation">
            <h4>Verbatim English Translation</h4>
            <p>{item['translation']}</p>
        </div>
        """
        builder_bilingual.add_chapter(item["title_en"], body, chapter_index=item["chapter_index"])
    builder_bilingual.build(epub_bilingual)
    print(f"  📘 Generated Bilingual Edition: {epub_bilingual.name} ({epub_bilingual.stat().st_size / 1024:.1f} KB)")

def main():
    print("=" * 80)
    print("🌟 AYNENGINE AI v4.0 SOVEREIGN DEEP WORKER: AL-RĀGHIB AL-IṢFAHĀNĪ")
    print("=" * 80)
    
    if not CATALOG_PATH.exists():
        print("❌ Catalog not found. Running scraper first...")
        import subprocess
        subprocess.run([sys.executable, str(BASE_DIR / "scripts/scrape_all_raghib_corpus.py")])
        
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)
        
    works = catalog.get("works", [])
    print(f"Loaded {len(works)} classical works for Al-Raghib al-Isfahani.\n")
    
    # Prioritize foundational ethics & spiritual happiness works first
    priority_order = [
        "tafsil_al_nashatayn",               # 17k words (~12 sections, fastest high-impact start!)
        "al_dhariah_ila_makarim_al_shariah",  # 58k words (Ghazali foundation)
        "adab_ikhtilat_al_nas",              # 21k words (social ethics)
        "al_mufradat_fi_gharib_al_quran",    # 233k words (master lexicon)
        "jami_al_tafsir",                    # 258k words
        "muhadarat_al_udaba"                 # 378k words
    ]
    
    sorted_works = sorted(works, key=lambda w: priority_order.index(w["slug"]) if w["slug"] in priority_order else 99)
    
    for w in sorted_works:
        translate_work(w)

if __name__ == "__main__":
    main()
