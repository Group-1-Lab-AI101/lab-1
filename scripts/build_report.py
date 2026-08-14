#!/usr/bin/env python3
"""Render the technical-report Markdown source as a polished, verified PDF."""

from __future__ import annotations

import argparse
import html
import json
import math
import os
import re
from pathlib import Path
from textwrap import wrap

from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    LongTable,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = PROJECT_ROOT / "docs" / "TECHNICAL_REPORT.md"
MEMBER_KEYS = ("hoang", "hau", "trung", "khang", "thai_kiet")
CONTENT_WIDTH = A4[0] - 30 * mm

INK = colors.HexColor("#17262B")
MUTED = colors.HexColor("#52636A")
TEAL = colors.HexColor("#08747C")
TEAL_DARK = colors.HexColor("#07545A")
CORAL = colors.HexColor("#D45C43")
PALE = colors.HexColor("#EAF3F3")
GRID = colors.HexColor("#CBD7D9")
WHITE = colors.white


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--draft",
        action="store_true",
        help="Render a watermarked layout-QA draft with synthetic identity data.",
    )
    args = parser.parse_args()
    if args.draft and args.metadata:
        parser.error("--draft and --metadata cannot be used together")
    if not args.draft and not args.metadata:
        parser.error("--metadata is required for a final report")
    if args.output.suffix.lower() != ".pdf":
        parser.error("--output must end in .pdf")
    return args


