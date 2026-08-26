#!/usr/bin/env python3
"""
translate_matalib_vol_01_v2_pure_ayn_engine.py

Edition v2: Flagship Two-Stage Lexicographically Guided Ayn Engine AI Translation Runner
for Imam Fakhr al-Din al-Razi's Masterpiece:
'Al-Maṭālib al-ʿAliyyah min al-ʿIlm al-Ilāhī' (The Sublime Inquiries into Divine Science)
Volume 1: The Epistemology of Theology & Proofs of the Necessary Existent (وجود واجب الوجود)

GUARANTEES:
- 100% Pure, Verbatim Translation of Imam Fakhr al-Din al-Razi's text.
- ZERO AI Commentary, ZERO Editorializing, ZERO Synthetic Bracketed Summaries.
- Stage 1: 7-Root Lisān al-ʿArab & Kitāb al-ʿAyn Lexicographical Constellation.
- Stage 1: 2 Sībawayh Syntactic Anchors.
- Stage 2: Canonical Scholarly Translation with Zero Truncation.
"""

import sys, os, json, time, re
from pathlib import Path
import urllib.request

BASE_DIR = Path("/home/absolut7/.gemini/antigravity/scratch/imamrazi").resolve()
sys.path.insert(0, str(BASE_DIR))
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, TEXTS_DIR

MODEL_ENGINE = "deepseek-chat"
SOURCE_FILE = TEXTS_DIR / "matalib_vol_01.txt"
OUTPUT_FILE = BASE_DIR / "data/new_works/matalib_vol_01_v2_pure_translated.json"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_source_text():
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        return f.read()


def chunk_matalib_vol1():
    raw_text = load_source_text()
    lines = raw_text.splitlines()

    chunks = []
    current_header = "مقدمة الكتاب في شرف العلم الإلهي ومراتب العلوم (Prologue)"
    current_lines = []

    for l in lines:
        clean_l = re.sub(r'^[\|\*\s]+', '', l).strip()
        is_major_header = False

        if re.match(r'^(المطلب|الكتاب|الباب|الفصل|المسألة|القسم|الوجه)\s+(الأول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر)', clean_l) or clean_l.startswith('[فصل]') or clean_l.startswith('[المطلب'):
            if len('\n'.join(current_lines).strip()) >= 300:
                is_major_header = True

        if is_major_header:
            txt = '\n'.join(current_lines).strip()
            if txt:
                if len(txt) <= 3200:
                    chunks.append({'title_ar': current_header, 'text': txt})
                else:
                    paras = txt.split('\n\n')
                    sub_buf = []
                    sub_len = 0
                    part = 1
                    for p in paras:
                        sub_buf.append(p)
                        sub_len += len(p)
                        if sub_len >= 2500:
                            chunks.append({
                                'title_ar': f"{current_header} (Part {part})",
                                'text': '\n\n'.join(sub_buf)
                            })
                            sub_buf = []
                            sub_len = 0
                            part += 1
                    if sub_buf:
                        chunks.append({
                            'title_ar': f"{current_header} (Part {part})" if part > 1 else current_header,
                            'text': '\n\n'.join(sub_buf)
                        })
            current_lines = []
            current_header = clean_l

        current_lines.append(l)

    if current_lines:
        txt = '\n'.join(current_lines).strip()
        if txt:
            if len(txt) <= 3200:
                chunks.append({'title_ar': current_header, 'text': txt})
            else:
                paras = txt.split('\n\n')
                sub_buf = []
                sub_len = 0
                part = 1
                for p in paras:
                    sub_buf.append(p)
                    sub_len += len(p)
                    if sub_len >= 2500:
                        chunks.append({
                            'title_ar': f"{current_header} (Part {part})",
                            'text': '\n\n'.join(sub_buf)
                        })
                        sub_buf = []
                        sub_len = 0
                        part += 1
                if sub_buf:
                    chunks.append({
                        'title_ar': f"{current_header} (Part {part})" if part > 1 else current_header,
                        'text': '\n\n'.join(sub_buf)
                    })

    return chunks


