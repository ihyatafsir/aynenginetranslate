#!/usr/bin/env python3
"""
build_classical_lexicons.py

High-performance acquisition and indexing pipeline for:
1. Al-Raghib al-Isfahani's 'Al-Mufradat fi Gharib al-Quran' (Theological & Quranic Semantics)
2. Al-Zamakhshari's 'Asas al-Balaghah' (Rhetorical & Literal/Metaphorical Majaz Lexicon)

Builds indexed JSON lookup dictionaries for AynEngine AI v3.0.0.
"""

import os
import re
import json
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
DATA_DIR = BASE_DIR / "data"
LEXICONS_DIR = DATA_DIR / "lexicons"

RAGHIB_DIR = LEXICONS_DIR / "raghib_mufradat"
ZAMAKHSHARI_DIR = LEXICONS_DIR / "zamakhshari_asas"

RAGHIB_DIR.mkdir(parents=True, exist_ok=True)
ZAMAKHSHARI_DIR.mkdir(parents=True, exist_ok=True)

RAGHIB_URL = "https://raw.githubusercontent.com/OpenITI/0525AH/master/data/0502RaghibIsbahani/0502RaghibIsbahani.Mufradat/0502RaghibIsbahani.Mufradat.Shamela0023636-ara1"
ZAMAKHSHARI_URL = "https://raw.githubusercontent.com/OpenITI/0550AH/master/data/0538JarAllahZamakhshari/0538JarAllahZamakhshari.AsasBalagha/0538JarAllahZamakhshari.AsasBalagha.Shamela0021568-ara1"

def normalize_root(text):
    if not text:
        return ""
    # Remove tashkeel/diacritics
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
    # Remove ms/page tags
    text = re.sub(r'ms\d+|PageV\d+P\d+|###|\#|\|', '', text)
    # Normalize alefs and hamzas
    text = re.sub(r'[إأآٱ]', 'ا', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'ة', 'ه', text)
    # Remove spaces and non-Arabic chars
    text = re.sub(r'[^\u0621-\u064A]', '', text)
    return text.strip()

def download_file(url, dest_path):
    if dest_path.exists() and dest_path.stat().st_size > 10000:
        print(f"✅ Found local cache: {dest_path} ({dest_path.stat().st_size / (1024*1024):.2f} MB)")
        return dest_path.read_text(encoding="utf-8", errors="ignore")
    
    print(f"📥 Downloading {url} -> {dest_path.name}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read().decode("utf-8", errors="ignore")
        dest_path.write_text(content, encoding="utf-8")
        print(f"✅ Downloaded {dest_path.name} ({len(content)/(1024*1024):.2f} MB)")
        return content

def clean_text_body(text):
    # Remove OpenITI editorial line markers and page tags
    text = re.sub(r'~~', '', text)
    text = re.sub(r'#\s*PageV\d+P\d+', '', text)
    text = re.sub(r'ms\d+', '', text)
    text = re.sub(r'#\s*', '', text)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)

def build_raghib_mufradat_index(raw_text):
    print("⚙️ Parsing Al-Raghib al-Isfahani's Al-Mufradat...")
    # Entries start after intro with '### | ' followed by root or term
    dict_index = {}
    
    # Split text by section markers
    sections = re.split(r'\n(?=###\s*\|\s*)', raw_text)
    
    for sec in sections:
        sec = sec.strip()
        if not sec.startswith('###'):
            continue
        
        lines = sec.split('\n')
        header_line = lines[0].replace('###', '').replace('|', '').strip()
        
        # Skip introductions and book headers
        if any(skip in header_line for skip in ['مقدمة', 'ترجمة', 'اسمه', 'شيوخه', 'مؤلفاته', 'كتاب']):
            continue
        
        raw_root = header_line.split()[0] if header_line.split() else ""
        norm_root = normalize_root(raw_root)
        
        if not norm_root or len(norm_root) > 5:
            continue
        
        body_text = clean_text_body('\n'.join(lines[1:]))
        if len(body_text) < 15:
            continue
        
        # Extract Quranic citations if present
        quran_citations = re.findall(r'[«"“]([\u0600-\u06FF\s،؛]+)[»"”]', body_text)
        quran_citations = [c.strip() for c in quran_citations if len(c.strip()) > 8]
        
        entry = {
            "root": norm_root,
            "raw_header": header_line,
            "definition": body_text[:1200].strip(),
            "full_text": body_text.strip(),
            "quranic_citations": quran_citations[:5]
        }
        
        if norm_root not in dict_index or len(body_text) > len(dict_index[norm_root]["full_text"]):
            dict_index[norm_root] = entry

    out_file = RAGHIB_DIR / "raghib_mufradat_dictionary.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(dict_index, f, ensure_ascii=False, indent=2)
    
    print(f"✨ Successfully indexed Al-Mufradat: {len(dict_index)} roots -> {out_file}")
    return dict_index

def build_zamakhshari_asas_index(raw_text):
    print("⚙️ Parsing Al-Zamakhshari's Asas al-Balaghah...")
    dict_index = {}
    
    sections = re.split(r'\n(?=###\s*\|\s*)', raw_text)
    
    for sec in sections:
        sec = sec.strip()
        if not sec.startswith('###'):
            continue
        
        lines = sec.split('\n')
        header_line = lines[0].replace('###', '').replace('|', '').strip()
        
        if 'مقدمة' in header_line or 'كتاب' in header_line:
            continue
            
        norm_root = normalize_root(header_line)
        if not norm_root or len(norm_root) > 5:
            continue
            
        body_text = clean_text_body('\n'.join(lines[1:]))
        if len(body_text) < 10:
            continue
            
        # Partition into literal (haqiqah) and metaphorical (majaz)
        parts = re.split(r'ومن المجاز[:\s]*', body_text)
        literal = parts[0].strip()
        metaphorical = parts[1].strip() if len(parts) > 1 else ""
        
        entry = {
            "root": norm_root,
            "raw_header": header_line,
            "literal_usage": literal[:800],
            "metaphorical_usage": metaphorical[:800],
            "full_text": body_text.strip()
        }
        
        if norm_root not in dict_index or len(body_text) > len(dict_index[norm_root]["full_text"]):
            dict_index[norm_root] = entry

    out_file = ZAMAKHSHARI_DIR / "asas_balagha_dictionary.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(dict_index, f, ensure_ascii=False, indent=2)
        
    print(f"✨ Successfully indexed Asas al-Balaghah: {len(dict_index)} roots -> {out_file}")
    return dict_index

def main():
    print("==================================================================")
    print("🏛️ AYNENGINE AI: CLASSICAL LEXICON ACQUISITION & INDEXING PIPELINE")
    print("==================================================================")
    
    # 1. Raghib al-Isfahani - Al-Mufradat
    raghib_raw = download_file(RAGHIB_URL, RAGHIB_DIR / "mufradat.txt")
    build_raghib_mufradat_index(raghib_raw)
    
    # 2. Zamakhshari - Asas al-Balaghah
    zam_raw = download_file(ZAMAKHSHARI_URL, ZAMAKHSHARI_DIR / "asas_balagha.txt")
    build_zamakhshari_asas_index(zam_raw)
    
    print("\n🎉 Classical Lexicon Ingestion Completed Successfully!")

if __name__ == "__main__":
    main()
