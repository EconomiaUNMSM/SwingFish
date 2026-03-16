"""
Generador de PDFs profesionales para el sistema multiagente.
Incluye un parser de Markdown ligero que convierte la salida de los LLMs
en documentos visualmente atractivos con jerarquía tipográfica.
"""
import os
import re
from fpdf import FPDF
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════
# COLORES DEL SISTEMA DE DISEÑO
# ═══════════════════════════════════════════════════════════════════
COLORS = {
    "primary":      (0, 51, 102),       # Azul marino corporativo
    "secondary":    (41, 98, 155),       # Azul medio
    "accent":       (0, 136, 204),       # Azul claro
    "success":      (0, 128, 72),        # Verde
    "danger":       (180, 30, 30),       # Rojo
    "warning":      (200, 130, 0),       # Naranja
    "text_dark":    (30, 30, 30),        # Texto principal
    "text_medium":  (80, 80, 80),        # Texto secundario
    "text_light":   (120, 120, 120),     # Texto terciario
    "bg_light":     (245, 247, 250),     # Fondo claro
    "bg_accent":    (230, 240, 250),     # Fondo acento
    "border":       (200, 210, 220),     # Bordes
    "white":        (255, 255, 255),
}


class MarkdownPDF(FPDF):
    """
    Extensión de FPDF que renderiza Markdown básico de forma profesional.
    Soporta: **bold**, headers (#, ##, ###), listas (- y 1.), separadores (---).
    """

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    def _safe(self, text: str) -> str:
        """Convierte texto a latin-1 seguro para FPDF, reemplazando caracteres no soportados."""
        replacements = {
            '\u2013': '-', '\u2014': '--', '\u2018': "'", '\u2019': "'",
            '\u201c': '"', '\u201d': '"', '\u2022': '-', '\u2026': '...',
            '\u00b7': '-', '\u2192': '->', '\u2190': '<-', '\u2023': '>',
            '\u25cf': '*', '\u25cb': 'o', '\u2605': '*', '\u2713': 'OK',
            '\u2717': 'X', '\u00a0': ' ',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text.encode('latin-1', 'replace').decode('latin-1')

    def _render_bold_text(self, text: str, font_size: int = 10, line_height: float = 5.5,
                          color: tuple = None):
        """
        Renderiza texto con soporte para **bold** inline.
        Divide el texto por segmentos bold/non-bold y los escribe secuencialmente.
        """
        if color is None:
            color = COLORS["text_dark"]

        # Dividir por segmentos **bold**
        parts = re.split(r'(\*\*.*?\*\*)', text)
        
        for part in parts:
            if not part:
                continue
            try:
                # Si el cursor está demasiado a la derecha, saltar línea
                if self.get_x() > self.w - self.r_margin - 10:
                    self.ln(line_height)
                    self.set_x(self.l_margin)
                    
                if part.startswith('**') and part.endswith('**'):
                    clean = part[2:-2]
                    self.set_font('helvetica', 'B', font_size)
                    self.set_text_color(*color)
                    self.write(line_height, self._safe(clean))
                else:
                    self.set_font('helvetica', '', font_size)
                    self.set_text_color(*color)
                    self.write(line_height, self._safe(part))
            except Exception:
                self.ln(line_height)
                self.set_x(self.l_margin)
    def _clean_md_markers(self, text: str) -> str:
        """Limpia marcadores Markdown residuales de un texto."""
        return text.replace('**', '').replace('*', '').strip()

    def _render_paragraph(self, text: str, font_size: int = 10, line_height: float = 5.5,
                          color: tuple = None):
        """
        Renderiza un párrafo completo con soporte para **bold** inline.
        Usa multi_cell para wrapping automático correcto.
        """
        if color is None:
            color = COLORS["text_dark"]
        
        self.set_x(self.l_margin)
        
        # Si no tiene bold, usar multi_cell directamente (más limpio)
        if '**' not in text:
            self.set_font('helvetica', '', font_size)
            self.set_text_color(*color)
            self.multi_cell(0, line_height, self._safe(text))
            return
        
        # Con bold: usar write() con control de overflow
        self._render_bold_text(text, font_size, line_height, color)
        self.ln(line_height)

    def render_markdown(self, md_text: str):
        """
        Parser principal de Markdown -> PDF.
        Soporta: # ## ### #### headers, **bold**, - listas, 1. numeradas, --- separadores
        """
        lines = md_text.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].rstrip()
            
            # ── Líneas vacías ──
            if not line.strip():
                self.ln(3)
                i += 1
                continue
            
            # ── Separadores (--- o ===) ──
            if re.match(r'^[-=]{3,}$', line.strip()):
                self.ln(2)
                self.set_draw_color(*COLORS["border"])
                self.set_line_width(0.3)
                y = self.get_y()
                self.line(self.l_margin, y, self.w - self.r_margin, y)
                self.ln(4)
                i += 1
                continue
            
            # ── Headers (#### → #) orden de más específico a más general ──
            header_match = re.match(r'^(#{1,6})\s+(.*)', line)
            if header_match:
                level = len(header_match.group(1))
                header_text = self._clean_md_markers(header_match.group(2))
                
                if level == 1:
                    self.ln(6)
                    self.set_font('helvetica', 'B', 14)
                    self.set_text_color(*COLORS["primary"])
                    self.set_x(self.l_margin)
                    self.multi_cell(0, 8, self._safe(header_text))
                    self.set_draw_color(*COLORS["primary"])
                    self.set_line_width(0.7)
                    y = self.get_y()
                    self.line(self.l_margin, y, self.w - self.r_margin, y)
                    self.ln(5)
                elif level == 2:
                    self.ln(5)
                    self.set_font('helvetica', 'B', 12)
                    self.set_text_color(*COLORS["primary"])
                    self.set_x(self.l_margin)
                    self.multi_cell(0, 7, self._safe(header_text))
                    self.set_draw_color(*COLORS["accent"])
                    self.set_line_width(0.5)
                    y = self.get_y()
                    self.line(self.l_margin, y, self.l_margin + 60, y)
                    self.ln(4)
                elif level == 3:
                    self.ln(4)
                    self.set_font('helvetica', 'B', 11)
                    self.set_text_color(*COLORS["secondary"])
                    self.set_x(self.l_margin)
                    self.multi_cell(0, 6, self._safe(header_text))
                    self.ln(2)
                else:  # level 4, 5, 6
                    self.ln(3)
                    self.set_font('helvetica', 'BI', 10)
                    self.set_text_color(*COLORS["secondary"])
                    self.set_x(self.l_margin)
                    self.multi_cell(0, 6, self._safe(header_text))
                    self.ln(2)
                
                i += 1
                continue
            
            # ── Listas con viñeta (- item o * item) ──
            bullet_match = re.match(r'^(\s*)[-*]\s+(.*)', line)
            if bullet_match:
                indent = len(bullet_match.group(1))
                content = bullet_match.group(2)
                x_offset = self.l_margin + 5 + (indent * 3)
                
                # Viñeta
                self.set_font('helvetica', 'B', 10)
                self.set_text_color(*COLORS["accent"])
                self.set_x(x_offset - 4)
                self.write(5.5, self._safe("•"))
                self.set_x(x_offset)
                
                # Contenido — si es largo, usar multi_cell
                if len(content) > 80 and '**' not in content:
                    self.set_font('helvetica', '', 10)
                    self.set_text_color(*COLORS["text_dark"])
                    available_w = self.w - self.r_margin - x_offset
                    self.multi_cell(available_w, 5.5, self._safe(content))
                else:
                    self._render_bold_text(content, font_size=10, line_height=5.5)
                    self.ln(5.5)
                i += 1
                continue
            
            # ── Listas numeradas (1. item) ──
            num_match = re.match(r'^(\s*)(\d+)\.\s+(.*)', line)
            if num_match:
                indent = len(num_match.group(1))
                number = num_match.group(2)
                content = num_match.group(3)
                x_offset = self.l_margin + 5 + (indent * 3)
                
                self.set_font('helvetica', 'B', 10)
                self.set_text_color(*COLORS["primary"])
                self.set_x(x_offset - 4)
                self.write(5.5, self._safe(f"{number}."))
                self.set_x(x_offset + 3)
                
                if len(content) > 80 and '**' not in content:
                    self.set_font('helvetica', '', 10)
                    self.set_text_color(*COLORS["text_dark"])
                    available_w = self.w - self.r_margin - (x_offset + 3)
                    self.multi_cell(available_w, 5.5, self._safe(content))
                else:
                    self._render_bold_text(content, font_size=10, line_height=5.5)
                    self.ln(5.5)
                i += 1
                continue
            
            # ── Texto normal (párrafo) ──
            paragraph = []
            while i < len(lines) and lines[i].strip():
                l = lines[i].strip()
                # Detenerse si la siguiente línea es un header, lista o separador
                if (re.match(r'^#{1,6}\s+', l) or re.match(r'^[-*]\s+', l) or
                    re.match(r'^\d+\.\s+', l) or re.match(r'^[-=]{3,}$', l)):
                    break
                paragraph.append(l)
                i += 1
            
            if paragraph:
                full_text = ' '.join(paragraph)
                self._render_paragraph(full_text, font_size=10, line_height=5.5)
                self.ln(4)
                continue
            
            i += 1

    def header(self):
        """Header discreto en cada página con línea decorativa."""
        self.set_font('helvetica', 'I', 7)
        self.set_text_color(*COLORS["text_light"])
        self.cell(0, 8, self._safe('SwingFish Multiagent Analysis System'), align='L')
        self.cell(0, 8, self._safe(f'Pag. {self.page_no()}'), align='R', ln=True)
        self.set_draw_color(*COLORS["border"])
        self.set_line_width(0.2)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self):
        """Footer discreto."""
        self.set_y(-15)
        self.set_font('helvetica', 'I', 7)
        self.set_text_color(*COLORS["text_light"])
        self.cell(0, 10, self._safe(
            'Documento generado automaticamente | SwingFish AI | Confidencial'
        ), align='C')


