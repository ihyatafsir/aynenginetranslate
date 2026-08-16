"""
translate_ismat_v4_pro_7roots.py

Flagship v4 Pro Translation of Imam Fakhr al-Din al-Razi's
'ʿIṣmat al-Anbiyāʾ' (The Infallibility of the Prophets).

Features:
1. 7-Root Classical Lexicographical Constellation (*Al-Manẓūma al-Sabʿiyya*) extracted per chapter from Lisān al-ʿArab.
2. Multi-Rule Sībawayh Syntactic Anchors from *al-Kitāb*.
3. Canonical Sectarian Transliterations (al-Imāmiyya, al-Rawāfiḍ, al-Muʿtazila, al-Ḥashwiyya, al-Ashāʿira, al-Khawārij, al-Murjiʾa).
4. Kalām Infallibility Precision (al-Sahw = Inadvertence/momentary oversight, Jāʾiz = Rationally & humanly possible).
5. Output saved to data/new_works/ismat_v4_pro_7roots_translated.json.
"""

import sys, json, time, re
from pathlib import Path
import urllib.request

sys.path.insert(0, str(Path(__file__).parent.resolve()))
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, TEXTS_DIR

MODEL_PRIMARY = "deepseek-v4-pro"
MODEL_FALLBACK = "deepseek-v4-flash"
SOURCE_FILE = TEXTS_DIR / "razi_ismat_anbiya.txt"
OUTPUT_FILE = Path("data/new_works/ismat_v4_pro_7roots_translated.json")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_source_text():
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        return f.read()


def chunk_ismat():
    raw_text = load_source_text()

    lines = raw_text.splitlines()
    chunks = []
    cur_title = "Introduction to ʿIṣmat al-Anbiyāʾ (المقدمة في عصمة الأنبياء)"
    cur_lines = []

    for l in lines:
        clean_l = re.sub(r'^\|+\s*\*?\s*', '', l).strip()
        if clean_l.startswith('الباب') or clean_l.startswith('الفصل') or clean_l.startswith('المسألة') or clean_l.startswith('المقدمة') or clean_l.startswith('قصة') or 'عصمة' in clean_l[:25]:
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
        if len(t) <= 6500:
            final_chunks.append(c)
        else:
            paras = t.split('\n\n')
            sub_buf = []
            sub_len = 0
            part_num = 1
            for p in paras:
                sub_buf.append(p)
                sub_len += len(p)
                if sub_len >= 5500:
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


def call_api(model, system_prompt, user_prompt, max_tokens=16384):
    url = f"{DEEPSEEK_BASE_URL}/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
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
        return f"[API Error: {e}]", "error"


