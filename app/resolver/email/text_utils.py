# onboarding_deterministic/text_utils.py

import re
import html
import unicodedata


def remove_accents(text: str) -> str:
    """
    Remove Vietnamese accents but preserve spaces and word boundaries.
    """
    if not text:
        return ""

    text = unicodedata.normalize("NFD", text)
    text = "".join(
        c for c in text
        if unicodedata.category(c) != "Mn"
    )
    text = text.replace("đ", "d").replace("Đ", "D")
    return text


def clean_spaces(text: str) -> str:
    """
    Normalize spaces but do not merge words.
    """
    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_text_value(text: str) -> str:
    """
    Business normalization for extracted values:
    - remove accents
    - preserve spaces
    - trim redundant spaces
    """
    return clean_spaces(remove_accents(text))


def normalize_label(label: str) -> str:
    """
    Normalize field labels for deterministic matching.
    """
    label = remove_accents(label or "")
    label = label.lower().strip()
    label = re.sub(r"\s+", " ", label)
    return label


def html_to_text(html_content: str) -> str:
    """
    Lightweight HTML to text converter for email body.
    Does not require BeautifulSoup.
    """
    if not html_content:
        return ""

    text = html_content

    # Convert common line-break/block tags to newline
    text = re.sub(r"(?i)<\s*br\s*/?\s*>", "\n", text)
    text = re.sub(r"(?i)</\s*p\s*>", "\n", text)
    text = re.sub(r"(?i)</\s*div\s*>", "\n", text)
    text = re.sub(r"(?i)</\s*tr\s*>", "\n", text)

    # Remove all remaining tags
    text = re.sub(r"<[^>]+>", " ", text)

    text = html.unescape(text)
    return clean_spaces(text)