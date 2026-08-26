# 🌌 AynEngine AI (v3.2.0): Sovereign Quad-Lexical Classical Translation & Dual-Edition Publishing Framework

A state-of-the-art, high-fidelity scholarly translation pipeline and multi-volume publishing engine designed for classical Arabic philosophical, theological (Kalām), legal (Fiqh/Uṣūl), and Hadith literature.

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
   - Master grammatical corpus with parsed syntactic rule index.

---

## 📚 Complete Classical Ingested Corpora (48 Masterworks)

### 1. Imam Abū Ḥāmid al-Ghazālī (d. 505 AH) — 26 Masterworks
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

### 2. Imam Abū Zakariyyā Yaḥyā ibn Sharaf al-Nawawī (d. 676 AH) — 22 Masterworks
* *Al-Arbaʿūn al-Nawawiyyah* (The 40 Hadith)
* *Riyāḍ al-Ṣāliḥīn* (Gardens of the Righteous)
* *Al-Tibyān fī Ādāb Ḥamalat al-Qurʾān* (Etiquette with the Quran)
* *Kitāb al-Adhkār* (The Book of Remembrances)
* *Minhāj al-Ṭālibīn* (The Path of the Seekers)
* *Sharḥ Ṣaḥīḥ Muslim* (The Commentary on Sahih Muslim)
* *Al-Majmūʿ Sharḥ al-Muhadhdhab* (Comparative Jurisprudence)
* *Rawḍat al-Ṭālibīn* (The Meadow of the Seekers)
* *Bustān al-ʿĀrifīn* (Garden of the Gnostics)
* *Tahdhīb al-Asmāʾ wa-l-Lughāt*, *Al-Taqrīb wa-l-Taysīr*, *Al-Īḍāḥ fī Manāsik al-Ḥajj*, *Ādāb al-Fatwā*, *Daqāʾiq al-Minhāj*, *Khulāṣat al-Aḥkām*, *Irshād Ṭullāb al-Ḥaqāʾiq*, *Taḥrīr Alfāẓ al-Tanbīh*, and *Fatāwā al-Nawawī*.

---

## 📖 Dual-Edition Publishing Architecture

For every classical work, AynEngine AI compiles **Two Distinct Publishing Editions**:

1. **Edition 1: Pure English Scholarly Edition (`_pure_en.epub`)**:
   - 100% Verbatim 1st-person authorial translation (*"I say...", "Know that..."*).
   - Zero AI commentary.
   - Scriptural preservation: `{«...»}` verbatim Arabic retention for Quran and Hadith.

2. **Edition 2: Bilingual Scholarly Apparatus Edition (`_bilingual_lexical_en.epub`)**:
   - Complete Classical Arabic source text with Amiri RTL typography.
   - **Quad-Lexical Apparatus Box**: Extracted root definitions from Al-Rāghib (Kalām), Al-Zamakhsharī (Ḥaqīqah vs. Majāz), Lisān al-ʿArab, and Sībawayh syntax.
   - English scholarly translation following each Arabic section.

---

## 🚀 Running the Dual-Edition Pipeline

```bash
# 1. Scrape & Ingest Complete Corpora
python3 scripts/scrape_all_ghazali_corpus.py
python3 scripts/scrape_all_nawawi_corpus.py

# 2. Run Unified Dual-Edition Pipeline
python3 scripts/run_classical_library_dual_edition_pipeline.py --author ghazali
python3 scripts/run_classical_library_dual_edition_pipeline.py --author nawawi
python3 scripts/run_classical_library_dual_edition_pipeline.py --author all

# 3. Sync to Google Drive
rclone copy data/epubs/ gdrive:aynengine_ai_classical_library/
```