def _is_placeholder(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return True
    upper = value.upper()
    return "REPLACE_" in upper or "REQUIRED" in upper or "{{" in value


def load_metadata(path: Path | None, draft: bool) -> dict:
    if draft:
        return {
            "group_id": "DRAFT-QA",
            "members": {
                key: {
                    "full_name": f"Layout QA Member {index}",
                    "student_id": f"QA{index:03d}",
                }
                for index, key in enumerate(MEMBER_KEYS, start=1)
            },
        }

    assert path is not None
    try:
        metadata = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot read valid metadata JSON: {exc}") from exc

    group_id = metadata.get("group_id")
    if _is_placeholder(group_id):
        raise SystemExit("metadata.group_id must contain the verified Group ID")
    if any(char in str(group_id) for char in '<>:"/\\|?*'):
        raise SystemExit("metadata.group_id contains a filename-unsafe character")

    members = metadata.get("members")
    if not isinstance(members, dict):
        raise SystemExit("metadata.members must be an object")
    for key in MEMBER_KEYS:
        member = members.get(key)
        if not isinstance(member, dict):
            raise SystemExit(f"metadata.members.{key} is required")
        for field in ("full_name", "student_id"):
            if _is_placeholder(member.get(field)):
                raise SystemExit(f"metadata.members.{key}.{field} must be verified")
    return metadata


def apply_metadata(source: str, metadata: dict) -> str:
    replacements = {"GROUP_ID": metadata["group_id"]}
    for key in MEMBER_KEYS:
        prefix = key.upper()
        member = metadata["members"][key]
        replacements[f"{prefix}_FULL_NAME"] = member["full_name"]
        replacements[f"{prefix}_STUDENT_ID"] = member["student_id"]
    for token, value in replacements.items():
        source = source.replace("{{" + token + "}}", str(value))
    unresolved = sorted(set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", source)))
    if unresolved:
        raise SystemExit(f"Unresolved report tokens: {', '.join(unresolved)}")
    return re.sub(r"<!--.*?-->", "", source, flags=re.DOTALL)


def register_fonts() -> dict[str, str]:
    windows_fonts = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    candidates = {
        "body": windows_fonts / "arial.ttf",
        "bold": windows_fonts / "arialbd.ttf",
        "italic": windows_fonts / "ariali.ttf",
        "code": windows_fonts / "consola.ttf",
        "code_bold": windows_fonts / "consolab.ttf",
    }
    missing = [str(path) for path in candidates.values() if not path.exists()]
    if missing:
        raise SystemExit("Required Unicode fonts are missing: " + ", ".join(missing))

    names = {
        "body": "SaigonArial",
        "bold": "SaigonArialBold",
        "italic": "SaigonArialItalic",
        "code": "SaigonConsolas",
        "code_bold": "SaigonConsolasBold",
    }
    for role, path in candidates.items():
        pdfmetrics.registerFont(TTFont(names[role], str(path)))
    pdfmetrics.registerFontFamily(
        names["body"],
        normal=names["body"],
        bold=names["bold"],
        italic=names["italic"],
        boldItalic=names["bold"],
    )
    return names


def make_styles(fonts: dict[str, str]) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "body": ParagraphStyle(
            "ReportBody",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=9.2,
            leading=13.2,
            textColor=INK,
            spaceAfter=5.5,
            allowWidows=0,
            allowOrphans=0,
        ),
        "heading1": ParagraphStyle(
            "Heading1",
            parent=base["Heading1"],
            fontName=fonts["bold"],
            fontSize=16,
            leading=20,
            textColor=TEAL_DARK,
            spaceBefore=12,
            spaceAfter=7,
            keepWithNext=True,
        ),
        "heading2": ParagraphStyle(
            "Heading2",
            parent=base["Heading2"],
            fontName=fonts["bold"],
            fontSize=11.8,
            leading=15,
            textColor=CORAL,
            spaceBefore=9,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "bullet": ParagraphStyle(
            "ReportBullet",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=9.1,
            leading=12.8,
            leftIndent=13,
            firstLineIndent=-8,
            bulletIndent=3,
            textColor=INK,
            spaceAfter=3,
        ),
        "note": ParagraphStyle(
            "ReportNote",
            parent=base["BodyText"],
            fontName=fonts["italic"],
            fontSize=8.8,
            leading=12.5,
            leftIndent=10,
            rightIndent=10,
            borderColor=TEAL,
            borderWidth=0,
            borderPadding=7,
            backColor=PALE,
            textColor=MUTED,
            spaceAfter=7,
        ),
        "caption": ParagraphStyle(
            "ReportCaption",
            parent=base["BodyText"],
            fontName=fonts["italic"],
            fontSize=8.2,
            leading=11,
            alignment=TA_CENTER,
            textColor=MUTED,
            spaceBefore=3,
            spaceAfter=8,
        ),
        "table": ParagraphStyle(
            "TableCell",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=7.6,
            leading=9.6,
            textColor=INK,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=base["BodyText"],
            fontName=fonts["bold"],
            fontSize=7.4,
            leading=9.2,
            textColor=WHITE,
            alignment=TA_LEFT,
        ),
        "code": ParagraphStyle(
            "ReportCode",
            parent=base["Code"],
            fontName=fonts["code"],
            fontSize=7.6,
            leading=10.2,
            textColor=INK,
        ),
        "cover_title": ParagraphStyle(
            "CoverTitle",
            parent=base["Title"],
            fontName=fonts["bold"],
            fontSize=27,
            leading=31,
            alignment=TA_LEFT,
            textColor=WHITE,
            spaceAfter=10,
        ),
        "cover_subtitle": ParagraphStyle(
            "CoverSubtitle",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=12,
            leading=17,
            textColor=WHITE,
            spaceAfter=8,
        ),
        "toc_title": ParagraphStyle(
            "ContentsTitle",
            parent=base["Heading1"],
            fontName=fonts["bold"],
            fontSize=19,
            textColor=TEAL_DARK,
            spaceAfter=12,
        ),
    }


def inline_markup(text: str, fonts: dict[str, str]) -> str:
    value = html.escape(text.strip())
    value = re.sub(
        r"`([^`]+)`",
        lambda match: f'<font name="{fonts["code"]}" color="#07545A">{match.group(1)}</font>',
        value,
    )
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", value)
    value = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<link href="\2" color="#08747C"><u>\1</u></link>',
        value,
    )
    value = re.sub(
        r"(?<![\"'=])(https?://[^\s<]+)",
        r'<link href="\1" color="#08747C"><u>\1</u></link>',
        value,
    )
    return value


def _box(
    drawing: Drawing,
    x: float,
    y: float,
    width: float,
    height: float,
    label: str,
    fonts: dict[str, str],
    fill=PALE,
) -> None:
    drawing.add(Rect(x, y, width, height, rx=4, ry=4, fillColor=fill, strokeColor=TEAL))
    lines = wrap(label, max(12, int(width / 6.3))) or [label]
    line_height = 9.5
    start_y = y + height / 2 + (len(lines) - 1) * line_height / 2 - 3
    for index, line in enumerate(lines):
        drawing.add(
            String(
                x + width / 2,
                start_y - index * line_height,
                line,
                textAnchor="middle",
                fontName=fonts["bold"],
                fontSize=7.3,
                fillColor=INK,
            )
        )


def _arrow(drawing: Drawing, x1: float, y1: float, x2: float, y2: float) -> None:
    drawing.add(Line(x1, y1, x2, y2, strokeColor=TEAL_DARK, strokeWidth=1.1))
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 5
    points = [x2, y2]
    for delta in (2.55, -2.55):
        points.extend(
            [x2 + size * math.cos(angle + delta), y2 + size * math.sin(angle + delta)]
        )
    drawing.add(Polygon(points, fillColor=TEAL_DARK, strokeColor=TEAL_DARK))


def architecture_diagram(fonts: dict[str, str]) -> Drawing:
    drawing = Drawing(CONTENT_WIDTH, 195)
    drawing.add(String(0, 181, "Application architecture", fontName=fonts["bold"], fontSize=9, fillColor=TEAL_DARK))
    _box(drawing, 10, 132, 125, 34, "User controls", fonts)
    _box(drawing, 170, 132, 145, 34, "React and Leaflet GUI", fonts)
    _box(drawing, 350, 132, 145, 34, "FastAPI service", fonts, colors.HexColor("#FCEEEA"))
    for x, label in (
        (7, "Cost and traffic profile"),
        (132, "Search algorithms"),
        (257, "Multi-location optimizer"),
        (382, "Route explanation"),
    ):
        _box(drawing, x, 65, 115, 36, label, fonts)
    _box(drawing, 174, 7, 160, 34, "Directed OSM graph", fonts, colors.HexColor("#EDF1F5"))
    _arrow(drawing, 135, 149, 170, 149)
    _arrow(drawing, 315, 149, 350, 149)
    for x in (64, 189, 314, 439):
        _arrow(drawing, 423, 132, x, 101)
    _arrow(drawing, 189, 65, 220, 41)
    _arrow(drawing, 314, 65, 270, 41)
    drawing.add(String(239, 155, "REST + WebSocket", fontName=fonts["body"], fontSize=6.8, fillColor=MUTED))
    return drawing


def search_flow_diagram(fonts: dict[str, str]) -> Drawing:
    drawing = Drawing(CONTENT_WIDTH, 405)
    drawing.add(String(0, 391, "Search request flow", fontName=fonts["bold"], fontSize=9, fillColor=TEAL_DARK))
    x, width, height = 72, 230, 30
    nodes = [
        (350, "Validate request"),
        (307, "Apply traffic profile and cost weights"),
        (264, "Initialize frontier"),
        (221, "Pop next state"),
    ]
    for y, label in nodes:
        _box(drawing, x, y, width, height, label, fonts)
    for y1, y2 in ((350, 337), (307, 294), (264, 251)):
        _arrow(drawing, x + width / 2, y1, x + width / 2, y2)

    cx, cy = x + width / 2, 169
    diamond = [cx, cy + 28, cx + 74, cy, cx, cy - 28, cx - 74, cy]
    drawing.add(Polygon(diamond, fillColor=colors.HexColor("#FCEEEA"), strokeColor=CORAL))
    drawing.add(String(cx, cy - 3, "Goal reached?", textAnchor="middle", fontName=fonts["bold"], fontSize=8, fillColor=INK))
    _arrow(drawing, cx, 221, cx, cy + 28)

    _box(drawing, 330, 154, 165, 30, "Expand directed neighbors", fonts)
    _box(drawing, 330, 99, 165, 36, "Update parent, cost, frontier, and trace", fonts)
    _arrow(drawing, cx + 74, cy, 330, 169)
    _arrow(drawing, 412, 154, 412, 135)
    drawing.add(String(303, 177, "No", fontName=fonts["bold"], fontSize=7, fillColor=CORAL))
    drawing.add(Line(495, 117, 506, 117, strokeColor=TEAL_DARK, strokeWidth=1.1))
    drawing.add(Line(506, 117, 506, 236, strokeColor=TEAL_DARK, strokeWidth=1.1))
    _arrow(drawing, 506, 236, x + width, 236)

    _box(drawing, x, 99, width, 32, "Reconstruct path and metrics", fonts)
    _box(drawing, x, 52, width, 32, "Compare a distinct alternative", fonts)
    _box(drawing, x, 5, width, 32, "Return JSON and GeoJSON", fonts, colors.HexColor("#E8F4EC"))
    _arrow(drawing, cx, cy - 28, cx, 131)
    _arrow(drawing, cx, 99, cx, 84)
    _arrow(drawing, cx, 52, cx, 37)
    drawing.add(String(cx + 8, 136, "Yes", fontName=fonts["bold"], fontSize=7, fillColor=TEAL_DARK))
    return drawing


def code_block(lines: list[str], styles: dict[str, ParagraphStyle]) -> Table:
    content = Preformatted("\n".join(lines), styles["code"])
    table = Table([[content]], colWidths=[CONTENT_WIDTH])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F6F6")),
                ("BOX", (0, 0), (-1, -1), 0.5, GRID),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def table_widths(headers: list[str]) -> list[float]:
    count = len(headers)
    joined = " ".join(headers).lower()
    if "main contribution" in joined and count == 4:
        raw = [105, 78, 250, 78]
    elif "evidence" in joined and count == 3:
        raw = [145, 280, 86]
    elif count == 2:
        raw = [185, 326]
    elif count == 7:
        raw = [78, 62, 72, 62, 70, 70, 82]
    elif count == 6:
        raw = [92, 58, 58, 58, 58, 187]
    elif count == 5:
        raw = [122, 92, 92, 92, 113]
    elif count == 4:
        raw = [92, 220, 145, 54]
    elif count == 3:
        raw = [125, 105, 281]
    else:
        raw = [CONTENT_WIDTH / count] * count
    scale = CONTENT_WIDTH / sum(raw)
    return [value * scale for value in raw]


def markdown_table(
    lines: list[str], styles: dict[str, ParagraphStyle], fonts: dict[str, str]
) -> LongTable:
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    if len(rows) > 1 and all(re.fullmatch(r":?-{3,}:?", cell) for cell in rows[1]):
        rows.pop(1)
    headers = rows[0]
    data = [
        [
            Paragraph(inline_markup(cell, fonts), styles["table_header"] if row_index == 0 else styles["table"])
            for cell in row
        ]
        for row_index, row in enumerate(rows)
    ]
    table = LongTable(data, colWidths=table_widths(headers), repeatRows=1, hAlign="LEFT")
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), TEAL_DARK),
        ("GRID", (0, 0), (-1, -1), 0.35, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4.5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for row_index in range(1, len(data)):
        if row_index % 2 == 0:
            commands.append(("BACKGROUND", (0, row_index), (-1, row_index), colors.HexColor("#F5F8F8")))
    table.setStyle(TableStyle(commands))
    return table


def image_flowable(path: Path) -> Image:
    image = Image(str(path))
    max_width = CONTENT_WIDTH
    max_height = 112 * mm
    scale = min(max_width / image.imageWidth, max_height / image.imageHeight)
    image.drawWidth = image.imageWidth * scale
    image.drawHeight = image.imageHeight * scale
    image.hAlign = "CENTER"
    return image


class ReportDocTemplate(SimpleDocTemplate):
    def afterFlowable(self, flowable) -> None:  # noqa: N802 - ReportLab callback
        if not isinstance(flowable, Paragraph):
            return
        if flowable.style.name not in {"Heading1", "Heading2"}:
            return
        level = 0 if flowable.style.name == "Heading1" else 1
        text = flowable.getPlainText()
        key = f"section-{self.seq.nextf('section')}"
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key, level=level, closed=False)
        self.notify("TOCEntry", (level, text, self.page, key))


