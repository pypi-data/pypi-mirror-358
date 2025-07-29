import json
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic_settings import BaseSettings, SettingsConfigDict
from rapidfuzz import fuzz, process

from ragchat.definitions import (
    IndexedMetadata,
    Message,
    Node,
    NodeType,
    Relation,
)
from ragchat.log import get_logger
from ragchat.prompts import _facts, _summary
from ragchat.utils import get_unique

logger = get_logger(__name__)


class ParserSettings(BaseSettings):
    score_cutoff: int = 80
    chunk_char_size: int = 2000
    max_chars_key: int = 99
    max_chars_val: int = 256

    model_config = SettingsConfigDict(case_sensitive=False, env_prefix="PARSER_")


settings = ParserSettings()


def header_items_to_markdown(
    header: str, items: List[Any], header_level: str = "##", bullet_char: str = "-"
) -> str:
    """Converts a list of items into markdown format with the given header."""
    markdown = f"{header_level} {header}\n"
    markdown += "\n".join([f"{bullet_char} {item}" for item in items])
    return markdown


def markdown_to_heading_items(
    markdown: str,
    match_headings: Optional[List[str]] = None,
    headings_pool: Optional[List[str]] = None,
    match_items: Optional[List[str]] = None,
    items_pool: Optional[List[str]] = None,
    mutually_exclusive: bool = False,
    exclude_nones: bool = True,
    score_cutoff: int = settings.score_cutoff,
) -> Dict[str, List[str]]:
    """
    Parses markdown text to extract list items organized by headings,
    with optional fuzzy validation against pools or exact (fuzzy) matching sets.
    Content directly under a heading (not a bulleted list item) will also be parsed as an item.
    """
    lines = markdown.split("\n")
    list_item_pattern = re.compile(r"^\s*[-*+]\s+(.*?)$")
    heading_pattern = re.compile(r"^(#{1,6})\s+(.*?)$")

    result: Dict[str, List[str]] = {}
    current_heading: Optional[str] = None

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        if line_stripped.strip().strip("'\"").lower() == "none":
            continue

        heading_match = heading_pattern.match(line)
        if heading_match:
            current_heading = " ".join(
                heading_match.group(2).strip().strip("'\"").split()
            )
            if current_heading not in result:
                result[current_heading] = []
            continue

        if current_heading:
            match = list_item_pattern.match(line)
            if match:
                # This is a bulleted list item
                item = " ".join(match.group(1).strip().split())
                result[current_heading].append(item)
            else:
                # This is content directly under the current heading, not a bulleted list item
                content = " ".join(line_stripped.split())
                if (
                    content
                ):  # Only add if there's actual content after stripping/normalizing
                    result[current_heading].append(content)

    # Flatten the list of lists of items into a single list for validation
    all_parsed_items: List[str] = [
        item for sublist in result.values() for item in sublist
    ]
    parsed_headings: List[str] = list(result.keys())
    parsed_items: List[str] = get_unique(all_parsed_items)

    def check_pool(items_to_check: List[str], pool: List[str], item_type: str) -> None:
        if not pool:
            if items_to_check:
                raise ValueError(
                    f"Found {item_type}s {items_to_check} but {item_type} pool is empty."
                )
            return

        invalid_items: Set[str] = set()
        for item in items_to_check:
            match = process.extractOne(
                item, pool, scorer=fuzz.ratio, score_cutoff=score_cutoff
            )
            if match is None:
                invalid_items.add(item)
        if invalid_items:
            logger.debug(
                f"Found {item_type}s not in the allowed pool: "
                f"{list(invalid_items)}. Pool: {pool}"
            )
            raise ValueError(f"Select only from the allowed {item_type}s: {pool}.")

    def check_match(parsed: List[str], expected: List[str], item_type: str) -> None:
        unmatched_parsed = []
        if expected:
            for item in parsed:
                match = process.extractOne(
                    item, expected, scorer=fuzz.ratio, score_cutoff=score_cutoff
                )
                if match is None:
                    unmatched_parsed.append(item)
        elif parsed:
            unmatched_parsed = parsed

        if unmatched_parsed:
            logger.debug(
                f"Found unexpected {item_type}s: "
                f"Found {unmatched_parsed}. Expected: {expected}"
            )
            raise ValueError(f"Adhere strictly to {item_type}s: {expected}")

        unmatched_expected = []
        if parsed:
            for item in expected:
                match = process.extractOne(
                    item, parsed, scorer=fuzz.ratio, score_cutoff=score_cutoff
                )
                if match is None:
                    unmatched_expected.append(item)
        elif expected:
            unmatched_expected = expected

        if unmatched_expected:
            logger.debug(
                f"Missing {item_type}s: Found: {parsed}. Missing {unmatched_expected}"
            )
            raise ValueError(f"Adhere strictly to {item_type}s: {expected}")

    if headings_pool is not None:
        check_pool(parsed_headings, headings_pool, "heading")

    if items_pool is not None:
        check_pool(parsed_items, items_pool, "item")

    if match_headings is not None:
        check_match(parsed_headings, match_headings, "heading")

    if match_items is not None:
        check_match(parsed_items, match_items, "item")

    if mutually_exclusive:
        all_items = [item for items in result.values() for item in items]
        if len(set(all_items)) != len(all_items):
            counts: dict[str, int] = {}
            duplicates = set()
            for item in all_items:
                counts[item] = counts.get(item, 0) + 1
                if counts[item] > 1:
                    duplicates.add(item)
            logger.debug(
                f"Items are not mutually exclusive across headings. Duplicates found: {list(duplicates)}"
            )
            raise ValueError("Items cannot repeat across headings.")

    if exclude_nones:
        cleaned_result = {}
        for k, v in result.items():
            filtered_items = [item for item in v if item and item.lower() != "none"]
            if filtered_items:
                cleaned_result[k] = filtered_items
        result = cleaned_result

    return result


