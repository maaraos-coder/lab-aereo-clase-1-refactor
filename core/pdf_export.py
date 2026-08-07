"""Generador editorial de apuntes de laboratorio en PDF.

El documento NO imprime Streamlit. Extrae solo contenido académico estático de
las etapas, omite widgets/estados de sesión y compone una versión editorial A4.
"""
from __future__ import annotations

import ast
import html
import io
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)

from config.laboratorios import (
    LAB1_STAGE_TITLES, LAB2_STAGE_TITLES,
    LAB2_ACTIVE_MINUTES, LAB2_BREAK_MINUTES, LAB2_TOTAL_MINUTES,
)

COURSE_TITLE = "Curso 1 · Aislamiento acústico al ruido aéreo"
LAB_TITLES = {
    1: "Laboratorio 1 · Fundamentos del aislamiento acústico",
    2: "Laboratorio 2 · Modelos de predicción del aislamiento acústico",
}
LAB_STAGE_TITLES = {1: LAB1_STAGE_TITLES, 2: LAB2_STAGE_TITLES}

LAB2_IMAGES = {
    "panel_simple": "panel_simple_transmision_profesional.png",
    "panel_doble": "etapa4_sistema_doble_profesional.webp",
    "metalcon": "metalcon_simple_vs_doble.svg",
    "yeso_carton": "panel_simple_yeso_carton.png",
    "madera": "panel_simple_madera.png",
    "vidrio": "material_vidrio_monolitico.svg",
    "hormigon": "muro_simple_hormigon.png",
    "comparador_hormigon": "comparador_panel_hormigon.svg",
    "comparador_tabique": "comparador_tabique_doble.svg",
    "s2_punto1": "punto1_placa_masa_superficial_profesional.webp",
    "s2_punto2": "punto2_tipos_incidencia_profesional.webp",
    "s2_punto3": "punto3_rigidez_flexion_profesional.webp",
    "s2_punto4": "punto4_promedio_campo_profesional.webp",
    "s2_tau_angulo": "punto3_tau_angulo_profesional.png",
    "s2_ley_masa": "punto6_impedancia_ley_masa_profesional.png",
    "s2_frecuencia_critica": "punto7_frecuencia_critica_profesional.png",
    "s4_propiedades_placas": "etapa4_propiedades_placas_profesional.webp",
    "s4_resonancia": "etapa4_resonancia_profesional.webp",
    "s4_regiones": "etapa4_tres_regiones_profesional.webp",
    "s5_tabique_real": "etapa5_tabique_real_profesional.webp",
    "s5_ideal_vs_conectado": "etapa5_ideal_vs_conectado_profesional.webp",
    "s5_conexion_lineal_metal": "etapa5_conexion_lineal_metal_profesional.png",
    "s5_conexion_lineal_madera": "etapa5_conexion_lineal_madera_profesional.png",
    "s5_conexion_puntual": "etapa5_conexion_puntual_profesional.png",
    "s5_geometria_camara_montantes": "etapa5_geometria_camara_montantes_profesional.png",
    "stage7_espectro_a_bandas": "stage7_espectro_a_bandas.png",
    "stage7_octava_vs_tercio": "stage7_octava_vs_tercio.png",
    "stage8_airborne_rw": "stage8_airborne_rw.png",
}

WIDGET_CALLS = {
    "st.radio", "st.selectbox", "st.multiselect", "st.text_input",
    "st.text_area", "st.number_input", "st.slider", "st.button",
    "st.download_button", "st.checkbox", "st.toggle", "st.data_editor",
    "st.file_uploader", "st.metric", "st.plotly_chart", "st.pyplot",
    "st.dataframe", "st.table",
}

@dataclass
class ContentBlock:
    kind: str
    text: str = ""
    level: int = 0
    path: str = ""
    caption: str = ""
    rows: list[list[str]] = field(default_factory=list)
    tone: str = "info"


