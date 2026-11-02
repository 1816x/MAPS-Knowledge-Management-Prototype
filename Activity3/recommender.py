"""Transparent Top-K document recommender for Aster Systems.

TF-IDF represents words and adjacent word pairs; cosine similarity ranks
documents by shared terms. This is lexical retrieval, not an embedding model.
"""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DEFAULT_CORPUS = Path(__file__).with_name("corpus.csv")
REQUIRED = {"id", "title", "text", "category"}


def clean_text(value: str) -> str:
    """Lowercase and replace punctuation with spaces; retain Unicode letters."""
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", value.lower())).strip()


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    text: str
    category: str


@dataclass(frozen=True)
class Recommendation:
    document: Document
    score: float


class Recommender:
    def __init__(self, corpus_path: Path = DEFAULT_CORPUS):
        with Path(corpus_path).open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
                raise ValueError(f"CSV needs columns: {', '.join(sorted(REQUIRED))}")
            self.documents = [
                Document(
                    id=row["id"].strip(),
                    title=row["title"].strip(),
                    text=row["text"].strip(),
                    category=row["category"].strip(),
                )
                for row in reader
            ]
        ids = [doc.id for doc in self.documents]
        if len(ids) < 6 or len(ids) != len(set(ids)):
            raise ValueError("Corpus needs at least six distinct document IDs")
        if any(not doc.id or not doc.title or not doc.text for doc in self.documents):
            raise ValueError("ID, title, and text cannot be empty")
        self.id_to_index = {doc.id: i for i, doc in enumerate(self.documents)}
        self.vectorizer = TfidfVectorizer(
            preprocessor=clean_text, stop_words="english", ngram_range=(1, 2),
            sublinear_tf=True
        )
        self.matrix = self.vectorizer.fit_transform(
            [doc.text for doc in self.documents]
        )

    def _rank(self, vector, exclude: int | None, top_k: int) -> list[Recommendation]:
        if top_k < 1:
            raise ValueError("top_k must be at least 1")
        scores = cosine_similarity(vector, self.matrix).ravel()
        candidates = [
            Recommendation(doc, float(scores[i]))
            for i, doc in enumerate(self.documents)
            if i != exclude and scores[i] > 0
        ]
        candidates.sort(key=lambda item: (-item.score, item.document.id))
        return candidates[:top_k]

    def by_id(self, document_id: str, top_k: int = 5) -> list[Recommendation]:
        if document_id not in self.id_to_index:
            raise ValueError(f"Unknown document ID: {document_id}")
        index = self.id_to_index[document_id]
        return self._rank(self.matrix[index], exclude=index, top_k=top_k)

    def by_query(self, query: str, top_k: int = 5) -> list[Recommendation]:
        if not clean_text(query):
            raise ValueError("Query cannot be empty")
        return self._rank(self.vectorizer.transform([query]), exclude=None, top_k=top_k)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--id", help="Seed document ID, e.g. PP-01")
    source.add_argument("--query", help="Natural-language query")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    try:
        engine = Recommender(args.csv)
        results = (
            engine.by_id(args.id, args.top_k)
            if args.id else engine.by_query(args.query, args.top_k)
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    print(f"Input: {'ID ' + args.id if args.id else 'query ' + repr(args.query)}")
    print(f"Corpus: {len(engine.documents)} documents | Method: TF-IDF + cosine")
    print("Rank  ID     Score   Category           Title")
    for rank, item in enumerate(results, 1):
        doc = item.document
        print(f"{rank:>4}  {doc.id:<5}  {item.score:.4f}  {doc.category:<18} {doc.title}")
    if not results:
        print("No overlapping terms; no positive-similarity recommendations.")


if __name__ == "__main__":
    main()
