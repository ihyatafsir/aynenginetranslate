# 🌌 AynEngine AI (v3.0.0): Sovereign Quad-Lexical & Syntactic Classical Translation Framework

A state-of-the-art, high-fidelity scholarly translation pipeline and multi-volume publishing engine designed for classical Arabic philosophical, theological (Kalām), and scientific literature.

---

## 🏛️ The Quad-Lexical Semantic Constellation (*Al-Manẓūma al-Rubāʿiyya*)

AynEngine AI v3.0.0 moves beyond generic AI translation by enforcing a **strict two-stage grounding architecture** anchored in four foundational classical lexicons and the premier grammatical text of the Arabic language:

```
                          ┌────────────────────────────────────────────────────────┐
                          │                CLASSICAL INPUT PASSAGE                 │
                          └──────────────────────────┬─────────────────────────────┘
                                                     │
                                                     ▼
    ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
    │                                STAGE 1: SEMANTIC & SYNTACTIC ANCHORING                          │
    ├────────────────────────────────┬────────────────────────────────┬───────────────────────────────┤
    │  📖 Lisān al-ʿArab (Ibn Manẓūr)│  🏛️ Kitāb al-ʿAyn (Al-Farāhīdī) │  ⚖️ Al-Kitāb (Sībawayh)       │
    │  Universal classical roots     │  Archaic phonetic permutations │  Syntactic sentence structure │
    ├────────────────────────────────┼────────────────────────────────┴───────────────────────────────┤
    │  🕊️ Al-Mufradāt (Al-Rāghib)    │  🎨 Asās al-Balāghah (Al-Zamakhsharī)                          │
    │  Theological & Kalām semantics │  Literal (Ḥaqīqah) vs Metaphorical (Majāz) rhetorical nuance   │
    └────────────────────────────────┴────────────────────────────────────────────────────────────────┘
                                                     │
                                                     ▼
    ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
    │                                STAGE 2: PURE SCHOLARLY TRANSLATION                              │
    │  • 100% Verbatim 1st-Person Authorial Voice ('I say...', 'Know that...')                        │
    │  • Zero AI Commentary Guarantee (no extraneous moralizing or unsolicited modern opinions)       │
    │  • Verbatim Arabic Script in {«...»} for Quranic & Hadith Citations                             │
    │  • Transliterated Technical Terminology in Parentheses (e.g., 'necessary existence (wujūb)')    │
    └────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                     │
                                                     ▼
                          ┌────────────────────────────────────────────────────────┐
                          │             KINDLE-OPTIMIZED EPUB3 / JSON              │
                          └────────────────────────────────────────────────────────┘
```

---

## 📚 Integrated Classical Corpus

1. **Al-Rāghib al-Iṣfahānī (الراغب الأصفهاني - d. 502 AH)**: *Al-Mufradāt fī Gharīb al-Qurʾān* (المفردات في غريب القرآن)
   - Indexed database: `1,623` classical roots mapping theological, metaphysical, and Quranic terminology.
2. **Al-Zamakhsharī (الزمخشري جار الله - d. 538 AH)**: *Asās al-Balāghah* (أساس البلاغة)
   - Indexed database: `3,721` classical roots with explicit separation between literal (*ḥaqīqah*) and metaphorical (*majāz*) rhetorical usages.
3. **Ibn Manẓūr (ابن منظور - d. 711 AH)**: *Lisān al-ʿArab* (لسان العرب)
   - Exhaustive root definitions and morphological forms.
4. **Al-Khalīl ibn Aḥmad al-Farāhīdī (الخليل بن أحمد الفراهيدي - d. 175 AH)**: *Kitāb al-ʿAyn* (كتاب العين)
   - The first dictionary in the Arabic language; combinatorial phonetic permutation engine.
5. **Sībawayh (سيبويه - d. 180 AH)**: *Al-Kitāb* (الكتاب لسيبويه)
   - 2.58 MB master grammatical corpus with parsed syntactic rule index.

---

## 📁 Directory Structure

```
translation_engine_framework/
├── README.md                                          # Comprehensive framework documentation
├── config.py                                          # Configuration & OpenITI corpus registry
├── core/
│   ├── lexicographical_engine.py                      # Reusable Quad-Lexical Translation Engine class
│   └── epub_builder.py                                # Reusable Kindle & EPUB3 publishing builder
├── data/
│   ├── lisanclean.json                                # Lisān al-ʿArab root corpus
│   ├── grammars/
│   │   └── sibawayh_kitab/                           # Sībawayh's Al-Kitāb & rule index
│   └── lexicons/
│       ├── kitab_al_ayn/                             # Kitāb al-ʿAyn database
│       ├── raghib_mufradat/                          # Al-Mufradāt raw text & JSON dictionary
│       └── zamakhshari_asas/                         # Asās al-Balāghah raw text & JSON dictionary
├── scripts/
│   └── build_classical_lexicons.py                   # Automated scraper & indexing pipeline
└── examples/
    ├── translate_quad_lexicon_demo.py                 # Quad-Lexicon Kalām translation demo
    ├── translate_matalib_all_volumes_ayn_engine_demo.py # Multi-volume automated pipeline (Vols 2-9)
    ├── translate_matalib_vol_01_v2_pure_ayn_engine_demo.py # Pure scholarly edition demo
    ├── build_matalib_omnibus_epub_demo.py             # Multi-volume master omnibus EPUB compiler
    ├── translate_ismat_v4_pro_7roots_demo.py          # 7-Root constellation translation example
    └── build_asrar_epub_demo.py                       # Kindle EPUB builder demo
```

---

## 🚀 Quick Usage Example

```python
from core.lexicographical_engine import LexicographicalTranslationEngine
from core.epub_builder import AynEpubBuilder

# 1. Initialize AynEngine v3.0.0
engine = LexicographicalTranslationEngine(
    author="Imam Fakhr al-Din al-Razi",
    book_title_ar="المطالب العالية من العلم الإلهي",
    book_title_en="The Higher Inquiries into Divine Science",
    engine_mode="QUAD_LEXICAL"
)

# 2. Query Lexicon Constellation Directly
kalam_anchor = engine.get_quad_anchor_summary("قدر")
print(kalam_anchor["raghib_theology"])        # Al-Raghib's theological definition
print(kalam_anchor["zamakhshari_rhetoric"])   # Al-Zamakhshari's literal vs majaz

# 3. Translate with Quad-Anchors
result = engine.translate_passage(
    passage_text="اعلم أن الموجود إما أن يكون واجب الوجود لذاته...",
    title_ar="إثبات واجب الوجود"
)

# 4. Build Kindle EPUB
builder = AynEpubBuilder(title="The Higher Inquiries", author="Imam Fakhr al-Din al-Razi")
builder.add_chapter("Chapter 1: The Necessary Existent", f"<p>{result['translation']}</p>")
builder.build("output/matalib_v3.epub")
```

---

## 🏷️ Version History
* **v3.0.0** *(August 2026)*: **The Quad-Lexical Suite** — Full ingestion and integration of **Al-Raghib al-Isfahani's *Al-Mufradāt*** (1,623 roots for theological/Quranic Kalām vocabulary) and **Al-Zamakhshari's *Asās al-Balāghah*** (3,721 roots for literal vs *majāz* rhetoric).
* **v2.0.0** *(August 2026)*: Pure Scholarly Edition, Multi-Volume Omnibus Compilation, Kitāb al-ʿAyn & Sībawayh full integration, Kindle EPUB3 builder.
* **v1.0.0**: Initial Lexicographically Guided 1M Translation Engine with Lisān al-ʿArab root extraction.
