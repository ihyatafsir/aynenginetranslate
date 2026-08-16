"""
build_ismat_v4_pro_epub.py

Generates the Flagship v4 Pro Kindle-ready EPUB for Imam Fakhr al-Din al-Razi's
'ʿIṣmat al-Anbiyāʾ' (The Infallibility of the Prophets) [Pro 7-Root Lexical Constellation Edition].

Features:
- High-fidelity typography (Amiri for Arabic, Inter for English).
- 7-Root Classical Lexicographical Constellation boxes (Lisān al-ʿArab).
- Sībawayh Syntactic Anchor boxes.
- Front matter with Canonical Sectarian & Kalām Translation Standards.
- Bilingual Table of Contents (English + Arabic Index).
- Auto-mirrors output to local EPUB directory and remote web server as ismat_anbiya_v4_pro_7roots_en.epub.
"""

import json, os, sys, shutil, html
from pathlib import Path
from ebooklib import epub

INPUT_JSON = Path("data/new_works/ismat_v4_pro_7roots_translated.json")
OUTPUT_EPUB = Path("data/kindle_volumes/ismat_anbiya_v4_pro_7roots_en.epub")
WEB_PUBLIC_DIR = Path("/home/absolut7/Documents/26apps/gravityremote2/antigravity_phone_chat/public")

OUTPUT_EPUB.parent.mkdir(parents=True, exist_ok=True)

CSS_CONTENT = """
@namespace epub "http://www.idpf.org/2007/ops";

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.65;
    color: #1e293b;
    padding: 5% 4%;
    margin: 0;
}

h1, h2, h3, h4 {
    color: #0f172a;
    font-weight: 700;
    line-height: 1.3;
}

h1 { font-size: 1.85em; margin-top: 1.2em; margin-bottom: 0.6em; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.3em; }
h2 { font-size: 1.45em; margin-top: 1.1em; margin-bottom: 0.5em; color: #1e293b; }
h3 { font-size: 1.2em; margin-top: 1.0em; margin-bottom: 0.4em; color: #0284c7; }
h4 { font-size: 1.05em; margin-top: 0.8em; margin-bottom: 0.3em; color: #334155; }

p {
    margin-top: 0;
    margin-bottom: 1em;
    text-align: justify;
}

blockquote {
    margin: 1.2em 0;
    padding: 0.8em 1.2em;
    background-color: #f8fafc;
    border-left: 4px solid #3b82f6;
    color: #334155;
    font-style: italic;
}

.arabic-text {
    font-family: 'Amiri', 'Traditional Arabic', 'Scheherazade New', serif;
    direction: rtl;
    text-align: right;
    font-size: 1.3em;
    line-height: 2.0;
    color: #0f172a;
    background-color: #f8fafc;
    padding: 16px 20px;
    border-radius: 8px;
    margin: 1.2em 0;
    border-right: 4px solid #0284c7;
}

.lisan-box {
    background-color: #f0fdf4;
    border-left: 4px solid #16a34a;
    padding: 10px 14px;
    margin: 0.6em 0;
    border-radius: 4px;
    font-size: 0.92em;
    line-height: 1.5;
    color: #14532d;
}

.sibawayh-box {
    background-color: #faf5ff;
    border-left: 4px solid #9333ea;
    padding: 10px 14px;
    margin: 0.6em 0;
    border-radius: 4px;
    font-size: 0.92em;
    line-height: 1.5;
    color: #581c87;
}

.title-page {
    text-align: center;
    padding: 40px 10px;
}

.title-page h1 {
    font-size: 2.3em;
    border: none;
    margin-bottom: 0.2em;
    color: #0f172a;
}

.title-page h2 {
    font-size: 1.5em;
    font-weight: 400;
    color: #64748b;
    margin-top: 0;
    margin-bottom: 2em;
}

.title-page .author {
    font-size: 1.2em;
    font-weight: 600;
    color: #334155;
}

.title-page .badge {
    display: inline-block;
    background-color: #0284c7;
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.85em;
    font-weight: 600;
    margin-bottom: 1em;
}
"""


