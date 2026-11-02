# MAPS Activity 3 · Document recommendations

**Organization:** Aster Systems, the fictional software company used in the earlier MAPS prototype. All records are simulated.

## Objective

Recommend the five most similar organizational documents to a document ID or a short natural-language query. The corpus has **38** documents: 32 existing incident reports, technical guides, test procedures and release notes, plus six new policy/process documents. The CSV is self-contained; no runtime dependency on the earlier phase.

## Dependencies

- Python 3.10+
- scikit-learn 1.3 to <2 (see `requirements.txt`)

## Setup and execution

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python recommender.py --id PP-01
python recommender.py --id IR-01
python recommender.py --query "How do we reproduce and fix the command display freeze after a network reconnect?"
python -m unittest discover -s tests -v
```

Windows PowerShell: use `.venv\Scripts\Activate.ps1` in place of `source .venv/bin/activate`.

Use `--top-k N` to change the default five recommendations. Use `--csv PATH` for another compatible corpus. An unknown ID or empty query receives a clear error. Documents with zero shared terms are not recommended.

## Method

The program reads `corpus.csv` columns `id,title,text,category`, lowercases the text, replaces punctuation with spaces, then fits a TF-IDF model with English stopwords and word unigrams/bigrams. It ranks cosine similarity in descending order, resolves ties by document ID, and excludes the seed document itself. Scores are relative similarities, **not** confidence or relevance probabilities. The query and documents use the same fitted vectorizer.

`build_corpus.py` reproduces the CSV from the earlier phase's `data/index.csv`, `data/documents/`, and this folder's `docs_txt/PP-*.txt`. The committed CSV remains usable independently.

## Evidence

- `evidencias/test1_policy.txt` and `.png`: seed `PP-01` (Policy/Process).
- `evidencias/test2_incident.txt` and `.png`: seed `IR-01` (Support/Incidents).
- `evidencias/test3_query.txt` and `.png`: free-text query.
- `evidencias/unit_tests.txt`: four automated behavioral checks.

The PNG files render **actual captured console output**; the matching plain-text logs are the direct executions. The comments identify useful links and false positives.

## Limits and next steps

TF-IDF matches vocabulary, not meaning. It can miss synonyms, overrank templated wording, and be unstable on short texts. A production system should add document owner, system, version, date and role metadata; apply authorization before retrieval; remove superseded instructions; and evaluate recommendations using specialist relevance judgments and click or resolution feedback. No real credentials or confidential records belong in this sample corpus.

## Deliverables

- `recommender.py`, `corpus.csv`, `docs_txt/`, `evidencias/`.
- `Activity3_Report.pdf` (two pages).
- `organizational_reflection.mp4` and `video_script.txt` (under five minutes).

Team: Hugo de la O and Santiago Rivera. Professor Alfredo Paul Aguirre Torres.
