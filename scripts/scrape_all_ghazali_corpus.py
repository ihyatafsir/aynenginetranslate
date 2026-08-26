#!/usr/bin/env python3
"""
scrape_all_ghazali_corpus.py

Scrapes and cleans all 28 digitized classical masterworks of Imam Abu Hamid al-Ghazali (d. 505 AH)
from the OpenITI corpus using direct raw endpoints (no rate limits).

Produces clean, machine-actionable Arabic text files in data/texts/ghazali/
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
GHAZALI_DIR = DATA_DIR / "texts" / "ghazali"
GHAZALI_DIR.mkdir(parents=True, exist_ok=True)

RAW_BASE = "https://raw.githubusercontent.com/OpenITI/0525AH/master/data/0505Ghazali"

GHAZALI_ALL_WORKS = [
    {
        "slug": "ihya_ulum_al_din",
        "title_ar": "إحياء علوم الدين",
        "title_en": "The Revival of the Religious Sciences",
        "category": "Spirituality & Ethics",
        "url": f"{RAW_BASE}/0505Ghazali.IhyaCulumDin/0505Ghazali.IhyaCulumDin.Shamela0009472-ara1.completed"
    },
    {
        "slug": "al_munqidh_min_al_dalal",
        "title_ar": "المنقذ من الضلال والمفصح عن الأحوال",
        "title_en": "Deliverance from Error",
        "category": "Autobiography & Epistemology",
        "url": f"{RAW_BASE}/0505Ghazali.Munqidh/0505Ghazali.Munqidh.Shamela0009246-ara1"
    },
    {
        "slug": "tahafut_al_falasifa",
        "title_ar": "تهافت الفلاسفة",
        "title_en": "The Incoherence of the Philosophers",
        "category": "Philosophy & Kalam",
        "url": f"{RAW_BASE}/0505Ghazali.Tahafut/0505Ghazali.Tahafut.Shamela0011055-ara1"
    },
    {
        "slug": "bidayat_al_hidayah",
        "title_ar": "بداية الهداية",
        "title_en": "The Beginning of Guidance",
        "category": "Praxis & Devotion",
        "url": f"{RAW_BASE}/0505Ghazali.BidayatHidaya/0505Ghazali.BidayatHidaya.Shamela0012718-ara1"
    },
    {
        "slug": "mishkat_al_anwar",
        "title_ar": "مشكاة الأنوار",
        "title_en": "The Niche of Lights",
        "category": "Esoteric Metaphysics",
        "url": f"{RAW_BASE}/0505Ghazali.MishkatAnwar/0505Ghazali.MishkatAnwar.Shamela0012421-ara1"
    },
    {
        "slug": "al_iqtisad_fi_al_itiqad",
        "title_ar": "الاقتصاد في الاعتقاد",
        "title_en": "Moderation in Belief",
        "category": "Kalam & Theology",
        "url": f"{RAW_BASE}/0505Ghazali.Iqtisad/0505Ghazali.Iqtisad.Shamela0009217-ara1"
    },
    {
        "slug": "kimiya_yi_saadat",
        "title_ar": "كيمياء السعادة",
        "title_en": "The Alchemy of Happiness",
        "category": "Spirituality",
        "url": f"{RAW_BASE}/0505Ghazali.KimiyaSacada/0505Ghazali.KimiyaSacada.Shamela0009261-ara1"
    },
    {
        "slug": "al_mustasfa",
        "title_ar": "المستصفى من علم الأصول",
        "title_en": "The Distilled Principles of Jurisprudence",
        "category": "Usul al-Fiqh",
        "url": f"{RAW_BASE}/0505Ghazali.Mustasfa/0505Ghazali.Mustasfa.Shamela0005459-ara1"
    },
    {
        "slug": "maqasid_al_falasifah",
        "title_ar": "مقاصد الفلاسفة",
        "title_en": "The Aims of the Philosophers",
        "category": "Philosophy",
        "url": f"{RAW_BASE}/0505Ghazali.MaqasidFalasifa/0505Ghazali.MaqasidFalasifa.ALCorpus00027-ara1"
    },
    {
        "slug": "mizan_al_amal",
        "title_ar": "ميزان العمل",
        "title_en": "The Criterion of Moral Action",
        "category": "Ethics & Philosophy",
        "url": f"{RAW_BASE}/0505Ghazali.MizanCamal/0505Ghazali.MizanCamal.Shamela0009264-ara1"
    },
    {
        "slug": "al_maqsad_al_asna",
        "title_ar": "المقصد الأسنى في شرح معاني أسماء الله الحسنى",
        "title_en": "The Noblest Goal in Explaining the Divine Names",
        "category": "Theology & Metaphysics",
        "url": f"{RAW_BASE}/0505Ghazali.MaqsadAsna/0505Ghazali.MaqsadAsna.Shamela0006465-ara1"
    },
    {
        "slug": "jawahir_al_quran",
        "title_ar": "جواهر القرآن ودرره",
        "title_en": "Jewels of the Quran",
        "category": "Quranic Sciences",
        "url": f"{RAW_BASE}/0505Ghazali.JawahirQuran/0505Ghazali.JawahirQuran.Shamela0009883-ara1"
    },
    {
        "slug": "minhaj_al_abidin",
        "title_ar": "منهاج العابدين إلى جنة رب العالمين",
        "title_en": "The Path of the Worshippers",
        "category": "Spirituality",
        "url": f"{RAW_BASE}/0505Ghazali.MinhajCabidin/0505Ghazali.MinhajCabidin.Kraken220414225509-ara1"
    },
    {
        "slug": "qawaid_al_aqaid",
        "title_ar": "قواعد العقائد",
        "title_en": "The Foundations of the Articles of Faith",
        "category": "Creed & Kalam",
        "url": f"{RAW_BASE}/0505Ghazali.QawacidCaqaid/0505Ghazali.QawacidCaqaid.Shamela0006397-ara1"
    },
    {
        "slug": "miyar_al_ilm",
        "title_ar": "معيار العلم في فن المنطق",
        "title_en": "The Standard Measure of Knowledge (Logic)",
        "category": "Logic & Dialectic",
        "url": f"{RAW_BASE}/0505Ghazali.MicyarCilm/0505Ghazali.MicyarCilm.Shamela0026575-ara1"
    },
    {
        "slug": "mihakk_al_nazar",
        "title_ar": "محك النظر في المنطق",
        "title_en": "The Touchstone of Reasoning",
        "category": "Logic & Dialectic",
        "url": f"{RAW_BASE}/0505Ghazali.MahkNazar/0505Ghazali.MahkNazar.Shamela0026538-ara1"
    },
    {
        "slug": "maarij_al_quds",
        "title_ar": "معارج القدس في مدارج معرفة النفس",
        "title_en": "The Ascents of Holiness in Knowledge of the Soul",
        "category": "Psychology & Metaphysics",
        "url": f"{RAW_BASE}/0505Ghazali.MacarijQuds/0505Ghazali.MacarijQuds.Shamela0006494-ara1"
    },
    {
        "slug": "fadaih_al_batiniyya",
        "title_ar": "فضائح الباطنية وفضائل المستظهرية",
        "title_en": "The Infamies of the Batinites",
        "category": "Polemics & Kalam",
        "url": f"{RAW_BASE}/0505Ghazali.Fadaih/0505Ghazali.Fadaih.Shamela0006554-ara1"
    },
    {
        "slug": "al_radd_al_jamil",
        "title_ar": "الرد الجميل لإلهية عيسى بصريح الإنجيل",
        "title_en": "The Elegant Refutation",
        "category": "Comparative Theology",
        "url": f"{RAW_BASE}/0505Ghazali.RaddJamil/0505Ghazali.RaddJamil.ShamAY0033896-ara1"
    },
    {
        "slug": "majmuat_rasail_al_ghazali",
        "title_ar": "مجموعة رسائل الإمام الغزالي",
        "title_en": "Collected Epistles of Imam al-Ghazali",
        "category": "Epistles & Treatises",
        "url": f"{RAW_BASE}/0505Ghazali.MajmucatRasail/0505Ghazali.MajmucatRasail.ShamAY0034794-ara1"
    },
    {
        "slug": "al_mankhul",
        "title_ar": "المنخول من تعليقات الأصول",
        "title_en": "The Sifted Treatise on Legal Theory",
        "category": "Usul al-Fiqh",
        "url": f"{RAW_BASE}/0505Ghazali.Mankhul/0505Ghazali.Mankhul.Shamela0003960-ara1"
    },
    {
        "slug": "shifa_al_ghalil",
        "title_ar": "شفاء الغليل في بيان الشبه والمخيل",
        "title_en": "Healing the Thirst on Legal Causality",
        "category": "Usul al-Fiqh",
        "url": f"{RAW_BASE}/0505Ghazali.ShifaGhalil/0505Ghazali.ShifaGhalil.Sham19Y0017827-ara1"
    },
    {
        "slug": "asnaf_al_maghrurin",
        "title_ar": "كشف المناهج والأصناف في حظوظ أهل الغرور والاعتساف",
        "title_en": "The Categories of the Deluded",
        "category": "Spiritual Psychology",
        "url": f"{RAW_BASE}/0505Ghazali.AsnafMaghrurin/0505Ghazali.AsnafMaghrurin.Shamela0009198-ara1"
    },
    {
        "slug": "sirr_al_alamin",
        "title_ar": "سر العالمين وكشف ما في الدارين",
        "title_en": "The Secret of the Two Worlds",
        "category": "Metaphysics",
        "url": f"{RAW_BASE}/0505Ghazali.SirrCalamin/0505Ghazali.SirrCalamin.JK009402-ara1"
    },
    {
        "slug": "al_tibr_al_masbuk",
        "title_ar": "التبر المسبوك في نصيحة الملوك",
        "title_en": "Counsel for Kings",
        "category": "Political Ethics",
        "url": f"{RAW_BASE}/0505Ghazali.TibrMasbuk/0505Ghazali.TibrMasbuk.Shamela0004129-ara1"
    },
    {
        "slug": "al_wajiz",
        "title_ar": "الوجيز في فقه الإمام الشافعي",
        "title_en": "The Epitome of Shafi'i Jurisprudence",
        "category": "Fiqh",
        "url": f"{RAW_BASE}/0505Ghazali.Wajiz/0505Ghazali.Wajiz.JK000308-ara1"
    },
    {
        "slug": "al_wasit",
        "title_ar": "الوسيط في المذهب",
        "title_en": "The Intermediate Compendium in Jurisprudence",
        "category": "Fiqh",
        "url": f"{RAW_BASE}/0505Ghazali.Wasit/0505Ghazali.Wasit.Shamela0006128-ara1"
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
            
    cleaned = '\n'.join(lines)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()

def scrape_all():
    print("==================================================================")
    print("📚 AYNENGINE AI: IMAM AL-GHAZALI CORPUS SCRAPER (27 MASTERWORKS)")
    print("==================================================================")
    
    catalog = []
    
    for item in GHAZALI_ALL_WORKS:
        dest_filename = f"{item['slug']}.txt"
        dest_path = GHAZALI_DIR / dest_filename
        
        print(f"\n📥 Processing: {item['title_ar']} ({item['title_en']})")
        print(f"   URL: {item['url']}")
        
        try:
            if dest_path.exists() and dest_path.stat().st_size > 5000:
                print(f"   ✅ Local cache verified: {dest_path.name} ({dest_path.stat().st_size/1024:.1f} KB)")
                cleaned_text = dest_path.read_text(encoding="utf-8")
            else:
                req = urllib.request.Request(item['url'], headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    raw_bytes = resp.read()
                    raw_text = raw_bytes.decode("utf-8", errors="ignore")
                    
                cleaned_text = clean_openiti_text(raw_text)
                dest_path.write_text(cleaned_text, encoding="utf-8")
                print(f"   ✅ Downloaded & cleaned: {dest_filename}")
                
            char_count = len(cleaned_text)
            word_count = len(cleaned_text.split())
            size_kb = dest_path.stat().st_size / 1024
            
            entry = {
                "slug": item["slug"],
                "title_ar": item["title_ar"],
                "title_en": item["title_en"],
                "category": item["category"],
                "file_path": str(dest_path),
                "file_name": dest_filename,
                "download_url": item["url"],
                "character_count": char_count,
                "word_count": word_count,
                "size_kb": round(size_kb, 2)
            }
            catalog.append(entry)
            print(f"   📊 Stats: {char_count:,} chars | {word_count:,} words ({size_kb:.1f} KB)")
        except Exception as e:
            print(f"   ❌ Failed to ingest {item['slug']}: {e}")
            
    # Save master catalog
    catalog_path = GHAZALI_DIR / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({
            "author": "Imam Abu Hamid al-Ghazali (d. 505 AH)",
            "total_works": len(catalog),
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "works": catalog
        }, f, ensure_ascii=False, indent=2)
        
    print(f"\n🎉 Successfully Ingested All {len(catalog)} Ghazali Masterworks -> {catalog_path}")
    return catalog

if __name__ == "__main__":
    scrape_all()
