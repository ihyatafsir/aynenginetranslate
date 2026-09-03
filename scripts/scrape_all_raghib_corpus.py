#!/usr/bin/env python3
"""
scrape_all_raghib_corpus.py

Scrapes and cleans all available classical works of Al-Raghib al-Isfahani (d. 502 AH)
from the OpenITI corpus.

Produces clean, machine-actionable Arabic text files in data/texts/raghib/
and a master index in catalog.json.
"""

import os
import re
import json
import time
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
DATA_DIR = BASE_DIR / "data"
RAGHIB_DIR = DATA_DIR / "texts" / "raghib"
RAGHIB_DIR.mkdir(parents=True, exist_ok=True)

RAW_BASE = "https://raw.githubusercontent.com/OpenITI/0525AH/master/data/0502RaghibIsbahani"

RAGHIB_ALL_WORKS = [
    {
        "slug": "al_mufradat_fi_gharib_al_quran",
        "title_ar": "المفردات في غريب القرآن",
        "title_en": "The Vocabulary of Rare and Sublimely Structured Quranic Terms",
        "category": "Quranic Semantics & Lexicography",
        "url": f"{RAW_BASE}/0502RaghibIsbahani.Mufradat/0502RaghibIsbahani.Mufradat.Shamela0023636-ara1"
    },
    {
        "slug": "al_dhariah_ila_makarim_al_shariah",
        "title_ar": "الذريعة إلى مكارم الشريعة",
        "title_en": "The Pathway to the Noblest Virtues of Sacred Law",
        "category": "Sacred Ethics & Moral Philosophy",
        "url": f"{RAW_BASE}/0502RaghibIsbahani.DharicaFiMakarimSharica/0502RaghibIsbahani.DharicaFiMakarimSharica.Shamela0001390-ara1"
    },
    {
        "slug": "tafsil_al_nashatayn",
        "title_ar": "تفصيل النشأتين وتحصيل السعادتين",
        "title_en": "The Exposition of the Two Developments and Attainment of the Two Felicities",
        "category": "Epistemology & Spiritual Felicity",
        "url": f"{RAW_BASE}/0502RaghibIsbahani.TafsilNashatayn/0502RaghibIsbahani.TafsilNashatayn.Shamela0021562-ara1"
    },
    {
        "slug": "jami_al_tafsir",
        "title_ar": "جامع التفسير ومقدمته",
        "title_en": "The Comprehensive Exegesis and Its Prolegomena",
        "category": "Tafsir & Exegetical Methodology",
        "url": f"{RAW_BASE}/0502RaghibIsbahani.Tafsir/0502RaghibIsbahani.Tafsir.Shamela0009231-ara1"
    },
    {
        "slug": "muhadarat_al_udaba",
        "title_ar": "محاضرات الأدباء ومحاورات الشعراء والبلغاء",
        "title_en": "Lectures of the Literati and Dialogues of the Poets and Rhetoricians",
        "category": "Classical Literature & Rhetoric",
        "url": f"{RAW_BASE}/0502RaghibIsbahani.MuhadaratUdaba/0502RaghibIsbahani.MuhadaratUdaba.Shamela0009078-ara1"
    },
    {
        "slug": "adab_ikhtilat_al_nas",
        "title_ar": "أدب مخالطة الناس",
        "title_en": "The Etiquette of Associating with People",
        "category": "Social Conduct & Spiritual Etiquette",
        "url": f"{RAW_BASE}/0502RaghibIsbahani.AdabIkhtilatNas/0502RaghibIsbahani.AdabIkhtilatNas.EScr20120414-ara1"
    }
]

def clean_openiti_text(raw_text):
    if "#META#Header#End#" in raw_text:
        body = raw_text.split("#META#Header#End#", 1)[1]
    else:
        body = raw_text
        
    body = re.sub(r'~~', '', body)
    body = re.sub(r'#\s*PageV\d+P\d+', '', body)
    body = re.sub(r'ms\d+', '', body)
    
    lines = []
    for line in body.split('\n'):
        l = line.strip()
        if not l:
            continue
        if l.startswith('### |'):
            lines.append(f"\n{l}\n")
        elif l.startswith('# '):
            lines.append(l[2:].strip())
        elif l.startswith('#'):
            lines.append(l[1:].strip())
        else:
            lines.append(l)
            
    clean = '\n'.join(lines)
    clean = re.sub(r'\n{3,}', '\n\n', clean)
    return clean.strip()

def download_and_clean_work(work):
    slug = work["slug"]
    out_file = RAGHIB_DIR / f"{slug}.txt"
    
    if out_file.exists() and out_file.stat().st_size > 1000:
        print(f"  ⚡ [{slug}] Already exists ({out_file.stat().st_size / 1024:.1f} KB). Skipping download.")
        with open(out_file, "r", encoding="utf-8") as f:
            content = f.read()
        return {
            **work,
            "file_path": str(out_file),
            "file_name": f"{slug}.txt",
            "character_count": len(content),
            "word_count": len(content.split()),
            "size_kb": round(out_file.stat().st_size / 1024, 2)
        }
        
    print(f"  📥 Downloading [{work['title_ar']}] from OpenITI...")
    req = urllib.request.Request(work["url"], headers={"User-Agent": "Mozilla/5.0 (AynEngine/3.2)"})
    
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            raw_bytes = resp.read()
            raw_text = raw_bytes.decode('utf-8', errors='ignore')
            
        cleaned = clean_openiti_text(raw_text)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(cleaned)
            
        size_kb = round(out_file.stat().st_size / 1024, 2)
        words = len(cleaned.split())
        chars = len(cleaned)
        print(f"  ✅ Saved [{slug}.txt]: {words:,} words, {size_kb} KB")
        
        return {
            **work,
            "file_path": str(out_file),
            "file_name": f"{slug}.txt",
            "character_count": chars,
            "word_count": words,
            "size_kb": size_kb
        }
    except Exception as e:
        print(f"  ❌ Error downloading [{slug}]: {e}")
        return None

def main():
    print("=" * 80)
    print("📖 AYNENGINE AI: AL-RĀGHIB AL-IṢFAHĀNĪ CORPUS INGESTION PIPELINE")
    print(f"Target Directory: {RAGHIB_DIR}")
    print("=" * 80)
    
    catalog = {
        "author": "Al-Rāghib al-Iṣfahānī (أبو القاسم الحسين بن محمد بن المفضل الراغب الأصفهاني - d. 502 AH)",
        "total_works": len(RAGHIB_ALL_WORKS),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "works": []
    }
    
    for w in RAGHIB_ALL_WORKS:
        res = download_and_clean_work(w)
        if res:
            catalog["works"].append(res)
        time.sleep(0.5)
        
    catalog_path = RAGHIB_DIR / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
        
    print("\n" + "=" * 80)
    print(f"🎉 Ingestion Complete! {len(catalog['works'])} works cataloged.")
    total_words = sum(w["word_count"] for w in catalog["works"])
    total_kb = sum(w["size_kb"] for w in catalog["works"])
    print(f"Total Corpus Volume: {total_words:,} words | {total_kb / 1024:.2f} MB")
    print(f"Master Catalog: {catalog_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