def _register_fonts() -> tuple[str, str]:
    regular_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    bold_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]
    regular = next((p for p in regular_candidates if Path(p).exists()), None)
    bold = next((p for p in bold_candidates if Path(p).exists()), None)
    if regular:
        pdfmetrics.registerFont(TTFont("DiplomaSans", regular))
    if bold:
        pdfmetrics.registerFont(TTFont("DiplomaSans-Bold", bold))
    return ("DiplomaSans" if regular else "Helvetica", "DiplomaSans-Bold" if bold else "Helvetica-Bold")


def _strip_markdown_inline(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", text)
    return text.strip()


def _clean_html(text: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</?(?:b|strong|em|i|span|div|p|h\d|small|code|section|article)[^>]*>", "", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


def _literal(node: ast.AST) -> Any:
    try:
        return ast.literal_eval(node)
    except Exception:
        if isinstance(node, ast.JoinedStr):
            parts: list[str] = []
            for value in node.values:
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    parts.append(value.value)
                elif isinstance(value, ast.FormattedValue):
                    try:
                        parts.append("{" + ast.unparse(value.value) + "}")
                    except Exception:
                        parts.append("{valor}")
            return "".join(parts)
        return None


def _has_runtime_placeholder(text: str) -> bool:
    """Detecta expresiones dinámicas de f-strings sin confundir grupos LaTeX."""
    runtime_names = (
        "selected", "score", "material", "regime", "answered", "student",
        "correct", "question", "item", "idx", "value", "result", "total",
        "wall", "window", "door", "base", "equivalent", "critical_frequency",
        "angular_frequency", "transmitted", "zone_explanations", "f0", "fl",
        "rw_value", "c_value", "ctr_value", "tau", "field_mode",
        "wr", "wc", "wt", "vr", "vc", "vt", "dr", "dc", "dtc",
        "cr", "cc", "cct", "weakest",
    )
    for content in re.findall(r"\{([^{}]+)\}", text):
        compact = content.strip()
        if compact.startswith("LAB") or "math." in compact:
            return True
        if any(ch in compact for ch in ("[", "]", ".lower", ".get", "()")):
            return True
        lowered = compact.lower()
        if any(lowered == name or lowered.startswith(name + "_") or name in lowered for name in runtime_names):
            return True
    return False


def _call_name(call: ast.Call) -> str:
    parts: list[str] = []
    obj: ast.AST = call.func
    while isinstance(obj, ast.Attribute):
        parts.append(obj.attr)
        obj = obj.value
    if isinstance(obj, ast.Name):
        parts.append(obj.id)
    return ".".join(reversed(parts))


def _parse_markdown(value: str) -> list[ContentBlock]:
    """Convierte markdown estático en bloques editoriales."""
    value = _clean_html(value)
    if not value or _has_runtime_placeholder(value):
        return []
    value = re.sub(r"```.*?```", "", value, flags=re.S)

    # Extrae ecuaciones de bloque antes de procesar párrafos.
    tokens: list[tuple[str, str]] = []
    pattern = re.compile(r"(\$\$.*?\$\$|\\\[.*?\\\])", re.S)
    pos = 0
    for match in pattern.finditer(value):
        if match.start() > pos:
            tokens.append(("text", value[pos:match.start()]))
        eq = match.group(0)
        eq = eq[2:-2] if eq.startswith("$$") else eq[2:-2]
        tokens.append(("equation", eq.strip()))
        pos = match.end()
    if pos < len(value):
        tokens.append(("text", value[pos:]))
    if not tokens:
        tokens = [("text", value)]

    blocks: list[ContentBlock] = []
    for kind, chunk in tokens:
        if kind == "equation":
            blocks.append(ContentBlock("equation", chunk))
            continue
        lines = [line.rstrip() for line in chunk.splitlines()]
        i = 0
        paragraph: list[str] = []

        def flush_paragraph() -> None:
            if paragraph:
                text = " ".join(x.strip() for x in paragraph if x.strip())
                text = _strip_markdown_inline(text)
                if text and not _has_runtime_placeholder(text):
                    blocks.append(ContentBlock("paragraph", text))
                paragraph.clear()

        while i < len(lines):
            line = lines[i].strip()
            if not line:
                flush_paragraph(); i += 1; continue
            heading = re.match(r"^(#{1,4})\s+(.+)$", line)
            if heading:
                flush_paragraph()
                blocks.append(ContentBlock("heading", _strip_markdown_inline(heading.group(2)), min(3, len(heading.group(1)))))
                i += 1; continue
            # Markdown table
            if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-+", lines[i + 1]):
                flush_paragraph()
                table_lines = [line]
                i += 2  # omite separador
                while i < len(lines) and lines[i].strip().startswith("|"):
                    table_lines.append(lines[i].strip()); i += 1
                rows = [[_strip_markdown_inline(c.strip()) for c in r.strip("|").split("|")] for r in table_lines]
                blocks.append(ContentBlock("table", rows=rows))
                continue
            bullet = re.match(r"^[-*+]\s+(.+)$", line)
            numbered = re.match(r"^\d+[.)]\s+(.+)$", line)
            if bullet or numbered:
                flush_paragraph()
                text = (bullet or numbered).group(1)
                blocks.append(ContentBlock("bullet", _strip_markdown_inline(text)))
                i += 1; continue
            paragraph.append(line)
            i += 1
        flush_paragraph()
    return blocks


class _StageExtractor(ast.NodeVisitor):
    def __init__(self, project_root: Path, lab_number: int, stage: int) -> None:
        self.blocks: list[ContentBlock] = []
        self.project_root = project_root
        self.lab_number = lab_number
        self.stage = stage

    def _append_markdown(self, value: Any) -> None:
        if isinstance(value, str):
            self.blocks.extend(_parse_markdown(value))

    def visit_If(self, node: ast.If) -> Any:
        try:
            condition = ast.unparse(node.test)
        except Exception:
            condition = ""
        # Excluye ramas docentes y estados posteriores al envío.
        if "Docente" in condition and ("role" in condition or "session_state" in condition):
            for statement in node.orelse:
                self.visit(statement)
            return
        if any(token in condition for token in ("submitted", "finished", "attempt_closed", "reviewed")):
            for statement in node.orelse:
                self.visit(statement)
            return
        for statement in node.body:
            self.visit(statement)
        for statement in node.orelse:
            self.visit(statement)

    def visit_Call(self, node: ast.Call) -> Any:
        name = _call_name(node)
        args = node.args

        if name in WIDGET_CALLS:
            return  # nunca imprimir controles

        if name == "header" and len(args) >= 3:
            purpose = _literal(args[2])
            if isinstance(purpose, str) and not _has_runtime_placeholder(purpose):
                self.blocks.append(ContentBlock("lead", _strip_markdown_inline(_clean_html(purpose))))
        elif name == "_lab2_heading" and len(args) >= 3:
            purpose = _literal(args[2])
            if isinstance(purpose, str):
                self.blocks.append(ContentBlock("lead", _strip_markdown_inline(purpose)))
        elif name == "st.markdown" and args:
            self._append_markdown(_literal(args[0]))
        elif name in {"st.write", "st.caption"} and args:
            value = _literal(args[0])
            if isinstance(value, str) and not _has_runtime_placeholder(value):
                self.blocks.append(ContentBlock("caption" if name == "st.caption" else "paragraph", _strip_markdown_inline(_clean_html(value))))
        elif name in {"st.info", "st.warning", "st.error", "st.success"} and args:
            value = _literal(args[0])
            if isinstance(value, str) and not _has_runtime_placeholder(value):
                tone = {"st.info": "info", "st.warning": "warning", "st.error": "warning", "st.success": "success"}[name]
                self.blocks.append(ContentBlock("callout", _strip_markdown_inline(_clean_html(value)), tone=tone))
        elif name == "st.latex" and args:
            value = _literal(args[0])
            if isinstance(value, str) and not _has_runtime_placeholder(value):
                self.blocks.append(ContentBlock("equation", value.strip()))
        elif name in {"student_lesson", "lesson", "full_matter"}:
            for arg in args:
                self._append_markdown(_literal(arg))
        elif name == "_lab2_plain_language_cards" and len(args) >= 3:
            labels = ["En palabras simples", "Qué observar", "Error frecuente"]
            tones = ["info", "success", "warning"]
            for label, tone, arg in zip(labels, tones, args[:3]):
                value = _literal(arg)
                if isinstance(value, str):
                    self.blocks.append(ContentBlock("callout", f"{label}: {value}", tone=tone))
        elif name in {"formative_development", "formative_numeric"} and len(args) >= 3:
            value = _literal(args[2])
            if isinstance(value, str):
                self.blocks.append(ContentBlock("question", _strip_markdown_inline(value)))
        elif name == "check":
            if len(args) >= 2:
                q = _literal(args[1])
                if isinstance(q, str):
                    self.blocks.append(ContentBlock("question", _strip_markdown_inline(q)))
            if len(args) >= 3:
                options = _literal(args[2])
                if isinstance(options, (list, tuple)):
                    for option in options:
                        if isinstance(option, str):
                            self.blocks.append(ContentBlock("option", option))
        elif name == "_lab2_image" and args:
            key = _literal(args[0])
            caption = _literal(args[1]) if len(args) > 1 else ""
            if isinstance(key, str):
                filename = LAB2_IMAGES.get(key)
                if filename:
                    path = self.project_root / "assets" / "lab2" / filename
                    if path.exists() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
                        self.blocks.append(ContentBlock("image", path=str(path), caption=str(caption or "")))
        self.generic_visit(node)


def _extract_stage_blocks(project_root: Path, module_path: Path, lab_number: int, stage: int) -> list[ContentBlock]:
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    target = f"_stage{stage}_impl"
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == target:
            extractor = _StageExtractor(project_root, lab_number, stage)
            for statement in node.body:
                extractor.visit(statement)
            blocks = extractor.blocks
            # Elimina duplicados consecutivos y fragmentos internos sin resolver.
            result: list[ContentBlock] = []
            last_key = None
            for block in blocks:
                if block.kind != "equation" and block.text and (_has_runtime_placeholder(block.text) or re.search(r"\b(session_state|selected_|idx\]|\.lower\(\))", block.text)):
                    continue
                if block.kind != "equation" and block.text and re.search(
                    r"(presiona nuevamente|resultado guardado|respuestas registradas|selecciona una alternativa|"
                    r"incorporado y guardado|puedes corregir y verificar|intento está cerrado)",
                    block.text, re.I,
                ):
                    continue
                key = (block.kind, block.text, block.path, tuple(tuple(r) for r in block.rows))
                if key == last_key:
                    continue
                result.append(block); last_key = key
            return result
    return []


def _styles():
    regular, bold = _register_fonts()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CoverKicker", parent=styles["Normal"], fontName=bold, fontSize=9, leading=12, textColor=colors.HexColor("#0B7DB7"), spaceAfter=14))
    styles.add(ParagraphStyle(name="CoverTitleX", parent=styles["Title"], fontName=bold, fontSize=24, leading=30, textColor=colors.HexColor("#123B5D"), alignment=TA_LEFT, spaceAfter=14))
    styles.add(ParagraphStyle(name="CoverSubtitleX", parent=styles["Normal"], fontName=regular, fontSize=13, leading=18, textColor=colors.HexColor("#35556F"), alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="H1X", parent=styles["Heading1"], fontName=bold, fontSize=18, leading=23, textColor=colors.HexColor("#0B5FA5"), spaceBefore=8, spaceAfter=10))
    styles.add(ParagraphStyle(name="H2X", parent=styles["Heading2"], fontName=bold, fontSize=13.5, leading=18, textColor=colors.HexColor("#126782"), spaceBefore=8, spaceAfter=6, keepWithNext=True))
    styles.add(ParagraphStyle(name="H3X", parent=styles["Heading3"], fontName=bold, fontSize=11.5, leading=15, textColor=colors.HexColor("#245A73"), spaceBefore=6, spaceAfter=4, keepWithNext=True))
    styles.add(ParagraphStyle(name="LeadX", parent=styles["BodyText"], fontName=regular, fontSize=10.2, leading=14.5, textColor=colors.HexColor("#35556F"), backColor=colors.HexColor("#EEF7FC"), borderColor=colors.HexColor("#B9DEF5"), borderWidth=.6, borderPadding=9, spaceAfter=10))
    styles.add(ParagraphStyle(name="BodyX", parent=styles["BodyText"], fontName=regular, fontSize=9.6, leading=13.7, textColor=colors.HexColor("#203447"), alignment=TA_JUSTIFY, spaceAfter=6))
    styles.add(ParagraphStyle(name="BulletX", parent=styles["BodyText"], fontName=regular, fontSize=9.4, leading=13.2, leftIndent=14, firstLineIndent=-8, textColor=colors.HexColor("#203447"), spaceAfter=3))
    styles.add(ParagraphStyle(name="OptionX", parent=styles["BodyText"], fontName=regular, fontSize=9.2, leading=12.5, leftIndent=18, firstLineIndent=-10, textColor=colors.HexColor("#34495E"), spaceAfter=2))
    styles.add(ParagraphStyle(name="QuestionX", parent=styles["BodyText"], fontName=bold, fontSize=9.6, leading=13.2, textColor=colors.HexColor("#126782"), backColor=colors.HexColor("#EEF7FC"), borderColor=colors.HexColor("#B9DEF5"), borderWidth=.5, borderPadding=7, spaceBefore=6, spaceAfter=4))
    styles.add(ParagraphStyle(name="CaptionX", parent=styles["BodyText"], fontName=regular, fontSize=7.8, leading=10, textColor=colors.HexColor("#647789"), alignment=TA_CENTER, spaceAfter=7))
    styles.add(ParagraphStyle(name="CalloutX", parent=styles["BodyText"], fontName=regular, fontSize=9.2, leading=13, textColor=colors.HexColor("#203447"), borderWidth=.6, borderPadding=8, spaceBefore=4, spaceAfter=7))
    return styles, regular, bold


def _sanitize_math(expr: str) -> str:
    expr = expr.strip().replace("\n", " ")
    expr = expr.replace("\\displaystyle", "")
    expr = expr.replace("\\text{", "\\mathrm{")
    expr = re.sub(r"\\boxed\{(.+)\}", r"\1", expr)
    return expr


def _equation_image(expr: str, fontsize: float = 14.5) -> io.BytesIO | None:
    expr = _sanitize_math(expr)
    try:
        fig = plt.figure(figsize=(8.0, 0.9), dpi=200)
        fig.patch.set_alpha(0)
        fig.text(0.5, 0.5, f"${expr}$", ha="center", va="center", fontsize=fontsize, color="#123B5D")
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", transparent=True, bbox_inches="tight", pad_inches=0.08)
        plt.close(fig); buffer.seek(0)
        return buffer
    except Exception:
        plt.close("all")
        return None


def _equation_flowables(expr: str) -> list:
    """Renderiza ecuaciones; las expresiones por casos se maquetan por líneas."""
    if "\\begin{cases}" in expr:
        before, _, rest = expr.partition("\\begin{cases}")
        body, _, _ = rest.partition("\\end{cases}")
        rows = [r.strip() for r in body.split("\\\\") if r.strip()]
        out: list = []
        if before.strip():
            b = _equation_image(before.strip() + r"\;=\;\left\{")
            if b: out.append(_scaled_image(b, max_height=1.5 * cm))
        for row in rows:
            row = row.replace("&", r"\quad")
            b = _equation_image(row, fontsize=12.5)
            if b: out.append(_scaled_image(b, max_height=1.25 * cm))
        return out
    rendered = _equation_image(expr)
    return [_scaled_image(rendered, max_height=2.3 * cm)] if rendered else []


def _scaled_image(path_or_buffer, max_width: float = 15.9 * cm, max_height: float = 9.2 * cm) -> Image:
    if isinstance(path_or_buffer, (str, Path)):
        pil = PILImage.open(path_or_buffer)
    else:
        position = path_or_buffer.tell(); pil = PILImage.open(path_or_buffer); path_or_buffer.seek(position)
    width, height = pil.size
    scale = min(max_width / width, max_height / height)
    return Image(path_or_buffer, width=width * scale, height=height * scale)


def _header_footer(canvas, doc):
    canvas.saveState(); width, height = A4
    canvas.setStrokeColor(colors.HexColor("#D8E7F2")); canvas.line(2.0 * cm, height - 1.25 * cm, width - 2.0 * cm, height - 1.25 * cm)
    canvas.setFillColor(colors.HexColor("#687B8D")); canvas.setFont("Helvetica", 7.5)
    canvas.drawString(2.0 * cm, height - 1.05 * cm, "Diplomado en Acústica Aplicada a la Edificación")
    canvas.drawRightString(width - 2.0 * cm, 0.85 * cm, f"Página {doc.page}")
    canvas.restoreState()


def _safe_paragraph(text: str, style) -> Paragraph:
    return Paragraph(html.escape(text).replace("\n", "<br/>"), style)


def _add_table(story: list, rows: list[list[str]], styles) -> None:
    if not rows: return
    width = 16.2 * cm
    cols = max(len(r) for r in rows)
    normalized = [r + [""] * (cols - len(r)) for r in rows]
    data = [[Paragraph(html.escape(c), styles["BodyX"]) for c in r] for r in normalized]
    table = Table(data, colWidths=[width / cols] * cols, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCEFFA")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0B5FA5")),
        ("FONTNAME", (0, 0), (-1, 0), "DiplomaSans-Bold"),
        ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#C8DAE7")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([table, Spacer(1, 7)])


def _add_block(story: list, block: ContentBlock, styles) -> None:
    if block.kind == "heading":
        style = styles["H2X" if block.level <= 2 else "H3X"]
        story.append(_safe_paragraph(block.text, style))
    elif block.kind == "lead":
        story.append(_safe_paragraph(block.text, styles["LeadX"]))
    elif block.kind == "equation":
        flows = _equation_flowables(block.text)
        if flows:
            story.append(KeepTogether([Spacer(1, 3), *flows, Spacer(1, 5)]))
    elif block.kind == "question":
        story.append(_safe_paragraph(block.text, styles["QuestionX"]))
    elif block.kind == "option":
        story.append(_safe_paragraph("□ " + block.text, styles["OptionX"]))
    elif block.kind == "bullet":
        story.append(_safe_paragraph("• " + block.text, styles["BulletX"]))
    elif block.kind == "caption":
        story.append(_safe_paragraph(block.text, styles["CaptionX"]))
    elif block.kind == "callout":
        bg = {"info": "#EEF7FC", "success": "#EFF9F2", "warning": "#FFF8E7"}.get(block.tone, "#EEF7FC")
        border = {"info": "#89C7EA", "success": "#93D2A2", "warning": "#F0C66A"}.get(block.tone, "#89C7EA")
        style = ParagraphStyle("tmp", parent=styles["CalloutX"], backColor=colors.HexColor(bg), borderColor=colors.HexColor(border))
        story.append(_safe_paragraph(block.text, style))
    elif block.kind == "table":
        _add_table(story, block.rows, styles)
    elif block.kind == "image" and block.path:
        try:
            image = _scaled_image(block.path)
            story.append(image)
            if block.caption:
                story.append(_safe_paragraph(block.caption, styles["CaptionX"]))
            else:
                story.append(Spacer(1, 5))
        except Exception:
            pass
    elif block.text:
        story.append(_safe_paragraph(block.text, styles["BodyX"]))


def _stage_intro_blocks(lab_number: int, stage: int) -> list[ContentBlock]:
    if lab_number == 2 and stage == 0:
        return [
            ContentBlock("callout", f"Duración total: {LAB2_TOTAL_MINUTES} minutos ({LAB2_ACTIVE_MINUTES} minutos de aprendizaje y evaluación, más {LAB2_BREAK_MINUTES} minutos de pausa).", tone="info"),
            ContentBlock("paragraph", "Ruta de aprendizaje: pérdida de transmisión; panel simple; comparación de placas; panel doble; conexiones estructurales; ventanas dobles; bandas de frecuencia; Rw, C y Ctr; evaluación de comprensión; y aplicación integradora."),
            ContentBlock("callout", "El apunte conserva el contenido técnico y las actividades. Las simulaciones, controles y resultados dinámicos se desarrollan en la aplicación interactiva.", tone="warning"),
        ]
    return []


def build_laboratory_pdf(project_root: str | Path, lab_number: int) -> bytes:
    root = Path(project_root)
    if lab_number not in (1, 2):
        raise ValueError("El laboratorio debe ser 1 o 2.")
    module_path = root / "labs" / f"laboratorio_{lab_number}.py"
    if not module_path.exists():
        raise FileNotFoundError(module_path)

    styles, _, _ = _styles(); output = io.BytesIO()
    doc = BaseDocTemplate(
        output, pagesize=A4, leftMargin=2.1 * cm, rightMargin=2.1 * cm,
        topMargin=1.65 * cm, bottomMargin=1.45 * cm,
        title=LAB_TITLES[lab_number], author="Diplomado en Acústica Aplicada a la Edificación",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=frame, onPage=_header_footer)])

    story: list = [Spacer(1, 1.1 * cm)]
    story.append(Paragraph("DIPLOMADO EN ACÚSTICA APLICADA A LA EDIFICACIÓN", styles["CoverKicker"]))
    story.append(Paragraph(html.escape(LAB_TITLES[lab_number]), styles["CoverTitleX"]))
    line = Table([[""]], colWidths=[doc.width], rowHeights=[2]); line.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0B5FA5"))]))
    story.extend([line, Spacer(1, 13), Paragraph(html.escape(COURSE_TITLE), styles["CoverSubtitleX"]), Spacer(1, 1.3 * cm)])
    story.append(Paragraph("Apunte técnico de la vista alumno. Los controles interactivos, estados de sesión, resultados variables y pautas docentes se excluyen deliberadamente.", styles["LeadX"]))
    story.append(PageBreak())

    titles = LAB_STAGE_TITLES[lab_number]
    story.append(Paragraph("Contenido", styles["H1X"]))
    for stage, (_, title) in enumerate(titles):
        story.append(Paragraph(f"Etapa {stage} · {html.escape(title)}", styles["BulletX"]))
    story.append(PageBreak())

    for stage, (_, stage_title) in enumerate(titles):
        if stage > 0:
            story.append(PageBreak())
        story.append(Paragraph(f"Etapa {stage}", styles["CoverKicker"]))
        story.append(Paragraph(html.escape(stage_title), styles["H1X"]))
        for block in _stage_intro_blocks(lab_number, stage):
            _add_block(story, block, styles)
        blocks = _extract_stage_blocks(root, module_path, lab_number, stage)
        if not blocks:
            story.append(Paragraph("Esta etapa se desarrolla principalmente mediante interacción en la aplicación.", styles["LeadX"]))
        else:
            interactive_note_added = False
            for block in blocks:
                if block.kind == "heading" and re.search(r"(laboratorio interactivo|explorador|analiza cada material|diseña|ingresa tus resultados)", block.text, re.I):
                    _add_block(story, block, styles)
                    if not interactive_note_added:
                        _add_block(story, ContentBlock("callout", "La actividad completa se realiza en la aplicación. En este apunte se conservan sus fundamentos, instrucciones y criterios de interpretación, pero no los controles ni resultados variables.", tone="info"), styles)
                        interactive_note_added = True
                    continue
                _add_block(story, block, styles)

    doc.build(story)
    return output.getvalue()
