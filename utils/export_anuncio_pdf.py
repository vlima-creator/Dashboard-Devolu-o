"""
Módulo para exportar análises de anúncios para PDF
"""

from fpdf import FPDF
from io import BytesIO
from datetime import datetime
from typing import Dict, Any

class PDFRelatorioAnuncio(FPDF):
    """Classe customizada para gerar PDF de análise de anúncios"""
    
    def __init__(self):
        super().__init__()
        self.WIDTH = 210
        self.HEIGHT = 297
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        """Cabeçalho do PDF"""
        # Logo/Título
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(31, 78, 120)  # Azul profissional
        self.cell(0, 10, "Analise de Anuncio", ln=True, align="C")
        
        # Linha separadora
        self.set_draw_color(31, 78, 120)
        self.line(15, self.get_y() + 2, 195, self.get_y() + 2)
        self.ln(8)
        
    def footer(self):
        """Rodapé do PDF"""
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Pagina {self.page_no()} | Gerado em {datetime.now().strftime('%d/%m/%Y as %H:%M:%S')}", 
                  align="C")
    
    def section_title(self, title):
        """Adiciona um título de seção"""
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(31, 78, 120)
        self.ln(5)
        self.cell(0, 8, title, ln=True)
        
        # Linha separadora
        self.set_draw_color(200, 200, 200)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(3)
    
    def subsection_title(self, title):
        """Adiciona um subtítulo"""
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(50, 50, 50)
        self.ln(2)
        self.cell(0, 6, title, ln=True)
        self.ln(1)
    
    def add_text(self, text, size=10, color=(0, 0, 0)):
        """Adiciona texto com quebra de linha automática"""
        self.set_font("Helvetica", "", size)
        self.set_text_color(*color)
        self.multi_cell(0, 5, text)
        self.ln(2)
    
    def add_info_box(self, label, value):
        """Adiciona uma caixa de informação"""
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(31, 78, 120)
        self.cell(50, 6, label + ":", ln=False)
        
        self.set_font("Helvetica", "", 9)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, str(value))
        self.ln(1)

def limpar_texto(texto: str) -> str:
    """Remove caracteres especiais e emojis do texto"""
    # Remover caracteres especiais comuns
    texto = texto.replace('**', '')
    texto = texto.replace('##', '')
    texto = texto.replace('###', '')
    texto = texto.replace('*', '-')
    
    # Remover emojis e caracteres especiais
    try:
        # Tentar codificar e decodificar apenas com caracteres ASCII
        texto = texto.encode('ascii', 'ignore').decode('ascii')
    except:
        pass
    
    return texto

def gerar_pdf_analise_anuncio(dados_anuncio: Dict[str, Any], analise_ia: str, url: str) -> BytesIO:
    """
    Gera um PDF com a análise completa do anúncio.
    
    Args:
        dados_anuncio: Dicionário com dados extraídos do anúncio
        analise_ia: Texto da análise gerada pela IA
        url: URL do anúncio
        
    Returns:
        BytesIO com o PDF gerado
    """
    
    pdf = PDFRelatorioAnuncio()
    pdf.add_page()
    
    # ========== SEÇÃO 1: INFORMAÇÕES DO ANÚNCIO ==========
    pdf.section_title("Informacoes do Anuncio")
    
    # Dados do anúncio
    pdf.add_info_box("Titulo", limpar_texto(str(dados_anuncio.get('titulo', 'Nao extraido'))))
    pdf.add_info_box("Preco", limpar_texto(str(dados_anuncio.get('preco', 'Nao extraido'))))
    pdf.add_info_box("Vendedor", limpar_texto(str(dados_anuncio.get('vendedor', 'Nao extraido'))))
    pdf.add_info_box("Avaliacoes", limpar_texto(str(dados_anuncio.get('avaliacoes', 'Nao extraido'))))
    pdf.add_info_box("URL", url)
    
    # Descrição
    if dados_anuncio.get('descricao'):
        pdf.ln(2)
        pdf.subsection_title("Descricao:")
        pdf.add_text(limpar_texto(str(dados_anuncio.get('descricao'))), size=9)
    
    # Aviso se foi bloqueado
    if dados_anuncio.get('status') == 'bloqueado':
        pdf.ln(2)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(200, 100, 0)
        pdf.multi_cell(0, 5, f"Nota: {limpar_texto(str(dados_anuncio.get('mensagem', 'Dados parcialmente extraidos')))}")
        pdf.ln(2)
    
    # ========== SEÇÃO 2: ANÁLISE DA IA ==========
    pdf.add_page()
    pdf.section_title("Analise Detalhada da IA")
    
    # Processar a análise para melhor formatação
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    
    # Dividir a análise em linhas e adicionar ao PDF
    linhas = analise_ia.split('\n')
    for linha in linhas:
        linha_limpa = limpar_texto(linha.strip())
        
        if not linha_limpa:
            pdf.ln(2)
            continue
        
        # Detectar títulos de seção (começam com ##)
        if '##' in linha and not '###' in linha:
            pdf.section_title(linha_limpa)
        # Detectar subtítulos (começam com ###)
        elif '###' in linha:
            pdf.subsection_title(linha_limpa)
        # Detectar listas com asterisco ou hífen
        elif linha_limpa.startswith('-') or linha_limpa.startswith('*'):
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 5, f"  {linha_limpa}")
        # Detectar listas numeradas
        elif linha_limpa and linha_limpa[0].isdigit() and '.' in linha_limpa[:3]:
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 5, f"  {linha_limpa}")
        # Texto normal
        else:
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 5, linha_limpa)
    
    # ========== RODAPÉ FINAL ==========
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(128, 128, 128)
    pdf.multi_cell(0, 4, 
        "Este relatorio foi gerado automaticamente pela ferramenta de Analise Inteligente de Anuncios. "
        "As recomendacoes sao baseadas em analise de IA e devem ser validadas conforme o contexto especifico do seu negocio.")
    
    # Retornar o PDF como BytesIO
    output = BytesIO()
    pdf_bytes = pdf.output(dest='S').encode('latin-1') if isinstance(pdf.output(dest='S'), str) else pdf.output(dest='S')
    output.write(pdf_bytes)
    output.seek(0)
    
    return output
