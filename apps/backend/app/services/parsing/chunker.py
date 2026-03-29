"""
Section chunking for insurance policy documents.

Splits a policy document into semantic sections so the LLM can:
1. Use the Policy Schedule for metadata (insurer, product, sums, premiums)
2. Use the Benefits section for coverage details
3. Use Exclusions for exclusions list
4. Handle Riders as separate sub-sections

Common Singapore policy section headers (case-insensitive):
"""

import re
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Section header patterns — order matters (first match wins per page)
SECTION_PATTERNS: list[tuple[str, re.Pattern]] = [
    # Policy identification
    (
        "policy_schedule",
        re.compile(
            r"(?i)(?:^|\n)\s*(?:policy\s*schedule|policy\s*document\s*schedule|schedule\s*of\s*policy|policy\s*details|insurance\s*certificate)",
            re.MULTILINE,
        ),
    ),
    # Policyholder / insured details
    (
        "policyholder",
        re.compile(
            r"(?i)(?:^|\n)\s*(?:policy\s*holder|insured\s*details?|life\s*insured|your\s*details?|member\s*details?)",
            re.MULTILINE,
        ),
    ),
    # Product / plan details
    (
        "product_details",
        re.compile(
            r"(?i)(?:^|\n)\s*(?:plan\s*details?|product\s*details?|table?\s*of?\s*benefits?|benefits?\s*illustration?)",
            re.MULTILINE,
        ),
    ),
    # Benefits section
    (
        "benefits",
        re.compile(
            r"(?i)(?:^|\n)\s*(?:benefits?\s*(?:\s+and\s+terms?)?|scope\s+of\s+coverage|coverage\s+details?|what\s+is?\s+(?:being|we)\s+covered|covered\s+for|included?\s+in\s+(?:your|the)\s+(?:policy|plan))",
            re.MULTILINE,
        ),
    ),
    # Critical illness benefits
    (
        "ci_benefits",
        re.compile(
            r"(?i)(?:^|\n)\s*(?:critical\s+illness|dread\s+disease|cancer\s*&\s*(?:other\s+)?critical\s+illness|ci\s+benefit)",
            re.MULTILINE,
        ),
    ),
    # Hospitalisation benefits
    (
        "hospitalisation",
        re.compile(
            r"(?i)(?:^|\n)\s*(?:hospitalisation|medical\s+benefit|in-patient|ward\s+(?:type|charges?)|surgical\s+benefit)",
            re.MULTILINE,
        ),
    ),
    # Death / TPD
    (
        "death_tpd",
        re.compile(
            r"(?i)(?:^|\n)\s*(?:death\s+(?:benefit|cover)|total\s+permanent\s+disab|basic\s+death|tpd\s+benefit|sum\s+assured\s+on\s+death)",
            re.MULTILINE,
        ),
    ),
    # Exclusions
    (
        "exclusions",
        re.compile(
            r"(?i)(?:^|\n)\s*(?:exclusions?|not\s+covered|limitations?|what\s+is\s+not\s+covered|excluded\s+from\s+coverage)",
            re.MULTILINE,
        ),
    ),
    # General exclusions
    (
        "general_exclusions",
        re.compile(
            r"(?i)(?:^|\n)\s*(?:general\s+exclusions?|standard\s+exclusions?)",
            re.MULTILINE,
        ),
    ),
    # Premiums
    (
        "premiums",
        re.compile(
            r"(?i)(?:^|\n)\s*(?:premium|contribution|payment\s+(?:amount|details?)|frequency\s+of\s+payment)",
            re.MULTILINE,
        ),
    ),
    # Policy conditions
    (
        "conditions",
        re.compile(
            r"(?i)(?:^|\n)\s*(?:policy\s+conditions?|terms?\s+and\s+conditions?|important\s+notes?|conditions?\s+of\s+the\s+policy|your\s+policy\s+at\s+a\s+glance)",
            re.MULTILINE,
        ),
    ),
    # Contestability
    (
        "contestability",
        re.compile(
            r"(?i)(?:^|\n)\s*(?:contestability|free-look|suicide\s+exclusion|survival\s+period|incontestability)",
            re.MULTILINE,
        ),
    ),
    # Riders / supplementary benefits
    (
        "riders",
        re.compile(
            r"(?i)(?:^|\n)\s*(?:riders?|supplementary\s+(?:benefits?|contracts?)|附加\s*保障|附加契约|additional\s+benefits?)",
            re.MULTILINE,
        ),
    ),
    # Definitions
    (
        "definitions",
        re.compile(
            r"(?i)(?:^|\n)\s*(?:definitions?|interpretation|meaning\s+of\s+(?:key\s+)?terms?)",
            re.MULTILINE,
        ),
    ),
    # Claim provisions
    (
        "claims",
        re.compile(
            r"(?i)(?:^|\n)\s*(?:making\s+a\s+claim|how\s+to\s+claim|notification|claim\s+provision|claim\s+procedure)",
            re.MULTILINE,
        ),
    ),
]


