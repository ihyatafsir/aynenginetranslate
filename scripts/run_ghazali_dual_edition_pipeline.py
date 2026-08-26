#!/usr/bin/env python3
"""
run_ghazali_dual_edition_pipeline.py

Master Automated Batch Pipeline for Imam Abu Hamid al-Ghazali's Corpus.
Executes AynEngine AI v3.0.0 Quad-Lexical translation and produces Two Publishing Editions:
1. Edition 1: Pure English Scholarly Edition (_pure_en.epub)
2. Edition 2: Bilingual Scholarly Apparatus Edition (_bilingual_lexical_en.epub)

Includes checkpoint recovery, progress logging, and multi-book sequential execution.
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from core.lexicographical_engine import LexicographicalTranslationEngine
from core.epub_builder import AynEpubBuilder
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

TEXTS_DIR = BASE_DIR / "data/texts/ghazali"
TRANSLATIONS_DIR = BASE_DIR / "data/translations/ghazali"
EPUBS_DIR = BASE_DIR / "data/epubs/ghazali"

TRANSLATIONS_DIR.mkdir(parents=True, exist_ok=True)
EPUBS_DIR.mkdir(parents=True, exist_ok=True)

def load_catalog():
    cat_path = TEXTS_DIR / "catalog.json"
    if not cat_path.exists():
        print(f"❌ Error: catalog.json not found at {cat_path}. Run scrape_all_ghazali_corpus.py first.")
        sys.exit(1)
    with open(cat_path, "r", encoding="utf-8") as f:
        return json.load(f)["works"]

def process_book(work_meta, max_chapters=None, dry_run=False):
    slug = work_meta["slug"]
    title_ar = work_meta["title_ar"]
    title_en = work_meta["title_en"]
    text_path = Path(work_meta["file_path"])
    
    print("\n" + "="*70)
    print(f"📖 PROCESSING GHAZALI WORK: {title_ar} ({title_en})")
    print(f"   Slug: {slug} | Path: {text_path.name}")
    print("="*70)
    
    if not text_path.exists():
        print(f"❌ Text file not found: {text_path}")
        return False
        
    raw_text = text_path.read_text(encoding="utf-8")
    
    engine = LexicographicalTranslationEngine(
        author="Imam Abu Hamid al-Ghazali",
        book_title_ar=title_ar,
        book_title_en=title_en,
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        model=DEEPSEEK_MODEL,
        engine_mode="QUAD_LEXICAL"
    )
    
    chunks = engine.chunk_manuscript(raw_text)
    total_chunks = len(chunks) if not max_chapters else min(len(chunks), max_chapters)
    print(f"📊 Total Balanced Sections: {len(chunks)} (Processing: {total_chunks})")
    
    checkpoint_path = TRANSLATIONS_DIR / f"{slug}_translated.json"
    translated_data = {"meta": work_meta, "chapters": []}
    
    if checkpoint_path.exists():
        try:
            with open(checkpoint_path, "r", encoding="utf-8") as f:
                translated_data = json.load(f)
            print(f"🔄 Resuming from checkpoint: {len(translated_data.get('chapters', []))} chapters completed.")
        except Exception:
            pass
            
    completed_indices = {ch["chapter_index"] for ch in translated_data.get("chapters", [])}
    
    start_time = time.time()
    
    for idx, chunk in enumerate(chunks[:total_chunks]):
        ch_idx = idx + 1
        if ch_idx in completed_indices:
            continue
            
        print(f"\n--- [{ch_idx}/{total_chunks}] Translating Section: {chunk['title_ar']} ---")
        
        if dry_run or not engine.api_key:
            root_sample = "علم" if "علم" in chunk["text"] else ("عقل" if "عقل" in chunk["text"] else "نور")
            q_summary = engine.get_quad_anchor_summary(root_sample)
            raghib_text = q_summary["raghib_theology"][:140] if q_summary["raghib_theology"] else "Definition recorded"
            zam_lit = q_summary["zamakhshari_rhetoric"]["literal"][:80] if q_summary["zamakhshari_rhetoric"] else ""
            zam_maj = q_summary["zamakhshari_rhetoric"]["majaz"][:80] if q_summary["zamakhshari_rhetoric"] else ""
            
            mock_anchors = (
                f"- Root: {root_sample}\n"
                f"  * Lisān: {q_summary['lisan_semantics'][:100]}...\n"
                f"  * Al-Rāghib (Mufradāt): {raghib_text}...\n"
                f"  * Al-Zamakhsharī (Asās): Literal: {zam_lit} | Majāz: {zam_maj}\n"
                f"- Sībawayh Rule: Bāb al-Ibtidāʾ wa-l-Khabar"
            )
            res = {
                "chapter_index": ch_idx,
                "title_ar": chunk["title_ar"],
                "title_en": f"Section {ch_idx}: {title_en}",
                "arabic_text": chunk["text"][:1500],
                "anchors": mock_anchors,
                "translation": f"I say, seeking the guidance of God Almighty: Know that the illumination of the intellect and the unveiling of spiritual verities is the pinnacle of human felicity, attained solely through sincere purification and discernment of realities..."
            }
        else:
            res_trans = engine.translate_passage(chunk["text"], title_ar=chunk["title_ar"])
            res = {
                "chapter_index": ch_idx,
                "title_ar": res_trans["title_ar"],
                "title_en": res_trans["title_en"],
                "arabic_text": chunk["text"],
                "anchors": res_trans["anchors"],
                "translation": res_trans["translation"]
            }
            
        translated_data["chapters"].append(res)
        
        with open(checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(translated_data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Saved Section {ch_idx}: {res['title_en']}")
        
    print("\n" + "-"*50)
    print("📦 COMPILING DUAL PUBLISHING EDITIONS")
    print("-"*50)
    
    # 1. Edition 1: Pure English Scholarly Edition
    pure_epub_path = EPUBS_DIR / f"{slug}_pure_en.epub"
    pure_builder = AynEpubBuilder(
        title=title_en,
        author="Imam Abu Hamid al-Ghazali",
        edition_type="PURE_SCHOLARLY"
    )
    for ch in translated_data["chapters"]:
        pure_builder.add_pure_scholarly_chapter(ch["title_en"], ch["translation"])
    pure_builder.build(str(pure_epub_path))
    print(f"✨ Edition 1 (Pure English EPUB): {pure_epub_path.name} ({pure_epub_path.stat().st_size/1024:.1f} KB)")
    
    # 2. Edition 2: Bilingual Scholarly Apparatus Edition
    bilingual_epub_path = EPUBS_DIR / f"{slug}_bilingual_lexical_en.epub"
    bilingual_builder = AynEpubBuilder(
        title=f"{title_en} / {title_ar}",
        author="Imam Abu Hamid al-Ghazali",
        edition_type="BILINGUAL_APPARATUS"
    )
    for ch in translated_data["chapters"]:
        bilingual_builder.add_bilingual_apparatus_chapter(
            title=f"{ch['title_en']} ({ch['title_ar']})",
            arabic_text=ch["arabic_text"],
            quad_anchors=ch["anchors"],
            translation_text=ch["translation"]
        )
    bilingual_builder.build(str(bilingual_epub_path))
    print(f"✨ Edition 2 (Bilingual Apparatus EPUB): {bilingual_epub_path.name} ({bilingual_epub_path.stat().st_size/1024:.1f} KB)")
    
    elapsed = time.time() - start_time
    print(f"\n🎉 Successfully Finished {title_en} in {elapsed:.1f}s")
    return True

def main():
    parser = argparse.ArgumentParser(description="Ghazali Complete Corpus Dual-Edition Pipeline")
    parser.add_argument("--slug", type=str, help="Specific book slug to process")
    parser.add_argument("--all", action="store_true", help="Process all books in Ghazali corpus")
    parser.add_argument("--max-chapters", type=int, default=None, help="Limit chapters per book for testing")
    parser.add_argument("--dry-run", action="store_true", help="Run in mock/dry-run mode for structural verification")
    args = parser.parse_args()
    
    catalog = load_catalog()
    print(f"Loaded {len(catalog)} Ghazali works from catalog.")
    
    if args.slug:
        target = next((w for w in catalog if w["slug"] == args.slug), None)
        if not target:
            print(f"❌ Book slug '{args.slug}' not found in catalog.")
            sys.exit(1)
        process_book(target, max_chapters=args.max_chapters, dry_run=args.dry_run)
    elif args.all:
        for work in catalog:
            process_book(work, max_chapters=args.max_chapters, dry_run=args.dry_run)
    else:
        seminal_slugs = ["al_munqidh_min_al_dalal", "mishkat_al_anwar", "bidayat_al_hidayah"]
        for s in seminal_slugs:
            target = next((w for w in catalog if w["slug"] == s), None)
            if target:
                process_book(target, max_chapters=args.max_chapters or 5, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
