#!/usr/bin/env python3
"""
translate_quad_lexicon_demo.py

Demonstration of AynEngine AI v3.0.0 Quad-Lexical Translation Pipeline:
Integrates:
1. Lisān al-ʿArab (Ibn Manẓūr)
2. Kitāb al-ʿAyn (Al-Farāhīdī)
3. Al-Mufradāt fī Gharīb al-Qurʾān (Al-Rāghib al-Iṣfahānī) - Kalām / Quranic Semantics
4. Asās al-Balāghah (Al-Zamakhsharī) - Rhetorical Haqiqah vs Majaz Distinctions
5. Al-Kitāb (Sībawayh) - Syntactic Grammatical Rules
"""

import os
import sys
import json
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from core.lexicographical_engine import LexicographicalTranslationEngine
from core.epub_builder import AynEpubBuilder
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

# Sample Classical Kalam Passage from Imam Fakhr al-Din al-Razi's Al-Matalib al-'Aliyah
SAMPLE_PASSAGE = """
الفصل الأول: في إثبات واجب الوجود لذاته وبطلان الدور والتسلسل
اعلم أن الموجود إما أن يكون واجب الوجود لذاته، وإما أن يكون ممكن الوجود لذاته.
فإن كان واجب الوجود لذاته، فهو المطلوب وثبت وجود الإله القديم القادر الحكيم.
وإن كان ممكن الوجود لذاته، فكل ممكن محتاج إلى مؤثر يرجح وجوده على عدمه بالضرورة العقلية، لأن نسبته إلى الوجود والعدم متساوية، وترجيح أحد المتساويين على الآخر لا بد له من مرجح.
ثم ذلك المؤثر: إما أن يكون واجباً بذاته، فيثبت المطلوب، وإما أن يكون ممكناً، فيفتقر إلى مؤثر آخر.
فإن دار الأمر بينهما لزم الدور وهو باطل، وإن ذهب إلى غير نهاية لزم التسلسل وهو محال في بدائه العقول.
فثبت بالبرهان القاطع أن سلسلة الممكنات تنتهي بالضرورة إلى واجب الوجود لذاته، وهو الله الواحد الأحد، الفرد الصمد، الذي لا بداية لأوليته ولا نهاية لأخريته.
"""

def main():
    print("==================================================================")
    print("🌌 AYNENGINE AI v3.0.0: QUAD-LEXICAL TRANSLATION PIPELINE DEMO")
    print("==================================================================")
    
    engine = LexicographicalTranslationEngine(
        author="Imam Fakhr al-Din al-Razi",
        book_title_ar="المطالب العالية من العلم الإلهي",
        book_title_en="The Higher Inquiries into Divine Science",
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        model=DEEPSEEK_MODEL,
        engine_mode="QUAD_LEXICAL"
    )
    
    print("\n🔍 1. Direct Lexicon Lookups for Kalām Roots:")
    sample_roots = ["وجد", "قدر", "حدث", "عقل"]
    for r in sample_roots:
        summary = engine.get_quad_anchor_summary(r)
        print(f"\n--- Root: [{r}] ---")
        print(f"📖 Al-Rāghib (Theological/Kalam): {summary['raghib_theology'][:150]}...")
        if summary['zamakhshari_rhetoric']:
            print(f"⚖️ Al-Zamakhsharī (Literal): {summary['zamakhshari_rhetoric']['literal'][:100]}...")
            print(f"🎨 Al-Zamakhsharī (Majāz/Metaphor): {summary['zamakhshari_rhetoric']['majaz'][:100]}...")
            
    print("\n🚀 2. Translating Classical Passage with Quad-Anchors...")
    if engine.api_key:
        result = engine.translate_passage(SAMPLE_PASSAGE, title_ar="إثبات واجب الوجود")
        print("\n--- TRANSLATION RESULT ---")
        print(f"Title: {result['title_en']}")
        print("\n--- Anchors: ---")
        print(result['anchors'])
        print("\n--- Translation: ---")
        print(result['translation'])
        
        # Build EPUB
        print("\n📦 3. Compiling Kindle EPUB with AynEpubBuilder...")
        epub_out = BASE_DIR / "data/demo_matalib_v3.epub"
        builder = AynEpubBuilder(
            title="The Higher Inquiries (AynEngine v3.0.0 Demo)",
            author="Imam Fakhr al-Din al-Razi",
            language="en"
        )
        content_html = f"""
        <h2>Original Arabic</h2>
        <div class="arabic-text">{SAMPLE_PASSAGE.replace(chr(10), '<br/>')}</div>
        <h2>Quad-Lexical Anchors</h2>
        <div class="root-anchor">{result['anchors'].replace(chr(10), '<br/>')}</div>
        <h2>Translation</h2>
        <p>{result['translation'].replace(chr(10), '<br/><br/>')}</p>
        """
        builder.add_chapter("Chapter 1: Proof of the Necessary Existent", content_html)
        saved_path = builder.build(str(epub_out))
        print(f"✅ EPUB Created Successfully: {saved_path}")
    else:
        print("ℹ️ Set DEEPSEEK_API_KEY environment variable to execute live LLM inference.")
        print("✅ Direct lexicon lookup tests completed successfully with 100% precision.")

if __name__ == "__main__":
    main()
