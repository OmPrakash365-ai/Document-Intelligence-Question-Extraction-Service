"""Text processing, cleaning, and normalization utilities."""

import re
import unicodedata


def clean_text(text: str) -> str:
    """Cleans raw extracted text: normalizes unicode, handles line breaks, removes strange characters."""
    if not text:
        return ""

    # Normalize unicode to NFKC
    normalized = unicodedata.normalize("NFKC", text)

    # Normalize quotes and dashes
    normalized = re.sub(r'[\u2018\u2019]', "'", normalized)
    normalized = re.sub(r'[\u201c\u201d]', '"', normalized)
    normalized = re.sub(r'[\u2013\u2014]', '-', normalized)

    # Replace consecutive spaces and tabs with a single space
    lines = []
    for line in normalized.splitlines():
        cleaned_line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(cleaned_line)

    # Join lines preserving logical paragraphs
    return "\n".join(lines).strip()


def normalize_question_number(raw_number: str) -> str:
    """Normalizes raw question number strings (e.g. 'Q1.', 'Q.1', '1)', '(1)', 'Question 1') to standard '1'."""
    if not raw_number:
        return ""

    # Extract digits or alphanumeric identifier
    match = re.search(r"(\d+(?:[a-zA-Z])?)", raw_number)
    if match:
        return match.group(1).upper()

    return raw_number.strip().rstrip(".:)- ").upper()


def normalize_option_key(raw_key: str) -> str:
    """Normalizes raw option keys (e.g. '(a)', 'A.', '1)', '(1)') to uppercase standard (e.g. 'A', '1')."""
    if not raw_key:
        return ""

    # Match single character or number inside parentheses or before dot
    match = re.search(r"([A-Za-z0-9])", raw_key)
    if match:
        return match.group(1).upper()

    return raw_key.strip().rstrip(".:)- ").upper()


def compute_text_completeness_score(text: str) -> float:
    """
    Evaluates how complete a question text appears based on punctuation, length, and sentence structure.
    Returns a score between 0.0 and 1.0.
    """
    if not text or len(text.strip()) < 5:
        return 0.2

    score = 0.5
    stripped = text.strip()

    # Ends with punctuation like '?', '.', ':'
    if stripped[-1] in "?.:!":
        score += 0.3
    elif stripped.endswith("___") or stripped.endswith("______"):
        score += 0.3
    else:
        # Dangling sentence end
        score -= 0.2

    # Reasonable question length
    word_count = len(stripped.split())
    if word_count >= 5:
        score += 0.2
    else:
        score -= 0.1

    return max(0.1, min(1.0, score))
