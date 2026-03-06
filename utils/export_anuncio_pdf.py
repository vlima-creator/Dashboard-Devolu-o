"""
Módulo para exportar análises de anúncios para PDF
Versão polida com design profissional, amigável e suporte Unicode.
"""

import os
from fpdf import FPDF
from io import BytesIO
from datetime import datetime
from typing import Dict, Any

# Caminho para as fontes
FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'fonts')

class PDFRelatorioAnuncio(FPDF):
    """Classe customizada para gerar PDF de análise de anúncios com design profissional"""
    
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_margins(18, 18, 18)
        self.set_auto_page_break(auto=True, margin=20)
        
        # Registrar fontes Unicode (LiberationSans)
        try:
            self.add_font("Liberation", "", os.path.join(FONT_DIR, "LiberationSans-Regular.ttf"), uni=True)
            self.add_font("Liberation", "B", os.path.join(FONT_DIR, "LiberationSans-Bold.ttf"), uni=True)
            self.add_font("Liberation", "I", os.path.join(FONT_DIR, "LiberationSans-Italic.ttf"), uni=True)
            self.add_font("Liberation", "BI", os.path.join(FONT_DIR, "LiberationSans-BoldItalic.ttf"), uni=True)
            self.font_family_main = "Liberation"
        except Exception as e:
            print(f"Erro ao carregar fontes: {e}")
            self.font_family_main = "Helvetica"
        
    def header(self):
        """Cabeçalho do PDF com design profissional"""
        if self.page_no() == 1:
            # Fundo azul no topo apenas na primeira página
            self.set_fill_color(31, 78, 120)
            self.rect(0, 0, 210, 45, 'F')
            
            # Título principal
            self.set_font(self.font_family_main, "B", 26)
            self.set_text_color(255, 255, 255)
            self.set_xy(18, 12)
            self.cell(0, 12, "Relatório de Análise", ln=True)
            
            # Subtítulo
            self.set_font(self.font_family_main, "", 11)
            self.set_text_color(200, 220, 240)
            self.set_xy(18, 26)
            self.cell(0, 8, "Análise Estratégica de Anúncios com Inteligência Artificial", ln=True)
            
            self.set_y(50)
        else:
            # Cabeçalho simplificado para outras páginas
            self.set_fill_color(31, 78, 120)
            self.rect(0, 0, 210, 15, 'F')
            self.set_font(self.font_family_main, "B", 10)
            self.set_text_color(255, 255, 255)
            self.set_xy(18, 4)
            self.cell(0, 7, "Relatório de Análise de Anúncio", ln=False)
            self.set_x(-40)
            self.cell(22, 7, f"Página {self.page_no()}", align="R")
            self.set_y(25)
        
        # Voltar para cor normal
        self.set_text_color(0, 0, 0)
        
    def footer(self):
        """Rodapé do PDF"""
        self.set_y(-18)
        self.set_font(self.font_family_main, "", 8)
        self.set_text_color(128, 128, 128)
        
        # Linha separadora
        self.set_draw_color(220, 220, 220)
        self.line(18, self.get_y(), 192, self.get_y())
        self.ln(2)
        
        # Conteúdo do rodapé
        self.cell(0, 4, "Dashboard de Devolução - Análise Inteligente", align="L")
        self.set_x(120)
        self.cell(0, 4, f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}", align="R")

    def section_title(self, titulo: str):
        """Cria um título de seção elegante"""
        self.ln(4)
        self.set_font(self.font_family_main, "B", 14)
        self.set_text_color(31, 78, 120)
        self.cell(0, 10, titulo.upper(), ln=True)
        
        # Linha decorativa abaixo do título
        self.set_draw_color(31, 78, 120)
        self.set_line_width(0.5)
        self.line(self.get_x(), self.get_y(), self.get_x() + 30, self.get_y())
        self.set_line_width(0.2)
        self.ln(5)

    def subsection_title(self, titulo: str):
        """Cria um subtítulo de seção"""
        self.ln(2)
        self.set_fill_color(245, 247, 249)
        self.set_font(self.font_family_main, "B", 11)
        self.set_text_color(50, 100, 150)
        
        # Caixa de fundo para o subtítulo
        curr_y = self.get_y()
        self.rect(18, curr_y, 174, 8, 'F')
        self.set_xy(21, curr_y + 1)
        self.cell(0, 6, titulo, ln=True)
        self.ln(2)

