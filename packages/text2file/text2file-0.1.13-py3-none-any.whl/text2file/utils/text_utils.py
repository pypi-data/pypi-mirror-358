"""Utility functions for text processing."""

import random
import re
import string
import textwrap
from typing import List, Tuple


def wrap_text(text: str, width: int = 80, **kwargs) -> str:
    """Wrap text to a specified width.

    Args:
        text: Input text to wrap
        width: Maximum line width
        **kwargs: Additional arguments to pass to textwrap.fill()

    Returns:
        Wrapped text
    """
    kwargs.setdefault("replace_whitespace", True)
    kwargs.setdefault("drop_whitespace", True)
    kwargs.setdefault("break_long_words", True)
    kwargs.setdefault("break_on_hyphens", True)

    return textwrap.fill(text, width=width, **kwargs)


def truncate_text(
    text: str,
    max_length: int = 100,
    ellipsis: str = "...",
    words: bool = False
) -> str:
    """Truncate text to a maximum length.

    Args:
        text: Input text to truncate
        max_length: Maximum length of the result
        ellipsis: String to append if text is truncated
        words: If True, truncate at word boundary

    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text

    if words:
        # Truncate at word boundary
        truncated = text[:max_length]
        if " " in truncated:
            # Find the last space before max_length
            last_space = truncated.rfind(" ")
            if last_space > 0:
                truncated = truncated[:last_space]
    else:
        truncated = text[:max_length]

    return truncated + ellipsis if len(truncated) < len(text) else truncated


def slugify(
    text: str,
    separator: str = "-",
    lowercase: bool = True,
    ascii_only: bool = True,
    allow_unicode: bool = False,
) -> str:
    """Convert text to a URL-friendly slug.

    Args:
        text: Input text
        separator: Word separator
        lowercase: Convert to lowercase
        ascii_only: Convert Unicode to ASCII (e.g., é → e)
        allow_unicode: Allow Unicode characters in the slug

    Returns:
        URL-friendly slug
    """
    import unicodedata

    # Convert to ASCII if requested
    if ascii_only and not allow_unicode:
        text = unicodedata.normalize("NFKD", text)
        text = text.encode("ascii", "ignore").decode("ascii")

    # Replace spaces and underscores with the separator
    text = re.sub(r"[\s_]+", separator, text)

    # Remove all non-word characters (alphanumerics and underscores)
    if allow_unicode:
        text = re.sub(r"[^\w\-]", "", text, flags=re.UNICODE)
    else:
        text = re.sub(r"[^\w\-]", "", text)

    # Replace multiple separators with a single one
    text = re.sub(rf"[{re.escape(separator)}]+", separator, text)

    # Remove leading/trailing separators
    text = text.strip(separator)

    # Convert to lowercase if requested
    if lowercase:
        text = text.lower()

    return text


def generate_random_string(
    length: int = 10, chars: str = string.ascii_letters + string.digits
) -> str:
    """Generate a random string of specified length.

    Args:
        length: Length of the string to generate
        chars: Characters to choose from

    Returns:
        Random string
    """
    return "".join(random.choice(chars) for _ in range(length))


def count_words(text: str) -> int:
    """Count the number of words in a text.

    Args:
        text: Input text

    Returns:
        Word count
    """
    if not text.strip():
        return 0
    # Split on any whitespace and filter out empty strings
    return len([word for word in re.split(r"\s+", text) if word])


def count_characters(text: str, include_whitespace: bool = True) -> int:
    """Count the number of characters in a text.

    Args:
        text: Input text
        include_whitespace: Whether to include whitespace characters

    Returns:
        Character count
    """
    if not include_whitespace:
        text = re.sub(r"\s+", "", text)
    return len(text)


def count_sentences(text: str) -> int:
    """Count the number of sentences in a text.

    Note: This is a simple implementation and may not work perfectly
    for all text, especially with abbreviations, numbers, etc.

    Args:
        text: Input text

    Returns:
        Sentence count
    """
    if not text.strip():
        return 0

    # Split on sentence terminators, but exclude common abbreviations
    sentences = re.split(r"(?<![A-Z][a-z]\.)(?<=\S[.!?])\s+", text)
    return len([s for s in sentences if s.strip()])


def count_paragraphs(text: str) -> int:
    """Count the number of paragraphs in a text.

    Args:
        text: Input text

    Returns:
        Paragraph count
    """
    if not text.strip():
        return 0
    # Split on double newlines and filter out empty paragraphs
    paragraphs = re.split(r"\n\s*\n", text)
    return len([p for p in paragraphs if p.strip()])


def remove_extra_whitespace(text: str) -> str:
    """Remove extra whitespace from text.

    Args:
        text: Input text

    Returns:
        Text with extra whitespace removed
    """
    # Replace any whitespace (including newlines) with a single space
    text = re.sub(r"\s+", " ", text)
    # Remove leading/trailing whitespace
    return text.strip()


def remove_html_tags(text: str) -> str:
    """Remove HTML tags from text.

    Args:
        text: Input text with HTML

    Returns:
        Text with HTML tags removed
    """
    return re.sub(r"<[^>]+>", "", text)


def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text.

    Args:
        text: Input text

    Returns:
        List of email addresses found
    """
    # Simple email regex (not 100% RFC compliant but good for most cases)
    email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    return re.findall(email_regex, text)


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text.

    Args:
        text: Input text

    Returns:
        List of URLs found
    """
    # Simple URL regex
    url_regex = r'https?://[^\s\n"]+'
    return re.findall(url_regex, text)


def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from text.

    Args:
        text: Input text

    Returns:
        List of hashtags (without the # symbol)
    """
    return re.findall(r"#(\w+)", text)


