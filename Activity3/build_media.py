"""Create a short narrated reflection video and a two-page PDF report."""

from __future__ import annotations

from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


HERE = Path(__file__).resolve().parent
FONT_DIR = HERE.parent / "MAPS-Knowledge-Management-Prototype" / "assets/fonts"
REG = str(FONT_DIR / "Outfit-Regular.ttf")
SEM = str(FONT_DIR / "Outfit-SemiBold.ttf")
pdfmetrics.registerFont(TTFont("Outfit", REG))
pdfmetrics.registerFont(TTFont("Outfit-Semi", SEM))

INK = colors.HexColor("#202B31")
MUTED = colors.HexColor("#51636B")
TEAL = colors.HexColor("#176E6D")
LINE = colors.HexColor("#D7DFDE")
PAPER = colors.HexColor("#F6F5F0")


def report() -> None:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TitleCustom", fontName="Outfit-Semi", fontSize=24, leading=27,
        textColor=INK, spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="Deck", fontName="Outfit", fontSize=10.2, leading=14.4,
        textColor=MUTED, spaceAfter=16,
    ))
    styles.add(ParagraphStyle(
        name="HeadCustom", fontName="Outfit-Semi", fontSize=12.2, leading=16,
        textColor=TEAL, spaceBefore=14, spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="BodyCustom", fontName="Outfit", fontSize=9.5, leading=13.8,
        textColor=INK, spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="SmallCustom", fontName="Outfit", fontSize=8.2, leading=11.7,
        textColor=INK,
    ))
    styles.add(ParagraphStyle(
        name="TableHeadCustom", fontName="Outfit-Semi", fontSize=8.2, leading=11,
        textColor=INK,
    ))
    styles.add(ParagraphStyle(
        name="LinkCustom", fontName="Outfit", fontSize=8.2, leading=11.7,
        textColor=TEAL, wordWrap="CJK",
    ))
    P = lambda t, st="BodyCustom": Paragraph(t, styles[st])
    story = [
        P("Activity 3 / Document recommendations", "TitleCustom"),
        P("MAPS · Aster Systems (fictional) · Hugo de la O &amp; Santiago Rivera<br/>"
          "Professor Alfredo Paul Aguirre Torres · 2 November 2026", "Deck"),
        P("Approach", "HeadCustom"),
        P("We reused 32 simulated records from the earlier Aster prototype and wrote six "
          "policy/process records, for a self-contained corpus of <b>38 documents</b>. "
          "The CSV stores ID, title, text and category. The Python program accepts a seed "
          "ID or free text and returns five ranked documents."),
        P("Text is lowercased and punctuation is replaced with spaces. "
          "<b>TfidfVectorizer</b> represents word unigrams and bigrams with English "
          "stopwords removed. Cosine similarity compares the seed or query vector with "
          "each document. Seed results exclude themselves; zero-overlap results are "
          "suppressed. This is a lexical baseline, not a semantic embedding model."),
        P("Three executed cases", "HeadCustom"),
    ]
    data = [
        [P("Input", "TableHeadCustom"), P("Top five, with cosine score", "TableHeadCustom")],
        [P("Policy / PP-01", "SmallCustom"),
         P("IR-01 .1999 · PP-03 .1427 · PP-06 .1207 · TG-01 .1165 · PP-02 .1046", "SmallCustom")],
        [P("Incident / IR-01", "SmallCustom"),
         P("PP-01 .1999 · IR-04 .1665 · TP-01 .1279 · RN-01 .1206 · IR-06 .1030", "SmallCustom")],
        [P("Free-text query", "SmallCustom"),
         P("IR-01 .3323 · TP-01 .2674 · RN-01 .1604 · PP-01 .0921 · TG-01 .0781", "SmallCustom")],
    ]
    table = Table(data, colWidths=[115, 370], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PAPER),
        ("GRID", (0, 0), (-1, -1), .35, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    story += [table, Spacer(1, 9),
              P("Query: “How do we reproduce and fix the command display freeze "
                "after a network reconnect?” The full inputs, output and commentary "
                "are in <b>evidencias/</b> as console logs and PNG captures.", "SmallCustom"),
              PageBreak(),
              P("What the results tell us", "TitleCustom"),
              P("A useful first pass, with visible limits", "Deck"),
              P("Business utility", "HeadCustom"),
              P("The policy seed leads to an incident, handoff and closure processes, "
                "and a recovery guide. The free-text question leads to the incident, "
                "reproduction procedure and release correction. Support can reuse "
                "past diagnoses; QA can start from a recorded test; Operations can "
                "check an approved guide. Shared references reduce duplicate "
                "investigation and make handoff decisions faster. A specialist must "
                "still verify the current version before acting."),
              P("Areas for improvement", "HeadCustom"),
              P("<b>Template bias:</b> IR-04 and IR-06 entered the incident Top-5 "
                "because tickets share standard wording, even though their symptoms "
                "differ. Reduce boilerplate weight and evaluate with human relevance labels."),
              P("<b>Synonyms and ambiguity:</b> terms such as sign-in and authentication "
                "may not overlap; a short query can refer to different systems. Compare "
                "this baseline with embeddings or a controlled vocabulary."),
              P("<b>Production controls:</b> add owner, system, version, review date and "
                "status; filter by user role before ranking; hide superseded guides; "
                "measure precision at five and collect resolution feedback. The small "
                "synthetic corpus is not evidence of live performance."),
              P("Reflection video", "HeadCustom"),
              P("The narrated reflection (2 minutes 29 seconds) answers how recommendations "
                "reduce rework, where they fail, and what a real deployment needs. "
                "The video file is included in this electronic folder as "
                "<b>organizational_reflection.mp4</b>."),
              P('<link href="organizational_reflection.mp4" color="#176E6D">'
                'Open the video in this electronic folder</link>', "LinkCustom"),
              P('<link href="https://github.com/1816x/MAPS-Knowledge-Management-Prototype/blob/main/Activity3/organizational_reflection.mp4" color="#176E6D">'
                'Repository video link (active after publication)</link>', "LinkCustom"),
              Spacer(1, 14),
              P("Method and evidence: recommender.py · corpus.csv · "
                "evidencias/test1_policy, test2_incident, test3_query · "
                "video_script.txt", "SmallCustom")]

    doc = SimpleDocTemplate(
        str(HERE / "Activity3_Report.pdf"), pagesize=A4,
        leftMargin=52, rightMargin=52, topMargin=48, bottomMargin=44,
        title="MAPS Activity 3 — Document recommendations",
        author="Hugo de la O and Santiago Rivera",
    )

    def page(canvas, document):
        w, h = A4
        canvas.setStrokeColor(LINE)
        canvas.line(52, 34, w - 52, 34)
        canvas.setFont("Outfit", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(52, 22, "ASTER SYSTEMS / MAPS")
        canvas.drawRightString(w - 52, 22, str(document.page))

    doc.build(story, onFirstPage=page, onLaterPages=page)


def video() -> None:
    size = (1280, 720)
    scenes = [
        ("01 / CONTEXT", "Aster Systems", "38 simulated documents", [
            "32 existing records from the earlier prototype",
            "6 new policy and process documents",
            "Support · Operations · QA · Engineering",
        ], 25),
        ("02 / METHOD", "One transparent baseline", "TF-IDF + cosine similarity", [
            "Clean text and build word / phrase vectors",
            "Accept a document ID or natural-language query",
            "Rank Top-5; exclude the seed document",
        ], 25),
        ("03 / TESTS", "Three executed cases", "Policy · incident · free text", [
            "PP-01 → IR-01, PP-03, PP-06, TG-01, PP-02",
            "IR-01 → PP-01, IR-04, TP-01, RN-01, IR-06",
            "Question → IR-01, TP-01, RN-01, PP-01, TG-01",
        ], 34),
        ("04 / USE", "Less duplicated work", "A shared starting point", [
            "Find an earlier diagnosis and validation procedure",
            "Handoff with the same documented references",
            "Verify the current guide before acting",
        ], 25),
        ("05 / LIMITS", "The ranking can be wrong", "Shared words are not shared meaning", [
            "Generic ticket language overranked IR-04 and IR-06",
            "Synonyms, ambiguity and short texts reduce recall",
            "Small simulated corpus does not predict live utility",
        ], 20),
        ("06 / NEXT", "Before real deployment", "Metadata, access and evaluation", [
            "System · owner · version · review date · status",
            "Role filters and removal of superseded guides",
            "Human labels, precision@5 and feedback",
        ], 23),
    ]
    regular = ImageFont.truetype(REG, 32)
    medium = ImageFont.truetype(SEM, 66)
    small = ImageFont.truetype(SEM, 23)
    subtitle = ImageFont.truetype(REG, 40)
    slide_dir = HERE / "slides"
    slide_dir.mkdir(exist_ok=True)
    manifest = []
    for index, (label, title, deck, bullets, duration) in enumerate(scenes, 1):
        im = Image.new("RGB", size, "#F6F5F0")
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, 18, 720), fill="#176E6D")
        d.text((80, 72), label, font=small, fill="#176E6D")
        d.text((80, 143), title, font=medium, fill="#202B31")
        d.text((80, 250), deck, font=subtitle, fill="#51636B")
        d.line((80, 336, 1200, 336), fill="#C8D2D0", width=3)
        for n, line in enumerate(bullets):
            y = 389 + n * 80
            d.ellipse((83, y + 13, 97, y + 27), fill="#176E6D")
            d.text((121, y), line, font=regular, fill="#202B31")
        d.text((80, 657), "MAPS  /  ACTIVITY 3", font=small, fill="#51636B")
        d.text((1167, 657), f"{index:02}", font=small, fill="#51636B")
        name = slide_dir / f"slide_{index:02}.png"
        im.save(name)
        manifest.append((name, duration))
    concat = slide_dir / "concat.txt"
    concat.write_text(
        "".join(f"file '{p}'\nduration {duration}\n" for p, duration in manifest)
        + f"file '{manifest[-1][0]}'\n", encoding="utf-8"
    )
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat),
        "-i", str(HERE / "narration.wav"), "-r", "24", "-c:v", "libx264",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
        "-shortest", str(HERE / "organizational_reflection.mp4")
    ], check=True)


if __name__ == "__main__":
    report()
    video()
