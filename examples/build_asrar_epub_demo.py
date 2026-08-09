"""
build_asrar_tanzil_epub.py

Generates a Kindle-ready EPUB for Imam Fakhr al-Din al-Razi's
'Asrār al-Tanzīl wa Anwār al-Taʾwīl' (Secrets of Revelation and Lights of Interpretation).

Features:
- High-fidelity typography (Amiri for Arabic, Inter for English).
- Front matter with Al-Farahidi & Bayt al-Hikmah translation methodology.
- Bilingual Table of Contents (English + Arabic Index).
- Auto-mirrors output to local EPUB directory and remote web server.
"""

import json, os, sys
from pathlib import Path
from ebooklib import epub

INPUT_JSON = Path("data/new_works/asrar_tanzil_translated.json")
OUTPUT_EPUB = Path("data/kindle_volumes/asrar_tanzil_en.epub")
OUTPUT_EPUB.parent.mkdir(parents=True, exist_ok=True)
PUBLIC_DEST = Path("/home/absolut7/Documents/26apps/gravityremote2/antigravity_phone_chat/public/asrar_tanzil_en.epub")

STYLE_CSS = """
@namespace epub "http://www.idpf.org/2007/ops";
body {
    font-family: 'Inter', Georgia, serif;
    font-size: 1em;
    line-height: 1.6;
    margin: 5%;
    color: #111111;
}
h1, h2, h3, h4 {
    font-family: 'Inter', sans-serif;
    color: #1a252f;
    line-height: 1.3;
}
h1 { font-size: 1.8em; border-bottom: 2px solid #34495e; padding-bottom: 0.3em; margin-top: 1em; text-align: center; }
h2 { font-size: 1.4em; color: #2c3e50; margin-top: 1.5em; border-bottom: 1px solid #bdc3c7; }
h3 { font-size: 1.2em; color: #16a085; margin-top: 1.2em; }
h4 { font-size: 1.1em; color: #7f8c8d; margin-top: 1em; text-transform: uppercase; letter-spacing: 0.05em; }
p { margin-bottom: 1em; text-align: justify; text-indent: 1.5em; }
.arabic-text {
    font-family: 'Amiri', 'Traditional Arabic', serif;
    font-size: 1.35em;
    line-height: 2.1;
    direction: rtl;
    text-align: right;
    background-color: #f8f9fa;
    border-right: 4px solid #16a085;
    padding: 15px 20px;
    margin: 1.5em 0;
    border-radius: 4px;
}
.translation-box {
    background-color: #ffffff;
    border-left: 4px solid #2980b9;
    padding: 15px 20px;
    margin: 1.5em 0;
}
.lexicon-box {
    background-color: #fdfefe;
    border: 1px solid #e1e8ed;
    border-left: 4px solid #f39c12;
    padding: 15px;
    margin: 1.5em 0;
    font-size: 0.95em;
}
.grammar-box {
    background-color: #fdfefe;
    border: 1px solid #e1e8ed;
    border-left: 4px solid #8e44ad;
    padding: 15px;
    margin: 1.5em 0;
    font-size: 0.95em;
}
.intro-box {
    background-color: #eaf2f8;
    border: 1px solid #aeb6bf;
    padding: 20px;
    border-radius: 5px;
    margin-bottom: 2em;
}
"""


def markdown_to_html(md_text):
    lines = md_text.splitlines()
    html_out = []
    in_p = False

    for line in lines:
        l = line.strip()
        if not l:
            if in_p:
                html_out.append("</p>")
                in_p = False
            continue

        if l.startswith("### "):
            if in_p: html_out.append("</p>"); in_p = False
            html_out.append(f"<h2>{l[4:]}</h2>")
        elif l.startswith("#### 📜 Original Arabic Text"):
            if in_p: html_out.append("</p>"); in_p = False
            html_out.append(f"<h3>📜 Original Arabic Text (النص العربي الأصلي)</h3>")
        elif l.startswith("#### 📖 Lisan"):
            if in_p: html_out.append("</p>"); in_p = False
            html_out.append(f"<h3>📖 Lisan al-Arab Lexical Note (Translation Anchor)</h3>")
        elif l.startswith("#### ⚖️ Sibawayh"):
            if in_p: html_out.append("</p>"); in_p = False
            html_out.append(f"<h3>⚖️ Sibawayh Grammatical Note (Syntactic Anchor)</h3>")
        elif l.startswith("#### 🌐 Translation"):
            if in_p: html_out.append("</p>"); in_p = False
            html_out.append(f"<h3>🌐 Translation (Imam Al-Razi's Voice — Lexically Guided)</h3>")
        elif l.startswith("**Root:") or l.startswith("**Rule:"):
            if in_p: html_out.append("</p>"); in_p = False
            html_out.append(f"<p style='text-indent:0;'><strong>{l}</strong></p>")
        else:
            if not in_p:
                html_out.append("<p>")
                in_p = True
            else:
                html_out.append(" ")
            html_out.append(l)

    if in_p:
        html_out.append("</p>")

    return "\n".join(html_out)


