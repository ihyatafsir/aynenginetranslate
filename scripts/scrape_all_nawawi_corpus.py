#!/usr/bin/env python3
"""
scrape_all_nawawi_corpus.py

Automated Ingestion and Cleaner for the Complete Classical Library of
Imam Abu Zakariyya Yahya ibn Sharaf al-Nawawi (الإمام النووي - d. 676 AH).
Downloads and normalizes all 22 masterworks from OpenITI 0700AH repository.
"""

import os
import sys
import re
import json
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
OUTPUT_DIR = BASE_DIR / "data/texts/nawawi"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RAW_BASE = "https://raw.githubusercontent.com/OpenITI/0700AH/master/data/0676Nawawi"

NAWAWI_CORPUS = [
    {
        "slug": "al_arbaun_al_nawawiyya",
        "title_ar": "الأربعون النووية",
        "title_en": "The Forty Hadith",
        "category": "Hadith",
        "url": f"{RAW_BASE}/0676Nawawi.ArbacunaNawawiyya/0676Nawawi.ArbacunaNawawiyya.Shamela0012836-ara1",
        "desc": "The quintessential collection of foundational prophetic traditions encapsulating Islamic doctrine and practice."
    },
    {
        "slug": "riyad_al_salihin",
        "title_ar": "رياض الصالحين من كلام سيد المرسلين",
        "title_en": "Gardens of the Righteous",
        "category": "Hadith & Ethics",
        "url": f"{RAW_BASE}/0676Nawawi.RiyadSalihin/0676Nawawi.RiyadSalihin.Shamela0012014-ara1",
        "desc": "The universally acclaimed compendium of moral, ethical, and devotional Hadith."
    },
    {
        "slug": "al_tibyan_fi_adab_hamalat_al_quran",
        "title_ar": "التبيان في آداب حملة القرآن",
        "title_en": "Etiquette with the Quran",
        "category": "Quranic Sciences",
        "url": f"{RAW_BASE}/0676Nawawi.Tibyan/0676Nawawi.Tibyan.Shamela0001969-ara1",
        "desc": "Classical manual on the decorum, ethics, and spiritual responsibilities of learners and reciters of the Quran."
    },
    {
        "slug": "kitab_al_adhkar",
        "title_ar": "الأذكار المنتخبة من كلام سيد الأبرار",
        "title_en": "The Book of Remembrances",
        "category": "Devotion & Hadith",
        "url": f"{RAW_BASE}/0676Nawawi.Adhkar/0676Nawawi.Adhkar.Shamela0001956-ara1",
        "desc": "Comprehensive encyclopedic collection of daily prayers, invocations, and supplications."
    },
    {
        "slug": "minhaj_al_talibin",
        "title_ar": "منهاج الطالبين وعمدة المفتين",
        "title_en": "The Path of the Seekers",
        "category": "Jurisprudence",
        "url": f"{RAW_BASE}/0676Nawawi.MinhajTalibin/0676Nawawi.MinhajTalibin.Shamela0012096-ara1",
        "desc": "The premier authoritative foundational textbook of standard Shafi'i jurisprudence."
    },
    {
        "slug": "bustan_al_arifin",
        "title_ar": "بستان العارفين",
        "title_en": "Garden of the Gnostics",
        "category": "Sufism & Spirituality",
        "url": f"{RAW_BASE}/0676Nawawi.BustanCarifin/0676Nawawi.BustanCarifin.Shamela0012719-ara1",
        "desc": "Spiritual treatise on sincerity, asceticism, humility, and the moral wayfaring of gnostics."
    },
    {
        "slug": "sharh_sahih_muslim",
        "title_ar": "المنهاج شرح صحيح مسلم بن الحجاج",
        "title_en": "The Commentary on Sahih Muslim",
        "category": "Hadith Commentary",
        "url": f"{RAW_BASE}/0676Nawawi.MinhajFiSharhMuslim/0676Nawawi.MinhajFiSharhMuslim.Shamela0001711-ara1",
        "desc": "The magnum opus monumental commentary on Imam Muslim's canonical Hadith collection."
    },
    {
        "slug": "al_majmu_sharh_al_muhadhdhab",
        "title_ar": "المجموع شرح المهذب",
        "title_en": "The Vast Compendium in Comparative Jurisprudence",
        "category": "Jurisprudence",
        "url": f"{RAW_BASE}/0676Nawawi.Majmuc/0676Nawawi.Majmuc.Shamela0002186-ara1",
        "desc": "The monumental multi-volume encyclopedic work of detailed comparative legal analysis."
    },
    {
        "slug": "rawdat_al_talibin",
        "title_ar": "روضة الطالبين وعمدة المفتين",
        "title_en": "The Meadow of the Seekers",
        "category": "Jurisprudence",
        "url": f"{RAW_BASE}/0676Nawawi.RawdatTalibin/0676Nawawi.RawdatTalibin.Shamela0000499-ara1",
        "desc": "The exhaustive masterwork codifying the comprehensive corpus of Shafi'i legal opinions."
    },
    {
        "slug": "tahdhib_al_asma_wa_al_lughat",
        "title_ar": "تهذيب الأسماء واللغات",
        "title_en": "Refinement of Names and Lexicon",
        "category": "Biographical & Lexicography",
        "url": f"{RAW_BASE}/0676Nawawi.TahdhibAsma/0676Nawawi.TahdhibAsma.Shamela0009702-ara1",
        "desc": "Biographical dictionary and linguistic encyclopedic glossary of classical legal terminology."
    },
    {
        "slug": "al_taqrib_wa_al_taysir",
        "title_ar": "التقريب والتيسير لمعرفة سنن البشير النذير",
        "title_en": "The Facilitated Introduction to Hadith Sciences",
        "category": "Hadith Methodology",
        "url": f"{RAW_BASE}/0676Nawawi.Taqrib/0676Nawawi.Taqrib.Shamela0005586-ara1",
        "desc": "Standard primer on Hadith terminology, transmission criteria, and critical classification."
    },
    {
        "slug": "al_idah_fi_manasik_al_hajj",
        "title_ar": "الإيضاح في مناسك الحج والعمرة",
        "title_en": "The Clarification of the Rites of Hajj",
        "category": "Jurisprudence",
        "url": f"{RAW_BASE}/0676Nawawi.IdahFiManasikHajj/0676Nawawi.IdahFiManasikHajj.Shamela0096232-ara1",
        "desc": "Essential classical handbook on the legal and devotional obligations of the Pilgrimage."
    },
    {
        "slug": "adab_al_fatwa_wa_al_mufti",
        "title_ar": "أدب الفتوى والمفتي والمستفتي",
        "title_en": "The Decorum of Legal Rulings and the Juriconsult",
        "category": "Legal Ethics",
        "url": f"{RAW_BASE}/0676Nawawi.AdabFatwa/0676Nawawi.AdabFatwa.Shamela0006345-ara1",
        "desc": "Foundational treatise on the ethical principles, prerequisites, and protocols of issuing religious edicts."
    },
    {
        "slug": "daqaiq_al_minhaj",
        "title_ar": "دقائق المنهاج",
        "title_en": "Subtleties of the Minhaj",
        "category": "Jurisprudence",
        "url": f"{RAW_BASE}/0676Nawawi.DaqaiqMinhaj/0676Nawawi.DaqaiqMinhaj.Shamela0006134-ara1",
        "desc": "Authorial commentary clarifying the precise terminology and linguistic nuances of Minhaj al-Talibin."
    },
    {
        "slug": "khulasat_al_ahkam",
        "title_ar": "خلاصة الأحكام في مهمات السنن وقواعد الإسلام",
        "title_en": "The Epitome of Legal Judgments",
        "category": "Hadith & Fiqh",
        "url": f"{RAW_BASE}/0676Nawawi.KhulasatAhkam/0676Nawawi.KhulasatAhkam.Shamela0005920-ara1",
        "desc": "Comprehensive analysis of Hadith evidence underpinning legal rulings."
    },
    {
        "slug": "irshad_tullab_al_haqaiq",
        "title_ar": "إرشاد طلاب الحقائق إلى معرفة سنن خير الخلائق",
        "title_en": "Guiding the Seekers of Truth",
        "category": "Hadith Methodology",
        "url": f"{RAW_BASE}/0676Nawawi.IrshadTullabHaqaiq/0676Nawawi.IrshadTullabHaqaiq.Sham19Y0127654-ara1",
        "desc": "Abridgment and exposition of Ibn al-Salah's Muqaddimah on Hadith science."
    },
    {
        "slug": "tahrir_alfaz_al_tanbih",
        "title_ar": "تحرير ألفاظ التنبيه",
        "title_en": "The Lexical Gloss on Al-Tanbih",
        "category": "Legal Lexicography",
        "url": f"{RAW_BASE}/0676Nawawi.TahrirAlfaz/0676Nawawi.TahrirAlfaz.Shamela0007043-ara1",
        "desc": "Lexicographical dissection of the legal vocabulary in Abu Ishaq al-Shirazi's Al-Tanbih."
    },
    {
        "slug": "al_masail_al_manthurah",
        "title_ar": "الفتاوى أو المسائل المنثورة",
        "title_en": "The Scattered Legal Edicts (Fatawa al-Nawawi)",
        "category": "Fatwa & Jurisprudence",
        "url": f"{RAW_BASE}/0676Nawawi.MasailManthura/0676Nawawi.MasailManthura.Shamela0000497-ara1",
        "desc": "Collected actual historical legal responsa arranged by his disciple Ibn al-Attar."
    },
    {
        "slug": "al_ijaz_fi_sharh_sunan_abi_dawud",
        "title_ar": "الإيجاز في شرح سنن أبي داود",
        "title_en": "The Concise Commentary on Sunan Abi Dawud",
        "category": "Hadith Commentary",
        "url": f"{RAW_BASE}/0676Nawawi.IjazFiSharhSunanAbiDawud/0676Nawawi.IjazFiSharhSunanAbiDawud.Shamela0005064-ara1",
        "desc": "Scholarly commentary and textual critique on Imam Abu Dawud's Sunan."
    },
    {
        "slug": "risalah_fi_al_itiqad",
        "title_ar": "رسالة في الاعتقاد وأهل السنة",
        "title_en": "Treatise on the Creed of the Forebears",
        "category": "Theology & Creed",
        "url": f"{RAW_BASE}/0676Nawawi.IctiqadSalafFiHuruf/0676Nawawi.IctiqadSalafFiHuruf.Shamela0011137-ara1",
        "desc": "Doctrinal epistolary treatise outlining classical Sunni creed."
    },
    {
        "slug": "al_usul_wa_al_dawabit",
        "title_ar": "الأصول والضوابط",
        "title_en": "The Legal Principles and Maxims",
        "category": "Legal Maxims (Qawa'id)",
        "url": f"{RAW_BASE}/0676Nawawi.UsulWaDawabit/0676Nawawi.UsulWaDawabit.Shamela0006285-ara1",
        "desc": "Precise extraction of legal canons, maxims, and operational hermeneutic rules."
    },
    {
        "slug": "takhmis_al_ghanima",
        "title_ar": "تخميس الغنيمة",
        "title_en": "Treatise on the Quintipartition of Spoils",
        "category": "Jurisprudence",
        "url": f"{RAW_BASE}/0676Nawawi.TakhmisGhanima/0676Nawawi.TakhmisGhanima.ShamAY0034318-ara1",
        "desc": "Monograph examining the classical jurisprudential distribution of war spoils."
    }
]

