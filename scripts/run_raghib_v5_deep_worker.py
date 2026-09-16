#!/usr/bin/env python3
"""
run_raghib_v5_deep_worker.py

AynEngine AI v5.0.0 Sovereign Morphological Edition Autonomous Zero-Loss Active-RAG Engine
Re-translating the Complete Classical Corpus of Imam Abu al-Qasim al-Husayn ibn Muhammad al-Raghib al-Isfahani (d. 502 AH).

Features:
- Powered strictly by DeepSeek (deepseek-chat)
- 5-Pillar Classical RAG Grounding:
  1. Al-Mufradat (al-Raghib al-Isfahani)
  2. Asas al-Balaghah (al-Zamakhshari)
  3. Lisan al-Arab (Ibn Manzur)
  4. Kitab al-Ayn (al-Farahidi)
  5. Al-Kitab (Sibawayh)
- v5.0.0 Classical Arabic awzan reduction and root extraction
- Dual-Pass Harmonization: References and heals all prior drafts
- Zero-Loss Standard: Sentence-safe chunking + auto-continuation on token limits
- Automated Dual-Edition EPUB Generation (Pure Scholarly & Bilingual Apparatus)
- Instant WyreSup distribution sync
"""

import os
import sys
import json
import time
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from core.lexicographical_engine import LexicographicalTranslationEngine
from core.epub_builder import AynEpubBuilder

DATA_DIR = BASE_DIR / "data"
RAGHIB_TEXTS = DATA_DIR / "texts" / "raghib"
RAGHIB_TRANS = DATA_DIR / "translations" / "raghib"
RAGHIB_EPUBS = DATA_DIR / "epubs" / "raghib"

RAGHIB_TRANS.mkdir(parents=True, exist_ok=True)
RAGHIB_EPUBS.mkdir(parents=True, exist_ok=True)

WYRESUP_EPUBS = Path("/home/absolut7/Documents/news/wyresup-mesh-app/public/epubs")
CATALOG_PATH = RAGHIB_TEXTS / "catalog.json"

PRIOR_SOURCES = [
    Path("/home/absolut7/Documents/news"),
    Path("/home/absolut7/.gemini/antigravity/scratch/translation_engine_framework/data/translations/raghib"),
    Path("/home/absolut7/aynengineai/data/translations/raghib")
]

def find_prior_draft(slug, chunk_idx):
    for p_dir in PRIOR_SOURCES:
        candidate_files = [
            p_dir / f"{slug}_v5_translated.json",
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
                        if it.get("chapter_index") == chunk_idx or it.get("chapter_num") == chunk_idx:
                            tr = it.get("translation", "")
                            if len(tr.strip()) > 50 and not tr.startswith("[API Error"):
                                return tr.strip()
                except Exception:
                    pass
    return None

def translate_raghib_work(work_meta):
    slug = work_meta["slug"]
    title_ar = work_meta["title_ar"]
    title_en = work_meta["title_en"]
    source_path = Path(work_meta["file_path"]) if "file_path" in work_meta else RAGHIB_TEXTS / f"{slug}.txt"
    
    trans_file = RAGHIB_TRANS / f"{slug}_v5_translated.json"
    epub_pure = RAGHIB_EPUBS / f"{slug}_pure_en.epub"
    epub_bilingual = RAGHIB_EPUBS / f"{slug}_bilingual_lexical_en.epub"
    
    print("\n" + "=" * 80)
    print(f"📖 STARTING IMAM RAGHIB WORK (v5 Sovereign Engine): {title_ar}")
    print(f"English: {title_en}")
    print(f"Slug: {slug} | Source: {source_path.name}")
    print("=" * 80)
    
    if not source_path.exists():
        print(f"❌ Error: Source file not found at {source_path}")
        return
        
    raw_text = source_path.read_text(encoding="utf-8", errors="ignore")
    
    engine = LexicographicalTranslationEngine(
        author="Imam Abu al-Qasim al-Husayn ibn Muhammad al-Raghib al-Isfahani (d. 502 AH)",
        book_title_ar=title_ar,
        book_title_en=title_en,
        max_chunk_chars=3200
    )
    
    chunks = engine.chunk_manuscript(raw_text)
    total_chunks = len(chunks)
    print(f"🧩 Partitioned into {total_chunks} sentence-safe chunks (Zero-Loss v5 standard).")
    
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
            
    print(f"\n📚 Translation complete for {slug}! Building Dual-Edition v5 EPUBs...")
    
    # 1. Pure English
    b_pure = AynEpubBuilder(title=title_en, author="Imam al-Raghib al-Isfahani (d. 502 AH)", edition_type="PURE_SCHOLARLY")
    for item in sorted(progress, key=lambda x: x["chapter_index"]):
        b_pure.add_pure_scholarly_chapter(
            title=item.get("title_en", f"Section {item.get('chapter_index', 1)}"),
            translation_text=item.get("translation", "")
        )
    b_pure.build(str(epub_pure))
    print(f"  📗 Generated Pure Edition: {epub_pure.name} ({epub_pure.stat().st_size / 1024:.1f} KB)")
    
    # 2. Bilingual Apparatus
    b_bil = AynEpubBuilder(title=f"{title_en} / {title_ar}", author="Imam al-Raghib al-Isfahani (d. 502 AH)", edition_type="BILINGUAL_APPARATUS")
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

    # 3. WyreSup instant sync
    if WYRESUP_EPUBS.exists():
        try:
            shutil.copy2(epub_pure, WYRESUP_EPUBS / epub_pure.name)
            shutil.copy2(epub_bilingual, WYRESUP_EPUBS / epub_bilingual.name)
            print(f"  🔄 Synced {epub_pure.name} and {epub_bilingual.name} to WyreSup public/epubs")
        except Exception as e:
            print(f"  ⚠️ WyreSup sync error: {e}")

def main():
    print("=" * 80)
    print("🌟 AYNENGINE AI v5.0.0: IMAM AL-RAGHIB AL-ISFAHANI RE-TRANSLATION PIPELINE")
    print("=" * 80)
    
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)
        
    works = catalog.get("works", [])
    print(f"Loaded {len(works)} classical works for Imam al-Raghib al-Isfahani.\n")
    
    priority = [
        "al_mufradat_fi_gharib_al_quran",
        "al_dhariah_ila_makarim_al_shariah",
        "tafsil_al_nashatayn",
        "adab_ikhtilat_al_nas",
        "jami_al_tafsir",
        "muhadarat_al_udaba"
    ]
    
    works_dict = {w["slug"]: w for w in works}
    ordered_works = [works_dict[s] for s in priority if s in works_dict]
    for w in works:
        if w["slug"] not in [ow["slug"] for ow in ordered_works]:
            ordered_works.append(w)
            
    for w in ordered_works:
        translate_raghib_work(w)

if __name__ == "__main__":
    main()