def markdown_story(
    markdown: str,
    source_dir: Path,
    styles: dict[str, ParagraphStyle],
    fonts: dict[str, str],
) -> list:
    lines = markdown.splitlines()
    story: list = []
    paragraph_lines: list[str] = []
    first_title_skipped = False
    diagram_index = 0

    def flush_paragraph() -> None:
        if paragraph_lines:
            text = " ".join(part.strip() for part in paragraph_lines)
            story.append(Paragraph(inline_markup(text, fonts), styles["body"]))
            paragraph_lines.clear()

    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            index += 1
            continue

        fence = re.match(r"^```([^`]*)$", stripped)
        if fence:
            flush_paragraph()
            language = fence.group(1).strip().lower()
            block: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                block.append(lines[index])
                index += 1
            if language == "mermaid":
                diagram_index += 1
                story.append(architecture_diagram(fonts) if diagram_index == 1 else search_flow_diagram(fonts))
                story.append(Spacer(1, 7))
            else:
                story.append(code_block(block, styles))
                story.append(Spacer(1, 7))
            index += 1
            continue

        heading = re.match(r"^(#{1,3})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            level = len(heading.group(1))
            title = heading.group(2)
            if level == 1 and not first_title_skipped:
                first_title_skipped = True
            else:
                if level == 2 and title == "15. References":
                    story.append(PageBreak())
                style = styles["heading1"] if level == 2 else styles["heading2"]
                story.append(Paragraph(inline_markup(title, fonts), style))
            index += 1
            continue

        if stripped.startswith("|"):
            flush_paragraph()
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            story.append(markdown_table(table_lines, styles, fonts))
            story.append(Spacer(1, 8))
            continue

        image_match = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", stripped)
        if image_match:
            flush_paragraph()
            image_path = (source_dir / image_match.group(2)).resolve()
            if not image_path.is_file():
                raise SystemExit(f"Report image not found: {image_path}")
            story.append(image_flowable(image_path))
            story.append(Spacer(1, 3))
            index += 1
            continue

        bullet = re.match(r"^[-*]\s+(.+)$", stripped)
        numbered = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if bullet or numbered:
            flush_paragraph()
            marker = "bullet" if bullet else numbered.group(1) + "."
            item = (bullet or numbered).group(1 if bullet else 2)
            index += 1
            while index < len(lines):
                continuation = lines[index]
                continuation_stripped = continuation.strip()
                if not continuation_stripped:
                    break
                if re.match(r"^[-*]\s+", continuation_stripped) or re.match(
                    r"^\d+\.\s+", continuation_stripped
                ):
                    break
                if re.match(r"^(#{1,3})\s+|^```|^\||^!\[", continuation_stripped):
                    break
                item += " " + continuation_stripped
                index += 1
            bullet_text = "•" if marker == "bullet" else marker
            story.append(
                Paragraph(
                    inline_markup(item, fonts),
                    styles["bullet"],
                    bulletText=bullet_text,
                )
            )
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[1:].strip(), fonts), styles["note"]))
            index += 1
            continue

        if stripped.startswith("*") and stripped.endswith("*"):
            flush_paragraph()
            story.append(
                Paragraph(f"<i>{inline_markup(stripped[1:-1], fonts)}</i>", styles["caption"])
            )
            index += 1
            continue

        paragraph_lines.append(stripped)
        index += 1

    flush_paragraph()
    return story