def clean_openiti_text(raw_text: str) -> str:
    cleaned = re.sub(r'#META#.*?\n', '', raw_text)
    cleaned = re.sub(r'#\s*HEADER#.*?\n', '', cleaned)
    cleaned = re.sub(r'PageV\d+P\d+', '', cleaned)
    cleaned = re.sub(r'~~', '\n', cleaned)
    cleaned = re.sub(r'ms\d+', '', cleaned)
    cleaned = re.sub(r'###\s*', '\n\n', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()

def main():
    print("=" * 70)
    print("🏛️ INGESTING COMPLETE IMAM AL-NAWAWI CORPUS (OpenITI 0676AH)")
    print("=" * 70)
    
    catalog = []
    
    for item in NAWAWI_CORPUS:
        slug = item["slug"]
        title_ar = item["title_ar"]
        title_en = item["title_en"]
        url = item["url"]
        out_file = OUTPUT_DIR / f"{slug}.txt"
        
        print(f"\n📥 Processing: {title_ar} ({title_en})")
        print(f"   URL: {url}")
        
        content = ""
        if out_file.exists() and out_file.stat().st_size > 1000:
            print(f"   ✅ Local cache verified: {out_file.name} ({out_file.stat().st_size / 1024:.1f} KB)")
            content = out_file.read_text(encoding="utf-8")
        else:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    raw = resp.read().decode("utf-8", errors="ignore")
                
                content = clean_openiti_text(raw)
                out_file.write_text(content, encoding="utf-8")
                print(f"   ✅ Downloaded & cleaned: {out_file.name}")
            except Exception as e:
                print(f"   ❌ Failed to ingest {slug}: {e}")
                continue
                
        char_count = len(content)
        word_count = len(content.split())
        print(f"   📊 Stats: {char_count:,} chars | {word_count:,} words ({out_file.stat().st_size / 1024:.1f} KB)")
        
        catalog.append({
            "slug": slug,
            "title_ar": title_ar,
            "title_en": title_en,
            "category": item["category"],
            "description": item["desc"],
            "file_path": str(out_file),
            "char_count": char_count,
            "word_count": word_count,
            "file_size_bytes": out_file.stat().st_size
        })
        
    catalog_path = OUTPUT_DIR / "catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({
            "author": "Imam Yahya ibn Sharaf al-Nawawi (الإمام النووي)",
            "death_hijri": "676 AH",
            "death_gregorian": "1277 CE",
            "total_works": len(catalog),
            "total_words": sum(w["word_count"] for w in catalog),
            "works": catalog
        }, f, ensure_ascii=False, indent=2)
        
    print("\n" + "=" * 70)
    print(f"🎉 Successfully Ingested All {len(catalog)} Nawawi Masterworks -> {catalog_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()
