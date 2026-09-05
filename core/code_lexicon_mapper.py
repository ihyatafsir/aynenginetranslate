#!/usr/bin/env python3
"""
code_lexicon_mapper.py

AynEngine AI Coding Edition: Epistemic Classical Lexicon Bridge
Maps modern software engineering concepts and programming invariants to the 5 Classical Arabic Lexicographical & Grammatical Pillars:
1. Al-Mufradāt fī Gharīb al-Qurʾān (al-Rāghib al-Iṣfahānī) -> Ontological Domain Modeling & Teleology
2. Asās al-Balāghah (al-Zamakhsharī) -> Idiomatic Eloquence & Abstraction Integrity (Ḥaqīqah vs Majāz)
3. Lisān al-ʿArab (Ibn Manẓūr) -> Exhaustive State-Space, Edge-Cases, & Error Taxonomy
4. Kitāb al-ʿAyn (al-Farāhīdī) -> Atomic Primitive Decomposition & State Combinatorics
5. Al-Kitāb (Sībawayh) -> Syntactic Governance (ʿĀmil/Maʿmūl), AST Hierarchy & Strict Typing
"""

import re
from typing import Dict, List, Any, Optional

# Software Engineering Dimension -> Classical Roots & Lexical Conceptual Anchors
CONCEPT_ROOT_TAXONOMY = {
    "concurrency": {
        "roots": ["جمع", "زمن", "سوق", "حجز"],
        "pillar_focus": "Kitāb al-ʿAyn & Sībawayh",
        "description": "Multi-agent coordination, event loops, mutexes, and non-blocking scheduling"
    },
    "immutability": {
        "roots": ["ثبت", "حفظ", "بقي", "صلب"],
        "pillar_focus": "Al-Mufradāt & Asās al-Balāghah",
        "description": "State permanence, pure functions, absence of side-effects, and persistent data structures"
    },
    "types": {
        "roots": ["ميز", "حدّ", "صنف", "حكم"],
        "pillar_focus": "Al-Kitāb (Sībawayh) & Al-Mufradāt",
        "description": "Algebraic data types, structural invariants, type guards, and compile-time correctness"
    },
    "error_handling": {
        "roots": ["درء", "عطب", "كشف", "رجع"],
        "pillar_focus": "Lisān al-ʿArab",
        "description": "Exhaustive edge-case matching, error taxonomy, backpressure, and fault-tolerance"
    },
    "abstraction": {
        "roots": ["جوز", "حقق", "لبس", "صفا"],
        "pillar_focus": "Asās al-Balāghah",
        "description": "Metaphor vs reality (Majāz vs Ḥaqīqah), zero leaky abstractions, and code minimalism"
    },
    "decomposition": {
        "roots": ["أصل", "فصل", "فرع", "بسط"],
        "pillar_focus": "Kitāb al-ʿAyn",
        "description": "Orthogonal primitive decomposition, single-responsibility, and modular cohesion"
    },
    "governance": {
        "roots": ["عمل", "حكم", "قود", "سلط"],
        "pillar_focus": "Al-Kitāb (Sībawayh)",
        "description": "Explicit caller-callee governance (ʿĀmil wa Maʿmūl), dependency inversion, and pipeline flow"
    },
    "teleology": {
        "roots": ["قصد", "غيا", "حقق", "وضع"],
        "pillar_focus": "Al-Mufradāt",
        "description": "Domain purpose (Ghāyah), self-evident naming, and semantic contracts"
    }
}

