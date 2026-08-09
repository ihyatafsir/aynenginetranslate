# 🌌 Two-Stage Lexicographically Guided 1M Translation Engine Framework

A production-grade, high-fidelity scholarly translation pipeline designed for classical Arabic philosophical, theological, and scientific literature.

---

## 🏛️ Architectural Pillars

### 1. Two-Stage Lexicographically Guided Translation
Unlike standard translation models that output footnotes after translation, this engine operates in a **two-stage paradigm**:
- **Stage 1 (Anchor Stage)**: The engine extracts a unique Arabic root from *Lisān al-ʿArab* (via Al-Farāhīdī's root permutation method) and a unique syntactic rule from *Sībawayh's Al-Kitāb* **FIRST**.
- **Stage 2 (Guided Rendering Stage)**: The extracted classical definitions and syntactic structures act as strict semantic anchors, constraining and guiding the model as it renders the text into English.

### 2. Al-Khalīl ibn Aḥmad al-Farāhīdī Root Permutation System
- Dynamically tracks used roots across thousands of pages to ensure **zero root repetition**.
- Employs Al-Farāhīdī's combinatorial lexicon model to map out rare technical terminology.

### 3. Bayt al-Ḥikmah Sense-for-Sense Standard
- Based on Ḥunayn ibn Isḥāq's methodology from the Baghdad Translation Movement.
- Renders 1st-person authentic voice of classical authors while preserving strict philosophical precision.

### 4. Zero Truncation Sub-Chunking Algorithm
- Automatically partitions large manuscripts into balanced sub-chapters capped at 6,000 characters.
- Ensures all responses complete without API text cutoffs.

### 5. Kindle-Ready EPUB Production
- Generates Kindle-optimized EPUBs with Amiri RTL Arabic fonts, semantic CSS styling, and bilingual indices.

---

## 📁 Directory Layout

```
translation_engine_framework/
├── README.md                          # Framework documentation
├── config.py                          # Environment & API configurations
├── core/
│   ├── lexicographical_engine.py      # Reusable translation engine class
│   └── epub_builder.py                # Reusable Kindle EPUB builder
├── data/
│   ├── lisanclean.json                # Extracted Lisān al-ʿArab root corpus
│   ├── grammars/
│   │   └── sibawayh_kitab/           # Sībawayh's Al-Kitāb (الكتاب لسيبويه)
│   │       ├── sibawayh_kitab.txt     # Complete 2.58 MB master text
│   │       └── sibawayh_rules.json    # Parsed syntactic rule index
│   └── lexicons/
│       └── kitab_al_ayn/             # Al-Khalīl ibn Aḥmad al-Farāhīdī's Kitāb al-ʿAyn
│           ├── kitab_al_ayn_dictionary.json
│           ├── 01_djvu.txt
│           ├── 02_djvu.txt
│           ├── 03_djvu.txt
│           └── 04_djvu.txt
└── examples/
    ├── translate_asrar_tanzil_demo.py # Complete working manuscript example
    └── build_asrar_epub_demo.py       # Working EPUB builder example
```

---

## 🚀 Quick Usage Example

```python
from core.lexicographical_engine import LexicographicalTranslationEngine

engine = LexicographicalTranslationEngine(
    author="Imam Fakhr al-Din al-Razi",
    book_title_ar="أسرار التنزيل",
    book_title_en="Secrets of Revelation",
    max_chunk_chars=6000
)

# Run full translation
engine.process_file("data/texts/sample_manuscript.txt", "data/output/translated.json")
```

---

*Engine Framework Created: August 2026 for General Reusability across Classical Translation Projects.*
