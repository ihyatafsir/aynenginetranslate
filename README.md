# 🌌 AynEngine AI (v3.0.0): Sovereign Quad-Lexical Classical Translation & Dual-Edition Publishing Framework

A state-of-the-art, high-fidelity scholarly translation pipeline and multi-volume publishing engine designed for classical Arabic philosophical, theological (Kalām), and scientific literature.

---

## 🏛️ The Quad-Lexical Semantic Constellation (*Al-Manẓūma al-Rubāʿiyya*)

AynEngine AI grounds classical Arabic translation into four foundational classical lexicons and the premier grammatical text of the Arabic language:

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

## 📚 Complete Imam al-Ghazali Corpus (26 Masterworks)

AynEngine AI contains automated scrapers and ingestion pipelines for the complete digitized library of **Imam Abū Ḥāmid al-Ghazālī (d. 505 AH)** under `data/texts/ghazali/`:

* *Iḥyāʾ ʿUlūm al-Dīn* (4 Volumes, 4.3M chars)
* *Al-Munqidh min al-Ḍalāl* (Deliverance from Error)
* *Tahāfut al-Falāsifah* (The Incoherence of the Philosophers)
* *Mishkāt al-Anwār* (The Niche of Lights)
* *Al-Iqtiṣād fī al-Iʿtiqād* (Moderation in Belief)
* *Bidāyat al-Hidāyah* (The Beginning of Guidance)
* *Al-Mustaṣfā min ʿIlm al-Uṣūl* (Legal Theory)
* *Maqāṣid al-Falāsifah* & *Mīzān al-ʿAmal*
* *Al-Maqṣad al-Asnā* & *Jawāhir al-Qurʾān*
* *Miʿyār al-ʿIlm*, *Miḥakk al-Naẓar*, *Maʿārij al-Quds*, *Faḍāʾiḥ al-Bāṭiniyya*, *Al-Mankhūl*, *Shifāʾ al-Ghalīl*, and all collected epistles.

---

## 📖 Dual-Edition Publishing Architecture

For every classical work, AynEngine AI compiles **Two Distinct Publishing Editions**:

### 1. Edition 1: Pure English Scholarly Edition (`_pure_en.epub`)
- **Reading Experience**: Uninterrupted, elegant Kindle-ready English reading.
- **Authorial Voice**: 100% Verbatim 1st-person authorial translation ("I say...", "Know that...").
- **Zero AI Commentary**: Zero unsolicited modern disclaimers or commentary.
- **Scriptural Preservation**: `{«...»}` verbatim Arabic retention for Quranic verses and Hadith.

### 2. Edition 2: Bilingual Scholarly Apparatus Edition (`_bilingual_lexical_en.epub`)
- **Comparative Layout**: Complete Classical Arabic text with Amiri RTL typography.
- **Quad-Lexical Apparatus**: Structured box detailing Al-Rāghib Kalām definitions, Al-Zamakhsharī Ḥaqīqah/Majāz distinctions, Lisān roots, and Sībawayh syntax rules.
- **English Translation**: Complete scholarly translation following each Arabic section.

---

## 🚀 Running the Ghazali Dual-Edition Pipeline

```bash
# 1. Scrape & Ingest All 26 Ghazali Masterworks
python3 scripts/scrape_all_ghazali_corpus.py

# 2. Run Dual-Edition Pipeline on Specific Book (e.g. Al-Munqidh min al-Dalal)
python3 scripts/run_ghazali_dual_edition_pipeline.py --slug al_munqidh_min_al_dalal

# 3. Run Pipeline on Entire Ghazali Corpus
python3 scripts/run_ghazali_dual_edition_pipeline.py --all
```

---

## 📁 Directory Structure

```
translation_engine_framework/
├── README.md                                          # Framework documentation & specifications
├── config.py                                          # Configuration & OpenITI corpus registry
├── core/
│   ├── lexicographical_engine.py                      # Reusable Quad-Lexical Translation Engine class
│   └── epub_builder.py                                # Reusable Kindle & EPUB3 Dual-Edition builder
├── data/
│   ├── texts/ghazali/                                # 26 Ingested & Cleaned Ghazali Arabic texts + catalog.json
│   ├── translations/ghazali/                         # Checkpoint JSON archives
│   ├── epubs/ghazali/                                # Output Pure & Bilingual EPUB3 editions
│   ├── lisanclean.json                                # Lisān al-ʿArab root corpus
│   ├── grammars/sibawayh_kitab/                      # Sībawayh's Al-Kitāb & rule index
│   └── lexicons/
│       ├── kitab_al_ayn/                             # Kitāb al-ʿAyn database
│       ├── raghib_mufradat/                          # Al-Mufradāt raw text & JSON dictionary (1,623 roots)
│       └── zamakhshari_asas/                         # Asās al-Balāghah raw text & JSON dictionary (3,721 roots)
├── scripts/
│   ├── build_classical_lexicons.py                   # Lexicon scraper & indexing pipeline
│   ├── scrape_all_ghazali_corpus.py                  # Ghazali 26-book corpus scraper
│   └── run_ghazali_dual_edition_pipeline.py          # Automated Ghazali dual-edition batch pipeline
└── examples/
    ├── translate_ghazali_dual_edition_demo.py         # Ghazali dual-edition demonstration
    ├── translate_quad_lexicon_demo.py                 # Quad-Lexicon Kalām translation demo
    └── build_matalib_omnibus_epub_demo.py             # Multi-volume omnibus compiler
```