@dataclass
class Chunk:
    """A section of the policy document."""

    section_type: str  # e.g. "benefits", "exclusions"
    text: str
    start_page: int
    end_page: int
    heading: str | None = None  # The matched heading text


@dataclass
class Chunks:
    """Collection of all chunks from a document."""

    raw: list[Chunk]
    metadata_chunk: Chunk | None = None  # policy_schedule
    benefits_chunk: Chunk | None = None
    exclusions_chunk: Chunk | None = None
    riders_chunk: Chunk | None = None
    conditions_chunk: Chunk | None = None
    all_text: str = ""  # Reassembled full text

    def get_priority_text(self) -> str:
        """
        Returns text ordered by importance for extraction.
        Metadata → Benefits → Exclusions → Riders → Conditions → everything else.
        """
        parts: list[str] = []

        for chunk in self.raw:
            parts.append(f"[{chunk.section_type.upper()}]\n{chunk.text}")

        return "\n\n".join(parts)

    def get_chunk_summary(self) -> list[dict]:
        """Returns a list of {section_type, page_start, page_end} for the LLM."""
        return [
            {
                "section": c.section_type,
                "pages": f"{c.start_page}-{c.end_page}",
                "chars": len(c.text),
                "heading": c.heading,
            }
            for c in self.raw
        ]


def chunk_by_sections(page_texts: list[str]) -> Chunks:
    """
    Split per-page text into semantic sections.

    Args:
        page_texts: List of text strings, one per page (0-indexed).

    Returns:
        Chunks object with all sections identified and ordered.
    """
    if not page_texts:
        return Chunks(raw=[], all_text="")

    # Track which section each page belongs to
    page_sections: list[tuple[int, str]] = []  # (page_idx, section_type)
    current_section = "unclassified"
    chunks_by_section: dict[str, list[tuple[int, str]]] = {}

    def assign_section(page_idx: int, section_type: str) -> None:
        nonlocal current_section
        if current_section != section_type:
            current_section = section_type
            page_sections.append((page_idx, section_type))
            if section_type not in chunks_by_section:
                chunks_by_section[section_type] = []
        chunks_by_section[section_type].append((page_idx, page_texts[page_idx]))

    for page_idx, page_text in enumerate(page_texts):
        matched = False
        for section_type, pattern in SECTION_PATTERNS:
            if pattern.search(page_text):
                assign_section(page_idx, section_type)
                matched = True
                break
        if not matched:
            assign_section(page_idx, current_section)

    # Build Chunk objects
    raw_chunks: list[Chunk] = []
    section_pages: dict[str, tuple[int, int]] = {}

    for section_type, pages_and_texts in chunks_by_section.items():
        if not pages_and_texts:
            continue
        page_indices = [p for p, _ in pages_and_texts]
        texts = [t for _, t in pages_and_texts]
        combined_text = "\n\n".join(texts)

        # Extract heading from first match in first page
        heading = None
        for _, pattern in SECTION_PATTERNS:
            m = pattern.search(texts[0])
            if m:
                heading = m.group(0).strip()
                break

        chunk = Chunk(
            section_type=section_type,
            text=combined_text,
            start_page=min(page_indices) + 1,  # 1-indexed for humans
            end_page=max(page_indices) + 1,
            heading=heading,
        )
        raw_chunks.append(chunk)
        section_pages[section_type] = (chunk.start_page, chunk.end_page)

    # Sort by first appearance in document
    raw_chunks.sort(key=lambda c: c.start_page)

    # Extract named chunks for priority access
    def find(section_type: str) -> Chunk | None:
        for c in raw_chunks:
            if c.section_type == section_type:
                return c
        return None

    all_text = "\n\n".join(p.page_texts for p in [Chunk("", "", 0, 0)] + raw_chunks)
    all_text = "\n\n".join(
        page_texts[i] for i in range(len(page_texts))
    )

    result = Chunks(
        raw=raw_chunks,
        metadata_chunk=find("policy_schedule")
        or find("product_details")
        or find("policyholder"),
        benefits_chunk=find("benefits")
        or find("ci_benefits")
        or find("hospitalisation")
        or find("death_tpd"),
        exclusions_chunk=find("exclusions") or find("general_exclusions"),
        riders_chunk=find("riders"),
        conditions_chunk=find("conditions") or find("contestability") or find("claims"),
        all_text="\n\n[PAGE_BREAK]\n\n".join(page_texts),
    )

    logger.info(
        f"Chunked {len(page_texts)} pages into {len(raw_chunks)} sections: "
        f"{[c.section_type for c in raw_chunks]}"
    )

    return result