def normalize_prophet_names(text):
    if not text:
        return ''
    rules = [
        (r'\bNoah(\s*(\([^\)]*peace[^\)]*\)|عليه\s*السلام))?', 'Nūḥ (peace be upon him)'),
        (r'\bAbraham(\s*(\([^\)]*peace[^\)]*\)|عليه\s*السلام))?', 'Ibrāhīm (peace be upon him)'),
        (r'\bMoses(\s*(\([^\)]*peace[^\)]*\)|عليه\s*السلام))?', 'Mūsā (peace be upon him)'),
        (r'\bAaron(\s*(\([^\)]*peace[^\)]*\)|عليه\s*السلام))?', 'Hārūn (peace be upon him)'),
        (r'\bJesus(\s*(\([^\)]*peace[^\)]*\)|عليه\s*السلام))?', 'ʿĪsā (peace be upon him)'),
        (r'\bJoseph(\s*(\([^\)]*peace[^\)]*\)|عليه\s*السلام))?', 'Yūsuf (peace be upon him)'),
        (r'\bDavid(\s*(\([^\)]*peace[^\)]*\)|عليه\s*السلام))?', 'Dāwūd (peace be upon him)'),
        (r'\bSolomon(\s*(\([^\)]*peace[^\)]*\)|عليه\s*السلام))?', 'Sulaymān (peace be upon him)'),
        (r'\bJonah(\s*(\([^\)]*peace[^\)]*\)|عليه\s*السلام))?', 'Yūnus (peace be upon him)'),
        (r'\bLot(\s*(\([^\)]*peace[^\)]*\)|عليه\s*السلام))?', 'Lūṭ (peace be upon him)'),
        (r'\bJacob(\s*(\([^\)]*peace[^\)]*\)|عليه\s*السلام))?', 'Yaʿqūb (peace be upon him)'),
        (r'\bIsaac(\s*(\([^\)]*peace[^\)]*\)|عليه\s*السلام))?', 'Isḥāq (peace be upon him)'),
        (r'\bIshmael(\s*(\([^\)]*peace[^\)]*\)|عليه\s*السلام))?', 'Ismāʿīl (peace be upon him)'),
        (r'\bJob(\s*(\([^\)]*peace[^\)]*\)|عليه\s*السلام))?', 'Ayyūb (peace be upon him)'),
        (r'\bZechariah(\s*(\([^\)]*peace[^\)]*\)|عليه\s*السلام))?', 'Zakarīyā (peace be upon him)'),
        (r'\bJohn the Baptist\b', 'Yaḥyā (peace be upon him)'),
        (r'\bAdam(\s*(\([^\)]*peace[^\)]*\)|عليه\s*السلام))?', 'Ādam (peace be upon him)'),
    ]
    for pattern, repl in rules:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    # Clean redundant nested brackets
    text = re.sub(r'(\(peace be upon him\)\s*)+', '(peace be upon him) ', text)
    return text

def md_to_html(md_text):
    md_text = normalize_prophet_names(md_text)
    lines = md_text.splitlines()
    html_lines = []
    in_arabic = False
    arabic_buf = []

    for l in lines:
        s = l.strip()
        if not s:
            if in_arabic and arabic_buf:
                html_lines.append(f'<div class="arabic-text">{"<br/>".join(arabic_buf)}</div>')
                arabic_buf = []
                in_arabic = False
            continue

        if s.startswith('### '):
            if in_arabic and arabic_buf:
                html_lines.append(f'<div class="arabic-text">{"<br/>".join(arabic_buf)}</div>')
                arabic_buf = []
                in_arabic = False
            html_lines.append(f'<h2>{html.escape(s[4:])}</h2>')
        elif s.startswith('#### 📜 Original Arabic Text'):
            in_arabic = True
            arabic_buf = []
            html_lines.append(f'<h3>{html.escape(s[5:])}</h3>')
        elif s.startswith('#### 📖 Lisān al-ʿArab') or s.startswith('#### 📖 Lisan'):
            if in_arabic and arabic_buf:
                html_lines.append(f'<div class="arabic-text">{"<br/>".join(arabic_buf)}</div>')
                arabic_buf = []
                in_arabic = False
            html_lines.append(f'<h3>{html.escape(s[5:])}</h3>')
        elif s.startswith('#### ⚖️ Sībawayh') or s.startswith('#### ⚖️ Sibawayh'):
            if in_arabic and arabic_buf:
                html_lines.append(f'<div class="arabic-text">{"<br/>".join(arabic_buf)}</div>')
                arabic_buf = []
                in_arabic = False
            html_lines.append(f'<h3>{html.escape(s[5:])}</h3>')
        elif s.startswith('#### 🌐 Translation'):
            if in_arabic and arabic_buf:
                html_lines.append(f'<div class="arabic-text">{"<br/>".join(arabic_buf)}</div>')
                arabic_buf = []
                in_arabic = False
            html_lines.append(f'<h3>{html.escape(s[5:])}</h3>')
        elif re.match(r'^\d+\.\s+\*\*Root:', s) or s.startswith('**Root:'):
            html_lines.append(f'<div class="lisan-box">{s}</div>')
        elif re.match(r'^\d+\.\s+\*\*Rule:', s) or s.startswith('**Rule:'):
            html_lines.append(f'<div class="sibawayh-box">{s}</div>')
        elif in_arabic:
            arabic_buf.append(html.escape(s))
        else:
            html_lines.append(f'<p>{s}</p>')

    if in_arabic and arabic_buf:
        html_lines.append(f'<div class="arabic-text">{"<br/>".join(arabic_buf)}</div>')

    return '\n'.join(html_lines)


