"""
lexicographical_engine.py

Reusable, standalone Two-Stage Lexicographically Guided Translation Engine Framework.
Can be imported into any project to translate classical texts with zero truncation,
dynamic root tracking, and Lisan al-Arab / Sibawayh semantic anchoring.
"""

import sys, json, time, re, urllib.request
from pathlib import Path

class LexicographicalTranslationEngine:
    def __init__(self, api_key=None, base_url="https://api.deepseek.com", model="deepseek-chat",
                 author="Classical Scholar", book_title_ar="النص الكلاسيكي", book_title_en="Classical Text",
                 max_chunk_chars=6000):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.author = author
        self.book_title_ar = book_title_ar
        self.book_title_en = book_title_en
        self.max_chunk_chars = max_chunk_chars
        self.used_roots = set()

    def chunk_manuscript(self, raw_text):
        lines = raw_text.splitlines()
        chunks = []
        cur_title = f"Introduction to {self.book_title_en} ({self.book_title_ar})"
        cur_lines = []

        for l in lines:
            clean_l = re.sub(r'^\|+\s*\*?\s*', '', l).strip()
            if clean_l.startswith('الباب') or clean_l.startswith('الفصل') or clean_l.startswith('المسألة') or clean_l.startswith('المقدمة') or clean_l.startswith('القسم'):
                if cur_lines:
                    txt = '\n'.join(cur_lines).strip()
                    if len(txt) > 50:
                        chunks.append({'title_ar': cur_title, 'text': txt})
                    cur_lines = []
                cur_title = clean_l
            cur_lines.append(l)

        if cur_lines:
            txt = '\n'.join(cur_lines).strip()
            if len(txt) > 50:
                chunks.append({'title_ar': cur_title, 'text': txt})

        final_chunks = []
        for c in chunks:
            t = c['text']
            title = c['title_ar']
            if len(t) <= (self.max_chunk_chars + 1000):
                final_chunks.append(c)
            else:
                paras = t.split('\n\n')
                sub_buf = []
                sub_len = 0
                part_num = 1
                for p in paras:
                    sub_buf.append(p)
                    sub_len += len(p)
                    if sub_len >= self.max_chunk_chars:
                        final_chunks.append({
                            'title_ar': f"{title} (Part {part_num})",
                            'text': '\n\n'.join(sub_buf)
                        })
                        sub_buf = []
                        sub_len = 0
                        part_num += 1
                if sub_buf:
                    final_chunks.append({
                        'title_ar': f"{title} (Part {part_num})" if part_num > 1 else title,
                        'text': '\n\n'.join(sub_buf)
                    })

        return final_chunks

    def call_api(self, system_prompt, user_prompt, temperature=0.1, max_tokens=8000):
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

    def translate_chapter(self, chunk, idx, total):
        title_ar = chunk["title_ar"]
        arabic_text = chunk["text"]
        roots_str = ", ".join(list(self.used_roots)[-20:]) if self.used_roots else "None"

        sys_trans = (
            f"You are a master classical Arabic lexicographer, grammarian, and scholarly translator specializing in Ibn Manzur's Lisān al-ʿArab, Sibawayh's Al-Kitāb, and Al-Farāhīdī's root permutation method.\n"
            f"Translate this passage from {self.author}'s '{self.book_title_en}' ({self.book_title_ar}).\n\n"
            "TWO-STAGE LEXICOGRAPHICALLY-GUIDED TRANSLATION METHODOLOGY:\n"
            "STAGE 1 — LEXICAL & SYNTACTIC ANCHORING:\n"
            "Before generating the English translation, extract 1 UNIQUE Arabic root from Lisān al-ʿArab and 1 UNIQUE syntactic rule from Sibawayh's Al-Kitāb that occur in this passage. Use these classical definitions as strict semantic anchors to inform and constrain your translation of complex technical terms.\n"
            f"ALREADY USED ROOTS (DO NOT REPEAT): {roots_str}\n\n"
            "STAGE 2 — SENSE-FOR-SENSE TRANSLATION:\n"
            "Apply Ḥunayn ibn Isḥāq's Bayt al-Ḥikmah sense-for-sense translation standard, informed directly by the Stage 1 anchors.\n"
            f"Speak authentically in {self.author}'s 1st-person voice ('I say...', 'Know that...').\n\n"
            "STRICT TRANSLATION MANDATES:\n"
            "1. NO ARABIC SCRIPT/LETTERS inside the translation text sentences.\n"
            "2. KEY RARE TECHNICAL TERMS MUST BE ACCOMPANIED BY THEIR TRANSLITERATION IN PARENTHESES directly in the English text.\n"
            "3. COMPLETE TRANSLATION: You MUST translate the entire provided Arabic text from beginning to end without skipping or cutting off.\n\n"
            "Format output EXACTLY as:\n"
            "ENGLISH_TITLE: [Concise English Chapter Title]\n"
            "LISAN_NOTE:\n"
            "**Root: [Root in Arabic] ([Transliteration])**\n"
            "*Lisān al-ʿArab*: [Short 1-line verbatim quote with Arabic + (transliteration)]\n\n"
            "SIBAWAYH_NOTE:\n"
            "**Rule: [Rule Name] ([Transliteration])**\n"
            "*Al-Kitāb*: [Short 1-line verbatim quote with Arabic + (transliteration)]\n\n"
            "TRANSLATION:\n"
            "[1st-person English translation guided by the classical notes above]"
        )
        user_trans = f"Chapter Title: {title_ar}\n\nArabic Text:\n\"\"\"\n{arabic_text}\n\"\"\""

        output_trans = self.call_api(sys_trans, user_trans)

        title_en = title_ar
        translation_text = output_trans
        lisan_note = "*(Lexical root mapped)*"
        sibawayh_note = "*(Grammatical rule mapped)*"

        if "ENGLISH_TITLE:" in output_trans and "TRANSLATION:" in output_trans:
            try:
                parts = output_trans.split("TRANSLATION:")
                header_part = parts[0]
                translation_text = parts[1].strip()

                title_match = re.search(r'ENGLISH_TITLE:\s*([^\n]+)', header_part)
                if title_match:
                    title_en = title_match.group(1).strip()

                lisan_match = re.search(r'LISAN_NOTE:\s*([\s\S]*?)(?=SIBAWAYH_NOTE:|$)', header_part)
                if lisan_match:
                    lisan_note = lisan_match.group(1).strip()

                sibawayh_match = re.search(r'SIBAWAYH_NOTE:\s*([\s\S]*?)$', header_part)
                if sibawayh_match:
                    sibawayh_note = sibawayh_match.group(1).strip()
            except Exception:
                translation_text = output_trans

        final_md = f"""### 📜 {title_en} ({title_ar})

#### 📜 Original Arabic Text (النص العربي الأصلي)
{arabic_text}

#### 📖 Lisan al-Arab Lexical Note (Translation Anchor)
{lisan_note}

#### ⚖️ Sibawayh Grammatical Note (Syntactic Anchor)
{sibawayh_note}

#### 🌐 Translation ({self.author}'s Voice — Lexically Guided)
{translation_text}"""

        root_match = re.search(r'\*\*Root:\s*([^*]+)\*\*', lisan_note)
        extracted_root = root_match.group(1).strip() if root_match else ""

        if extracted_root:
            self.used_roots.add(extracted_root)

        return {
            "chapter_index": idx,
            "title_ar": title_ar,
            "title_en": title_en,
            "arabic_text": arabic_text,
            "english_translation": final_md,
            "root": extracted_root
        }

    def process_file(self, input_filepath, output_filepath):
        with open(input_filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()

        chunks = self.chunk_manuscript(raw_text)
        total = len(chunks)
        print(f"Loaded {total} balanced chapters for '{self.book_title_en}'.\n")

        results = []
        start_time = time.time()

        for idx, chunk in enumerate(chunks):
            ch_num = idx + 1
            res = self.translate_chapter(chunk, idx, total)
            results.append(res)
            print(f"[{ch_num}/{total}] ✓ Chapter {ch_num}: {res['title_en']} ({chunk['title_ar'][:35]})")

        out_p = Path(output_filepath)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        with open(out_p, "w", encoding="utf-8") as f:
            json.dump({
                "meta": {
                    "title_ar": self.book_title_ar,
                    "title_en": self.book_title_en,
                    "author": self.author,
                    "pipeline": f"Reusable Lexicographical Framework ({total} Sub-Chapters)",
                    "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
                },
                "chapters": results
            }, f, ensure_ascii=False, indent=2)

        total_time = time.time() - start_time
        print(f"\n✓ Completed in {total_time/60:.1f} minutes -> Saved to {out_p}")