def cover_story(metadata: dict, styles: dict[str, ParagraphStyle], fonts: dict[str, str]) -> list:
    stats = Table(
        [
            [
                Paragraph("<b>481</b><br/>nodes", styles["body"]),
                Paragraph("<b>995</b><br/>directed edges", styles["body"]),
                Paragraph("<b>24</b><br/>landmarks", styles["body"]),
                Paragraph("<b>6</b><br/>algorithms", styles["body"]),
            ]
        ],
        colWidths=[CONTENT_WIDTH / 4] * 4,
    )
    stats.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EAF3F3")),
                ("BOX", (0, 0), (-1, -1), 0.6, TEAL),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, GRID),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    return [
        Spacer(1, 48 * mm),
        Paragraph("SAIGON ROUTE LAB", styles["cover_title"]),
        Paragraph(
            "Tourist Route Planner for Visiting Multiple Landmarks in Ho Chi Minh City",
            styles["cover_subtitle"],
        ),
        Paragraph(
            f"Introduction to Artificial Intelligence - Lab 1<br/><b>{html.escape(metadata['group_id'])}</b>",
            styles["cover_subtitle"],
        ),
        Spacer(1, 25 * mm),
        stats,
        Spacer(1, 18 * mm),
        Paragraph(
            "Technical report: graph modeling, search algorithms, multi-location optimization, "
            "traffic-aware evaluation, and interactive visualization.",
            ParagraphStyle(
                "CoverSummary",
                parent=styles["body"],
                fontName=fonts["body"],
                fontSize=10,
                leading=15,
                textColor=MUTED,
            ),
        ),
        PageBreak(),
    ]