def load_json(s: str) -> Any:
    """
    Extract and load JSON from a string that may contain Markdown formatting
    or LLM explanations.
    """
    # Remove Markdown-style code block markers
    s = re.sub(r"```(?:json)?\s*", "", s)
    s = re.sub(r"\s*```", "", s)

    # Try to locate the first balanced JSON object
    brace_stack: list[str] = []
    start = None
    for i, char in enumerate(s):
        if char == "{":
            if not brace_stack:
                start = i
            brace_stack.append("{")
        elif char == "}":
            if brace_stack:
                brace_stack.pop()
                if not brace_stack:
                    try:
                        json_str = s[start : i + 1]
                        # json.loads returns Dict[str, Any] for JSON objects
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        continue
    raise ValueError("No valid JSON object found in string")


def get_summary_facts(
    d: Dict[str, Any], max_fact_chars: int = 50, exclude_nones: bool = True
) -> Tuple[str, List[str]]:
    """
    Extracts unique, non-empty primitive values from a nested dictionary.
    Values are categorized as 'facts' or 'summary' based on their path (e.g., 'data', 'summary' in path)
    or, if unclassified, by string length (up to `max_fact_chars` for facts).

    Args:
        d (dict): The dictionary to search for values.
        exclude_nones (bool): If True, None values will be excluded.
        max_fact_chars (int): Max char length for a string to be an 'fact' by fallback.

    Returns:
        Tuple[str, List[str]]: A tuple: (newline-joined unique 'summary' values, sorted list of unique 'fact' values).
    """

    facts_values: Set[str] = set()
    summary_values: Set[Any] = set()

    for path_str, values_list in d.items():
        # Assuming _facts and _summary are available in the scope
        is_fact_path = _facts.is_me(path_str)
        is_summary_path = _summary.is_me(path_str)

        for value in values_list:
            if exclude_nones and value is None:
                continue

            is_string_value = isinstance(value, str)
            # Use original string value for facts, or its string representation for non-strings
            processed_fact_value_str = value if is_string_value else str(value)

            if is_string_value and not processed_fact_value_str:
                continue

            # Determine classification flags based on path
            is_classified_as_fact = is_fact_path
            is_classified_as_summary = is_summary_path

            # Fallback classification if not classified by path
            if not (is_classified_as_fact or is_classified_as_summary):
                if is_string_value and len(processed_fact_value_str) <= max_fact_chars:
                    is_classified_as_fact = True
                else:
                    is_classified_as_summary = True

            # Add to facts_values if classified as fact (using processed value)
            if is_classified_as_fact:
                facts_values.add(processed_fact_value_str)

            # Add to summary_values if classified as summary (using original value)
            if is_classified_as_summary:
                summary_values.add(value)

    return "\n".join(map(str, summary_values)), sorted(list(facts_values))


