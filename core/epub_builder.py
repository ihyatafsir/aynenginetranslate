#!/usr/bin/env python3
"""
epub_builder.py

Reusable Kindle and Standard EPUB3 Builder for AynEngine AI.
Generates Kindle-optimized EPUBs with Amiri RTL Arabic fonts, semantic CSS styling,
bilingual indices, and automatic chapter structure.
"""

import os
import re
from pathlib import Path
from ebooklib import epub

class AynEpubBuilder:
    def __init__(self, title, author, identifier=None, language='en'):
        self.title = title
        self.author = author
        self.language = language
        self.book = epub.EpubBook()
        self.book.set_identifier(identifier or f"ayn-engine-{re.sub(r'[^a-zA-Z0-9]', '-', title.lower())}")
        self.book.set_title(title)
        self.book.set_language(language)
        self.book.add_author(author)
        self.chapters = []
        self.css = self._default_css()

    def _default_css(self):
        css_content = '''
        @namespace epub "http://www.idpf.org/2007/ops";
        body {
            font-family: Georgia, serif;
            line-height: 1.6;
            margin: 1em;
            color: #1a1a1a;
        }
        h1, h2, h3 {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #111;
            text-align: center;
        }
        .arabic-text {
            font-family: 'Amiri', 'Traditional Arabic', serif;
            direction: rtl;
            text-align: right;
            font-size: 1.25em;
            line-height: 2.0;
            color: #0b3c5d;
        }
        .root-anchor {
            background-color: #f4f6f8;
            border-left: 4px solid #0b3c5d;
            padding: 10px 15px;
            margin: 15px 0;
            font-size: 0.95em;
        }
        .quran-quote {
            font-family: 'Amiri', serif;
            color: #1b5e20;
            text-align: center;
            direction: rtl;
            font-size: 1.3em;
            margin: 1em 0;
        }
        .footnote {
            font-size: 0.85em;
            color: #555;
            border-top: 1px solid #ddd;
            margin-top: 2em;
            padding-top: 0.5em;
        }
        '''
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=css_content)
        self.book.add_item(nav_css)
        return nav_css

    def add_chapter(self, title, html_content, file_name=None):
        idx = len(self.chapters) + 1
        fn = file_name or f"chap_{idx:02d}.xhtml"
        chapter = epub.EpubHtml(title=title, file_name=fn, lang=self.language)
        chapter.content = f"<html><head><title>{title}</title></head><body><h1>{title}</h1>{html_content}</body></html>"
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
        epub.write_epub(str(out), self.book, {})
        return str(out)