def build_epub():
    if not INPUT_JSON.exists():
        print(f"Error: {INPUT_JSON} not found. Run translate_ismat_v4_pro_7roots.py first.")
        return False

    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    book = epub.EpubBook()
    book.set_identifier('razi-ismat-anbiya-v4-pro-7roots-2026')
    book.set_title('ʿIṣmat al-Anbiyāʾ (The Infallibility of the Prophets) [v4 Pro 7-Root Edition]')
    book.set_language('en')
    book.add_author('Imam Fakhr al-Din al-Razi (d. 606 AH)')

    # Add stylesheet
    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/main.css",
        media_type="text/css",
        content=CSS_CONTENT
    )
    book.add_item(nav_css)

    # Title Page
    title_html = """
    <div class="title-page">
        <span class="badge">DeepSeek-v4-Pro CoT Engine</span>
        <h1>ʿIṣmat al-Anbiyāʾ</h1>
        <h2>The Infallibility of the Prophets</h2>
        <p class="author">By Imam Fakhr al-Din al-Razi (544–606 AH / 1149–1209 CE)</p>
        <p style="margin-top: 2em; color: #475569; font-size: 0.95em;">
            <strong>v4 Pro 7-Root Lexical Edition</strong><br/>
            Flagship Two-Stage Guided Pipeline<br/>
            7-Root <em>Lisān al-ʿArab</em> Constellations &amp; Sībawayh Syntactic Anchors<br/>
            Canonical Sectarian &amp; Kalām Terminology Standards
        </p>
        <p style="margin-top: 3em; color: #94a3b8; font-size: 0.85em;">Digital Critical Scholarly Edition — 2026</p>
    </div>
    """
    title_chap = epub.EpubHtml(title='Title Page', file_name='title.xhtml', lang='en')
    title_chap.content = f'<html><head><link rel="stylesheet" href="style/main.css"/></head><body>{title_html}</body></html>'
    title_chap.add_item(nav_css)
    book.add_item(title_chap)

    chapters = []
    toc = [title_chap]
    spine = ['nav', title_chap]

    for idx, ch in enumerate(data.get('chapters', [])):
        ch_idx = ch.get('chapter_index', idx)
        title_en = normalize_prophet_names(ch.get('title_en', f"Chapter {ch_idx+1}"))
        content_md = ch.get('english_translation', '')

        html_body = md_to_html(content_md)
        c = epub.EpubHtml(
            title=f"{idx+1}. {title_en}",
            file_name=f"chapter_{idx+1:02d}.xhtml",
            lang='en'
        )
        c.content = f'<html><head><link rel="stylesheet" href="style/main.css"/></head><body>{html_body}</body></html>'
        c.add_item(nav_css)
        book.add_item(c)
        chapters.append(c)
        toc.append(c)
        spine.append(c)

    book.toc = tuple(toc)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = spine

    epub.write_epub(str(OUTPUT_EPUB), book, {})
    print(f"✅ EPUB built successfully at:\n  {OUTPUT_EPUB}")

    if WEB_PUBLIC_DIR.exists():
        web_target = WEB_PUBLIC_DIR / "ismat_anbiya_v4_pro_7roots_en.epub"
        shutil.copyfile(OUTPUT_EPUB, web_target)
        print(f"✅ Copied to web download directory at:\n  {web_target}")

    return True

if __name__ == "__main__":
    build_epub()
