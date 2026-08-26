# 🌌 AynEngine AI: Sovereign Lexicographically Guided 1M Translation Engine Framework

A production-grade, high-fidelity scholarly translation pipeline and multi-volume publishing engine designed for classical Arabic philosophical, theological, and scientific literature.

---

## 🏛️ Architectural Pillars

### 1. Two-Stage Lexicographically Guided Translation
Unlike standard machine translation models that output unconstrained interpretations or hallucinations, **AynEngine AI** operates on a strict **two-stage anchor paradigm**:
- **Stage 1 (Anchor Extraction)**: The engine extracts 7 unique Arabic governing roots from *Lisān al-ʿArab* and *Kitāb al-ʿAyn* (via Al-Farāhīdī's permutation method) and 2 governing syntactic rules from *Sībawayh's Al-Kitāb* **FIRST**.
- **Stage 2 (Guided Scholarly Rendering)**: The extracted classical definitions and grammatical rules act as semantic anchors, strictly constraining the model as it renders the text into English.

### 2. Pure Scholarly Standard (Zero AI Commentary Guarantee)
- 100% Verbatim fidelity to original scholastic authorial voice (1st-person authenticity).
- Absolute elimination of extraneous AI introductions, summaries, moralizing disclaimers, or ungrounded commentary.
- Exact Arabic script preservation `{«...»}` for all Quranic verses and Hadith citations.

### 3. Al-Khalīl ibn Aḥmad al-Farāhīdī Root Permutation System
- Dynamically tracks used roots across thousands of pages to eliminate redundant root citations.
- Integrates complete digital lexicons of *Lisān al-ʿArab* (Ibn Manẓūr) and *Kitāb al-ʿAyn* (Al-Farāhīdī).

### 4. Sībawayh Syntactic Anchor Pipeline
- Evaluates the 2.58 MB master text of *Al-Kitāb* to resolve complex classical Arabic syntactic structures, conditionals, and scholastic kalām disputes.

### 5. Multi-Volume Omnibus & Kindle EPUB Builder
- Automated sub-chunking with zero truncation at 6,000 characters.
- Built-in `AynEpubBuilder` producing production-ready, Kindle-optimized EPUB3 files with Amiri RTL Arabic fonts and semantic CSS.
- Multi-volume omnibus compiler with unified table of contents.

---

## 📁 Directory Layout

```
translation_engine_framework/
├── README.md                                          # Framework documentation & specifications
├── config.py                                          # Environment, LLM endpoints & API configurations
├── core/
│   ├── lexicographical_engine.py                      # Core lexicographical translation engine class
│   └── epub_builder.py                                # Reusable Kindle & standard EPUB3 builder
├── data/
│   ├── lisanclean.json                                # Extracted Lisān al-ʿArab root corpus
│   ├── grammars/
│   │   └── sibawayh_kitab/                           # Sībawayh's Al-Kitāb (الكتاب لسيبويه)
│   │       ├── sibawayh_kitab.txt                     # Complete 2.58 MB master text
│   │       └── sibawayh_rules.json                    # Parsed syntactic rule index
│   └── lexicons/
│       └── kitab_al_ayn/                             # Kitāb al-ʿAyn by Al-Khalīl ibn Aḥmad
│           ├── kitab_al_ayn_dictionary.json
│           ├── 01_djvu.txt
│           ├── 02_djvu.txt
│           ├── 03_djvu.txt
│           └── 04_djvu.txt
└── examples/
    ├── translate_matalib_all_volumes_ayn_engine_demo.py # Automated multi-volume pipeline (Vols 2-9)
    ├── translate_matalib_vol_01_v2_pure_ayn_engine_demo.py # Pure scholarly edition pipeline
    ├── build_matalib_omnibus_epub_demo.py             # 9-Volume master omnibus EPUB compiler
    ├── translate_ismat_v4_pro_7roots_demo.py          # 7-Root constellation translation example
    ├── build_ismat_v4_pro_epub_demo.py                # Single-volume EPUB builder example
    ├── translate_asrar_tanzil_demo.py                 # Single-volume working manuscript example
    └── build_asrar_epub_demo.py                       # Working EPUB builder example
```

---

## 🚀 Quick Usage Example

```python
from core.lexicographical_engine import LexicographicalTranslationEngine
from core.epub_builder import AynEpubBuilder

# 1. Initialize Engine
engine = LexicographicalTranslationEngine(
    author="Imam Fakhr al-Din al-Razi",
    book_title_ar="المطالب العالية من العلم الإلهي",
    book_title_en="The Higher Inquiries into Divine Science",
    max_chunk_chars=6000
)

# 2. Process Manuscript with 7-Root + Sibawayh Anchors
engine.process_file("data/texts/sample_manuscript.txt", "data/output/translated.json")

# 3. Build Kindle-Ready EPUB
builder = AynEpubBuilder(
    title="The Higher Inquiries into Divine Science",
    author="Imam Fakhr al-Din al-Razi",
    language="en"
)
builder.add_chapter("Chapter 1: Divine Unity", "<p>Translation content...</p>")
builder.build("data/kindle/matalib.epub")
```

---

## 🏷️ Version History
* **v2.0.0**: Pure Scholarly Edition, Multi-Volume Omnibus Compilation, Kitāb al-ʿAyn & Sībawayh full integration, Kindle EPUB3 automation.
* **v1.0.0**: Initial Lexicographically Guided 1M Translation Engine with Lisān al-ʿArab root extraction.
