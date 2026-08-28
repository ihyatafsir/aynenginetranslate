#!/usr/bin/env python3
"""
epub_builder.py

Reusable Kindle and Standard EPUB3 Dual-Edition Builder for AynEngine AI.
Supports two publishing paradigms:
1. Pure English Scholarly Edition (_pure_en.epub): 100% Verbatim translation with authorial voice.
2. Bilingual Apparatus Edition (_bilingual_lexical_en.epub): Arabic text + Quad-Lexical apparatus + English translation.
"""

import os
import re
from pathlib import Path
from ebooklib import epub

class AynEpubBuilder:
    def __init__(self, title, author, identifier=None, language='en', edition_type="PURE_SCHOLARLY"):
        self.title = title
        self.author = author
        self.language = language
        self.edition_type = edition_type
        self.book = epub.EpubBook()
        
        safe_id = re.sub(r'[^a-zA-Z0-9]', '-', title.lower())
        self.book.set_identifier(identifier or f"ayn-engine-{safe_id}-{edition_type.lower()}")
        self.book.set_title(f"{title} ({'Pure English Edition' if edition_type == 'PURE_SCHOLARLY' else 'Bilingual Lexical Apparatus Edition'})")
        self.book.set_language(language)
        self.book.add_author(author)
        self.chapters = []
        self.css = self._default_css()

    def _default_css(self):
        css_content = '''
        @namespace epub "http://www.idpf.org/2007/ops";
        body {
            font-family: Georgia, 'Times New Roman', serif;
            line-height: 1.65;
            margin: 1.2em;
            color: #1a1a1a;
            background-color: #fff;
        }
        h1 {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 1.6em;
            color: #0b3c5d;
            text-align: center;
            margin-top: 1.5em;
            margin-bottom: 0.8em;
            border-bottom: 2px solid #0b3c5d;
            padding-bottom: 0.3em;
        }
        h2 {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 1.25em;
            color: #2c3e50;
            margin-top: 1.2em;
            margin-bottom: 0.5em;
        }
        p {
            margin-bottom: 1em;
            text-indent: 1.2em;
        }
        .arabic-block {
            font-family: 'Amiri', 'Scheherazade New', 'Traditional Arabic', serif;
            direction: rtl;
            text-align: right;
            font-size: 1.3em;
            line-height: 2.1;
            color: #1b365d;
            background-color: #f8fafc;
            border-right: 4px solid #1b365d;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .apparatus-box {
            background-color: #f4f6f8;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #0b3c5d;
            padding: 12px 18px;
            margin: 20px 0;
            font-size: 0.92em;
            border-radius: 4px;
            line-height: 1.6;
        }
        .apparatus-title {
            font-weight: bold;
            color: #0b3c5d;
            margin-bottom: 6px;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }
        .quran-quote {
            font-family: 'Amiri', serif;
            color: #1b5e20;
            font-weight: bold;
            font-size: 1.15em;
        }
        .translation-block {
            margin-top: 1.5em;
            line-height: 1.7;
        }
        .author-voice {
            font-style: normal;
        }
        '''
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=css_content)
        self.book.add_item(nav_css)
        return nav_css

    def add_pure_scholarly_chapter(self, title, translation_text, file_name=None):
        """Adds a pure 1st-person English translation chapter (Kindle-optimized)."""
        idx = len(self.chapters) + 1
        fn = file_name or f"chap_{idx:02d}.xhtml"
        chapter = epub.EpubHtml(title=title, file_name=fn, lang=self.language)
        
        paras = translation_text.strip().split('\n\n')
        html_paras = ''.join([f"<p>{p.strip().replace(chr(10), '<br/>')}</p>" for p in paras if p.strip()])
        
        chapter.content = f"""<html>
<head><title>{title}</title></head>
<body>
    <h1>{title}</h1>
    <div class="translation-block author-voice">
        {html_paras}
    </div>
</body>
</html>"""
        chapter.add_item(self.css)
        self.book.add_item(chapter)
        self.chapters.append(chapter)
        return chapter

    def add_bilingual_apparatus_chapter(self, title, arabic_text, quad_anchors, translation_text, file_name=None):
        """Adds a bilingual chapter with Arabic source, Quad-Lexical anchors, and English translation."""
        idx = len(self.chapters) + 1
        fn = file_name or f"chap_{idx:02d}.xhtml"
        chapter = epub.EpubHtml(title=title, file_name=fn, lang=self.language)
        
        ar_html = arabic_text.strip().replace('\n', '<br/>')
        anchors_html = quad_anchors.strip().replace('\n', '<br/>')
        
        paras = translation_text.strip().split('\n\n')
        html_paras = ''.join([f"<p>{p.strip().replace(chr(10), '<br/>')}</p>" for p in paras if p.strip()])
        
        chapter.content = f"""<html>
<head><title>{title}</title></head>
<body>
    <h1>{title}</h1>
    
    <h2>📜 Classical Arabic Text (النص العربي الأصلي)</h2>
    <div class="arabic-block">
        {ar_html}
    </div>
    
    <div class="apparatus-box">
        <div class="apparatus-title">🏛️ Quad-Lexical & Syntactic Apparatus (AynEngine AI v3.0.0)</div>
        <div>{anchors_html}</div>
    </div>
    
    <h2>🌐 English Scholarly Translation (Verbatim Authorial Voice)</h2>
    <div class="translation-block author-voice">
        {html_paras}
    </div>
</body>
</html>"""
        chapter.add_item(self.css)
        self.book.add_item(chapter)
        self.chapters.append(chapter)
        return chapter

    def build(self, output_path):
        self.book.toc = tuple(self.chapters)
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())
        self.book.spine = ['nav'] + self.chapters
        
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        epub.write_epub(str(out), self.book, {"epub3_pages": False})
        return str(out)