KEYWORD_TO_DIMENSIONS = {
    # Concurrency / Async
    "async": ["concurrency", "governance"],
    "await": ["concurrency", "governance"],
    "thread": ["concurrency"],
    "mutex": ["concurrency", "error_handling"],
    "lock": ["concurrency", "error_handling"],
    "channel": ["concurrency", "governance"],
    "queue": ["concurrency", "decomposition"],
    "worker": ["concurrency", "governance"],
    "pool": ["concurrency", "governance"],
    "stream": ["concurrency", "immutability"],
    "parallel": ["concurrency"],
    
    # Types / Contracts
    "type": ["types", "governance"],
    "class": ["types", "teleology"],
    "interface": ["types", "abstraction"],
    "struct": ["types", "teleology"],
    "enum": ["types", "decomposition"],
    "generic": ["types", "abstraction"],
    "contract": ["types", "teleology"],
    "invariant": ["types", "immutability"],
    "schema": ["types", "teleology"],
    
    # Immutability / State
    "immutable": ["immutability"],
    "const": ["immutability"],
    "pure": ["immutability", "teleology"],
    "state": ["immutability", "concurrency"],
    "cache": ["immutability", "concurrency"],
    "store": ["immutability", "teleology"],
    
    # Errors / Safety
    "error": ["error_handling"],
    "exception": ["error_handling"],
    "retry": ["error_handling", "governance"],
    "fallback": ["error_handling"],
    "timeout": ["error_handling", "concurrency"],
    "circuit": ["error_handling", "concurrency"],
    "catch": ["error_handling"],
    "panic": ["error_handling"],
    
    # Abstraction / Architecture
    "architecture": ["abstraction", "governance", "decomposition"],
    "pattern": ["abstraction", "decomposition"],
    "service": ["teleology", "governance"],
    "repository": ["abstraction", "teleology"],
    "controller": ["governance", "teleology"],
    "middleware": ["governance", "abstraction"],
    "factory": ["abstraction", "decomposition"],
    "refactor": ["abstraction", "decomposition", "governance"]
}