def extract_mentions(text: str) -> List[str]:
    """Extract @mentions from text.

    Args:
        text: Input text

    Returns:
        List of mentions (without the @ symbol)
    """
    return re.findall(r"@(\w+)", text)


def generate_lorem_ipsum(
    paragraphs: int = 3,
    sentences_per_paragraph: int = 3,
    words_per_sentence: Tuple[int, int] = (5, 15),
    start_with_lorem: bool = True,
) -> str:
    """Generate lorem ipsum placeholder text.

    Args:
        paragraphs: Number of paragraphs to generate
        sentences_per_paragraph: Number of sentences per paragraph
        words_per_sentence: Range of words per sentence (min, max)
        start_with_lorem: Whether to start with "Lorem ipsum..."

    Returns:
        Generated lorem ipsum text
    """
    lorem_words = [
        "lorem",
        "ipsum",
        "dolor",
        "sit",
        "amet",
        "consectetur",
        "adipiscing",
        "elit",
        "sed",
        "do",
        "eiusmod",
        "tempor",
        "incididunt",
        "ut",
        "labore",
        "et",
        "dolore",
        "magna",
        "aliqua",
        "ut",
        "enim",
        "ad",
        "minim",
        "veniam",
        "quis",
        "nostrud",
        "exercitation",
        "ullamco",
        "laboris",
        "nisi",
        "ut",
        "aliquip",
        "ex",
        "ea",
        "commodo",
        "consequat",
        "duis",
        "aute",
        "irure",
        "dolor",
        "in",
        "reprehenderit",
        "in",
        "voluptate",
        "velit",
        "esse",
        "cillum",
        "dolore",
        "eu",
        "fugiat",
        "nulla",
        "pariatur",
        "excepteur",
        "sint",
        "occaecat",
        "cupidatat",
        "non",
        "proident",
        "sunt",
        "in",
        "culpa",
        "qui",
        "officia",
        "deserunt",
        "mollit",
        "anim",
        "id",
        "est",
        "laborum",
    ]

    result = []

    # Add the standard lorem ipsum start if requested
    if start_with_lorem and paragraphs > 0:
        lorem_start = (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris."
        )
        result.append(lorem_start)
        paragraphs -= 1

    # Generate remaining paragraphs
    for _ in range(paragraphs):
        paragraph = []
        for _ in range(sentences_per_paragraph):
            # Random number of words for this sentence
            word_count = random.randint(*words_per_sentence)
            # Select random words
            sentence_words = random.sample(
                lorem_words, min(word_count, len(lorem_words))
            )
            # Capitalize first word
            if sentence_words:
                sentence_words[0] = sentence_words[0].capitalize()
            # Add period
            sentence = " ".join(sentence_words) + "."
            paragraph.append(sentence)

        result.append(" ".join(paragraph))

    # Join paragraphs with double newlines
    return "\n\n".join(result)
