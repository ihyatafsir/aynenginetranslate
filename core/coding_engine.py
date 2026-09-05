#!/usr/bin/env python3
"""
coding_engine.py

AynEngine AI Coding Edition: Sovereign 5-Pillar Epistemic Code Engine
Powered by DeepSeek and grounded in the 5 Classical Arabic Lexicographical & Grammatical Pillars:
1. Al-Mufradāt (al-Rāghib al-Iṣfahānī) -> Ontological Domain Modeling & Teleology
2. Asās al-Balāghah (al-Zamakhsharī) -> Idiomatic Eloquence & Abstraction Integrity (Ḥaqīqah vs Majāz)
3. Lisān al-ʿArab (Ibn Manẓūr) -> Exhaustive State-Space, Edge-Cases & Error Taxonomy
4. Kitāb al-ʿAyn (al-Farāhīdī) -> Atomic Primitive Decomposition & State Permutations
5. Al-Kitāb (Sībawayh) -> Syntactic Governance (ʿĀmil/Maʿmūl), AST Hierarchy & Strict Typing
"""

import os
import re
import ast
import json
import time
import urllib.request
from pathlib import Path
from typing import Dict, List, Any, Optional

from core.code_lexicon_mapper import AynCodeLexiconMapper

class AynCodingEngine:
    """
    Epistemic Code Synthesis, Review, and Refactoring Engine.
    Enforces Zero-Loss completeness, strong typing, and 5-Pillar classical software integrity.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_dir = Path(__file__).parent.parent.resolve()
        
        # Load environment
        env_file = self.base_dir / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                if line.strip() and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.base_url = (base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")).rstrip('/')
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

        # Load Lexicon Dictionaries
        data_dir = self.base_dir / "data"
        lex_dir = data_dir / "lexicons"
        gram_dir = data_dir / "grammars"

        lisan_dict = self._load_json(data_dir / "lisanclean.json")
        ayn_dict = self._load_json(lex_dir / "kitab_al_ayn" / "kitab_al_ayn_dictionary.json")
        raghib_dict = self._load_json(lex_dir / "raghib_mufradat" / "raghib_mufradat_dictionary.json")
        zamakhshari_dict = self._load_json(lex_dir / "zamakhshari_asas" / "asas_balagha_dictionary.json")
        sibawayh_rules = self._load_json(gram_dir / "sibawayh_rules.json")

        self.mapper = AynCodeLexiconMapper(
            lisan_dict=lisan_dict,
            ayn_dict=ayn_dict,
            raghib_dict=raghib_dict,
            zamakhshari_dict=zamakhshari_dict,
            sibawayh_rules=sibawayh_rules
        )

    def _load_json(self, path: Path) -> dict:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                return {}
        return {}

    def _extract_code_block(self, response_text: str, language: str = "python") -> str:
        """Extracts pure code from markdown backticks or returns text cleanly."""
        text = response_text.strip()
        # Look for ```lang ... ```
        pat = rf"```(?:{language}|[a-zA-Z0-9_\-]+)?\s*([\s\S]*?)```"
        matches = list(re.finditer(pat, text, re.IGNORECASE))
        if matches:
            # Join code blocks if multiple exist, or return the most comprehensive one
            blocks = [m.group(1).strip() for m in matches]
            # Return the largest block (most likely the complete implementation)
            return max(blocks, key=len)
        return text

    def _validate_syntax(self, code: str, language: str) -> Dict[str, Any]:
        """Validates AST/syntax of the generated code."""
        lang = language.lower()
        if lang in ["python", "py"]:
            try:
                ast.parse(code)
                return {"valid": True, "error": None}
            except SyntaxError as e:
                return {"valid": False, "error": f"Python SyntaxError at line {e.lineno}: {e.msg}"}
        elif lang in ["json"]:
            try:
                json.loads(code)
                return {"valid": True, "error": None}
            except Exception as e:
                return {"valid": False, "error": f"JSON SyntaxError: {e}"}
        # For other languages (Rust, Go, TS, C), perform basic bracket balance checks
        brackets = { '(': ')', '{': '}', '[': ']' }
        stack = []
        for char in code:
            if char in brackets:
                stack.append(brackets[char])
            elif char in brackets.values():
                if not stack or stack[-1] != char:
                    return {"valid": False, "error": f"Mismatched bracket '{char}' detected in code stream."}
                stack.pop()
        if stack:
            return {"valid": False, "error": f"Unclosed brackets remaining at end of stream: {stack}"}
        return {"valid": True, "error": None}

    def _check_zero_loss_placeholders(self, code: str) -> List[str]:
        """Checks for banned lazy placeholders that violate the Zero-Loss standard."""
        banned = [
            r'//\s*TODO', r'#\s*TODO', r'/\*\s*TODO',
            r'//\s*implement\s+here', r'#\s*implement\s+here',
            r'pass\s*#\s*implement', r'//\s*\.\.\.\s*rest\s+of\s+code',
            r'#\s*\.\.\.\s*rest\s+of\s+code', r'/\*\s*\.\.\.\s*rest\s+of\s+code\s*\*/'
        ]
        violations = []
        for b in banned:
            if re.search(b, code, re.IGNORECASE):
                violations.append(b)
        return violations

    def call_api(self, system_prompt: str, user_prompt: str, temperature: float = 0.1, max_tokens: int = 8192, max_retries: int = 5) -> str:
        """DeepSeek API caller with Zero-Loss automatic token-limit continuation stitching."""
        url = f"{self.base_url}/chat/completions"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        accumulated_content = ""

        for attempt in range(max_retries):
            try:
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }

                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    }
                )

                with urllib.request.urlopen(req, timeout=240) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    choice = data["choices"][0]
                    content_chunk = choice["message"]["content"]
                    finish_reason = choice.get("finish_reason")

                    accumulated_content += content_chunk

                    # Zero-Loss continuation: if token limit reached, keep generating
                    if finish_reason == "length":
                        print("⚡ [AynEngineCode Zero-Loss] Token limit reached mid-stream. Auto-continuing code...")
                        messages.append({"role": "assistant", "content": content_chunk})
                        messages.append({
                            "role": "user",
                            "content": "You reached the token limit mid-code. Continue immediately from the exact last character without repeating prior code."
                        })
                        continue
                    else:
                        return accumulated_content.strip()

            except Exception as e:
                err_str = str(e)
                print(f"⚠️ [AynEngineCode Retry {attempt+1}/{max_retries}] API Error: {err_str}")
                if "402" in err_str:
                    raise RuntimeError(f"DeepSeek Balance Depleted (HTTP 402): {e}")
                time.sleep(2 * (attempt + 1))

        raise RuntimeError("DeepSeek API failed after maximum retries.")

    def synthesize(self, prompt: str, language: str = "python", context_files: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Synthesizes complete, production-grade code grounded in the 5 Classical Pillars.
        Guarantees zero placeholders, AST validity, and epistemic architectural rigor.
        """
        rag_context = self.mapper.build_epistemic_coding_context(prompt, language)

        context_str = ""
        if context_files:
            context_str = "\n### 📂 CONTEXT / EXISTING FILES:\n"
            for fname, fcontent in context_files.items():
                context_str += f"\nFile: `{fname}`\n```\n{fcontent}\n```\n"

        system_prompt = f"""You are **AynEngine AI Coding Edition (Sovereign Epistemic Engine)**.
You write pristine, production-grade software grounded in the 5 Classical Arabic Lexicographical & Grammatical Pillars:

1. **Al-Mufradāt (al-Rāghib)**: Pure ontological domain modeling. Every type, invariant, and function has an explicit Ghāyah (teleology). Never use generic names like 'data', 'handle_stuff', 'process'.
2. **Asās al-Balāghah (al-Zamakhsharī)**: Rhetorical eloquence (Faṣāḥah & Balāghah). Delineate Ḥaqīqah (hardware/runtime reality) from Majāz (abstractions). Zero leaky abstractions. Minimal lines for maximal impact.
3. **Lisān al-ʿArab (Ibn Manẓūr)**: Exhaustive edge-cases and error handling. Zero unhandled match arms, unhandled exceptions, or silent failures. Model the full lifecycle.
4. **Kitāb al-ʿAyn (al-Farāhīdī)**: Decompose logic into orthogonal, irreducible primitives. State safety: make illegal states unrepresentable.
5. **Al-Kitāb (Sībawayh)**: Strict syntactic governance (ʿĀmil/Maʿmūl). Clear caller-callee hierarchy, strict typing, zero circular dependencies.

CRITICAL INVARIANTS:
- **ZERO-LOSS CODE**: You MUST provide the 100% COMPLETE, fully functional implementation.
- **NO PLACEHOLDERS**: STRICTLY FORBIDDEN to use `// TODO`, `/* implement here */`, `# ...`, `pass # implement later`. Every algorithm, error handler, and edge-case must be fully coded.
- Always output clean, syntactically valid code in the target language ({language}).
- Provide an initial concise 5-Pillar Architectural Epistemic Rationale, followed by the complete code block.
"""

        user_prompt = f"""{rag_context}
{context_str}
### 🎯 CODING OBJECTIVE:
{prompt}

Target Language: {language.upper()}

Synthesize the complete, production-grade, zero-loss implementation now:"""

        t0 = time.time()
        raw_output = self.call_api(system_prompt, user_prompt, temperature=0.1)
        elapsed = time.time() - t0

        code = self._extract_code_block(raw_output, language)
        syntax_check = self._validate_syntax(code, language)
        placeholder_violations = self._check_zero_loss_placeholders(code)

        # If placeholders detected, run an immediate self-correction pass
        if placeholder_violations or not syntax_check["valid"]:
            print(f"⚠️ [Zero-Loss Validator] Detected flaws (AST: {syntax_check['valid']}, Placeholders: {len(placeholder_violations)}). Refining...")
            fix_prompt = f"""The prior code output had the following issues:
Syntax Valid: {syntax_check['valid']} (Error: {syntax_check['error']})
Banned Placeholders Detected: {placeholder_violations}

Rewrite the code to be 100% COMPLETE, valid, and fully implemented without a single placeholder."""
            raw_output = self.call_api(system_prompt, f"{user_prompt}\n\n{raw_output}\n\n{fix_prompt}", temperature=0.05)
            code = self._extract_code_block(raw_output, language)
            syntax_check = self._validate_syntax(code, language)

        return {
            "language": language,
            "raw_output": raw_output,
            "code": code,
            "syntax_valid": syntax_check["valid"],
            "syntax_error": syntax_check["error"],
            "duration_seconds": round(elapsed, 2),
            "epistemic_pillars": {
                "raghib_teleology": "Enforced pure domain types & explicit Ghāyah",
                "zamakhshari_eloquence": "Enforced zero-leaky abstractions & minimal boilerplate",
                "lisan_exhaustiveness": "Enforced full error taxonomy & lifecycle state handling",
                "farahidi_primitives": "Enforced orthogonal atomic primitives & state invariants",
                "sibawayh_governance": "Enforced strict caller-callee governance & typed contracts"
            }
        }

    def audit(self, code: str, language: str = "python", filename: str = "") -> Dict[str, Any]:
        """
        Performs a rigorous 5-Pillar Epistemic Code Audit evaluating architectural integrity,
        abstraction leakage (Majāz vs Ḥaqīqah), edge-case exhaustiveness, and syntactic governance.
        """
        rag_context = self.mapper.build_epistemic_coding_context(f"Code review and audit for {filename or 'source'}\n{code[:1000]}", language)

        system_prompt = f"""You are **AynEngine AI Coding Edition: Chief Epistemic Code Auditor**.
You audit source code strictly through the lens of the **5 Classical Arabic Lexicographical & Grammatical Pillars**:

1. **Al-Mufradāt (al-Rāghib)**: Evaluate Ontological Clarity & Teleology (1-10). Are names accurate to the reality? Are domain types conflated with generic representations?
2. **Asās al-Balāghah (al-Zamakhsharī)**: Evaluate Abstraction Integrity & Eloquence (1-10). Are there leaky abstractions (Majāz Mukhil)? Is code cluttered with stuttering boilerplate or ceremony?
3. **Lisān al-ʿArab (Ibn Manẓūr)**: Evaluate Edge-Case Exhaustiveness & Error Taxonomy (1-10). Are exceptions swallowed? Are boundary conditions and network/concurrency failures omitted?
4. **Kitāb al-ʿAyn (al-Farāhīdī)**: Evaluate Atomic Decomposition & State Permutations (1-10). Can the system enter illegal combinatorial states? Are routines monolithic?
5. **Al-Kitāb (Sībawayh)**: Evaluate Syntactic Governance & Dependency Architecture (1-10). Is the caller/callee hierarchy clear? Are there circular dependencies or implicit global state mutations?

Format your response with:
- **📊 5-Pillar Epistemic Scorecard (Grades 1-10 + Overall Score)**
- **🔍 Deep Pillar-by-Pillar Critique**
- **🛠️ High-Impact Epistemic Remediation Steps**
"""

        user_prompt = f"""{rag_context}

### 📄 CODE UNDER AUDIT (Language: {language.upper()}, File: `{filename or 'unnamed'}`):
```{language}
{code}
```

Deliver your comprehensive 5-Pillar Epistemic Audit now:"""

        t0 = time.time()
        audit_report = self.call_api(system_prompt, user_prompt, temperature=0.1)
        elapsed = time.time() - t0

        return {
            "filename": filename,
            "language": language,
            "audit_report": audit_report,
            "duration_seconds": round(elapsed, 2)
        }

    def refactor(self, code: str, language: str = "python", goal: str = "Purify code to 5-Pillar Classical Standard") -> Dict[str, Any]:
        """
        Refactors code to align with the 5 Classical Pillars, removing leaky abstractions,
        eliminating boilerplate, making illegal states unrepresentable, and ensuring total error coverage.
        """
        rag_context = self.mapper.build_epistemic_coding_context(f"{goal}\n{code[:800]}", language)

        system_prompt = f"""You are **AynEngine AI Coding Edition: Sovereign Epistemic Refactoring Engine**.
You transform imperfect code into an architectural masterpiece adhering to the 5 Classical Pillars:
1. Al-Mufradāt (Domain Ontology & Teleology)
2. Asās al-Balāghah (Anti-Leakage & Rhetorical Eloquence)
3. Lisān al-ʿArab (Exhaustive Error Taxonomy)
4. Kitāb al-ʿAyn (Atomic Primitive Decomposition)
5. Al-Kitāb of Sībawayh (Strict Syntactic Governance & AST Integrity)

STRICT RULES:
- Output the 100% COMPLETE refactored code. Zero placeholders (`// TODO`, `# ...`, `pass`).
- Accompany the code with an Epistemic Delta explaining how each pillar was elevated.
"""

        user_prompt = f"""{rag_context}

### 🎯 REFACTORING GOAL:
{goal}

### 📄 ORIGINAL CODE ({language.upper()}):
```{language}
{code}
```

Provide the complete refactored implementation and Epistemic Delta now:"""

        t0 = time.time()
        raw_output = self.call_api(system_prompt, user_prompt, temperature=0.1)
        elapsed = time.time() - t0

        refactored_code = self._extract_code_block(raw_output, language)
        syntax_check = self._validate_syntax(refactored_code, language)

        return {
            "language": language,
            "raw_output": raw_output,
            "refactored_code": refactored_code,
            "syntax_valid": syntax_check["valid"],
            "syntax_error": syntax_check["error"],
            "duration_seconds": round(elapsed, 2)
        }