def md_to_relation(
    md: str,
    indexed_metadata: IndexedMetadata,
    chunk_content: str,
    min_chars: int = 32,
    exclude_nones: bool = True,
) -> Optional[Relation]:
    """"""
    if len(md) < min_chars:
        return None

    structured = markdown_to_heading_items(md)
    if not structured:
        return None
    summary, fact_contents = get_summary_facts(structured)
    facts: List[Node] = [
        Node.from_metadata(
            metadata=indexed_metadata,
            node_type=NodeType.FACT,
            content=s,
            summary=s,
        )
        for s in fact_contents
    ]

    chunk = Node.from_metadata(
        metadata=indexed_metadata,
        node_type=NodeType.CHUNK,
        content=chunk_content,
        structured={},
        summary=summary,
    )
    relation = Relation(
        chunk=chunk,
        facts=facts,
    )

    return relation


def _find_split(window: str, delimiters: list[str], min_window_size: int) -> int:
    """Finds an appropriate split point in a text window based on delimiters."""
    window_size = len(window)
    for delimiter in delimiters:
        idx = window.rfind(delimiter)
        if min_window_size < idx:
            window_size = idx
            break
    return window_size


def chunk_text(text: str, chunk_char_size: Optional[int] = None) -> List[str]:
    """Splits text into chunks, respecting markdown headings and paragraphs."""
    chunks = []
    start = 0
    text_length = len(text)
    chunk_char_size = chunk_char_size or settings.chunk_char_size
    while start < text_length:
        end = start + chunk_char_size
        if text_length < end:
            chunks.append(text[start:])
            break

        current_window = text[start:end]
        delimiters = [
            "\n# ",
            "\n## ",
            "\n### ",
            "\n\n\n\n",
            "\n\n\n",
            "\n\n",
            "\n",
            ". ",
            " ",
        ]
        end = start + _find_split(current_window, delimiters, chunk_char_size // 2)

        chunk = text[start:end]
        if chunk:
            if 0 < len(chunks) and (len(chunks[-1]) + len(chunk)) < chunk_char_size:
                chunks[-1] += chunk
            else:
                chunks.append(chunk)
        start = end

    return chunks


def dicts_to_messages(messages: List[Dict[str, Any] | Message]) -> List[Message]:
    """Converts a list of dictionaries and/or Message objects into a list of Message objects."""
    if not messages:
        return []

    new_messages = []
    for msg in messages:
        if isinstance(msg, Message):
            new_messages.append(msg)
        elif isinstance(msg, dict):
            new_messages.append(Message(**msg))
        else:
            raise ValueError(f"Cannot convert message of type {type(msg)} to Message")
    return new_messages


def messages_to_dicts(messages: List[Message | Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Converts a list of Message objects and/or dictionaries into a list of dictionaries."""
    if not messages:
        return []

    new_dicts = []
    for msg in messages:
        if isinstance(msg, dict):
            new_dicts.append(msg)
        elif isinstance(msg, Message):
            new_dicts.append(msg.model_dump(mode="json", exclude_none=True))
        else:
            raise ValueError(f"Cannot convert message of type {type(msg)} to dict")
    return new_dicts


def messages_to_user_text(
    messages: List[Message],
    limit: int = 3,
) -> str:
    """Creates a string from the last N user messages."""
    s = "\n\n".join([m.content for m in messages if m.role == "user"][-limit:])

    return s
