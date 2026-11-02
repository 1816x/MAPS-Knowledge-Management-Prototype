"""Build a self-contained CSV from the 32 existing Aster records and six processes."""

from __future__ import annotations

import csv
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRIOR_DATA = HERE.parent / "MAPS-Knowledge-Management-Prototype" / "data"


def build() -> int:
    rows: list[dict[str, str]] = []
    with (PRIOR_DATA / "index.csv").open(newline="", encoding="utf-8") as handle:
        for item in csv.DictReader(handle):
            text = (PRIOR_DATA / "documents" / item["file"]).read_text(
                encoding="utf-8"
            ).strip()
            rows.append(
                {
                    "id": item["id"],
                    "title": item["title"],
                    "text": text,
                    "category": item["category"],
                }
            )

    for path in sorted((HERE / "docs_txt").glob("PP-*.txt")):
        content = path.read_text(encoding="utf-8").strip()
        title = content.splitlines()[0]
        rows.append(
            {
                "id": path.stem,
                "title": title,
                "text": content,
                "category": "Policy/Process",
            }
        )

    if len(rows) != 38 or len({row["id"] for row in rows}) != 38:
        raise ValueError("Expected 38 unique documents: 32 existing + 6 processes")
    with (HERE / "corpus.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "title", "text", "category"])
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    print(f"Wrote {build()} documents to {HERE / 'corpus.csv'}")
