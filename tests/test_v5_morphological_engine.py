#!/usr/bin/env python3
"""
test_v5_morphological_engine.py

Unit and regression tests for AynEngine AI v5.0.0 Sovereign Morphological Edition.
Tests classical Arabic awzan reduction, theological root recovery, and Quad-Anchor RAG lookups.
"""

import os
import sys
import json
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from core.lexicographical_engine import LexicographicalTranslationEngine


class TestV5MorphologicalEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = LexicographicalTranslationEngine(
            author="Al-Ghazali",
            book_title_ar="إحياء علوم الدين",
            book_title_en="Revival of the Religious Sciences"
        )

    def test_faeel_faeelah_reduction(self):
        """Verify that adjectives and nouns of measure fa'il / fa'ilah un-affix to 3-letter radicals."""
        cases = {
            "اللطيفة": "لطف",
            "لطيفة": "لطف",
            "لطيف": "لطف",
            "عظيم": "عظم",
            "عظيمة": "عظم",
            "شريف": "شرف",
            "شريفة": "شرف",
            "قديم": "قدم",
            "كريم": "كرم",
            "حقيقة": "حقق",
            "طبيعة": "طبع",
            "فضيلة": "فضل",
            "شريعة": "شرع"
        }
        for word, expected_root in cases.items():
            roots = self.engine.extract_word_root_candidates(word)
            self.assertIn(expected_root, roots, f"Failed to extract '{expected_root}' from '{word}' (got: {roots})")

    def test_faail_reduction(self):
        """Verify that active participles (fa'il / fa'ilah) un-affix to 3-letter radicals."""
        cases = {
            "عارف": "عرف",
            "العارف": "عرف",
            "عالم": "علم",
            "حاكم": "حكم",
            "قادر": "قدر",
            "صانع": "صنع",
            "مدرك": "درك"
        }
        for word, expected_root in cases.items():
            roots = self.engine.extract_word_root_candidates(word)
            self.assertIn(expected_root, roots, f"Failed to extract '{expected_root}' from '{word}' (got: {roots})")

    def test_tafeel_and_iftiaal_reduction(self):
        """Verify verbal nouns (taf'il, ifti'al, infi'al, afa'il) un-affix correctly."""
        cases = {
            "تخصيص": "خصص",
            "تحويل": "حول",
            "تصريف": "صرف",
            "اشتراك": "شرك",
            "اشتراكها": "شرك",
            "انقلاب": "قلب",
            "أغاليط": "غلط"
        }
        for word, expected_root in cases.items():
            roots = self.engine.extract_word_root_candidates(word)
            self.assertIn(expected_root, roots, f"Failed to extract '{expected_root}' from '{word}' (got: {roots})")

    def test_broken_plurals_and_pronouns(self):
        """Verify broken plurals (fu'ul) and words with possessive pronouns un-affix correctly."""
        cases = {
            "حدود": "حدد",
            "حدودها": "حدد",
            "قلوب": "قلب",
            "قلوبهم": "قلب",
            "علوم": "علم",
            "أعراض": "عرض"
        }
        for word, expected_root in cases.items():
            roots = self.engine.extract_word_root_candidates(word)
            self.assertIn(expected_root, roots, f"Failed to extract '{expected_root}' from '{word}' (got: {roots})")

    def test_section_341_latif_salience(self):
        """Verify that Section 341 excerpt ranks root 'latf' and 'qalb' with top salience."""
        section_341_excerpt = """
        اعلم أن هذه الأسماء الأربعة تستعمل في هذه الأبواب ويقل في فحول العلماء
        من يحيط بهذه الأسامي واختلاف معانيها وحدودها ومسمياتها وأكثر الأغاليط
        منشؤها الجهل بمعنى هذه الأسامي واشتراكها بين مسميات مختلفة ونحن نشرح في
        معنى هذه الأسامي ما يتعلق بغرضنا.
        اللفظ الأول لفظ القلب: والمعنى الثاني هو لطيفة ربانية روحانية لها بهذا القلب
        الجسماني تعلق وتلك اللطيفة هي حقيقة الإنسان وهو المدرك العالم العارف من الإنسان.
        واللفظ الثاني لفظ الروح: وهو جسم لطيف منبعه تجويف القلب الجسماني.
        والثاني: اللطيفة العالمة المدركة من الإنسان.
        """
        top_roots = self.engine.extract_candidate_roots(section_341_excerpt, max_candidates=8)
        self.assertIn("لطف", top_roots, f"Expected 'لطف' in top candidate roots, got: {top_roots}")
        self.assertIn("قلب", top_roots, f"Expected 'قلب' in top candidate roots, got: {top_roots}")

    def test_full_section_341_theological_roots(self):
        """Verify that the full Arabic text of Section 341 extracts qalb, nafs, latf, and ruh in top 10."""
        trans_file = BASE_DIR / "data" / "translations" / "ghazali" / "ihya_ulum_al_din_translated.json"
        if trans_file.exists():
            with open(trans_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            ch = data["chapters"][341]
            ar_text = ch["arabic_text"]
            top_roots = self.engine.extract_candidate_roots(ar_text, max_candidates=10)
            self.assertIn("قلب", top_roots)
            self.assertIn("نفس", top_roots)
            self.assertIn("لطف", top_roots)
            self.assertIn("روح", top_roots)

    def test_rag_context_includes_raghib_latif(self):
        """Verify that when Section 341 excerpt is processed, Al-Raghib's scholia on 'latf' is injected."""
        section_341_excerpt = """
        اللفظ الأول لفظ القلب: والمعنى الثاني هو لطيفة ربانية روحانية لها بهذا القلب
        الجسماني تعلق وتلك اللطيفة هي حقيقة الإنسان وهو المدرك العالم العارف من الإنسان.
        واللفظ الثاني لفظ الروح: وهو جسم لطيف منبعه تجويف القلب الجسماني.
        """
        rag_context = self.engine.build_active_rag_context(section_341_excerpt)
        self.assertIn("[Root: لطف]", rag_context)
        self.assertIn("Al-Raghib", rag_context)
        self.assertIn("اللطائف", rag_context)


if __name__ == "__main__":
    unittest.main()
