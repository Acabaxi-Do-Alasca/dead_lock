"""Funções de formatação compartilhadas pelos geradores de documentos (.docx).

Usado por build_manual.py, build_documentacao.py e build_instalacao.py.
"""

import logging
import os
import subprocess
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Mm, Pt, RGBColor

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(DOCS_DIR)
IMG_DIR = os.path.join(DOCS_DIR, "imagens")
ENTREGA_DIR = os.path.join(PROJECT_DIR, "entrega")

sys.path.insert(0, PROJECT_DIR)

INTEGRANTES = [
    "Bruno Carvalho da Silva",
    "Leonardo Mendonça Monteiro",
    "Kelvin Ribeiro Estevam",
    "Deivid Luis Gomes Bitelli",
]
DISCIPLINA = "Fundamentos Sistemas Operacionais"
PROFESSOR = "Evandro Stevan"
DATA = "12/11/2026"

# Linhas de identificação usadas na capa de todos os documentos
CAPA_CAMPOS = [
    "Integrantes:", *INTEGRANTES, "",
    f"Disciplina: {DISCIPLINA}",
    f"Professor: {PROFESSOR}",
    f"Data: {DATA}",
]

ACCENT = RGBColor(0x1F, 0x4E, 0x5F)
GRAY = RGBColor(0x55, 0x55, 0x55)
ACCENT_HEX = "1F4E5F"

# Cores do terminal de log (mesma ideia das cores ANSI de simulation/terminal_log.py)
TERMINAL_COLORS = {
    "REQUEST": "4FC1E9", "GRANT": "8CD17D", "DENY": "F2C14E", "ROLLBACK": "F2726F",
    "RESULT": "D59BF6", "RECOVERY": "F2726F", "ABORT": "F2726F", "RELEASE": "7FA7E8",
}
TERMINAL_DEFAULT = "D4D4D4"

_fig_counter = [0]


# -- evidências geradas executando o próprio projeto ---------------------------

def capture_terminal_log_of_scenario_b():
    """Roda o Cenário B de verdade (P1 pede (1, 0) e é negado) e devolve as
    linhas exatamente como saem no terminal de log."""
    from scenarios.loader import build_engine_from_scenario
    return _capture_terminal_log(lambda: build_engine_from_scenario("B").request(1, [1, 0]))


def capture_terminal_log_of_scenario_c():
    """Roda o Cenário C de verdade (forçar deadlock -> detectar -> tratar) e
    devolve as linhas exatamente como saem no terminal de log."""
    from scenarios.loader import build_engine_from_scenario

    def run():
        engine = build_engine_from_scenario("C")
        engine.request(0, [0, 1, 0])
        engine.request(1, [0, 0, 1])
        engine.request(2, [1, 0, 0])
        engine.check_deadlock()
        engine.recover_from_deadlock()

    return _capture_terminal_log(run)


def _capture_terminal_log(run):
    from simulation.terminal_log import LOGGER_NAME, ConsoleFormatter

    lines = []

    class Collector(logging.Handler):
        def emit(self, record):
            lines.extend(self.format(record).split("\n"))

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = Collector()
    handler.setFormatter(ConsoleFormatter(use_colors=False))
    logger.addHandler(handler)
    try:
        run()
    finally:
        logger.removeHandler(handler)
    return ["-" * 78 if line and set(line) == {"-"} else line for line in lines]


def terminal_log_color(line):
    for category, hex_color in TERMINAL_COLORS.items():
        if line.startswith("[") and f"] {category} " in line:
            return hex_color
    return TERMINAL_DEFAULT


# -- documento e estilos --------------------------------------------------------

def set_cell_shading(cell, color_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color_hex)
    tcPr.append(shd)


def add_page_number_field(paragraph):
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)


def new_doc():
    _fig_counter[0] = 0
    doc = Document()

    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)

    for level, size in ((1, 18), (2, 14), (3, 12)):
        style = doc.styles[f"Heading {level}"]
        style.font.color.rgb = ACCENT
        style.font.size = Pt(size)

    footer_para = section.footer.paragraphs[0]
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_page_number_field(footer_para)

    return doc


def add_title_page(doc, title, subtitle, description, fields):
    doc.add_paragraph()
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(title)
    run.bold = True
    run.font.size = Pt(28)
    run.font.color.rgb = ACCENT

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(subtitle)
    run.font.size = Pt(16)
    run.font.color.rgb = GRAY

    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(description)
    run.italic = True
    run.font.color.rgb = GRAY

    for _ in range(6):
        doc.add_paragraph()

    for label in fields:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(label).font.color.rgb = GRAY

    doc.add_page_break()


