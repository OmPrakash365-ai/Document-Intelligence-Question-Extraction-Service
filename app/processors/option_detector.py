"""Option detection engine for multiple choice and multi-select questions."""

import re
from typing import List, Tuple
from app.processors.interfaces import DetectedOption
from app.utils.text_utils import normalize_option_key

# Patterns matching standard options:
# 1. "A. Option", "a. Option"
# 2. "(A) Option", "(a) Option"
# 3. "A) Option", "a) Option"
# 4. "[A] Option", "[a] Option"
# 5. "1. Option", "(1) Option", "1) Option"
OPTION_PATTERNS = [
    # (A) / (a) / (1)
    re.compile(r"(?:^|\s+)\(([A-Za-z0-9])\)\s+([^\(\)]+?)(?=(?:\s+\([A-Za-z0-9]\)|\Z))", re.MULTILINE),
    # A. / a. / 1. (at line start or preceded by multiple spaces)
    re.compile(r"(?:^|\n|\s{2,})([A-Za-z0-9])\.\s+([^\n\r]+?)(?=(?:\s{2,}[A-Za-z0-9]\.|\n[A-Za-z0-9]\.|\Z))", re.MULTILINE),
    # A) / a) / 1)
    re.compile(r"(?:^|\n|\s{2,})([A-Za-z0-9])\)\s+([^\n\r]+?)(?=(?:\s{2,}[A-Za-z0-9]\)|\n[A-Za-z0-9]\)|\Z))", re.MULTILINE),
    # [A] / [a]
    re.compile(r"(?:^|\s+)\[([A-Za-z0-9])\]\s+([^\[\]]+?)(?=(?:\s+\[[A-Za-z0-9]\]|\Z))", re.MULTILINE),
]


class OptionDetector:
    """Detects and parses options from question text."""

    def detect_options(self, text: str) -> Tuple[str, List[DetectedOption]]:
        """
        Parses options from text.
        Returns:
            Tuple of (remaining_question_text, list_of_detected_options)
        """
        if not text:
            return "", []

        best_options: List[DetectedOption] = []
        best_split_idx = -1

        # Check line-by-line first for structured layouts
        lines = text.splitlines()
        detected_line_options: List[DetectedOption] = []
        question_lines: List[str] = []
        in_options_mode = False

        line_option_regex = re.compile(
            r"^(?:\(?([A-Da-d1-4])[\.\)\]]|\b([A-Da-d1-4])[\.\)])\s+(.*)$"
        )

        for line in lines:
            line_str = line.strip()
            match = line_option_regex.match(line_str)
            if match:
                key = match.group(1) or match.group(2)
                opt_text = match.group(3).strip()
                norm_key = normalize_option_key(key)
                detected_line_options.append(
                    DetectedOption(key=norm_key, text=opt_text, confidence=0.95)
                )
                in_options_mode = True
            else:
                if in_options_mode and detected_line_options and not re.match(r"^\d+[\.\)]", line_str):
                    # Multi-line option continuation
                    detected_line_options[-1].text += f" {line_str}"
                else:
                    question_lines.append(line)

        if len(detected_line_options) >= 2:
            remaining_q = "\n".join(question_lines).strip()
            return remaining_q, detected_line_options

        # If line-by-line didn't find enough options, check horizontal or inline patterns
        # e.g., "A. Dog  B. Cat  C. Bird  D. Fish"
        for pattern in OPTION_PATTERNS:
            matches = list(pattern.finditer(text))
            if len(matches) >= 2:
                # Ensure keys look progressive (e.g. A, B, C or 1, 2, 3)
                keys = [normalize_option_key(m.group(1)) for m in matches]
                if self._are_keys_progressive(keys):
                    first_match_start = matches[0].start()
                    remaining_q = text[:first_match_start].strip()
                    options = [
                        DetectedOption(
                            key=normalize_option_key(m.group(1)),
                            text=m.group(2).strip(),
                            confidence=0.90,
                        )
                        for m in matches
                    ]
                    return remaining_q, options

        # No clear options detected
        return text.strip(), []

    @staticmethod
    def _are_keys_progressive(keys: List[str]) -> bool:
        """Validates that option keys follow expected sequences like A, B, C or 1, 2, 3."""
        if not keys:
            return False

        # Check alphabetical sequence
        alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        numeric = "123456789"

        if all(k in alpha for k in keys):
            indices = [alpha.index(k) for k in keys]
            # Must be ascending
            return indices == sorted(indices)

        if all(k in numeric for k in keys):
            indices = [int(k) for k in keys]
            return indices == sorted(indices)

        return False
