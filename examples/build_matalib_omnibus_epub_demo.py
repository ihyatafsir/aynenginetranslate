#!/usr/bin/env python3
"""
build_matalib_complete_omnibus_epub.py

Unified Single Omnibus EPUB Builder for Imam Fakhr al-Din al-Razi's
'Al-Maṭālib al-ʿAliyyah min al-ʿIlm al-Ilāhī' (The Sublime Inquiries into Divine Science)
Complete 9 Volumes in One Definitive Masterpiece Edition.
"""

import json, os, sys, re
from pathlib import Path
from ebooklib import epub

BASE_DIR = Path(__file__).parent.resolve()
NEW_WORKS_DIR = BASE_DIR / "data/new_works"
OUTPUT_EPUB = BASE_DIR / "data/kindle_volumes/al_matalib_al_aliyah_complete_en.epub"
OUTPUT_EPUB.parent.mkdir(parents=True, exist_ok=True)
PUBLIC_DEST = Path("/home/absolut7/Documents/26apps/gravityremote2/antigravity_phone_chat/public/al_matalib_al_aliyah_complete_en.epub")

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
h1 { font-size: 2.0em; border-bottom: 3px solid #16a085; padding-bottom: 0.3em; margin-top: 1em; text-align: center; }
h2 { font-size: 1.5em; color: #2c3e50; margin-top: 1.5em; border-bottom: 1px solid #bdc3c7; }
h3 { font-size: 1.25em; color: #16a085; margin-top: 1.2em; }
h4 { font-size: 1.1em; color: #7f8c8d; margin-top: 1em; text-transform: uppercase; letter-spacing: 0.05em; }
p { margin-bottom: 1em; text-align: justify; text-indent: 1.5em; }
.arabic-quran {
    font-family: 'Amiri', 'Traditional Arabic', serif;
    font-size: 1.35em;
    line-height: 2.1;
    direction: rtl;
    text-align: right;
    background-color: #f0fdf4;
    border-right: 4px solid #16a085;
    padding: 12px 18px;
    margin: 1.2em 0;
    border-radius: 4px;
    color: #064e3b;
}
.arabic-source {
    font-family: 'Amiri', 'Traditional Arabic', serif;
    font-size: 1.18em;
    line-height: 2.0;
    direction: rtl;
    text-align: right;
    background-color: #fdfbf7;
    border-right: 4px solid #d97706;
    padding: 15px 20px;
    margin: 1.5em 0;
    border-radius: 4px;
    color: #27272a;
}
.translation-box {
    background-color: #ffffff;
    border-left: 4px solid #2980b9;
    padding: 15px 20px;
    margin: 1.5em 0;
}
.lexicon-box {
    background-color: #f8fafc;
    border-left: 4px solid #8e44ad;
    padding: 15px;
    margin: 1.5em 0;
    border-radius: 4px;
    font-size: 0.92em;
}
.sibawayh-box {
    background-color: #fbfbfb;
    border-left: 4px solid #e67e22;
    padding: 12px 16px;
    margin: 1.2em 0;
    font-size: 0.90em;
}
.volume-divider {
    text-align: center;
    padding: 3em 1em;
    background: #f8f9fa;
    border: 2px solid #16a085;
    border-radius: 8px;
    margin: 2em 0;
}
.volume-badge {
    text-align: center;
    font-size: 0.85em;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #7f8c8d;
    margin-bottom: 0.5em;
}
"""

VOLUMES_METADATA = [
    {"vol": 1, "title_ar": "دلائل وجود واجب الوجود وتوحيده وتنزيهه", "title_en": "Volume 1: The Epistemology of Theology & Proofs of the Necessary Existent"},
    {"vol": 2, "title_ar": "الدلائل الدالة على التوحيد والتنزيه ونفي المكان والتحيز", "title_en": "Volume 2: Divine Unicity, Incorporeality & Non-Spatiality"},
    {"vol": 3, "title_ar": "الصفات الإيجابية (العلم والقدرة والإرادة والسمع والبصر والكلام)", "title_en": "Volume 3: The Positive Essential Attributes of Divine Perfection"},
    {"vol": 4, "title_ar": "مباحث الحدوث والقدم وخلق العالم", "title_en": "Volume 4: Primordial Eternity, Temporal Origination & Cosmogony"},
    {"vol": 5, "title_ar": "مباحث الزمان والمكان والخلاء والملاء", "title_en": "Volume 5: Time, Space, Motion, Void & Plenum"},
    {"vol": 6, "title_ar": "مباحث الهيولى والصورة والجوهر الفرد والأجسام", "title_en": "Volume 6: Matter, Form, Indivisible Monads & Physical Ontology"},
    {"vol": 7, "title_ar": "مباحث الأرواح العالية والسافلة والنفوس الإنسانية وتجردها", "title_en": "Volume 7: Celestial & Human Spirits, Psychology & Incorporeality"},
    {"vol": 8, "title_ar": "مباحث النبوات ومعجزات الرسل وحقائق الوحي", "title_en": "Volume 8: Prophethood, Miracles, Revelatory Epistemology & Refutations"},
    {"vol": 9, "title_ar": "مباحث المعاد والبعث والنشور ومراتب السعادات الروحية", "title_en": "Volume 9: Eschatology, Resurrection, Celestial Spheres & Spiritual Felicity"}
]


def build_omnibus():
    book = epub.EpubBook()
    book.set_identifier("al-matalib-al-aliyah-complete-omnibus-en")
    book.set_title("The Sublime Inquiries into Divine Science (Al-Maṭālib al-ʿAliyyah) — Complete 9 Volumes")
    book.set_language("en")
    book.add_author("Imam Fakhr al-Dīn al-Rāzī (544–606 AH / 1149–1210 CE)")

    book.add_metadata('DC', 'description', 'The definitive English translation of Imam Fakhr al-Din al-Razi\'s masterwork Al-Maṭālib al-ʿAliyyah min al-ʿIlm al-Ilāhī in one unified omnibus edition. Produced via the Two-Stage Lexicographically Guided Ayn Engine AI.')
    book.add_metadata('DC', 'publisher', 'Ayn Engine Classical Islamic Metaphysics Initiative')

    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=STYLE_CSS)
    book.add_item(nav_css)

    spine = ['nav']
    toc = []

    # Master Front Matter
    front_page = epub.EpubHtml(title="Master Front Matter", file_name="front_matter.xhtml", lang="en")
    front_page.content = """
    <div class="volume-badge">The Definitive Philosophical &amp; Theological Summa</div>
    <h1>Al-Maṭālib al-ʿAliyyah<br/><span style="font-size:0.65em; color:#7f8c8d;">(المطالب العالية من العلم الإلهي)</span></h1>
    <h2>The Sublime Inquiries into Divine Science</h2>
    <h3>Complete 9 Volumes in One Master Omnibus</h3>
    <hr/>
    <p><strong>Author:</strong> Imam Fakhr al-Dīn al-Rāzī (d. 606 AH / 1210 CE)</p>
    <p><strong>Translation Engine:</strong> Two-Stage Lexicographically Guided Ayn Engine AI (Lisān al-ʿArab, Kitāb al-ʿAyn &amp; Sībawayh)</p>
    <p><strong>Overview:</strong> <em>Al-Maṭālib al-ʿAliyyah</em> represents Imam al-Rāzī's crowning intellectual achievement, composed at the very apex of his career in Herat prior to his death in 606 AH. It is the most comprehensive synthesis of rational Kalām theology, Avicennian philosophical ontology, and spiritual metaphysics in Islamic history.</p>
    """
    front_page.add_item(nav_css)
    book.add_item(front_page)
    spine.append(front_page)
    toc.append(front_page)

    total_chapters_overall = 0

    for vol_meta in VOLUMES_METADATA:
        vol_num = vol_meta["vol"]
        vol_file = NEW_WORKS_DIR / f"matalib_vol_{vol_num:02d}_translated.json"
        
        if not vol_file.exists():
            continue

        with open(vol_file, "r", encoding="utf-8") as f:
            vdata = json.load(f)

        v_chapters = vdata.get("chapters", [])
        if not v_chapters:
            continue

        # Volume Divider Page
        vol_div = epub.EpubHtml(title=f"Volume {vol_num}: {vol_meta['title_en']}", file_name=f"vol_{vol_num:02d}_title.xhtml", lang="en")
        vol_div.content = f"""
        <div class="volume-divider">
            <div class="volume-badge">Part {vol_num} of 9</div>
            <h1>Volume {vol_num}</h1>
            <h2>{vol_meta['title_en']}</h2>
            <div class="arabic-source" style="text-align:center; font-size:1.3em;">{vol_meta['title_ar']}</div>
            <p style="text-align:center; margin-top:1.5em;"><strong>Chapters in this volume:</strong> {len(v_chapters)}</p>
        </div>
        """
        vol_div.add_item(nav_css)
        book.add_item(vol_div)
        spine.append(vol_div)

        vol_sub_toc = []

        for ch in v_chapters:
            total_chapters_overall += 1
            idx = ch.get("chapter_index", 1)
            title_en = ch.get("title_en", f"Chapter {idx}")
            title_ar = ch.get("title_ar", "")
            translation_text = ch.get("translation", "")
            lisan_text = ch.get("lisan_constellation", "")
            sibawayh_text = ch.get("sibawayh_notes", "")

            formatted_trans = re.sub(
                r'\{«(.*?)»\}',
                r'<div class="arabic-quran">\1</div>',
                translation_text
            )
            html_paras = "".join(f"<p>{p.strip()}</p>" for p in formatted_trans.split("\n\n") if p.strip())

            ch_page = epub.EpubHtml(title=title_en, file_name=f"v{vol_num:02d}_c{idx:03d}.xhtml", lang="en")
            ch_page.content = f"""
            <div class="volume-badge">Volume {vol_num} • Chapter {idx}</div>
            <h2>{title_en}</h2>
            <div class="arabic-source" style="font-size:1.05em; padding:8px 12px; margin-bottom:1em;">{title_ar}</div>
            
            {f'<div class="lexicon-box"><strong>🌌 Lisān al-ʿArab &amp; Kitāb al-ʿAyn Roots:</strong><br/>{lisan_text.replace(chr(10), "<br/>")}</div>' if lisan_text else ''}
            {f'<div class="sibawayh-box"><strong>📜 Sībawayh Syntactic Anchors:</strong><br/>{sibawayh_text.replace(chr(10), "<br/>")}</div>' if sibawayh_text else ''}
            
            <div class="translation-box">
                {html_paras}
            </div>
            """
            ch_page.add_item(nav_css)
            book.add_item(ch_page)
            spine.append(ch_page)
            vol_sub_toc.append(ch_page)

        toc.append((epub.Section(f"Volume {vol_num}: {vol_meta['title_en']}"), tuple(vol_sub_toc)))

    book.toc = tuple(toc)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = spine

    epub.write_epub(str(OUTPUT_EPUB), book)
    print(f"✓ Successfully built Complete Omnibus EPUB: {OUTPUT_EPUB} ({OUTPUT_EPUB.stat().st_size / 1024:.1f} KB)")
    print(f"✓ Total Chapters Included: {total_chapters_overall}")

    if PUBLIC_DEST.parent.exists():
        import shutil
        shutil.copy2(OUTPUT_EPUB, PUBLIC_DEST)
        print(f"✓ Mirrored to Phone Chat: {PUBLIC_DEST}")


if __name__ == "__main__":
    build_omnibus()