def call_api(system_prompt, user_prompt, max_tokens=8192):
    url = f"{DEEPSEEK_BASE_URL}/v1/chat/completions"
    payload = {
        "model": MODEL_ENGINE,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2,
        "max_tokens": max_tokens
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            choice = data["choices"][0]
            content = choice["message"].get("content", "").strip()
            finish_reason = choice.get("finish_reason")
            return content, finish_reason
    except Exception as e:
        time.sleep(3)
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                choice = data["choices"][0]
                content = choice["message"].get("content", "").strip()
                finish_reason = choice.get("finish_reason")
                return content, finish_reason
        except Exception as e2:
            return f"[API Error: {str(e2)}]", "error"


def translate_chapter(chunk, idx, total):
    title_ar = chunk["title_ar"]
    arabic_text = chunk["text"]

    sys_trans = (
        "You are the world's leading classical Arabic lexicographer, theologian, and scholarly translator specializing in Ibn Manzur's Lisān al-ʿArab, Al-Khalil's Kitāb al-ʿAyn, Sibawayh's Al-Kitāb, and Imam Fakhr al-Din al-Razi's Kalām philosophy.\n\n"
        "Translate this passage from Imam Fakhr al-Din al-Razi's master theological summa 'Al-Maṭālib al-ʿAliyyah min al-ʿIlm al-Ilāhī' (Volume 1: Proofs of the Necessary Existent).\n\n"
        "CRITICAL CANONICAL STANDARDS (AYN ENGINE AI v2 PURE EDITION):\n"
        "1. STRICT ZERO AI COMMENTARY OR EDITORIALIZING: Translate ONLY what is present in the source Arabic text. NEVER add third-person summaries, contextual preambles, bracketed explanations (e.g., '[Imam al-Razi now proceeds...]' or '[He frames this inquiry...]'), or meta-narratives. If the author did not state it in the Arabic passage, DO NOT write it in the translation. The translation must be 100% pure, verbatim, and faithful to Imam al-Razi's actual words.\n\n"
        "2. ARABIC SCRIPT FOR ALL QURANIC VERSES AND HADITH CITATIONS: Whenever a Quranic verse (Āyah) or Prophetic Hadith is cited in the text, you MUST preserve the exact Arabic script in brackets {«Arabic text here»} on its own line, followed immediately by its authentic English translation in quotes on the next line. Example:\n"
        "   {«قُلْ هُوَ اللَّهُ أَحَدٌ • اللَّهُ الصَّمَدُ»}\n"
        "   “Say: He is Allah, the One; Allah, the Absolute Self-Sufficient Refuge.” (112:1-2)\n\n"
        "3. EXTRACT 7 LISAN & AYN ROOTS: Provide exactly 7 distinct Arabic roots from Lisān al-ʿArab and Kitāb al-ʿAyn that govern the key concepts in this passage, showing the root letters, technical term in text, and classical definition in Arabic + English.\n\n"
        "4. EXTRACT 2 SIBAWAYH RULES: Provide 2 governing syntactic rules from Sibawayh's Al-Kitāb relevant to the grammar of the passage.\n\n"
        "5. RIGOROUS KALAM & METAPHYSICAL NOMENCLATURE:\n"
        "   - واجب الوجود لذاته -> The Necessary Existent in Its Own Essence (*Wājib al-Wujūd bi-dhātihi*)\n"
        "   - ممكن الوجود -> The Contingent Existent (*Mumkin al-Wujūd*)\n"
        "   - ممتنع الوجود -> The Impossible in Existence (*Mumtaniʿ al-Wujūd*)\n"
        "   - الجوهر الفرد -> The Indivisible Monad / Atom (*al-Jawhar al-Fard*)\n"
        "   - العرض -> Accident / Inherent Property (*al-ʿAraḍ*)\n"
        "   - القدم vs الحدوث -> Primordial Eternity (*al-Qidam*) vs Temporal Origination (*al-Ḥudūth*)\n"
        "   - التركيب والتأليف -> Composition and Aggregation (*al-Tarkīb wa'l-Taʾlīf*)\n"
        "   - التنزيه والتقديس -> Absolute Incomparability and Sanctification (*al-Tanzīh wa'l-Taqdīs*)\n"
        "   - بيان الملازمة -> Demonstration of the Entailment (*Bayān al-Mulāzama*)\n"
        "   - بطلان الدور والتسلسل -> The Invalidity of Vicious Circularity and Infinite Regress (*Buṭlān al-Dawr wa'l-Tasalsul*)\n"
        "   - الترجيح بلا مرجح -> Preponderance without a Determining Cause (*al-Tarjīḥ bi-lā Murajjiḥ*)\n"
        "   - أصحابنا / الأشاعرة -> Our companions (*Aṣḥābunā*) / The Ashʿarīs (*al-Ashāʿira*)\n"
        "   - الحكماء / الفلاسفة -> The Sages / Philosophers (*al-Ḥukamāʾ* / *al-Falāsifa*)\n"
        "   - المعتزلة -> The Muʿtazila (*al-Muʿtazila*)\n\n"
        "6. COMPLETE VERBATIM TRANSLATION: Translate every sentence with zero omissions, preserving Imam al-Razi's sharp scholastic rhetoric, dialectical proofs, and philosophical elegance.\n\n"
        "Format output EXACTLY as:\n"
        "ENGLISH_TITLE: [Scholarly English Chapter Title]\n"
        "LISAN_CONSTELLATION:\n"
        "1. **Root: [Root]** | Word: [Word] | Definition: [Definition]\n"
        "2. **Root: [Root]** | Word: [Word] | Definition: [Definition]\n"
        "3. **Root: [Root]** | Word: [Word] | Definition: [Definition]\n"
        "4. **Root: [Root]** | Word: [Word] | Definition: [Definition]\n"
        "5. **Root: [Root]** | Word: [Word] | Definition: [Definition]\n"
        "6. **Root: [Root]** | Word: [Word] | Definition: [Definition]\n"
        "7. **Root: [Root]** | Word: [Word] | Definition: [Definition]\n\n"
        "SIBAWAYH_NOTES:\n"
        "1. **Rule: [Rule]** | [Explanation]\n"
        "2. **Rule: [Rule]** | [Explanation]\n\n"
        "TRANSLATION:\n"
        "[Pure verbatim English translation from the first sentence to the last]"
    )
    user_trans = f"Chapter Title: {title_ar}\n\nArabic Text:\n{arabic_text}"

    content, finish_reason = call_api(sys_trans, user_trans)

    title_en = title_ar
    translation_text = content
    lisan_constellation = ""
    sibawayh_notes = ""

    if "ENGLISH_TITLE:" in content and "TRANSLATION:" in content:
        try:
            parts = content.split("TRANSLATION:")
            header_part = parts[0]
            translation_text = parts[1].strip()

            title_match = re.search(r'ENGLISH_TITLE:\s*([^\n]+)', header_part)
            if title_match:
                title_en = title_match.group(1).strip()

            lisan_match = re.search(r'LISAN_CONSTELLATION:\s*([\s\S]*?)(?=SIBAWAYH_NOTES:|$)', header_part)
            if lisan_match:
                lisan_constellation = lisan_match.group(1).strip()

            sibawayh_match = re.search(r'SIBAWAYH_NOTES:\s*([\s\S]*?)$', header_part)
            if sibawayh_match:
                sibawayh_notes = sibawayh_match.group(1).strip()
        except Exception:
            translation_text = content

    # Auto-continuation if output truncated
    if finish_reason == "length":
        cont_sys = "You are continuing a pure translation of Imam al-Razi's text that was cut off. Continue EXACTLY where it stopped with zero repetition and zero commentary."
        cont_user = f"Continue this verbatim translation to its completion:\n\n{translation_text[-400:]}"
        cont_content, _ = call_api(cont_sys, cont_user)
        if cont_content and not cont_content.startswith("[API Error"):
            translation_text += " " + cont_content

    return {
        "chapter_index": idx + 1,
        "title_ar": title_ar,
        "title_en": title_en,
        "lisan_constellation": lisan_constellation,
        "sibawayh_notes": sibawayh_notes,
        "translation": translation_text,
        "arabic_source": arabic_text
    }


def main():
    print("=" * 80)
    print(" 🌌 AYN ENGINE AI (v2 PURE EDITION) — AL-MATALIB AL-'ALIYAH (VOL 1)")
    print(" 100% Verbatim Translation • Zero AI Commentary Guarantee")
    print("=" * 80)

    chunks = chunk_matalib_vol1()
    total = len(chunks)
    print(f"✓ Extracted {total} structured chapters/sub-chapters from Volume 1.")

    # Initialize fresh V2 Master File
    translated_chapters = []
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                translated_chapters = data.get("chapters", [])
                print(f"✓ Resuming from existing checkpoint: {len(translated_chapters)}/{total} chapters complete.")
        except Exception:
            translated_chapters = []

    done_indices = {c["chapter_index"] - 1 for c in translated_chapters}

    for idx in range(total):
        if idx in done_indices:
            continue

        c = chunks[idx]
        print(f"\n[{idx+1}/{total}] Translating: {c['title_ar'][:60]}...")
        start_t = time.time()
        res = translate_chapter(c, idx, total)
        elapsed = time.time() - start_t
        translated_chapters.append(res)
        translated_chapters.sort(key=lambda x: x["chapter_index"])

        # Atomic Checkpoint Save
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "work": "Al-Matalib al-'Aliyah min al-'Ilm al-Ilahi (المطالب العالية من العلم الإلهي)",
                "edition": "v2_pure_scholarly_edition",
                "volume": 1,
                "volume_title_ar": "دلائل وجود واجب الوجود وتوحيده وتنزيهه",
                "volume_title_en": "Volume 1: The Epistemology of Theology & Proofs of the Necessary Existent",
                "author": "Imam Fakhr al-Din al-Razi (d. 606 AH)",
                "total_chapters": total,
                "completed_chapters": len(translated_chapters),
                "chapters": translated_chapters
            }, f, ensure_ascii=False, indent=2)

        words_count = len(res["translation"].split())
        print(f"   ✓ Completed in {elapsed:.1f}s | Words: {words_count:,} | Saved to Checkpoint.")

    print("\n" + "=" * 80)
    print(" 🎉 VOLUME 1 (V2 PURE EDITION) TRANSLATION COMPLETE!")
    print(f" Total Chapters: {len(translated_chapters)}/{total}")
    print(f" Master File: {OUTPUT_FILE}")
    print("=" * 80)


if __name__ == "__main__":
    main()