def build_epub():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    book = epub.EpubBook()
    book.set_identifier("razi-asrar-tanzil-2026")
    book.set_title("Secrets of Revelation and Lights of Interpretation (أسرار التنزيل وأنوار التأويل)")
    book.set_language("en")
    book.add_author("Imam Fakhr al-Din al-Razi (d. 606 AH)")

    style_item = epub.EpubItem(
        uid="style_default", file_name="style/default.css",
        media_type="text/css", content=STYLE_CSS
    )
    book.add_item(style_item)

    # Title Page
    title_item = epub.EpubHtml(title="Title Page", file_name="title.xhtml", lang="en")
    title_item.content = f"""
        <html>
        <head><link rel="stylesheet" href="style/default.css" type="text/css"/></head>
        <body>
          <div style="text-align: center; margin-top: 3em;">
            <h1 style="font-size: 2.2em; border: none;">Secrets of Revelation and Lights of Interpretation</h1>
            <h2 style="font-size: 1.6em; border: none; color: #16a085;">أسرار التنزيل وأنوار التأويل</h2>
            <p style="text-indent: 0; font-size: 1.2em; margin-top: 2em;"><strong>Author:</strong> Imam Fakhr al-Din al-Razi (d. 606 AH / 1210 CE)</p>
            <p style="text-indent: 0; font-size: 1.1em;"><strong>Translator:</strong> Two-Stage Lexicographically Guided 1M DeepSeek Engine</p>
            <p style="text-indent: 0; font-size: 0.9em; color: #7f8c8d; margin-top: 3em;">Standardized Sense-for-Sense Edition</p>
          </div>
        </body>
        </html>
    """
    book.add_item(title_item)

    # Academic Notice with Al-Farahidi & Bayt al-Hikmah methodology
    notice_item = epub.EpubHtml(title="Academic Notice", file_name="notice.xhtml", lang="en")
    notice_item.content = """
        <html>
        <head><link rel="stylesheet" href="style/default.css" type="text/css"/></head>
        <body>
          <h1>Academic Notice & Classical Methodology</h1>
          <div class="intro-box">
            <p style="text-indent: 0;"><strong>Two-Stage Guided Engine:</strong> In this edition, <strong>Lisān al-ʿArab</strong> root analysis and <strong>Sibawayh's Al-Kitāb</strong> syntax rules are extracted <em>first</em> to anchor and constrain the English translation, followed by the sense-for-sense rendering in <strong>Imam al-Razi's authentic voice</strong>.</p>
          </div>
          
          <h2>Foundational Translation & Lexicographical Principles</h2>
          <p><strong>Al-Khalīl ibn Aḥmad al-Farāhīdī (718–786 AD):</strong> Creator of the first Arabic dictionary (<em>Kitāb al-ʿAyn</em>). He introduced an algorithmic approach to classical Arabic linguistics by calculating every possible combination and permutation of Arabic root letters to map out the entire vocabulary of the language.</p>
          <p><strong>The Translation Movement (Bayt al-Ḥikmah):</strong> Master scholars like <strong>Ḥunayn ibn Isḥāq</strong> created early standardization rules for cross-lingual translation—moving away from literal word-for-word rendering toward systematic, sense-for-sense translation theories that preserve philosophical nuance while maintaining total fidelity to original semantic intent.</p>
        </body>
        </html>
    """
    book.add_item(notice_item)

    chapters_items = [title_item, notice_item]
    toc_links = [title_item, notice_item]

    for ch in data["chapters"]:
        ch_idx = ch["chapter_index"] + 1
        title_ar = ch["title_ar"]
        title_en = ch["title_en"]
        body_html = markdown_to_html(ch["english_translation"])

        ch_item = epub.EpubHtml(
            title=f"Chapter {ch_idx}: {title_en}",
            file_name=f"chapter_{ch_idx:02d}.xhtml",
            lang="en"
        )
        ch_item.content = f"""
            <html>
            <head><link rel="stylesheet" href="style/default.css" type="text/css"/></head>
            <body>
              {body_html}
            </body>
            </html>
        """
        book.add_item(ch_item)
        chapters_items.append(ch_item)
        toc_links.append(epub.Link(f"chapter_{ch_idx:02d}.xhtml", f"{ch_idx}. {title_en} ({title_ar})", f"ch_{ch_idx}"))

    book.toc = toc_links
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ['nav'] + chapters_items

    epub.write_epub(OUTPUT_EPUB, book, {})
    print(f"✅ EPUB built successfully at:\n  {OUTPUT_EPUB.resolve()}")

    if PUBLIC_DEST.parent.exists():
        import shutil
        shutil.copy(OUTPUT_EPUB, PUBLIC_DEST)
        print(f"✅ Copied to web download directory at:\n  {PUBLIC_DEST.resolve()}")


if __name__ == "__main__":
    build_epub()