def limpar_texto_pdf(texto: str) -> str:
    """Limpa o texto para ser compatível com PDF, mantendo Unicode"""
    if not texto:
        return ""
    
    texto = str(texto)
    # Remove marcações de markdown que poluem o PDF
    texto = texto.replace('**', '').replace('##', '').replace('###', '')
    texto = texto.replace('`', '').replace('*', '')
    
    return texto

def quebrar_texto(texto: str, max_chars: int = 80) -> list:
    """Quebra o texto em linhas com número máximo de caracteres"""
    linhas = []
    # Preservar quebras de linha originais
    paragrafos = texto.split('\n')
    
    for paragrafo in paragrafos:
        if not paragrafo.strip():
            linhas.append("")
            continue
            
        palavras = paragrafo.split()
        linha_atual = ""
        
        for palavra in palavras:
            if len(linha_atual) + len(palavra) + 1 <= max_chars:
                linha_atual += (" " if linha_atual else "") + palavra
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra
        
        if linha_atual:
            linhas.append(linha_atual)
    
    return linhas if linhas else [""]

def gerar_pdf_analise_anuncio(dados_anuncio: Dict[str, Any], analise_ia: str, url: str) -> BytesIO:
    """
    Gera um PDF profissional com a análise completa do anúncio.
    """
    
    pdf = PDFRelatorioAnuncio()
    pdf.add_page()
    
    # ========== RESUMO DO ANÚNCIO ==========
    # Verificar se temos dados reais além da URL
    tem_dados = any(dados_anuncio.get(k) for k in ['titulo', 'preco', 'vendedor'] if dados_anuncio.get(k) and dados_anuncio.get(k) != 'Não extraído')
    
    if tem_dados:
        pdf.section_title("Informações do Anúncio")
        
        # Grid de informações
        pdf.set_font(pdf.font_family_main, "B", 10)
        pdf.set_text_color(80, 80, 80)
        
        campos = [
            ("Título", dados_anuncio.get('titulo')),
            ("Preço", dados_anuncio.get('preco')),
            ("Vendedor", dados_anuncio.get('vendedor')),
            ("Avaliações", dados_anuncio.get('avaliacoes'))
        ]
        
        for label, valor in campos:
            if valor and valor != 'Não extraído':
                pdf.set_font(pdf.font_family_main, "B", 10)
                pdf.set_text_color(31, 78, 120)
                pdf.cell(30, 7, f"{label}:", ln=False)
                
                pdf.set_font(pdf.font_family_main, "", 10)
                pdf.set_text_color(0, 0, 0)
                
                valor_limpo = limpar_texto_pdf(str(valor))
                linhas = quebrar_texto(valor_limpo, 75)
                for i, linha in enumerate(linhas):
                    if i > 0: pdf.cell(30, 7, "", ln=False)
                    pdf.cell(0, 7, linha, ln=True)
        
        pdf.ln(3)
    
    # Link do anúncio em destaque (sempre presente)
    pdf.set_fill_color(240, 245, 255)
    pdf.set_draw_color(200, 210, 230)
    curr_y = pdf.get_y()
    pdf.rect(18, curr_y, 174, 12, 'DF')
    pdf.set_xy(22, curr_y + 3)
    
    pdf.set_font(pdf.font_family_main, "B", 9)
    pdf.set_text_color(31, 78, 120)
    pdf.cell(35, 6, "Link do Anúncio:", ln=False)
    
    pdf.set_font(pdf.font_family_main, "", 8)
    pdf.set_text_color(0, 100, 200)
    # Encurtar URL visualmente se necessário, mas manter link funcional
    url_display = url if len(url) < 85 else url[:82] + "..."
    pdf.cell(0, 6, url_display, ln=True, link=url)
    
    pdf.ln(8)
    
    # ========== ANÁLISE DETALHADA ==========
    pdf.section_title("Análise Estratégica")
    
    # Processar análise linha por linha
    linhas_analise = analise_ia.split('\n')
    
    for linha in linhas_analise:
        linha_orig = linha.strip()
        linha_limpa = limpar_texto_pdf(linha_orig)
        
        if not linha_limpa:
            pdf.ln(2)
            continue
        
        # Detectar títulos de seção (##)
        if linha_orig.startswith('##') and not linha_orig.startswith('###'):
            pdf.subsection_title(linha_limpa)
        
        # Detectar subtítulos (###)
        elif linha_orig.startswith('###'):
            pdf.ln(2)
            pdf.set_font(pdf.font_family_main, "B", 10)
            pdf.set_text_color(50, 100, 150)
            pdf.cell(0, 6, f"• {linha_limpa}", ln=True)
            pdf.ln(1)
        
        # Detectar listas numeradas (1., 2., etc)
        elif linha_limpa and linha_limpa[0].isdigit() and '.' in linha_limpa[:3]:
            pdf.set_font(pdf.font_family_main, "", 9.5)
            pdf.set_text_color(40, 40, 40)
            linhas_quebradas = quebrar_texto(linha_limpa, 82)
            for i, linha_quebrada in enumerate(linhas_quebradas):
                prefixo = "  " if i == 0 else "     "
                pdf.cell(0, 5.5, f"{prefixo}{linha_quebrada}", ln=True)
            pdf.ln(1)
        
        # Detectar listas com hífen ou asterisco
        elif linha_orig.startswith('-') or linha_orig.startswith('*'):
            pdf.set_font(pdf.font_family_main, "", 9.5)
            pdf.set_text_color(40, 40, 40)
            # Usar um bullet point real
            texto_lista = linha_limpa.lstrip('-* ').strip()
            linhas_quebradas = quebrar_texto(texto_lista, 78)
            for i, linha_quebrada in enumerate(linhas_quebradas):
                if i == 0:
                    pdf.set_text_color(31, 78, 120)
                    pdf.cell(8, 5.5, "  •", ln=False)
                    pdf.set_text_color(40, 40, 40)
                    pdf.cell(0, 5.5, linha_quebrada, ln=True)
                else:
                    pdf.cell(8, 5.5, "", ln=False)
                    pdf.cell(0, 5.5, linha_quebrada, ln=True)
            pdf.ln(1)
        
        # Texto normal
        else:
            pdf.set_font(pdf.font_family_main, "", 9.5)
            pdf.set_text_color(30, 30, 30)
            linhas_quebradas = quebrar_texto(linha_limpa, 85)
            for linha_quebrada in linhas_quebradas:
                pdf.cell(0, 5.5, linha_quebrada, ln=True)
            pdf.ln(1)
    
    # ========== NOTA FINAL ==========
    pdf.ln(10)
    pdf.set_fill_color(250, 250, 250)
    pdf.set_draw_color(230, 230, 230)
    curr_y = pdf.get_y()
    
    # Verificar se cabe na página, senão add nova
    if curr_y > 250:
        pdf.add_page()
        curr_y = pdf.get_y()

    pdf.rect(18, curr_y, 174, 20, 'DF')
    pdf.set_xy(22, curr_y + 4)
    pdf.set_font(pdf.font_family_main, "I", 8)
    pdf.set_text_color(100, 100, 100)
    
    nota = "Aviso: Este relatório foi gerado por inteligência artificial para fins de suporte à decisão. As recomendações devem ser analisadas estrategicamente considerando as particularidades do seu negócio e as políticas vigentes da plataforma."
    linhas_nota = quebrar_texto(nota, 95)
    for linha in linhas_nota:
        pdf.cell(0, 4, linha, ln=True, align="C")
    
    # Gerar PDF
    output = BytesIO()
    pdf_content = pdf.output()
    
    if isinstance(pdf_content, str):
        output.write(pdf_content.encode('utf-8'))
    else:
        output.write(pdf_content)
    
    output.seek(0)
    return output