# ═══════════════════════════════════════════════════════════════════
# GENERADOR DEL REPORTE PRINCIPAL
# ═══════════════════════════════════════════════════════════════════
class ReportGenerator:
    """
    Genera el PDF del análisis multiagente con renderizado Markdown profesional.
    Solo muestra la interpretación de cada analista (sin datos crudos).
    """

    def __init__(self, ticker: str):
        self.ticker = ticker
        self.date_str = datetime.now().strftime("%Y-%m-%d")

    def _extract_interpretation(self, combined: str) -> str:
        marker = "=== INTERPRETACIÓN DEL ANALISTA ==="
        if marker in combined:
            return combined.split(marker, 1)[1].strip()
        return combined

    def _build_cover(self, pdf: MarkdownPDF):
        """Portada corporativa."""
        pdf.add_page()
        
        # Banda superior decorativa
        pdf.set_fill_color(*COLORS["primary"])
        pdf.rect(0, 0, 210, 45, 'F')
        
        pdf.set_font('helvetica', 'B', 28)
        pdf.set_text_color(*COLORS["white"])
        pdf.set_y(12)
        pdf.cell(0, 12, "SWING TRADING", ln=True, align='C')
        pdf.set_font('helvetica', '', 16)
        pdf.cell(0, 8, "AUDIT REPORT", ln=True, align='C')
        
        # Ticker destacado
        pdf.ln(25)
        pdf.set_font('helvetica', 'B', 42)
        pdf.set_text_color(*COLORS["primary"])
        pdf.cell(0, 20, self.ticker, ln=True, align='C')
        
        # Línea decorativa
        pdf.set_draw_color(*COLORS["accent"])
        pdf.set_line_width(1)
        y = pdf.get_y() + 3
        pdf.line(70, y, 140, y)
        pdf.ln(12)
        
        # Metadata
        pdf.set_font('helvetica', '', 11)
        pdf.set_text_color(*COLORS["text_medium"])
        pdf.cell(0, 7, f"Fecha de Generacion: {self.date_str}", ln=True, align='C')
        pdf.cell(0, 7, "Motor: LangGraph Multiagent + GPT-4o / GPT-4o-mini", ln=True, align='C')
        pdf.ln(15)
        
        # Descripción
        pdf.set_font('helvetica', 'I', 10)
        pdf.set_text_color(*COLORS["text_medium"])
        pdf.multi_cell(0, 6, pdf._safe(
            "Este documento consolida el veredicto de un comite de 6 agentes IA especializados: "
            "Tecnico, Sentimiento, Macro, Opciones, Riesgos y Fundamental. Cada agente opera con "
            "datos reales extraidos de APIs financieras (yfinance, Finviz, ForexFactory) y "
            "emite su analisis independiente antes de que el Portfolio Manager sintetice el mandato final."
        ), align='C')

    def _add_section(self, pdf: MarkdownPDF, number: int, title: str, icon: str, content: str):
        """Añade una sección con header estilizado y contenido Markdown renderizado."""
        pdf.add_page()
        
        # Badge de sección
        pdf.set_fill_color(*COLORS["primary"])
        pdf.set_font('helvetica', 'B', 18)
        pdf.set_text_color(*COLORS["white"])
        badge_w = 10
        pdf.cell(badge_w, 10, f" {number}", fill=True)
        
        # Título de sección
        pdf.set_font('helvetica', 'B', 14)
        pdf.set_text_color(*COLORS["primary"])
        pdf.cell(0, 10, f"  {icon} {title}")
        pdf.ln(12)
        
        # Línea decorativa
        pdf.set_draw_color(*COLORS["accent"])
        pdf.set_line_width(0.5)
        y = pdf.get_y()
        pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
        pdf.ln(6)
        
        # Contenido Markdown
        pdf.render_markdown(content)

    def generate_pdf(self, state: dict, output_dir: str = ".") -> str:
        pdf = MarkdownPDF()
        
        # Portada
        self._build_cover(pdf)
        
        # Secciones
        sections = [
            (1, "DECISION DEL PORTFOLIO MANAGER", "🎯", "manager_decision"),
            (2, "ANALISIS TECNICO", "📊", "technical_analysis"),
            (3, "ANALISIS DE SENTIMIENTO (NLP)", "🧠", "sentiment_analysis"),
            (4, "CONTEXTO MACROECONOMICO", "🌐", "macro_analysis"),
            (5, "ANALISIS DE RIESGOS (VaR/CVaR)", "⚠️", "risk_analysis"),
            (6, "MERCADO DE OPCIONES (DERIVADOS)", "📈", "options_analysis"),
            (7, "FUNDAMENTALES E INSIDERS", "🏛️", "fundamental_analysis"),
        ]
        
        for num, title, icon, key in sections:
            raw_combined = state.get(key, "N/A")
            if key == "manager_decision":
                content = raw_combined  # Manager no tiene separador
            else:
                content = self._extract_interpretation(raw_combined)
            self._add_section(pdf, num, title, "", content)
        
        filename = f"Analisis_Auditoria_{self.ticker}_{self.date_str}.pdf"
        filepath = os.path.join(output_dir, filename)
        pdf.output(filepath)
        return filepath


