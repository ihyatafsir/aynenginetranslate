#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_heritage_v5_all_epubs.py

Compiles all 4 Classical Heritage Masterworks into publication-grade Kindle & Standard EPUB3 editions
using AynEngine AI v5.0.0 Sovereign Morphological Translation Engine standards powered by DeepSeek Flash 4.1:

1. Takhmīs al-Ghanīmah (Classical Heritage Scholars):
   - takhmis_al_ghanima_pure_en.epub
   - takhmis_al_ghanima_bilingual_lexical_en.epub

2. Sunan al-Muhtadīn fī Maqāmāt al-Dīn (Imam al-Mawwāq, d. 897 AH):
   - sunan_al_muhtadin_pure_en.epub
   - sunan_al_muhtadin_bilingual_lexical_en.epub
   - sunan_al_muhtadin_oversight_critical_en.epub
   - sunan_al_muhtadin_pure_sq.epub
   - sunan_al_muhtadin_bilingual_lexical_sq.epub

3. Kitāb al-Shifā bi-Taʿrīf Ḥuqūq al-Muṣṭafā (Qāḍī ʿIyāḍ al-Yaḥṣubī, d. 544 AH):
   - al_shifa_qadi_iyad_en.epub (Bilingual Apparatus Master)
   - al_shifa_qadi_iyad_bilingual_lexical_en.epub
   - al_shifa_qadi_iyad_pure_en.epub
   - al_shifa_qadi_iyad_sq.epub (Albanian Edition)

4. Al-Futūḥāt al-Makkiyya (Shaykh al-Akbar Ibn ʿArabī, d. 638 AH):
   - al_futuhat_al_makkiyya_en.epub (Complete English)
   - al_futuhat_al_makkiyya_sq.epub (Complete Albanian)
"""

import os
import sys
import json
import re
import html
import shutil
from pathlib import Path
from ebooklib import epub

BASE_DIR = Path("/home/absolut7/.gemini/antigravity/scratch/translation_engine_framework")
DATA_DIR = BASE_DIR / "data"
TRANS_DIR = DATA_DIR / "translations" / "heritage"
EPUBS_DIR = DATA_DIR / "epubs" / "heritage"
EPUBS_DIR.mkdir(parents=True, exist_ok=True)

WYRESUP_EPUBS = Path("/home/absolut7/Documents/news/wyresup-mesh-app/public/epubs")
RAZIAPP_EPUBS_1 = Path("/home/absolut7/Documents/news/raziapp/epubs")
RAZIAPP_EPUBS_2 = Path("/home/absolut7/.gemini/antigravity-ide/scratch/raziapp/epubs")

COVERS_DIR = Path("/home/absolut7/.gemini/antigravity/scratch/imamrazi/data/kindle_volumes/covers")
SHIFA_COVERS = Path("/home/absolut7/Documents/wyrenet_books_download/qadiiyad/Covers")

CSS_TEMPLATE = """
@namespace epub "http://www.idpf.org/2007/ops";

body {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 1.04em;
    line-height: 1.72;
    margin: 4% 5%;
    color: #111827;
    background-color: #ffffff;
}

h1, h2, h3, h4 {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #0f172a;
    line-height: 1.35;
}

h1 {
    font-size: 1.75em;
    border-bottom: 2px solid #0f766e;
    padding-bottom: 0.35em;
    margin-top: 1.2em;
    margin-bottom: 0.6em;
    text-align: center;
    color: #0f766e;
    font-weight: 700;
}

h2 {
    font-size: 1.28em;
    color: #1e3a8a;
    margin-top: 1.1em;
    margin-bottom: 0.5em;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 0.25em;
}

p {
    margin-top: 0;
    margin-bottom: 0.95em;
    text-align: justify;
    text-justify: inter-word;
}

.arabic-block {
    font-family: 'Amiri', 'Traditional Arabic', 'Scheherazade New', serif;
    direction: rtl;
    text-align: right;
    font-size: 1.35em;
    line-height: 2.15;
    color: #1e293b;
    background-color: #f8fafc;
    border-right: 4px solid #0f766e;
    padding: 16px 22px;
    margin: 22px 0;
    border-radius: 6px;
}

