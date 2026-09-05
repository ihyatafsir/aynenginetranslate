#!/usr/bin/env python3
"""
run_nawawi_v4_deep_worker.py

AynEngine AI v4.0 Autonomous Zero-Loss Active-RAG Engine
Re-translating the Complete Classical Corpus of Imam Abu Zakariyya Yahya ibn Sharaf al-Nawawi (d. 676 AH).

Features:
- Powered strictly by DeepSeek (deepseek-chat)
- 5-Pillar Classical RAG Grounding:
  1. Al-Mufradat (al-Raghib al-Isfahani)
  2. Asas al-Balaghah (al-Zamakhshari)
  3. Lisan al-Arab (Ibn Manzur)
  4. Kitab al-Ayn (al-Farahidi)
  5. Al-Kitab (Sibawayh)
- Dual-Pass Harmonization: References and heals all prior drafts
- Zero-Loss Standard: Sentence-safe chunking + auto-continuation on token limits
- Automated Dual-Edition EPUB Generation (Pure Scholarly & Bilingual Apparatus)
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
NAWAWI_TEXTS = DATA_DIR / "texts" / "nawawi"
NAWAWI_TRANS = DATA_DIR / "translations" / "nawawi"
NAWAWI_EPUBS = DATA_DIR / "epubs" / "nawawi"

NAWAWI_TRANS.mkdir(parents=True, exist_ok=True)
NAWAWI_EPUBS.mkdir(parents=True, exist_ok=True)

CATALOG_PATH = NAWAWI_TEXTS / "catalog.json"

PRIOR_SOURCES = [
    Path("/home/absolut7/Documents/news"),
    Path("/home/absolut7/.gemini/antigravity/scratch/nawawi"),
    Path("/home/absolut7/aynengineai/data/translations/nawawi")
]

def find_prior_draft(slug, chunk_idx):
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
                        if it.get("chapter_index") == chunk_idx or it.get("chapter_num") == chunk_idx:
                            tr = it.get("translation", "")
                            if len(tr.strip()) > 50 and not tr.startswith("[API Error"):
                                return tr.strip()
                except Exception:
                    pass
    return None

def translate_nawawi_work(work_meta):
    slug = work_meta["slug"]
    title_ar = work_meta["title_ar"]
    title_en = work_meta["title_en"]
    source_path = Path(work_meta["file_path"]) if "file_path" in work_meta else NAWAWI_TEXTS / f"{slug}.txt"
    
    trans_file = NAWAWI_TRANS / f"{slug}_v4_translated.json"
    epub_pure = NAWAWI_EPUBS / f"{slug}_pure_en.epub"
    epub_bilingual = NAWAWI_EPUBS / f"{slug}_bilingual_lexical_en.epub"
    
    print("\n" + "=" * 80)
    print(f"📖 STARTING IMAM NAWAWI WORK: {title_ar}")
    print(f"English: {title_en}")
    print(f"Slug: {slug} | Source: {source_path.name}")
    print("=" * 80)
    
    if not source_path.exists():
        print(f"❌ Error: Source file not found at {source_path}")
        return
        
    raw_text = source_path.read_text(encoding="utf-8", errors="ignore")
    
    engine = LexicographicalTranslationEngine(
        author="Imam Yahya ibn Sharaf al-Nawawi (d. 676 AH)",
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
    b_pure = AynEpubBuilder(title=title_en, author="Imam Yahya ibn Sharaf al-Nawawi (d. 676 AH)", edition_type="PURE_SCHOLARLY")
    for item in sorted(progress, key=lambda x: x["chapter_index"]):
        b_pure.add_pure_scholarly_chapter(
            title=item.get("title_en", f"Section {item.get('chapter_index', 1)}"),
            translation_text=item.get("translation", "")
        )
    b_pure.build(str(epub_pure))
    print(f"  📗 Generated Pure Edition: {epub_pure.name} ({epub_pure.stat().st_size / 1024:.1f} KB)")
    
    # 2. Bilingual Apparatus
    b_bil = AynEpubBuilder(title=f"{title_en} / {title_ar}", author="Imam Yahya ibn Sharaf al-Nawawi (d. 676 AH)", edition_type="BILINGUAL_APPARATUS")
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
    print("🌟 AYNENGINE AI v4.0: IMAM YAHYA IBN SHARAF AL-NAWAWI RE-TRANSLATION PIPELINE")
    print("=" * 80)
    
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)
        
    works = catalog.get("works", [])
    print(f"Loaded {len(works)} classical works for Imam al-Nawawi.\n")
    
    priority = [
        "al_arbaun_al_nawawiyya",             # The Forty Hadith
        "riyad_al_salihin",                   # Gardens of the Righteous
        "al_tibyan_fi_adab_hamalat_al_quran", # Etiquette of Quran Carriers
        "kitab_al_adhkar",                    # Book of Remembrances
        "bustan_al_arifin",                   # Garden of the Gnostics
        "minhaj_al_talibin",                  # The Path of Seekers (Shafi'i Fiqh)
        "al_taqrib_wa_al_taysir",             # Hadith Methodology
        "al_idah_fi_manasik_al_hajj",         # Clarification of Hajj Rites
        "adab_al_fatwa_wa_al_mufti",          # Etiquette of Fatwa
        "daqaiq_al_minhaj",                   # Subtleties of Minhaj
        "khulasat_al_ahkam",                  # Summary of Legal Judgments
        "irshad_tullab_al_haqaiq",            # Guiding Truth Seekers
        "tahrir_alfaz_al_tanbih",             # Lexical Gloss on Tanbih
        "al_masail_al_manthurah",             # Fatawa of Imam Nawawi
        "al_ijaz_fi_sharh_sunan_abi_dawud",   # Commentary on Sunan Abi Dawud
        "risalah_fi_al_itiqad",               # Epistle on Creed
        "al_usul_wa_al_dawabit",              # Legal Principles & Maxims
        "takhmis_al_ghanima",                 # Quintipartition of Spoils
        "tahdhib_al_asma_wa_al_lughat",       # Biographical & Lexical Compendium
        "sharh_sahih_muslim",                 # Al-Minhaj Commentary on Sahih Muslim
        "rawdat_al_talibin",                  # Meadow of Seekers
        "al_majmu_sharh_al_muhadhdhab"        # The Vast Compendium in Jurisprudence
    ]
    
    works_dict = {w["slug"]: w for w in works}
    ordered_works = [works_dict[s] for s in priority if s in works_dict]
    for w in works:
        if w["slug"] not in [ow["slug"] for ow in ordered_works]:
            ordered_works.append(w)
            
    for w in ordered_works:
        translate_nawawi_work(w)

if __name__ == "__main__":
    main()