def translate_chapter(chunk, idx, total):
    title_ar = chunk["title_ar"]
    arabic_text = chunk["text"]

    sys_trans = (
        "You are the world's leading classical Arabic lexicographer, theologian, and scholarly translator specializing in Ibn Manzur's Lisān al-ʿArab, Sibawayh's Al-Kitāb, and Imam Fakhr al-Din al-Razi's Kalām philosophy.\n"
        "Think concisely in your reasoning step, then immediately generate the complete response.\n\n"
        "Translate this passage from Imam Fakhr al-Din al-Razi's 'ʿIṣmat al-Anbiyāʾ' (The Infallibility of the Prophets).\n\n"
        "CRITICAL CANONICAL STANDARDS (v4 PRO):\n"
        "1. EXTRACT 7 ROOTS: Provide exactly 7 distinct Arabic roots from Lisān al-ʿArab that govern this chapter with root letters, derived word in text, and classical definition in Arabic + English.\n"
        "2. EXTRACT 2 SIBAWAYH RULES: Provide 2 governing syntactic rules from Sibawayh's Al-Kitāb.\n"
        "3. CANONICAL SECTARIAN TRANSLITERATION:\n"
        "   - الشيعة / الإمامية -> the Imāmiyya (*al-Imāmiyya*) or the Shīʿa (*al-Shīʿa / al-Imāmiyya*).\n"
        "   - الروافض / الرافضة -> the Rawāfiḍ (*al-Rawāfiḍ*).\n"
        "   - المعتزلة -> the Muʿtazila (*al-Muʿtazila*).\n"
        "   - الحشوية -> the Ḥashwiyya (*al-Ḥashwiyya* / literalists).\n"
        "   - الخوارج / الفضيلية -> the Khawārij (*al-Khawārij*) / the Fuḍayliyya (*al-Fuḍayliyya*).\n"
        "   - الأشاعرة / أصحابنا -> the Ashʿarīs (*al-Ashāʿira*) / our companions (*aṣḥābunā*).\n"
        "   - المرجئة -> the Murjiʾa (*al-Murjiʾa*).\n"
        "   - القدرية -> the Qadariyya (*al-Qadariyya*).\n"
        "   - الجبرية / المجبرة -> the Jabriyya (*al-Jabriyya*).
   - PROPHET NAMES (CANONICAL ARABIC): Always use canonical Arabic transliterations with honorifics: Ādam (peace be upon him), Nūḥ (peace be upon him), Ibrāhīm (peace be upon him), Lūṭ (peace be upon him), Ismāʿīl (peace be upon him), Isḥāq (peace be upon him), Yaʿqūb (peace be upon him), Yūsuf (peace be upon him), Ayyūb (peace be upon him), Shuʿayb (peace be upon him), Mūsā (peace be upon him), Hārūn (peace be upon him), Dāwūd (peace be upon him), Sulaymān (peace be upon him), Yūnus (peace be upon him), Zakarīyā (peace be upon him), Yaḥyā (peace be upon him), ʿĪsā (peace be upon him), Muḥammad (peace and blessings be upon him). Do NOT use Anglicized biblical names like Noah, Abraham, Moses, Jesus, Lot, Joseph, David, Solomon, Jonah.\n"
        "4. KALAM INFALLIBILITY VOCABULARY:\n"
        "   - السهو (al-sahw) -> Inadvertence / momentary oversight (*al-sahw*). NEVER translate as 'sin of forgetfulness' or 'permissible sins'.\n"
        "   - النسيان (al-nisyān) -> Forgetfulness / slip of memory (*al-nisyān*).\n"
        "   - جائز (jāʾiz) -> In Kalām theology, means 'rationally and humanly possible' / 'permissible'.\n"
        "   - بيان الملازمة -> The demonstration of the entailment (*bayān al-mulāzama*).\n"
        "   - ترك الأولى -> Omission of the optimal course (*tark al-awlā*).\n"
        "   - العمد -> Deliberate intention (*al-ʿamd*).\n"
        "5. FULL TRANSLATION: 1st-person scholastic voice in fluent English without omitting any sentences.\n\n"
        "Format output EXACTLY as:\n"
        "ENGLISH_TITLE: [Concise English Chapter Title]\n"
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
        "[Full English translation]"
    )
    user_trans = f"Chapter Title: {title_ar}\n\nArabic Text:\n{arabic_text}"

    # Try Primary Pro model first with 16k tokens; if length truncated or error, fallback to Flash
    content, finish_reason = call_api(MODEL_PRIMARY, sys_trans, user_trans, max_tokens=16384)
    model_used = MODEL_PRIMARY

    if finish_reason != "stop" or len(content) < 500 or "TRANSLATION:" not in content:
        print(f"    ⚠️ [Fallback] Switching to {MODEL_FALLBACK} for chapter {idx+1}...")
        content, finish_reason = call_api(MODEL_FALLBACK, sys_trans, user_trans, max_tokens=8192)
        model_used = MODEL_FALLBACK

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

    final_md = f"""### 📜 {title_en} ({title_ar})

#### 📜 Original Arabic Text (النص العربي الأصلي)
{arabic_text}

#### 📖 Lisān al-ʿArab 7-Root Lexical Constellation (المنظومة المعجمية السبعية)
{lisan_constellation}

#### ⚖️ Sībawayh Grammatical & Syntactic Anchors (الشواهد النحوية والتركيبية)
{sibawayh_notes}

#### 🌐 Translation (Imam Al-Razi's Voice — Lexically & Syntactically Guided)
{translation_text}"""

    return {
        "chapter_index": idx,
        "title_ar": title_ar,
        "title_en": title_en,
        "arabic_text": arabic_text,
        "english_translation": final_md,
        "lisan_constellation": lisan_constellation,
        "sibawayh_notes": sibawayh_notes,
        "model_used": model_used
    }


def main():
    print("=" * 75)
    print("  DEEPSEEK 7-ROOT PRO ENGINE — ʿIṢMAT AL-ANBIYĀʾ (v4 PRO 7-ROOT CONSTELLATION)")
    print("  1. Primary Engine: deepseek-v4-pro with 16k Token Context Budget")
    print("  2. 7-Root Classical Lexical Constellation per Chapter from Lisān al-ʿArab")
    print("  3. Multi-Rule Sībawayh Syntactic Anchors from al-Kitāb")
    print("  4. Canonical Sectarian Standards (Imāmiyya, Rawāfiḍ, Muʿtazila, Ḥashwiyya)")
    print("  5. Rigorous Kalām Infallibility Vocabulary (al-Sahw = Inadvertence)")
    print("  6. Output saved to data/new_works/ismat_v4_pro_7roots_translated.json")
    print("=" * 75)

    chunks = chunk_ismat()
    total = len(chunks)
    print(f"Loaded {total} balanced chapters.\n")

    results = []
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                results = saved.get('chapters', [])
                print(f'🔄 Resuming existing translation: {len(results)}/{total} chapters already done.')
        except Exception as e:
            print(f'⚠️ Warning loading existing file: {e}')
            results = []

    start_time = time.time()

    for idx, chunk in enumerate(chunks):
        if idx < len(results):
            continue
        ch_num = idx + 1
        print(f"[{ch_num}/{total}] ⏳ Translating ({chunk['title_ar'][:40]})...")
        t0 = time.time()
        res = translate_chapter(chunk, idx, total)
        dt = time.time() - t0
        results.append(res)
        print(f"[{ch_num}/{total}] ✓ Finished in {dt:.1f}s [{res.get('model_used', 'api')}] — {res['title_en']}")

        # Save incrementally
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "meta": {
                    "title_ar": "عصمة الأنبياء",
                    "title_en": "The Infallibility of the Prophets (v4 Pro 7-Root Edition)",
                    "author": "Imam Fakhr al-Din al-Razi",
                    "pipeline": "DeepSeek-v4-Pro / Flash Guided Engine (22 Sub-Chapters, 7-Root Constellation)",
                    "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
                },
                "chapters": results
            }, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - start_time
    print("\n" + "=" * 75)
    print(f"🎉 Complete! 22 chapters translated in {elapsed:.1f}s")
    print(f"📁 Output saved: {OUTPUT_FILE}")
    print("=" * 75)


if __name__ == "__main__":
    main()