def page_decorator(metadata: dict, fonts: dict[str, str], draft: bool):
    def decorate(canvas, doc) -> None:
        canvas.saveState()
        width, height = A4
        if doc.page == 1:
            canvas.setFillColor(TEAL_DARK)
            canvas.rect(0, height - 128 * mm, width, 128 * mm, fill=1, stroke=0)
            canvas.setFillColor(CORAL)
            canvas.rect(0, height - 132 * mm, width, 4 * mm, fill=1, stroke=0)
        else:
            canvas.setStrokeColor(GRID)
            canvas.setLineWidth(0.5)
            canvas.line(15 * mm, height - 13 * mm, width - 15 * mm, height - 13 * mm)
            canvas.setFont(fonts["body"], 7.5)
            canvas.setFillColor(MUTED)
            canvas.drawString(15 * mm, height - 10 * mm, "Saigon Route Lab - Technical Report")
            canvas.drawRightString(width - 15 * mm, height - 10 * mm, str(metadata["group_id"]))
        canvas.setFont(fonts["body"], 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(15 * mm, 9 * mm, "Introduction to Artificial Intelligence - Lab 1")
        canvas.drawRightString(width - 15 * mm, 9 * mm, f"Page {doc.page}")
        if draft:
            canvas.saveState()
            canvas.setFillColor(colors.Color(0.8, 0.15, 0.1, alpha=0.10))
            canvas.setFont(fonts["bold"], 34)
            canvas.translate(width / 2, height / 2)
            canvas.rotate(35)
            canvas.drawCentredString(0, 0, "DRAFT - IDENTITY DATA REQUIRED")
            canvas.restoreState()
        canvas.restoreState()

    return decorate


def build_pdf(source_path: Path, output_path: Path, metadata: dict, draft: bool) -> None:
    try:
        source = source_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"Cannot read report source: {exc}") from exc
    source = apply_metadata(source, metadata)
    fonts = register_fonts()
    styles = make_styles(fonts)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = ReportDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title="Saigon Route Lab - Technical Report",
        author=str(metadata["group_id"]),
        subject="Introduction to Artificial Intelligence - Lab 1",
    )

    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(
            "TOC1",
            fontName=fonts["body"],
            fontSize=9.5,
            leading=14,
            leftIndent=0,
            firstLineIndent=0,
            textColor=INK,
            spaceBefore=3,
        ),
        ParagraphStyle(
            "TOC2",
            fontName=fonts["body"],
            fontSize=8.5,
            leading=12,
            leftIndent=14,
            firstLineIndent=0,
            textColor=MUTED,
        ),
    ]

    story = cover_story(metadata, styles, fonts)
    story.extend([Paragraph("Contents", styles["toc_title"]), toc, PageBreak()])
    story.extend(markdown_story(source, source_path.parent, styles, fonts))
    decorator = page_decorator(metadata, fonts, draft)
    doc.multiBuild(story, onFirstPage=decorator, onLaterPages=decorator)
    if not output_path.is_file() or output_path.stat().st_size < 20_000:
        raise SystemExit("Report PDF generation produced an unexpectedly small file")
    print(output_path.resolve())


def main() -> None:
    args = parse_args()
    metadata = load_metadata(args.metadata, args.draft)
    build_pdf(args.source.resolve(), args.output.resolve(), metadata, args.draft)


if __name__ == "__main__":
    main()