# ═══════════════════════════════════════════════════════════════════
# GENERADOR DEL AUDIT TRAIL
# ═══════════════════════════════════════════════════════════════════
class AuditReportGenerator:
    """
    Genera el PDF de auditoría: datos crudos vs interpretación LLM.
    Permite detectar alucinaciones comparando los valores reales contra
    lo que el modelo generó.
    """

    def __init__(self, ticker: str):
        self.ticker = ticker
        self.date_str = datetime.now().strftime("%Y-%m-%d")

    def _extract_parts(self, combined: str) -> tuple:
        raw_marker = "=== DATOS CRUDOS VERIFICADOS ==="
        interp_marker = "=== INTERPRETACIÓN DEL ANALISTA ==="
        
        raw_data = ""
        interpretation = ""
        
        if raw_marker in combined and interp_marker in combined:
            after_raw = combined.split(raw_marker, 1)[1]
            raw_data = after_raw.split(interp_marker, 1)[0].strip()
            interpretation = combined.split(interp_marker, 1)[1].strip()
        else:
            raw_data = "[NO SE ENCONTRO SECCION DE DATOS CRUDOS]"
            interpretation = combined
            
        return raw_data, interpretation

    def _add_audit_section(self, pdf: MarkdownPDF, agent_name: str, raw_data: str, 
                           interpretation: str):
        pdf.add_page()
        
        # Header del agente
        pdf.set_fill_color(*COLORS["primary"])
        pdf.set_font('helvetica', 'B', 13)
        pdf.set_text_color(*COLORS["white"])
        pdf.cell(0, 9, pdf._safe(f"  AUDITORIA: {agent_name}"), fill=True, ln=True)
        pdf.ln(5)
        
        # ── Sección: Datos Crudos ──
        pdf.set_fill_color(*COLORS["bg_light"])
        pdf.set_font('helvetica', 'B', 10)
        pdf.set_text_color(*COLORS["success"])
        pdf.cell(0, 7, pdf._safe("  DATOS CRUDOS VERIFICADOS (Fuente: APIs Financieras)"), 
                 fill=True, ln=True)
        pdf.ln(2)
        
        pdf.set_font('courier', '', 8)
        pdf.set_text_color(*COLORS["text_dark"])
        for line in raw_data.split('\n'):
            if line.strip():
                pdf.set_x(pdf.l_margin)  # Reset X al margen izquierdo
                try:
                    pdf.multi_cell(0, 4.5, pdf._safe(line))
                except Exception:
                    pdf.ln(4.5)  # Saltar línea si no cabe
        pdf.ln(6)
        
        # ── Sección: Interpretación LLM ──
        pdf.set_fill_color(255, 240, 240)
        pdf.set_font('helvetica', 'B', 10)
        pdf.set_text_color(*COLORS["danger"])
        pdf.cell(0, 7, pdf._safe("  INTERPRETACION DEL LLM (Verificar contra datos crudos)"), 
                 fill=True, ln=True)
        pdf.ln(2)
        
        # Renderizar la interpretación como Markdown
        pdf.render_markdown(interpretation)

    def generate_audit_pdf(self, state: dict, output_dir: str = ".") -> str:
        pdf = MarkdownPDF()
        pdf.add_page()
        
        # Portada Audit Trail
        pdf.set_fill_color(*COLORS["danger"])
        pdf.rect(0, 0, 210, 40, 'F')
        
        pdf.set_font('helvetica', 'B', 24)
        pdf.set_text_color(*COLORS["white"])
        pdf.set_y(10)
        pdf.cell(0, 12, "AUDIT TRAIL REPORT", ln=True, align='C')
        pdf.set_font('helvetica', '', 12)
        pdf.cell(0, 8, pdf._safe(f"Ticker: {self.ticker} | {self.date_str}"), ln=True, align='C')
        
        pdf.ln(20)
        pdf.set_font('helvetica', '', 10)
        pdf.set_text_color(*COLORS["text_dark"])
        pdf.multi_cell(0, 6, pdf._safe(
            "PROPOSITO: Este documento permite auditar la fidelidad de cada agente LLM. "
            "Para cada analista se muestran:\n\n"
            "1. DATOS CRUDOS VERIFICADOS (verde): Numeros reales de APIs financieras. "
            "Esta es la FUENTE DE VERDAD.\n\n"
            "2. INTERPRETACION DEL LLM (rojo): Analisis generado por GPT-4o-mini. "
            "Compare los valores contra los datos crudos para detectar alucinaciones."
        ))
        
        # Auditorías por agente
        agents = [
            ("ANALISTA TECNICO", "technical_analysis"),
            ("ANALISTA DE SENTIMIENTO", "sentiment_analysis"),
            ("ANALISTA MACROECONOMICO", "macro_analysis"),
            ("ANALISTA DE RIESGOS", "risk_analysis"),
            ("ANALISTA DE OPCIONES", "options_analysis"),
            ("ANALISTA FUNDAMENTAL", "fundamental_analysis"),
        ]
        
        for agent_name, key in agents:
            combined = state.get(key, "N/A")
            raw_data, interpretation = self._extract_parts(combined)
            self._add_audit_section(pdf, agent_name, raw_data, interpretation)
        
        # Decisión del Manager
        pdf.add_page()
        pdf.set_fill_color(*COLORS["primary"])
        pdf.set_font('helvetica', 'B', 13)
        pdf.set_text_color(*COLORS["white"])
        pdf.cell(0, 9, pdf._safe("  DECISION FINAL DEL PORTFOLIO MANAGER (GPT-4o)"), 
                 fill=True, ln=True)
        pdf.ln(5)
        pdf.render_markdown(state.get("manager_decision", "N/A"))
        
        filename = f"Audit_Trail_{self.ticker}_{self.date_str}.pdf"
        filepath = os.path.join(output_dir, filename)
        pdf.output(filepath)
        return filepath