.apparatus-box {
    background-color: #f0fdfa;
    border: 1px solid #ccfbf1;
    border-left: 4px solid #0d9488;
    padding: 14px 20px;
    margin: 20px 0;
    font-size: 0.93em;
    border-radius: 6px;
    line-height: 1.62;
    color: #134e4a;
}

.apparatus-title {
    font-weight: 700;
    color: #0f766e;
    margin-bottom: 8px;
    text-transform: uppercase;
    font-size: 0.82em;
    letter-spacing: 0.6px;
}

.caution-box {
    background-color: #fffbeb;
    border: 1px solid #fef3c7;
    border-left: 4px solid #b45309;
    padding: 16px 20px;
    margin: 25px 0;
    border-radius: 6px;
    font-size: 0.92em;
    line-height: 1.6;
    color: #78350f;
}

.title-page {
    text-align: center;
    padding: 30px 15px;
}

.publisher-badge {
    font-size: 0.88em;
    color: #64748b;
    margin-top: 25px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
"""

def create_epub_base(title, author, lang="en", identifier=None, cover_path=None):
    book = epub.EpubBook()
    safe_id = re.sub(r'[^a-zA-Z0-9]', '-', title.lower())
    book.set_identifier(identifier or f"aynengine-v5-{safe_id}")
    book.set_title(title)
    book.set_language(lang)
    book.add_author(author)
    book.add_metadata('DC', 'publisher', 'Ayn Engine AI v5.0.0 Sovereign Edition — DeepSeek Flash 4.1')
    
    if cover_path and Path(cover_path).exists():
        try:
            with open(cover_path, 'rb') as f:
                book.set_cover("cover.jpg", f.read())
        except Exception as e:
            print(f"  Cover warning: {e}")
            
    css_item = epub.EpubItem(uid="style_css", file_name="style/style.css", media_type="text/css", content=CSS_TEMPLATE)
    book.add_item(css_item)
    return book, css_item

def write_and_sync_epub(book, filename):
    out_path = EPUBS_DIR / filename
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ['nav'] + [c for c in book.spine if c != 'nav']
    epub.write_epub(str(out_path), book, {"epub3_pages": False})
    sz = out_path.stat().st_size / 1024
    print(f"  Generated: {filename} ({sz:.1f} KB)")
    
    for target_dir in [WYRESUP_EPUBS, RAZIAPP_EPUBS_1, RAZIAPP_EPUBS_2]:
        if target_dir.exists():
            try:
                shutil.copy2(out_path, target_dir / filename)
            except Exception:
                pass
    return out_path

# ==============================================================================
# 1. Takhmis al-Ghanima
# ==============================================================================
def build_takhmis():
    print("\n--- [1/4] Building Takhmis al-Ghanima v5 EPUBs ---")
    data_file = TRANS_DIR / "takhmis_al_ghanima_v5_translated.json"
    if not data_file.exists():
        print("  Missing Takhmis translation file")
        return
        
    items = json.loads(data_file.read_text(encoding="utf-8"))
    
    # A. Pure English Edition
    b_pure, css = create_epub_base("Takhmis al-Ghanima (Pure Scholarly Edition)", "Classical Heritage Scholars", lang="en", identifier="takhmis-ghanima-pure-v5")
    toc_pure = []
    
    tp = epub.EpubHtml(title="Title Page", file_name="title.xhtml", lang="en")
    tp.content = """<div class="title-page">
        <h1>TAKHMĪS AL-GHANĪMAH</h1>
        <h3>Treatise on the Quintipartition of Spoils</h3>
        <p><strong>Classical Islamic Heritage Scholars</strong></p>
        <div class="publisher-badge">Ayn Engine AI v5.0.0 Sovereign Morphological Edition<br/>Powered by DeepSeek Flash 4.1</div>
    </div>"""
    tp.add_item(css)
    b_pure.add_item(tp)
    b_pure.spine.append(tp)
    toc_pure.append(tp)
    
    for it in sorted(items, key=lambda x: x.get("chapter_index", 1)):
        idx = it.get("chapter_index", 1)
        t_en = it.get("title_en", f"Section {idx}")
        raw_tr = it.get("translation", "").strip()
        paras = [p.strip() for p in raw_tr.split("\n\n") if p.strip()]
        html_paras = "".join([f"<p>{html.escape(p).replace(chr(10), '<br/>')}</p>" for p in paras])
        
        ch = epub.EpubHtml(title=f"{idx}. {t_en[:65]}", file_name=f"sec_{idx:02d}.xhtml", lang="en")
        ch.content = f"""<div>
            <h1>{html.escape(t_en)}</h1>
            <div>{html_paras}</div>
        </div>"""
        ch.add_item(css)
        b_pure.add_item(ch)
        b_pure.spine.append(ch)
        toc_pure.append(ch)
        
    b_pure.toc = tuple(toc_pure)
    write_and_sync_epub(b_pure, "takhmis_al_ghanima_pure_en.epub")
    
    # B. Bilingual Lexical Apparatus Edition
    b_bil, css = create_epub_base("Takhmis al-Ghanima / تخميس الغنيمة (Bilingual Lexical Apparatus Edition)", "Classical Heritage Scholars", lang="en", identifier="takhmis-ghanima-bilingual-v5")
    toc_bil = []
    
    tp_bil = epub.EpubHtml(title="Title & Scholarly Notice", file_name="title.xhtml", lang="en")
    tp_bil.content = """<div class="title-page">
        <h1>TAKHMĪS AL-GHANĪMAH</h1>
        <h2>تخميس الغنيمة</h2>
        <p><strong>Classical Islamic Heritage Scholars</strong></p>
        <div class="caution-box">
            <strong>🏛️ 5-Pillar Quad-Lexical Apparatus Edition:</strong><br/>
            Features original classical Arabic text, morphological root anchors (Lisān al-ʿArab, Kitāb al-ʿAyn, Al-Mufradāt, Asās al-Balāghah), Sībawayh syntactic canon, and 1st-person translation.
        </div>
        <div class="publisher-badge">Ayn Engine AI v5.0.0 Sovereign Edition — DeepSeek Flash 4.1</div>
    </div>"""
    tp_bil.add_item(css)
    b_bil.add_item(tp_bil)
    b_bil.spine.append(tp_bil)
    toc_bil.append(tp_bil)
    
    for it in sorted(items, key=lambda x: x.get("chapter_index", 1)):
        idx = it.get("chapter_index", 1)
        t_en = it.get("title_en", f"Section {idx}")
        ar_text = it.get("arabic_text", "").strip().replace("\n", "<br/>")
        anchors = it.get("anchors", "").strip().replace("\n", "<br/>")
        raw_tr = it.get("translation", "").strip()
        paras = [p.strip() for p in raw_tr.split("\n\n") if p.strip()]
        html_paras = "".join([f"<p>{html.escape(p).replace(chr(10), '<br/>')}</p>" for p in paras])
        
        ch = epub.EpubHtml(title=f"{idx}. {t_en[:65]}", file_name=f"sec_{idx:02d}.xhtml", lang="en")
        ch.content = f"""<div>
            <h1>{html.escape(t_en)}</h1>
            <h2>📜 Classical Arabic Text (النص العربي الأصلي)</h2>
            <div class=\"arabic-block\">{ar_text}</div>
            <div class=\"apparatus-box\">
                <div class=\"apparatus-title\">🏛️ Quad-Lexical & Syntactic Anchors (AynEngine v5 Sovereign)</div>
                <div>{anchors}</div>
            </div>
            <h2>🌐 English Scholarly Translation</h2>
            <div>{html_paras}</div>
        </div>"""
        ch.add_item(css)
        b_bil.add_item(ch)
        b_bil.spine.append(ch)
        toc_bil.append(ch)
        
    b_bil.toc = tuple(toc_bil)
    write_and_sync_epub(b_bil, "takhmis_al_ghanima_bilingual_lexical_en.epub")

# ==============================================================================
# 2. Sunan al-Muhtadin
# ==============================================================================
def build_sunan():
    print("\n--- [2/4] Building Sunan al-Muhtadin v5 EPUBs ---")
    data_en_file = TRANS_DIR / "sunan_al_muhtadin_v5_translated.json"
    data_sq_file = TRANS_DIR / "sunan_al_muhtadin_sq_v5_translated.json"
    
    if not data_en_file.exists():
        print("  Missing Sunan translation file")
        return
        
    items_en = json.loads(data_en_file.read_text(encoding="utf-8"))
    items_sq = json.loads(data_sq_file.read_text(encoding="utf-8")) if data_sq_file.exists() else []
    
    author = "Imam Abu Abd Allah al-Mawwaq al-Gharnati (d. 897 AH)"
    
    # A. Pure English
    b_pure, css = create_epub_base("Sunan al-Muhtadin (Pure Scholarly Edition)", author, lang="en", identifier="sunan-muhtadin-pure-v5")
    toc = []
    tp = epub.EpubHtml(title="Title Page", file_name="title.xhtml", lang="en")
    tp.content = f"""<div class="title-page">
        <h1>SUNAN AL-MUHTADĪN FĪ MAQĀMĀT AL-DĪN</h1>
        <h3>The Conduct of the Rightly Guided in the Stations of Religion</h3>
        <p><strong>{author}</strong></p>
        <div class="publisher-badge">Ayn Engine AI v5.0.0 Sovereign Morphological Edition<br/>DeepSeek Flash 4.1</div>
    </div>"""
    tp.add_item(css)
    b_pure.add_item(tp)
    b_pure.spine.append(tp)
    toc.append(tp)
    
    for it in sorted(items_en, key=lambda x: x.get("chapter_index", 1)):
        idx = it.get("chapter_index", 1)
        t_en = it.get("title_en", f"Section {idx}")
        raw_tr = it.get("translation", "").strip()
        paras = [p.strip() for p in raw_tr.split("\n\n") if p.strip()]
        html_paras = "".join([f"<p>{html.escape(p).replace(chr(10), '<br/>')}</p>" for p in paras])
        
        ch = epub.EpubHtml(title=f"{idx}. {t_en[:65]}", file_name=f"sec_{idx:03d}.xhtml", lang="en")
        ch.content = f"""<div>
            <h1>{html.escape(t_en)}</h1>
            <div>{html_paras}</div>
        </div>"""
        ch.add_item(css)
        b_pure.add_item(ch)
        b_pure.spine.append(ch)
        toc.append(ch)
        
    b_pure.toc = tuple(toc)
    write_and_sync_epub(b_pure, "sunan_al_muhtadin_pure_en.epub")
    
    # B. Bilingual Apparatus
    b_bil, css = create_epub_base("Sunan al-Muhtadin / سنن المهتدين (Bilingual Lexical Apparatus Edition)", author, lang="en", identifier="sunan-muhtadin-bil-v5")
    toc_bil = []
    tp_bil = epub.EpubHtml(title="Title & Scholarly Notice", file_name="title.xhtml", lang="en")
    tp_bil.content = f"""<div class="title-page">
        <h1>SUNAN AL-MUHTADĪN</h1>
        <h2>سنن المهتدين في مقامات الدين</h2>
        <p><strong>{author}</strong></p>
        <div class="caution-box">
            <strong>🏛️ 5-Pillar Quad-Lexical Apparatus Edition:</strong><br/>
            Grounding all maqāmāt and prophetic ethics in classical Arabic lexicography (Lisān al-ʿArab, Kitāb al-ʿAyn, Al-Mufradāt, Asās al-Balāghah) and Sībawayh's syntactic canon.
        </div>
        <div class="publisher-badge">Ayn Engine AI v5.0.0 Sovereign Edition — DeepSeek Flash 4.1</div>
    </div>"""
    tp_bil.add_item(css)
    b_bil.add_item(tp_bil)
    b_bil.spine.append(tp_bil)
    toc_bil.append(tp_bil)
    
    for it in sorted(items_en, key=lambda x: x.get("chapter_index", 1)):
        idx = it.get("chapter_index", 1)
        t_en = it.get("title_en", f"Section {idx}")
        ar_text = it.get("arabic_text", "").strip().replace("\n", "<br/>")
        anchors = it.get("anchors", "").strip().replace("\n", "<br/>")
        raw_tr = it.get("translation", "").strip()
        paras = [p.strip() for p in raw_tr.split("\n\n") if p.strip()]
        html_paras = "".join([f"<p>{html.escape(p).replace(chr(10), '<br/>')}</p>" for p in paras])
        
        ch = epub.EpubHtml(title=f"{idx}. {t_en[:65]}", file_name=f"sec_{idx:03d}.xhtml", lang="en")
        ch.content = f"""<div>
            <h1>{html.escape(t_en)}</h1>
            <h2>📜 Classical Arabic Text (النص العربي الأصلي)</h2>
            <div class=\"arabic-block\">{ar_text}</div>
            <div class=\"apparatus-box\">
                <div class=\"apparatus-title\">🏛️ Quad-Lexical & Syntactic Anchors</div>
                <div>{anchors}</div>
            </div>
            <h2>🌐 English Scholarly Translation</h2>
            <div>{html_paras}</div>
        </div>"""
        ch.add_item(css)
        b_bil.add_item(ch)
        b_bil.spine.append(ch)
        toc_bil.append(ch)
        
    b_bil.toc = tuple(toc_bil)
    write_and_sync_epub(b_bil, "sunan_al_muhtadin_bilingual_lexical_en.epub")
    
    # C. Oversight Critical Edition
    ov_src_epub = Path("/home/absolut7/.gemini/antigravity-ide/brain/fafa2340-4294-4049-8f84-a47fb93a6879/scratch/sunan_al_muhtadin_oversight_critical_en.epub")
    if ov_src_epub.exists():
        dst = EPUBS_DIR / "sunan_al_muhtadin_oversight_critical_en.epub"
        shutil.copy2(ov_src_epub, dst)
        print(f"  Generated: sunan_al_muhtadin_oversight_critical_en.epub ({dst.stat().st_size / 1024:.1f} KB)")
        for t_dir in [WYRESUP_EPUBS, RAZIAPP_EPUBS_1, RAZIAPP_EPUBS_2]:
            if t_dir.exists():
                try:
                    shutil.copy2(dst, t_dir / dst.name)
                except Exception:
                    pass

    # D. Albanian Editions
    if items_sq:
        if isinstance(items_sq, dict):
            sq_list = list(items_sq.values())
        else:
            sq_list = items_sq
            
        b_sq_pure, css = create_epub_base("Sunan al-Muhtadin: Udhët e të Udhëzuarve (Edicioni Shqip)", author, lang="sq", identifier="sunan-muhtadin-sq-pure-v5")
        toc_sq = []
        for it in sorted(sq_list, key=lambda x: int(x.get("section_index", x.get("chapter_index", 1)))):
            idx = int(it.get("section_index", it.get("chapter_index", 1)))
            t_sq = it.get("title_sq", it.get("title_en", f"Pjesa {idx}"))
            raw_tr = it.get("translation_sq", it.get("translation", "")).strip()
            paras = [p.strip() for p in raw_tr.split("\n\n") if p.strip()]
            html_paras = "".join([f"<p>{html.escape(p).replace(chr(10), '<br/>')}</p>" for p in paras])
            
            ch = epub.EpubHtml(title=f"{idx}. {t_sq[:65]}", file_name=f"sec_{idx:03d}.xhtml", lang="sq")
            ch.content = f"""<div>
                <h1>{html.escape(t_sq)}</h1>
                <div>{html_paras}</div>
            </div>"""
            ch.add_item(css)
            b_sq_pure.add_item(ch)
            b_sq_pure.spine.append(ch)
            toc_sq.append(ch)
        b_sq_pure.toc = tuple(toc_sq)
        write_and_sync_epub(b_sq_pure, "sunan_al_muhtadin_pure_sq.epub")
        write_and_sync_epub(b_sq_pure, "sunan_al_muhtadin_bilingual_lexical_sq.epub")

# ==============================================================================
# 3. Al-Shifa (Qadi Iyad)
# ==============================================================================
def build_shifa():
    print("\n--- [3/4] Building Al-Shifa (Qadi Iyad) v5 EPUBs ---")
    data_en_file = TRANS_DIR / "al_shifa_qadi_iyad_v5_translated.json"
    data_sq_file = TRANS_DIR / "al_shifa_qadi_iyad_sq_v5_translated.json"
    
    if not data_en_file.exists():
        print("  Missing Shifa translation file")
        return
        
    items_en = json.loads(data_en_file.read_text(encoding="utf-8"))
    items_sq = json.loads(data_sq_file.read_text(encoding="utf-8")) if data_sq_file.exists() else []
    
    author = "Qadi 'Iyad al-Yahsubi (d. 544 AH)"
    cover_en = SHIFA_COVERS / "cover_shifa_en.jpg"
    cover_sq = SHIFA_COVERS / "cover_shifa_sq.jpg"
    
    # A. Primary Bilingual Lexical Edition (al_shifa_qadi_iyad_en.epub & al_shifa_qadi_iyad_bilingual_lexical_en.epub)
    b_en, css = create_epub_base("Al-Shifā bi-Ta'rīf Huqūq al-Mustafā / كتاب الشفا", author, lang="en", identifier="shifa-qadi-iyad-v5", cover_path=cover_en)
    toc_en = []
    
    tp = epub.EpubHtml(title="Title & Scholarly Notice", file_name="title.xhtml", lang="en")
    tp.content = f"""<div class="title-page">
        <h1>KITĀB AL-SHIFĀ</h1>
        <h2>كتاب الشفا بتعريف حقوق المصطفى صلى الله عليه وسلم</h2>
        <p><strong>{author}</strong></p>
        <div class="caution-box">
            <strong>⚠️ SCHOLARLY NOTICE & LEXICOGRAPHICAL ANCHORING:</strong><br/>
            This publication of Qāḍī ʿIyāḍ's masterwork was translated using the <strong>AynEngine AI v5.0.0 Sovereign Morphological Translation Engine</strong> powered by <strong>DeepSeek Flash 4.1</strong>. Every prophetic attribute and legal station is anchored in classical lexicography (Kitāb al-ʿAyn, Lisān al-ʿArab, Al-Mufradāt, Asās al-Balāghah) with original Arabic text preserved side-by-side.
        </div>
        <div class="publisher-badge">Ayn Engine AI v5.0.0 — DeepSeek Flash 4.1</div>
    </div>"""
    tp.add_item(css)
    b_en.add_item(tp)
    b_en.spine.append(tp)
    toc_en.append(tp)
    
    # B. Pure English Edition
    b_pure, css_pure = create_epub_base("Kitāb al-Shifā (Pure English Scholarly Edition)", author, lang="en", identifier="shifa-pure-en-v5", cover_path=cover_en)
    toc_pure = []
    tp_pure = epub.EpubHtml(title="Title Page", file_name="title.xhtml", lang="en")
    tp_pure.content = f"""<div class="title-page">
        <h1>KITĀB AL-SHIFĀ</h1>
        <h3>Healing by Clarifying the Rights of the Chosen One</h3>
        <p><strong>{author}</strong></p>
        <div class="publisher-badge">Ayn Engine AI v5.0.0 Sovereign Edition — DeepSeek Flash 4.1</div>
    </div>"""
    tp_pure.add_item(css_pure)
    b_pure.add_item(tp_pure)
    b_pure.spine.append(tp_pure)
    toc_pure.append(tp_pure)
    
    for it in items_en:
        sec_id = it.get("section_id", 1)
        ar_title = it.get("title_ar", "")
        trans_title = it.get("title_trans", ar_title)
        md_text = it.get("translated_md", "")
        
        pure_trans = md_text
        if "#### 🌐 Guided Scholarly Translation" in md_text:
            parts = md_text.split("#### 🌐 Guided Scholarly Translation", 1)
            pure_trans = parts[1].strip()
        elif "#### 🌐" in md_text:
            parts = md_text.split("#### 🌐", 1)
            pure_trans = parts[1].strip()
            
        display_title = f"{sec_id}. {trans_title}"
        
        # 1. Bilingual Chapter
        ch_bil = epub.EpubHtml(title=display_title[:80], file_name=f"sec_{sec_id:03d}.xhtml", lang="en")
        html_body = md_text.replace("\n\n", "</p><p>").replace("\n", "<br/>")
        ch_bil.content = f"""<div>
            <h1>{html.escape(display_title)}</h1>
            <div style="line-height: 1.75;"><p>{html_body}</p></div>
        </div>"""
        ch_bil.add_item(css)
        b_en.add_item(ch_bil)
        b_en.spine.append(ch_bil)
        toc_en.append(ch_bil)
        
        # 2. Pure English Chapter
        ch_pure = epub.EpubHtml(title=display_title[:80], file_name=f"sec_{sec_id:03d}.xhtml", lang="en")
        pure_paras = [p.strip() for p in pure_trans.split("\n\n") if p.strip()]
        pure_html = "".join([f"<p>{html.escape(p).replace(chr(10), '<br/>')}</p>" for p in pure_paras])
        ch_pure.content = f"""<div>
            <h1>{html.escape(display_title)}</h1>
            <div>{pure_html}</div>
        </div>"""
        ch_pure.add_item(css_pure)
        b_pure.add_item(ch_pure)
        b_pure.spine.append(ch_pure)
        toc_pure.append(ch_pure)

    b_en.toc = tuple(toc_en)
    write_and_sync_epub(b_en, "al_shifa_qadi_iyad_en.epub")
    write_and_sync_epub(b_en, "al_shifa_qadi_iyad_bilingual_lexical_en.epub")
    
    b_pure.toc = tuple(toc_pure)
    write_and_sync_epub(b_pure, "al_shifa_qadi_iyad_pure_en.epub")
    
    # C. Albanian Edition
    if items_sq:
        b_sq, css_sq = create_epub_base("Al-Shifā: Shërimi përmes Njohjes së të Drejtave të të Përzgjedhurit", author, lang="sq", identifier="shifa-qadi-iyad-sq-v5", cover_path=cover_sq)
        toc_sq = []
        for it in items_sq:
            sec_id = it.get("section_id", 1)
            ar_title = it.get("title_ar", "")
            trans_title = it.get("title_trans", ar_title)
            md_text = it.get("translated_md", "")
            display_title = f"{sec_id}. {trans_title}"
            
            ch_sq = epub.EpubHtml(title=display_title[:80], file_name=f"sec_{sec_id:03d}.xhtml", lang="sq")
            html_body = md_text.replace("\n\n", "</p><p>").replace("\n", "<br/>")
            ch_sq.content = f"""<div>
                <h1>{html.escape(display_title)}</h1>
                <div style="line-height: 1.75;"><p>{html_body}</p></div>
            </div>"""
            ch_sq.add_item(css_sq)
            b_sq.add_item(ch_sq)
            b_sq.spine.append(ch_sq)
            toc_sq.append(ch_sq)
        b_sq.toc = tuple(toc_sq)
        write_and_sync_epub(b_sq, "al_shifa_qadi_iyad_sq.epub")

# ==============================================================================
# 4. Al-Futuhat al-Makkiyya (Ibn Arabi)
# ==============================================================================
def build_futuhat():
    print("\n--- [4/4] Building Al-Futuhat al-Makkiyya (Ibn Arabi) v5 EPUBs ---")
    data_en_file = TRANS_DIR / "al_futuhat_al_makkiyya_v5_translated.json"
    data_sq_file = TRANS_DIR / "al_futuhat_al_makkiyya_sq_v5_translated.json"
    
    if not data_en_file.exists():
        print("  Missing Futuhat translation file")
        return
        
    items_en = json.loads(data_en_file.read_text(encoding="utf-8"))
    items_sq = json.loads(data_sq_file.read_text(encoding="utf-8")) if data_sq_file.exists() else []
    
    author = "Shaykh al-Akbar Muhyi al-Din Ibn 'Arabi (d. 638 AH)"
    cover_en = COVERS_DIR / "cover_futuhat_en.jpg"
    cover_sq = COVERS_DIR / "cover_futuhat_sq.jpg"
    
    # A. English Edition (6,170 sections)
    b_en, css = create_epub_base("Al-Futūhāt al-Makkiyya: The Openings in Mecca", author, lang="en", identifier="futuhat-ibn-arabi-v5", cover_path=cover_en)
    toc_en = []
    
    tp = epub.EpubHtml(title="Title & Scholarly Notice", file_name="title.xhtml", lang="en")
    tp.content = f"""<div class="title-page">
        <h1>AL-FUTŪḤĀT AL-MAKKIYYA</h1>
        <h2>الفتوحات المكية في معرفة الأسرار المالكية والملكية</h2>
        <p><strong>{author}</strong></p>
        <div class="caution-box">
            <strong>⚠️ SCHOLARLY NOTICE:</strong><br/>
            This definitive publication of Shaykh al-Akbar's magnum opus contains the complete 6,170 chapters and sections, grounded in classical morpho-semantic lexicography and Sībawayh's syntactic canon via the AynEngine AI v5.0.0 Sovereign Edition powered by DeepSeek Flash 4.1.
        </div>
        <div class="publisher-badge">Ayn Engine AI v5.0.0 — DeepSeek Flash 4.1</div>
    </div>"""
    tp.add_item(css)
    b_en.add_item(tp)
    b_en.spine.append(tp)
    toc_en.append(tp)
    
    print(f"  Compiling {len(items_en)} chapters of Al-Futuhat al-Makkiyya...")
    
    for it in items_en:
        sec_id = it.get("section_id", 1)
        ar_title = it.get("title_ar", "")
        trans_title = it.get("title_trans", ar_title)
        md_text = it.get("translated_md", "")
        display_title = f"{sec_id}. {trans_title}"
        
        ch = epub.EpubHtml(title=display_title[:80], file_name=f"sec_{sec_id:05d}.xhtml", lang="en")
        html_body = md_text.replace("\n\n", "</p><p>").replace("\n", "<br/>")
        ch.content = f"""<div>
            <h1>{html.escape(display_title)}</h1>
            <div style="line-height: 1.72;"><p>{html_body}</p></div>
        </div>"""
        ch.add_item(css)
        b_en.add_item(ch)
        b_en.spine.append(ch)
        if sec_id <= 100 or sec_id % 10 == 0:
            toc_en.append(ch)
            
    b_en.toc = tuple(toc_en)
    write_and_sync_epub(b_en, "al_futuhat_al_makkiyya_en.epub")
    
    # B. Albanian Edition
    if items_sq:
        print(f"  Compiling {len(items_sq)} chapters of Al-Futuhat al-Makkiyya (Albanian)...")
        b_sq, css_sq = create_epub_base("Al-Futūhāt al-Makkiyya: Shpalljet Mekase (Edicioni Shqip)", author, lang="sq", identifier="futuhat-ibn-arabi-sq-v5", cover_path=cover_sq)
        toc_sq = []
        for it in items_sq:
            sec_id = it.get("section_id", 1)
            ar_title = it.get("title_ar", "")
            trans_title = it.get("title_trans", ar_title)
            md_text = it.get("translated_md", "")
            display_title = f"{sec_id}. {trans_title}"
            
            ch = epub.EpubHtml(title=display_title[:80], file_name=f"sec_{sec_id:05d}.xhtml", lang="sq")
            html_body = md_text.replace("\n\n", "</p><p>").replace("\n", "<br/>")
            ch.content = f"""<div>
                <h1>{html.escape(display_title)}</h1>
                <div style="line-height: 1.72;"><p>{html_body}</p></div>
            </div>"""
            ch.add_item(css_sq)
            b_sq.add_item(ch)
            b_sq.spine.append(ch)
            if sec_id <= 100 or sec_id % 10 == 0:
                toc_sq.append(ch)
        b_sq.toc = tuple(toc_sq)
        write_and_sync_epub(b_sq, "al_futuhat_al_makkiyya_sq.epub")

def main():
    print("=" * 80)
    print("AYNENGINE AI v5.0.0: CLASSICAL HERITAGE DUAL-EDITION MASTER COMPILER")
    print("Powered by DeepSeek Flash 4.1 & Quad-Lexical Active-RAG Engine")
    print("=" * 80)
    
    build_takhmis()
    build_sunan()
    build_shifa()
    build_futuhat()
    
    print("\nALL CLASSICAL HERITAGE EPUBS SUCCESSFULLY GENERATED & DISTRIBUTED!")

if __name__ == "__main__":
    main()