def add_summary(doc, items):
    doc.add_heading("Sumário", level=1)
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(item)
    doc.add_page_break()


# -- blocos de conteúdo -------------------------------------------------------------

def add_heading(doc, text, level=1):
    doc.add_heading(text, level=level)


def add_para(doc, text, italic=False, bold=False, size=None):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.italic = italic
    run.bold = bold
    if size:
        run.font.size = Pt(size)
    return p


def add_bullets(doc, items, numbered=False):
    style = "List Number" if numbered else "List Bullet"
    for item in items:
        doc.add_paragraph(item, style=style)


def add_steps(doc, items):
    """Lista numerada que sempre recomeça em 1 (o estilo "List Number" do
    Word continua a contagem da lista anterior)."""
    for n, item in enumerate(items, start=1):
        p = doc.add_paragraph(f"{n}. {item}")
        p.paragraph_format.left_indent = Cm(1.0)
        p.paragraph_format.first_line_indent = Cm(-0.5)
        p.paragraph_format.space_after = Pt(2)


def add_command(doc, command):
    """Um comando de terminal em destaque (fonte monoespaçada)."""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.6)
    run = p.add_run(command)
    run.font.name = "Consolas"
    run.font.size = Pt(10.5)
    run.bold = True
    run.font.color.rgb = ACCENT
    return p


def add_image(doc, filename, caption, width_cm=15):
    _fig_counter[0] += 1
    doc.add_picture(os.path.join(IMG_DIR, filename), width=Cm(width_cm))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cap.add_run(f"Figura {_fig_counter[0]} — {caption}")
    run.italic = True
    run.font.size = Pt(9.5)
    run.font.color.rgb = GRAY


def add_table(doc, header, rows, col_widths_cm=None, font_size=None, cell_colors=None):
    """Tabela com cabeçalho escuro. `cell_colors` mapeia (linha, coluna) -> cor
    hexadecimal de fundo (linha 0 = primeira linha de dados)."""
    table = doc.add_table(rows=1, cols=len(header))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    for i, text in enumerate(header):
        hdr_cells[i].text = text
        for p in hdr_cells[i].paragraphs:
            for r in p.runs:
                r.bold = True
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                if font_size:
                    r.font.size = Pt(font_size)
        set_cell_shading(hdr_cells[i], ACCENT_HEX)
    for row_index, row in enumerate(rows):
        cells = table.add_row().cells
        for i, text in enumerate(row):
            cells[i].text = text
            if font_size:
                for p in cells[i].paragraphs:
                    for r in p.runs:
                        r.font.size = Pt(font_size)
            if cell_colors and (row_index, i) in cell_colors:
                set_cell_shading(cells[i], cell_colors[(row_index, i)])
    if col_widths_cm:
        for row in table.rows:
            for i, w in enumerate(col_widths_cm):
                row.cells[i].width = Cm(w)
    doc.add_paragraph()
    return table


def add_code_block(doc, lines, font_size=7.5, color_for_line=terminal_log_color):
    """Bloco com fundo escuro e fonte monoespaçada, imitando um terminal."""
    for line in lines:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), "1E1E1E")
        p._p.get_or_add_pPr().append(shd)
        run = p.add_run(line or " ")
        run.font.name = "Consolas"
        run.font.size = Pt(font_size)
        run.font.color.rgb = RGBColor.from_string(color_for_line(line))
    doc.add_paragraph()


def add_qa(doc, question, answer):
    p = doc.add_paragraph()
    p.add_run("P: " + question).bold = True
    doc.add_paragraph().add_run("R: " + answer)
    doc.add_paragraph()


# -- saída ----------------------------------------------------------------------------

def save_with_pdf(doc, docx_path):
    """Salva o .docx e, se o Microsoft Word estiver instalado (Windows),
    exporta também o .pdf ao lado."""
    os.makedirs(os.path.dirname(docx_path), exist_ok=True)
    doc.save(docx_path)
    print("Documento salvo em:", docx_path)

    if os.name != "nt":
        return
    pdf_path = os.path.splitext(docx_path)[0] + ".pdf"
    script = (
        "$w = New-Object -ComObject Word.Application; $w.Visible = $false; "
        f"$d = $w.Documents.Open('{docx_path}'); "
        f"$d.SaveAs([ref]'{pdf_path}', [ref]17); $d.Close(); $w.Quit()"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", script], capture_output=True, text=True
    )
    if result.returncode == 0 and os.path.exists(pdf_path):
        print("PDF salvo em:", pdf_path)
    else:
        print("Aviso: não foi possível exportar o PDF (o Microsoft Word está instalado?).")