class AynCodeLexiconMapper:
    """
    Connects programming requests and source code to the 5 Classical Arabic Lexicons:
    1. Al-Mufradāt (al-Rāghib)
    2. Asās al-Balāghah (al-Zamakhsharī)
    3. Lisān al-ʿArab (Ibn Manẓūr)
    4. Kitāb al-ʿAyn (al-Farāhīdī)
    5. Al-Kitāb (Sībawayh)
    """

    def __init__(self, lisan_dict=None, ayn_dict=None, raghib_dict=None, zamakhshari_dict=None, sibawayh_rules=None):
        self.lisan_dict = lisan_dict or {}
        self.ayn_dict = ayn_dict or {}
        self.raghib_dict = raghib_dict or {}
        self.zamakhshari_dict = zamakhshari_dict or {}
        self.sibawayh_rules = sibawayh_rules or {}

    def extract_relevant_dimensions(self, text: str) -> List[str]:
        """Analyzes text/prompt/code and determines active software engineering dimensions."""
        tokens = re.findall(r'[a-zA-Z_]+', text.lower())
        dimension_counts: Dict[str, int] = {}
        
        for token in tokens:
            if token in KEYWORD_TO_DIMENSIONS:
                for dim in KEYWORD_TO_DIMENSIONS[token]:
                    dimension_counts[dim] = dimension_counts.get(dim, 0) + 1
                    
        # Always ensure core structural dimensions are active
        default_dims = ["teleology", "abstraction", "governance"]
        for d in default_dims:
            dimension_counts[d] = dimension_counts.get(d, 0) + 1
            
        sorted_dims = sorted(dimension_counts.items(), key=lambda x: x[1], reverse=True)
        return [d[0] for d in sorted_dims[:4]]

    def extract_relevant_roots(self, text: str) -> List[str]:
        """Extracts candidate classical roots corresponding to the programming context."""
        dims = self.extract_relevant_dimensions(text)
        roots = []
        for d in dims:
            if d in CONCEPT_ROOT_TAXONOMY:
                roots.extend(CONCEPT_ROOT_TAXONOMY[d]["roots"])
        # Deduplicate while preserving order
        seen = set()
        unique_roots = []
        for r in roots:
            if r not in seen:
                seen.add(r)
                unique_roots.append(r)
        return unique_roots[:6]

    def build_epistemic_coding_context(self, prompt: str, language: str = "python") -> str:
        """
        Builds the 5-Pillar Classical RAG context to ground code synthesis or review.
        """
        dims = self.extract_relevant_dimensions(prompt)
        roots = self.extract_relevant_roots(prompt)

        lines = [
            "🏛️ AYNENGINE AI: 5-PILLAR CLASSICAL EPISTEMIC CODING APPARATUS",
            f"Target Architecture / Language: {language.upper()}",
            f"Active Conceptual Dimensions: {', '.join(dims).title()}",
            ""
        ]

        # 1. Al-Mufradāt (al-Rāghib al-Iṣfahānī)
        lines.append("1️⃣ AL-MUFRADĀT (Al-Rāghib al-Iṣfahānī) — Teleology & Ontological Domain Modeling:")
        lines.append("   • Invariant: Every type, entity, and function must have an unambiguous Ghāyah (teleology).")
        lines.append("   • Rule: Eliminate amorphous, bloated types (no generic 'data', 'processor', or 'manager').")
        for r in roots[:2]:
            if r in self.raghib_dict:
                entry = self.raghib_dict[r].get("definition", "")[:180].replace('\n', ' ')
                lines.append(f"   • Root [{r}]: \"{entry}\"")
            else:
                lines.append(f"   • Classical Anchor [{r}]: Maintain ontological distinction between essential nature and accidental state.")

        # 2. Asās al-Balāghah (al-Zamakhsharī)
        lines.append("\n2️⃣ ASĀS AL-BALĀGHAH (Al-Zamakhsharī) — Rhetorical Eloquence & Abstraction Integrity (Ḥaqīqah vs Majāz):")
        lines.append("   • Invariant: Delineate literal runtime reality (CPU, IO, allocations) from software metaphors (ORMs, wrappers, promises).")
        lines.append("   • Rule: Zero leaky abstractions (Majāz Mukhil). Eliminate stuttering boilerplate; write idiomatic, high-impact code.")
        for r in roots[2:4]:
            if r in self.zamakhshari_dict:
                z = self.zamakhshari_dict[r]
                lit = z.get("literal_usage", "")[:120].replace('\n', ' ')
                maj = z.get("metaphorical_usage", "")[:120].replace('\n', ' ')
                lines.append(f"   • Root [{r}]: [Ḥaqīqah: {lit}] [Majāz: {maj}]")
            else:
                lines.append(f"   • Classical Anchor [{r}]: Avoid unwarranted abstraction; maximum communicative power with minimal syntax.")

        # 3. Lisān al-ʿArab (Ibn Manẓūr)
        lines.append("\n3️⃣ LISĀN AL-ʿARAB (Ibn Manẓūr) — Exhaustive State-Space, Edge-Cases & Error Taxonomy:")
        lines.append("   • Invariant: Exhaustive morphological coverage. Zero unhandled match cases, unhandled rejections, or silent failures.")
        lines.append("   • Rule: Model every state of the lifecycle: Initializing -> Active -> Degraded -> Closed -> Failed.")
        for r in roots[:2]:
            if r in self.lisan_dict:
                l_def = str(self.lisan_dict[r])[:160].replace('\n', ' ')
                lines.append(f"   • Root [{r}]: \"{l_def}\"")

        # 4. Kitāb al-ʿAyn (al-Farāhīdī)
        lines.append("\n4️⃣ KITĀB AL-ʿAYN (Al-Farāhīdī) — Atomic Primitive Decomposition & State Permutations:")
        lines.append("   • Invariant: Decompose complex logic into orthogonal, irreducible mathematical primitives.")
        lines.append("   • Rule: Combinatorial state safety — Make illegal states unrepresentable in the type system.")
        lines.append("   • Ensure foundational primitives are pure, stateless, and idempotent.")

        # 5. Al-Kitāb (Sībawayh)
        lines.append("\n5️⃣ AL-KITĀB (Sībawayh) — Syntactic Governance (ʿĀmil/Maʿmūl) & AST Integrity:")
        lines.append("   • Invariant: Strict caller-callee hierarchy. The Governor (ʿĀmil) explicitly controls the Governed (Maʿmūl).")
        lines.append("   • Rule: Zero circular dependencies. Strict static typing, pure data flow, and unambiguous function signatures.")
        if self.sibawayh_rules:
            first_k = list(self.sibawayh_rules.keys())[0]
            rule_sample = str(self.sibawayh_rules[first_k])[:150].replace('\n', ' ')
            lines.append(f"   • Syntactic Canon: \"{rule_sample}\"")

        return "\n".join(lines)
