"""
Seed script: parses the DSA patterns PDF and loads questions into MongoDB.

Usage:
    1. Place the PDF at backend/data/Dsa_important_patterns.pdf
       (or pass a custom path as the first CLI argument).
    2. From the backend/ folder, run:
         python seed.py
"""

import asyncio
import re
import sys
from pathlib import Path

import pdfplumber
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import settings
from app.models import User, Question, Progress

DEFAULT_PDF_PATH = Path(__file__).parent / "data" / "Dsa_important_patterns.pdf"

# Known category headers, in the order they appear in the PDF.
# Used to split the raw extracted text into category blocks.
CATEGORY_HEADERS = [
    "Arrays & Hashing (core)",
    "Two Pointers & Sliding Window",
    "Binary Search (on value, answer, or index)",
    "Prefix Sum / Difference Array / Kadane",
    "Stack & Monotonic Stack / Deque",
    "Intervals",
    "Matrices & Grids (including flood fill)",
    "Linked List (classic + tricky)",
    "Trees & BSTs",
    "Trie / Prefix Trees",
    "Heaps / Priority Queue & Greedy",
    "Backtracking (combinatorics & search)",
    "Dynamic Programming — 1D / Sequences",
    "Dynamic Programming — 2D / Grid / Edit",
    "Graphs — BFS/DFS/Topo/Components",
    "Union-Find (Disjoint Set)",
    "Shortest Path / Dijkstra / Binary Search on Answer",
    "Bit Manipulation",
    "Math / Strings / Parsing",
    "Design (common LLD-style)",
]


def slugify(title: str) -> str:
    """Best-effort LeetCode-style slug. Not guaranteed to be correct for every title."""
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug).strip("-")
    return slug


def extract_text(pdf_path: Path) -> str:
    full_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            full_text.append(text)
    return "\n".join(full_text)


def parse_questions(raw_text: str) -> list[dict]:
    """
    Splits raw_text into category blocks using CATEGORY_HEADERS as delimiters,
    then splits each block on the '●' bullet character to get question titles.
    """
    # Normalize whitespace/newlines so headers match even if PDF wrapped them.
    normalized = re.sub(r"\s+", " ", raw_text)

    # Build a regex that finds each header's position in the normalized text.
    positions = []
    for header in CATEGORY_HEADERS:
        header_norm = re.sub(r"\s+", " ", header)
        match = re.search(re.escape(header_norm), normalized)
        if match:
            positions.append((match.start(), header))
        else:
            print(f"  [warn] header not found in PDF text: {header!r}")

    positions.sort(key=lambda x: x[0])

    questions = []
    for i, (start, header) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(normalized)
        block = normalized[start + len(header):end]

        # Split on the bullet character.
        raw_items = block.split("●")
        order = 0
        for item in raw_items:
            title = item.strip(" \t\n-–—•")
            if not title:
                continue
            # Guard against stray fragments that are too short/long to be real titles.
            if len(title) < 2 or len(title) > 120:
                continue
            questions.append(
                {
                    "category": header,
                    "title": title,
                    "url": f"https://leetcode.com/problems/{slugify(title)}/",
                    "order": order,
                }
            )
            order += 1

    return questions


async def seed(pdf_path: Path):
    if not pdf_path.exists():
        print(f"PDF not found at {pdf_path}. Pass a path as the first argument or place it there.")
        sys.exit(1)

    print(f"Reading {pdf_path} ...")
    raw_text = extract_text(pdf_path)

    print("Parsing questions ...")
    questions = parse_questions(raw_text)
    print(f"Parsed {len(questions)} questions across {len({q['category'] for q in questions})} categories.")

    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.mongo_db_name]
    await init_beanie(database=db, document_models=[User, Question, Progress])

    existing_count = await Question.find_all().count()
    if existing_count > 0:
        confirm = input(
            f"{existing_count} questions already exist in the DB. Clear and reseed? [y/N] "
        )
        if confirm.strip().lower() != "y":
            print("Aborted.")
            return
        await Question.find_all().delete()

    docs = [Question(**q) for q in questions]
    if docs:
        await Question.insert_many(docs)
    print(f"Inserted {len(docs)} questions into '{settings.mongo_db_name}.questions'.")


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PDF_PATH
    asyncio.run(seed(path))
