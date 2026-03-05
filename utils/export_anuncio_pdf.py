"""
Módulo para exportar análises de anúncios para PDF
Abordagem ultra-robusta para evitar erros de espaço horizontal.
"""

from fpdf import FPDF
from io import BytesIO
from datetime import datetime
from typing import Dict, Any

class PDFRelatorioAnuncio(FPDF):
    """Classe customizada para gerar PDF de análise de anúncios"""
    
    def __init__(self):
        # Definir orientação Retrato, unidade mm, formato A4
        super().__init__(orientation='P', unit='mm', format='A4')
        # Definir margens fixas e seguras (20mm em cada lado)
        self.set_margins(20, 20, 20)
        self.set_auto_page_break(auto=True, margin=20)
        # Largura útil da página (A4 = 210mm - 20mm*2 = 170mm)
        self.effective_width = 170
        
    def header(self):
        """Cabeçalho do PDF"""
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(31, 78, 120)
        self.cell(0, 10, "Relatorio de Analise de Anuncio", ln=True, align="C")
        self.ln(5)
        
    def footer(self):
        """Rodapé do PDF"""
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Pagina {self.page_no()} | Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}", align="C")

def limpar_texto_pdf(texto: str) -> str:
    """Limpa o texto para ser compatível com PDF (ASCII)"""
    if not texto:
        return ""
    
    # Substituições básicas de Markdown e caracteres especiais
    texto = texto.replace('**', '').replace('##', '').replace('###', '').replace('*', '-')
    
    # Remover emojis e caracteres não-latin1
    try:
        # Tentar converter para latin-1 (padrão do FPDF) ignorando erros
        return texto.encode('latin-1', 'ignore').decode('latin-1')
    except:
        # Fallback para ASCII se latin-1 falhar
        return texto.encode('ascii', 'ignore').decode('ascii')

def gerar_pdf_analise_anuncio(dados_anuncio: Dict[str, Any], analise_ia: str, url: str) -> BytesIO:
    """
    Gera um PDF com a análise completa do anúncio usando uma abordagem simplificada e robusta.
    """
    
    pdf = PDFRelatorioAnuncio()
    pdf.add_page()
    
    # --- SEÇÃO 1: DADOS DO ANÚNCIO ---
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(31, 78, 120)
    pdf.cell(0, 8, "1. Informacoes do Anuncio", ln=True)
    pdf.set_draw_color(31, 78, 120)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(3)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(0, 0, 0)
    
    # Função auxiliar para adicionar linhas de dados
    def add_row(label, value):
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(30, 6, f"{label}:", ln=0)
        pdf.set_font("Helvetica", "", 9)
        # Usar multi_cell com largura fixa para o valor
        pdf.multi_cell(140, 6, limpar_texto_pdf(str(value)))
        pdf.ln(1)

    add_row("Titulo", dados_anuncio.get('titulo', 'Nao extraido'))
    add_row("Preco", dados_anuncio.get('preco', 'Nao extraido'))
    add_row("Vendedor", dados_anuncio.get('vendedor', 'Nao extraido'))
    add_row("Avaliacoes", dados_anuncio.get('avaliacoes', 'Nao extraido'))
    add_row("URL", url)
    
    if dados_anuncio.get('descricao'):
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 6, "Descricao Curta:", ln=True)
        pdf.set_font("Helvetica", "", 8)
        # Limitar descrição para não ocupar muito espaço no PDF
        desc = limpar_texto_pdf(str(dados_anuncio.get('descricao')))[:500]
        pdf.multi_cell(0, 5, desc)
        pdf.ln(2)

    # --- SEÇÃO 2: ANÁLISE DA IA ---
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(31, 78, 120)
    pdf.cell(0, 8, "2. Analise Detalhada da IA", ln=True)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(4)
    
    # Processar o texto da análise linha por linha
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(0, 0, 0)
    
    linhas = analise_ia.split('\n')
    for linha in linhas:
        linha_limpa = limpar_texto_pdf(linha.strip())
        if not linha_limpa:
            pdf.ln(2)
            continue
            
        # Detectar se é um título de seção (Markdown ##)
        if linha.startswith('##'):
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(31, 78, 120)
            pdf.multi_cell(0, 6, linha_limpa)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(0, 0, 0)
        # Detectar se é um subtítulo (Markdown ###)
        elif linha.startswith('###'):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(0, 5, linha_limpa)
            pdf.set_font("Helvetica", "", 9)
        # Texto normal ou lista
        else:
            # Se começar com marcador de lista, adicionar um pequeno recuo visual
            prefixo = "  " if (linha_limpa.startswith('-') or linha_limpa.startswith('*')) else ""
            pdf.multi_cell(0, 5, prefixo + linha_limpa)
            
    # Finalização
    output = BytesIO()
    # Gerar PDF como string e converter para bytes
    pdf_content = pdf.output(dest='S')
    if isinstance(pdf_content, str):
        output.write(pdf_content.encode('latin-1'))
    else:
        output.write(pdf_content)
    output.seek(0)
    
    return output
