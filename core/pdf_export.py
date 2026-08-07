"""Exportación editorial de laboratorios a PDF.

Genera un apunte estático desde las etapas 0-10 en vista alumno. Las ecuaciones
LaTeX se rasterizan con MathText para preservar fracciones, integrales,
sumatorias, raíces, subíndices, superíndices y letras griegas.
"""
from __future__ import annotations

import ast
import html
import io
import re
from dataclasses import dataclass
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
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

COURSE_TITLE = "Curso 1 · Aislamiento acústico al ruido aéreo"
LAB_TITLES = {
    1: "Laboratorio 1 · Fundamentos del aislamiento acústico",
    2: "Laboratorio 2 · Modelos de predicción del aislamiento acústico",
}

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


@dataclass
class ContentBlock:
    kind: str
    text: str = ""
    level: int = 0
    path: str = ""
    caption: str = ""


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


def _strip_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", text)
    text = re.sub(r"(?<!_)_([^_]+)_(?!_)", r"\1", text)
    text = re.sub(r"^\s*[-*+]\s+", "• ", text, flags=re.M)
    return text


def _clean_html(text: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</?(?:b|strong|em|i|span|div|p|h\d|small|code|section|article)[^>]*>", "", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = _strip_markdown(text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


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


def _call_name(call: ast.Call) -> str:
    parts: list[str] = []
    obj: ast.AST = call.func
    while isinstance(obj, ast.Attribute):
        parts.append(obj.attr)
        obj = obj.value
    if isinstance(obj, ast.Name):
        parts.append(obj.id)
    return ".".join(reversed(parts))


class _StageExtractor(ast.NodeVisitor):
    def __init__(self, project_root: Path, lab_number: int) -> None:
        self.blocks: list[ContentBlock] = []
        self.project_root = project_root
        self.lab_number = lab_number

    def _append(self, kind: str, value: Any, level: int = 0) -> None:
        if not isinstance(value, str):
            return
        value = _clean_html(value)
        if value:
            self.blocks.append(ContentBlock(kind=kind, text=value, level=level))

    def visit_If(self, node: ast.If) -> Any:
        try:
            condition = ast.unparse(node.test)
        except Exception:
            condition = ""
        if "Docente" in condition and ("role" in condition or "session_state" in condition):
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

        if name == "header" and len(args) >= 3:
            self._append("heading", _literal(args[0]), 1)
            self._append("heading", _literal(args[1]), 2)
            self._append("paragraph", _literal(args[2]))
        elif name in {"st.markdown", "st.write", "st.info", "st.warning", "st.caption", "st.error", "st.success"} and args:
            value = _literal(args[0])
            if isinstance(value, str):
                cleaned = _clean_html(value)
                match = re.match(r"^(#{1,4})\s+(.+)$", cleaned)
                if match:
                    self._append("heading", match.group(2), min(3, len(match.group(1))))
                else:
                    self._append("paragraph", cleaned)
        elif name == "st.latex" and args:
            value = _literal(args[0])
            if isinstance(value, str):
                self.blocks.append(ContentBlock("equation", value.strip()))
        elif name in {"student_lesson", "lesson", "full_matter"}:
            for arg in args:
                value = _literal(arg)
                if isinstance(value, str) and len(value.strip()) > 2:
                    self._append("paragraph", value)
        elif name in {"formative_development", "formative_numeric"} and len(args) >= 3:
            self._append("question", _literal(args[2]))
        elif name == "check":
            if len(args) >= 2:
                self._append("question", _literal(args[1]))
            if len(args) >= 3:
                options = _literal(args[2])
                if isinstance(options, (list, tuple)):
                    for option in options:
                        self._append("bullet", option)
        elif name in {"st.radio", "st.selectbox", "st.multiselect", "st.text_input", "st.text_area", "st.number_input", "st.slider"} and args:
            self._append("question", _literal(args[0]))
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
            extractor = _StageExtractor(project_root, lab_number)
            for statement in node.body:
                extractor.visit(statement)
            return extractor.blocks
    return []


def _styles():
    regular, bold = _register_fonts()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CoverKicker", parent=styles["Normal"], fontName=bold, fontSize=9, leading=12, textColor=colors.HexColor("#0B7DB7"), spaceAfter=14))
    styles.add(ParagraphStyle(name="CoverTitleX", parent=styles["Title"], fontName=bold, fontSize=25, leading=31, textColor=colors.HexColor("#123B5D"), alignment=TA_LEFT, spaceAfter=14))
    styles.add(ParagraphStyle(name="CoverSubtitleX", parent=styles["Normal"], fontName=regular, fontSize=13, leading=18, textColor=colors.HexColor("#35556F"), alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="H1X", parent=styles["Heading1"], fontName=bold, fontSize=18, leading=23, textColor=colors.HexColor("#0B5FA5"), spaceBefore=8, spaceAfter=10))
    styles.add(ParagraphStyle(name="H2X", parent=styles["Heading2"], fontName=bold, fontSize=14, leading=18, textColor=colors.HexColor("#126782"), spaceBefore=7, spaceAfter=7))
    styles.add(ParagraphStyle(name="H3X", parent=styles["Heading3"], fontName=bold, fontSize=11.5, leading=15, textColor=colors.HexColor("#245A73"), spaceBefore=5, spaceAfter=5))
    styles.add(ParagraphStyle(name="BodyX", parent=styles["BodyText"], fontName=regular, fontSize=9.5, leading=13.5, textColor=colors.HexColor("#203447"), alignment=TA_JUSTIFY, spaceAfter=6))
    styles.add(ParagraphStyle(name="BulletX", parent=styles["BodyText"], fontName=regular, fontSize=9.3, leading=13, leftIndent=14, firstLineIndent=-8, textColor=colors.HexColor("#203447"), spaceAfter=4))
    styles.add(ParagraphStyle(name="QuestionX", parent=styles["BodyText"], fontName=bold, fontSize=9.5, leading=13, textColor=colors.HexColor("#126782"), backColor=colors.HexColor("#EEF7FC"), borderColor=colors.HexColor("#B9DEF5"), borderWidth=.5, borderPadding=7, spaceBefore=5, spaceAfter=6))
    styles.add(ParagraphStyle(name="CaptionX", parent=styles["BodyText"], fontName=regular, fontSize=8, leading=10, textColor=colors.HexColor("#647789"), alignment=TA_CENTER, spaceAfter=7))
    return styles, regular, bold


def _sanitize_math(expr: str) -> str:
    expr = expr.strip()
    expr = expr.replace("\\displaystyle", "")
    expr = expr.replace("\\begin{aligned}", "").replace("\\end{aligned}", "")
    expr = expr.replace("\\begin{array}", "").replace("\\end{array}", "")
    expr = expr.replace("&", " ")
    expr = expr.replace("\\text{", "\\mathrm{")
    expr = re.sub(r"\\boxed\{(.+)\}", r"\1", expr)
    return expr


def _equation_image(expr: str) -> io.BytesIO | None:
    expr = _sanitize_math(expr)
    try:
        fig = plt.figure(figsize=(8.0, 0.75), dpi=180)
        fig.patch.set_alpha(0)
        fig.text(0.5, 0.5, f"${expr}$", ha="center", va="center", fontsize=15, color="#123B5D")
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", transparent=True, bbox_inches="tight", pad_inches=0.08)
        plt.close(fig)
        buffer.seek(0)
        return buffer
    except Exception:
        plt.close("all")
        return None


def _scaled_image(path_or_buffer, max_width: float = 16.3 * cm, max_height: float = 10.5 * cm) -> Image:
    if isinstance(path_or_buffer, (str, Path)):
        pil = PILImage.open(path_or_buffer)
    else:
        position = path_or_buffer.tell()
        pil = PILImage.open(path_or_buffer)
        path_or_buffer.seek(position)
    width, height = pil.size
    scale = min(max_width / width, max_height / height)
    return Image(path_or_buffer, width=width * scale, height=height * scale)


def _header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#D8E7F2"))
    canvas.line(2.0 * cm, height - 1.25 * cm, width - 2.0 * cm, height - 1.25 * cm)
    canvas.setFillColor(colors.HexColor("#687B8D"))
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(2.0 * cm, height - 1.05 * cm, "Diplomado en Acústica Aplicada a la Edificación")
    canvas.drawRightString(width - 2.0 * cm, 0.85 * cm, f"Página {doc.page}")
    canvas.restoreState()


def _add_block(story: list, block: ContentBlock, styles) -> None:
    if block.kind == "heading":
        style = styles["H1X" if block.level <= 1 else "H2X" if block.level == 2 else "H3X"]
        story.append(Paragraph(html.escape(block.text), style))
    elif block.kind == "equation":
        rendered = _equation_image(block.text)
        if rendered:
            story.append(KeepTogether([Spacer(1, 4), _scaled_image(rendered, max_height=2.2 * cm), Spacer(1, 5)]))
        else:
            story.append(Paragraph(html.escape(block.text), styles["BodyX"]))
    elif block.kind == "question":
        story.append(Paragraph(html.escape(block.text).replace("\n", "<br/>"), styles["QuestionX"]))
    elif block.kind == "bullet":
        story.append(Paragraph("• " + html.escape(block.text), styles["BulletX"]))
    elif block.kind == "image" and block.path:
        try:
            elements = [_scaled_image(block.path)]
            if block.caption:
                elements.extend([Spacer(1, 3), Paragraph(html.escape(block.caption), styles["CaptionX"])])
            story.append(KeepTogether(elements))
        except Exception:
            pass
    else:
        for part in block.text.split("\n\n"):
            if part.strip():
                lines = part.splitlines()
                for line in lines:
                    clean = line.strip()
                    if not clean:
                        continue
                    if clean.startswith("• "):
                        story.append(Paragraph(html.escape(clean), styles["BulletX"]))
                    else:
                        story.append(Paragraph(html.escape(clean), styles["BodyX"]))


def build_laboratory_pdf(project_root: str | Path, lab_number: int) -> bytes:
    root = Path(project_root)
    if lab_number not in (1, 2):
        raise ValueError("El laboratorio debe ser 1 o 2.")
    module_path = root / "labs" / f"laboratorio_{lab_number}.py"
    if not module_path.exists():
        raise FileNotFoundError(module_path)

    styles, _, _ = _styles()
    output = io.BytesIO()
    doc = BaseDocTemplate(
        output,
        pagesize=A4,
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=1.65 * cm,
        bottomMargin=1.45 * cm,
        title=LAB_TITLES[lab_number],
        author="Diplomado en Acústica Aplicada a la Edificación",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=frame, onPage=_header_footer)])

    story: list = []
    story.append(Spacer(1, 1.1 * cm))
    story.append(Paragraph("DIPLOMADO EN ACÚSTICA APLICADA A LA EDIFICACIÓN", styles["CoverKicker"]))
    story.append(Paragraph(html.escape(LAB_TITLES[lab_number]), styles["CoverTitleX"]))
    line = Table([[""]], colWidths=[doc.width], rowHeights=[2])
    line.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0B5FA5"))]))
    story.extend([line, Spacer(1, 13)])
    story.append(Paragraph(html.escape(COURSE_TITLE), styles["CoverSubtitleX"]))
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph("Apunte generado desde la vista del alumno. Se excluyen los controles interactivos y las pautas reservadas al docente.", styles["BodyX"]))
    story.append(PageBreak())

    story.append(Paragraph("Contenido", styles["H1X"]))
    for stage in range(11):
        story.append(Paragraph(f"• Etapa {stage}", styles["BulletX"]))
    story.append(PageBreak())

    for stage in range(11):
        story.append(Paragraph(f"Etapa {stage}", styles["H1X"]))
        blocks = _extract_stage_blocks(root, module_path, lab_number, stage)
        if not blocks:
            story.append(Paragraph("Contenido no disponible para exportación.", styles["BodyX"]))
        else:
            for block in blocks:
                _add_block(story, block, styles)
        if stage < 10:
            story.append(PageBreak())

    doc.build(story)
    return output.getvalue()
