#!/usr/bin/env python3
"""
test_coding_engine.py

Comprehensive test suite for AynEngine AI Coding Edition:
- AynCodeLexiconMapper (5-Pillar RAG context generation & root extraction)
- AynCodingEngine syntax validator & placeholder detector
- AST parsing & bracket balancing
- Integration test for synthesis and audit
"""

import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from core.code_lexicon_mapper import AynCodeLexiconMapper
from core.coding_engine import AynCodingEngine

class TestAynCodeLexiconMapper(unittest.TestCase):
    def setUp(self):
        self.mapper = AynCodeLexiconMapper()

    def test_dimension_extraction(self):
        prompt = "Create an async worker pool with mutex locks, queue dispatch, and backpressure error handling."
        dims = self.mapper.extract_relevant_dimensions(prompt)
        self.assertIn("concurrency", dims)
        self.assertIn("error_handling", dims)

    def test_root_extraction(self):
        prompt = "Build an immutable state store with pure functional updates and type invariants."
        roots = self.mapper.extract_relevant_roots(prompt)
        self.assertTrue(len(roots) > 0)
        # Should contain roots related to immutability/types
        self.assertTrue(any(r in roots for r in ["ثبت", "حفظ", "ميز", "حدّ"]))

    def test_epistemic_context_generation(self):
        prompt = "Implement a distributed rate limiter in Rust using token bucket algorithm."
        ctx = self.mapper.build_epistemic_coding_context(prompt, "rust")
        self.assertIn("AL-MUFRADĀT", ctx)
        self.assertIn("ASĀS AL-BALĀGHAH", ctx)
        self.assertIn("LISĀN AL-ʿARAB", ctx)
        self.assertIn("KITĀB AL-ʿAYN", ctx)
        self.assertIn("AL-KITĀB", ctx)

class TestAynCodingEngineValidation(unittest.TestCase):
    def setUp(self):
        self.engine = AynCodingEngine()

    def test_syntax_validator_valid_python(self):
        valid_py = """
def calculate_ratio(num: float, den: float) -> float:
    if den == 0:
        raise ValueError("Denominator cannot be zero")
    return num / den
"""
        res = self.engine._validate_syntax(valid_py, "python")
        self.assertTrue(res["valid"])
        self.assertIsNone(res["error"])

    def test_syntax_validator_invalid_python(self):
        invalid_py = """
def broken_fn(:
    return 42
"""
        res = self.engine._validate_syntax(invalid_py, "python")
        self.assertFalse(res["valid"])
        self.assertIsNotNone(res["error"])

    def test_bracket_balancer_valid(self):
        valid_rust = "fn main() { let x = vec![1, 2, (3 + 4)]; println!(\"{}\", x.len()); }"
        res = self.engine._validate_syntax(valid_rust, "rust")
        self.assertTrue(res["valid"])

    def test_bracket_balancer_invalid(self):
        invalid_rust = "fn main() { let x = vec![1, 2, (3 + 4]; }"
        res = self.engine._validate_syntax(invalid_rust, "rust")
        self.assertFalse(res["valid"])
        self.assertIn("Mismatched", res["error"])

    def test_zero_loss_placeholder_detection(self):
        lazy_code = """
class DataHandler:
    def process(self):
        # TODO: implement data processing here
        pass
"""
        violations = self.engine._check_zero_loss_placeholders(lazy_code)
        self.assertTrue(len(violations) > 0)

    def test_extract_code_block(self):
        markdown_text = """Here is the implementation:
```python
def pure_function(x: int) -> int:
    return x * 2
```
Hope this helps!"""
        code = self.engine._extract_code_block(markdown_text, "python")
        self.assertIn("def pure_function", code)
        self.assertNotIn("```", code)
        self.assertNotIn("Here is the implementation", code)

if __name__ == "__main__":
    unittest.main()
