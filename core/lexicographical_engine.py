#!/usr/bin/env python3
"""
lexicographical_engine.py

AynEngine AI v3.0.0: Sovereign Quad-Lexical & Syntactic Translation Framework
Designed for classical Arabic philosophical, theological (Kalam), and scientific literature.

Architectural Anchor Suite:
1. Lisān al-ʿArab (Ibn Manẓūr, d. 711 AH) — Universal classical root corpus.
2. Kitāb al-ʿAyn (Al-Khalīl ibn Aḥmad al-Farāhīdī, d. 175 AH) — Archaic phonetic permutations.
3. Al-Mufradāt fī Gharīb al-Qurʾān (Al-Rāghib al-Iṣfahānī, d. 502 AH) — Theological & Quranic semantics.
4. Asās al-Balāghah (Al-Zamakhsharī, d. 538 AH) — Rhetorical & Literal (Haqiqah) vs Metaphorical (Majaz) distinctions.
5. Al-Kitāb (Sībawayh, d. 180 AH) — Governing syntactic and grammatical rules.
"""

import os
import re
import json
import time
import urllib.request
from pathlib import Path

class LexicographicalTranslationEngine:
    def __init__(self, author, book_title_ar, book_title_en,
                 api_key=None, base_url=None, model=None,
                 max_chunk_chars=6000, engine_mode="QUAD_LEXICAL"):
        self.author = author
        self.book_title_ar = book_title_ar
        self.book_title_en = book_title_en
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.base_url = (base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")).rstrip('/')
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.max_chunk_chars = max_chunk_chars
        self.engine_mode = engine_mode
        self.used_roots = set()
        
        # Load Lexicon Databases
        self.base_dir = Path(__file__).parent.parent.resolve()
        self.data_dir = self.base_dir / "data"
        self.lexicons_dir = self.data_dir / "lexicons"
        self.grammars_dir = self.data_dir / "grammars"
        
        self.lisan_dict = self._load_json(self.data_dir / "lisanclean.json")
        self.ayn_dict = self._load_json(self.lexicons_dir / "kitab_al_ayn" / "kitab_al_ayn_dictionary.json")
        self.raghib_dict = self._load_json(self.lexicons_dir / "raghib_mufradat" / "raghib_mufradat_dictionary.json")
        self.zamakhshari_dict = self._load_json(self.lexicons_dir / "zamakhshari_asas" / "asas_balagha_dictionary.json")
        self.sibawayh_rules = self._load_json(self.grammars_dir / "sibawayh_kitab" / "sibawayh_rules.json")

    def _load_json(self, path):
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Warning: Could not parse {path.name}: {e}")
        return {}

    def normalize_root(self, root):
        if not root:
            return ""
        root = re.sub(r'[\u064B-\u065F\u0670]', '', root)
        root = re.sub(r'[إأآٱ]', 'ا', root)
        root = re.sub(r'ى', 'ي', root)
        root = re.sub(r'ة', 'ه', root)
        root = re.sub(r'[^\u0621-\u064A]', '', root)
        return root.strip()

    def lookup_raghib(self, root):
        """Lookup theological definition in Al-Raghib al-Isfahani's Al-Mufradat."""
        n_root = self.normalize_root(root)
        return self.raghib_dict.get(n_root)

    def lookup_zamakhshari(self, root):
        """Lookup rhetorical literal/metaphorical distinctions in Asas al-Balaghah."""
        n_root = self.normalize_root(root)
        return self.zamakhshari_dict.get(n_root)

    def lookup_lisan(self, root):
        """Lookup linguistic definition in Lisan al-Arab."""
        n_root = self.normalize_root(root)
        return self.lisan_dict.get(n_root)

    def get_quad_anchor_summary(self, root):
        """Extract multi-dimensional classical semantics for a root across all 4 lexicons."""
        n_root = self.normalize_root(root)
        summary = {
            "root": n_root,
            "raghib_theology": None,
            "zamakhshari_rhetoric": None,
            "lisan_semantics": None
        }
        
        r_entry = self.lookup_raghib(n_root)
        if r_entry:
            summary["raghib_theology"] = r_entry.get("definition", "")[:300]
            
        z_entry = self.lookup_zamakhshari(n_root)
        if z_entry:
            summary["zamakhshari_rhetoric"] = {
                "literal": z_entry.get("literal_usage", "")[:200],
                "majaz": z_entry.get("metaphorical_usage", "")[:200]
            }
            
        l_entry = self.lookup_lisan(n_root)
        if l_entry:
            summary["lisan_semantics"] = str(l_entry)[:250]
            
        return summary

    def chunk_manuscript(self, raw_text):
        """Zero-truncation adaptive chunking partitioned on section markers."""
        chunks = []
        raw_sections = re.split(r'\n(?=(?:#+\s*PageV\d+P\d+|###\s*\|\s*|\#+\s*(?:الفصل|الباب|المسألة|القول|الأصل)))', raw_text)
        
        current_chunk = []
        current_len = 0
        section_idx = 1
        
        for sec in raw_sections:
            sec_str = sec.strip()
            if not sec_str:
                continue
            
            sec_len = len(sec_str)
            if current_len + sec_len > self.max_chunk_chars and current_chunk:
                chunks.append({
                    "chapter_index": section_idx,
                    "title_ar": f"Section {section_idx}",
                    "text": "\n\n".join(current_chunk)
                })
                section_idx += 1
                current_chunk = [sec_str]
                current_len = sec_len
            else:
                current_chunk.append(sec_str)
                current_len += sec_len
                
        if current_chunk:
            chunks.append({
                "chapter_index": section_idx,
                "title_ar": f"Section {section_idx}",
                "text": "\n\n".join(current_chunk)
            })
            
        return chunks

    def call_api(self, system_prompt, user_prompt, temperature=0.1, max_tokens=8000):
        url = f"{self.base_url}/chat/completions" if not self.base_url.endswith("/v1") else f"{self.base_url}/chat/completions"
        if not url.endswith("/chat/completions"):
            url = f"{self.base_url}/v1/chat/completions"
            
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"[API Error: {e}]"

    def translate_passage(self, passage_text, title_ar="Section"):
        """Executes the v3.0.0 Quad-Lexical translation pipeline."""
        roots_str = ", ".join(list(self.used_roots)[-20:]) if self.used_roots else "None"

        system_prompt = (
            f"You are AynEngine AI (v3.0.0) — the Sovereign Quad-Lexical Classical Arabic Translation Engine.\n"
            f"You specialize in high-precision scholarly translation of classical Islamic theological (Kalām), philosophical, and Quranic texts by {self.author}.\n\n"
            "🏛️ QUAD-LEXICAL & SYNTACTIC ANCHOR CONSTELLATION:\n"
            "Before rendering the translation, establish your semantic anchors across the 4 Classical Lexicons & Sibawayh:\n"
            "1. LISĀN AL-ʿARAB (Ibn Manẓūr) & KITĀB AL-ʿAYN (Al-Farāhīdī): Root etymology and core lexicographical semantics.\n"
            "2. AL-MUFRADĀT (Al-Rāghib al-Iṣfahānī): Theological, metaphysical, and Quranic technical terminology.\n"
            "3. ASĀS AL-BALĀGHAH (Al-Zamakhsharī): Classical Arabic rhetoric distinguishing literal (Ḥaqīqah) from metaphorical (Majāz) usage.\n"
            "4. AL-KITĀB (Sībawayh): Syntactic parsing rules for complex periodic sentences.\n\n"
            f"DO NOT REPEAT PREVIOUSLY USED ROOTS: {roots_str}\n\n"
            "📜 PURE SCHOLARLY STANDARDS:\n"
            "- 100% Verbatim translation in the authentic 1st-person authorial voice ('I say...', 'Know that...').\n"
            "- ZERO extraneous AI commentary, modern opinions, or moralizing additions.\n"
            "- Retain exact Arabic script in {«...»} braces for Quranic citations and Hadith.\n"
            "- Transliterate key technical philosophical terms in parentheses (e.g. 'origination (ḥudūth)', 'necessary existence (wujūb al-wujūd)').\n\n"
            "Format your output strictly as:\n"
            "ENGLISH_TITLE: [Concise English Title]\n"
            "QUAD_ANCHORS:\n"
            "- Root: [Arabic Root] ([Transliteration])\n"
            "  * Lisān / ʿAyn: [Core linguistic root meaning]\n"
            "  * Al-Rāghib (Mufradāt): [Theological/Kalam semantic nuance]\n"
            "  * Al-Zamakhsharī (Asās): [Literal vs Metaphorical distinction]\n"
            "- Sībawayh Rule: [Syntactic Rule Name] ([Short rule explanation])\n\n"
            "TRANSLATION:\n"
            "[Verbatim 1st-person English translation guided by the anchors above]"
        )

        user_prompt = f"Book: {self.book_title_en} ({self.book_title_ar})\nAuthor: {self.author}\nSection Title: {title_ar}\n\nArabic Text:\n\"\"\"\n{passage_text}\n\"\"\""

        output = self.call_api(system_prompt, user_prompt)
        
        # Parse output
        title_en = title_ar
        translation_text = output
        anchors_block = "*(Anchors generated)*"

        if "TRANSLATION:" in output:
            parts = output.split("TRANSLATION:")
            header = parts[0]
            translation_text = parts[1].strip()
            
            t_match = re.search(r'ENGLISH_TITLE:\s*([^\n]+)', header)
            if t_match:
                title_en = t_match.group(1).strip()
                
            a_match = re.search(r'QUAD_ANCHORS:\s*([\s\S]*?)$', header)
            if a_match:
                anchors_block = a_match.group(1).strip()

        # Update used roots
        root_matches = re.findall(r'-\s*Root:\s*([\u0600-\u06FF\w]+)', anchors_block)
        for r in root_matches:
            self.used_roots.add(self.normalize_root(r))

        return {
            "title_ar": title_ar,
            "title_en": title_en,
            "anchors": anchors_block,
            "arabic_text": passage_text,
            "translation": translation_text
        }
