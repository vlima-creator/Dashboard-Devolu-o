"""
Módulo para exportar análises de anúncios para PDF
Versão polida com design profissional e amigável
Suporte a caracteres Unicode (UTF-8)
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
        self.set_auto_page_break(auto=True, margin=18)
        
        # Registrar fontes Unicode (LiberationSans)
        try:
            self.add_font("Liberation", "", os.path.join(FONT_DIR, "LiberationSans-Regular.ttf"), uni=True)
            self.add_font("Liberation", "B", os.path.join(FONT_DIR, "LiberationSans-Bold.ttf"), uni=True)
            self.add_font("Liberation", "I", os.path.join(FONT_DIR, "LiberationSans-Italic.ttf"), uni=True)
            self.add_font("Liberation", "BI", os.path.join(FONT_DIR, "LiberationSans-BoldItalic.ttf"), uni=True)
            self.font_family_main = "Liberation"
        except Exception as e:
            # Fallback para Helvetica se as fontes não forem encontradas
            print(f"Erro ao carregar fontes: {e}")
            self.font_family_main = "Helvetica"
        
    def header(self):
        """Cabeçalho do PDF com design profissional"""
        # Fundo azul no topo
        self.set_fill_color(31, 78, 120)
        self.rect(0, 0, 210, 35, 'F')
        
        # Título principal
        self.set_font(self.font_family_main, "B", 24)
        self.set_text_color(255, 255, 255)
        self.set_xy(18, 8)
        self.cell(0, 12, "Relatório de Análise", ln=True)
        
        # Subtítulo
        self.set_font(self.font_family_main, "", 10)
        self.set_text_color(200, 220, 240)
        self.set_xy(18, 22)
        self.cell(0, 8, "Análise Inteligente de Anúncios com IA", ln=True)
        
        # Voltar para cor normal
        self.set_text_color(0, 0, 0)
        self.ln(8)
        
    def footer(self):
        """Rodapé do PDF"""
        self.set_y(-18)
        self.set_font(self.font_family_main, "", 8)
        self.set_text_color(128, 128, 128)
        
        # Linha separadora
        self.set_draw_color(200, 200, 200)
        self.line(18, self.get_y(), 192, self.get_y())
        self.ln(2)
        
        # Conteúdo do rodapé
        self.cell(0, 4, f"Página {self.page_no()}", align="L")
        self.set_x(120)
        self.cell(0, 4, f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}", align="R")

    def section_header(self, numero: int, titulo: str, icone: str = ""):
        """Cria um cabeçalho de seção numerada com design atraente"""
        # Fundo cinza claro para a seção
        self.set_fill_color(240, 245, 250)
        self.rect(18, self.get_y(), 174, 10, 'F')
        
        # Número da seção
        self.set_font(self.font_family_main, "B", 11)
        self.set_text_color(31, 78, 120)
        self.set_xy(20, self.get_y() + 1)
        self.cell(0, 8, f"{numero}. {titulo}", ln=True)
        
        self.ln(2)

    def subsection(self, titulo: str):
        """Cria um subtítulo de subsseção"""
        self.set_font(self.font_family_main, "B", 10)
        self.set_text_color(50, 100, 150)
        self.ln(1)
        self.cell(0, 6, f"► {titulo}", ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def info_box(self, label: str, value: str):
        """Cria uma caixa de informação estilizada"""
        self.set_font(self.font_family_main, "B", 9)
        self.set_text_color(31, 78, 120)
        self.cell(40, 5, f"{label}:", ln=False)
        
        self.set_font(self.font_family_main, "", 9)
        self.set_text_color(0, 0, 0)
        
        # Quebrar valor se muito longo
        value_limpo = limpar_texto_pdf(str(value))
        linhas = quebrar_texto(value_limpo, 70)
        
        for i, linha in enumerate(linhas):
            if i == 0:
                self.cell(0, 5, linha, ln=True)
            else:
                self.cell(40, 5, "", ln=False)
                self.cell(0, 5, linha, ln=True)
        
        self.ln(0.5)

def limpar_texto_pdf(texto: str) -> str:
    """Limpa o texto para ser compatível com PDF, mantendo Unicode"""
    if not texto:
        return ""
    
    texto = str(texto)
    # Remove apenas marcações de markdown que poluem o PDF
    texto = texto.replace('**', '').replace('##', '').replace('###', '')
    texto = texto.replace('`', '').replace('*', '')
    
    return texto

def quebrar_texto(texto: str, max_chars: int = 80) -> list:
    """Quebra o texto em linhas com número máximo de caracteres"""
    linhas = []
    palavras = texto.split()
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
    
    # ========== SEÇÃO 1: INFORMAÇÕES DO ANÚNCIO ==========
    pdf.section_header(1, "Informações do Anúncio")
    
    pdf.info_box("Título", str(dados_anuncio.get('titulo', 'Não extraído')))
    pdf.info_box("Preço", str(dados_anuncio.get('preco', 'Não extraído')))
    pdf.info_box("Vendedor", str(dados_anuncio.get('vendedor', 'Não extraído')))
    pdf.info_box("Avaliações", str(dados_anuncio.get('avaliacoes', 'Não extraído')))
    pdf.info_box("URL", url[:80])
    
    if dados_anuncio.get('descricao'):
        pdf.ln(2)
        pdf.set_font(pdf.font_family_main, "B", 9)
        pdf.set_text_color(31, 78, 120)
        pdf.cell(0, 5, "Descrição Resumida:", ln=True)
        
        pdf.set_font(pdf.font_family_main, "", 8)
        pdf.set_text_color(60, 60, 60)
        desc = limpar_texto_pdf(str(dados_anuncio.get('descricao')))[:500]
        linhas_desc = quebrar_texto(desc, 75)
        
        for linha in linhas_desc:
            pdf.cell(0, 4, linha, ln=True)
        
        pdf.ln(2)
    
    # ========== SEÇÃO 2: ANÁLISE DETALHADA ==========
    pdf.add_page()
    pdf.section_header(2, "Análise Detalhada da IA")
    
    # Processar análise linha por linha
    linhas_analise = analise_ia.split('\n')
    numero_secao = 2
    
    for linha in linhas_analise:
        linha_limpa = limpar_texto_pdf(linha.strip())
        
        if not linha_limpa:
            pdf.ln(1)
            continue
        
        # Detectar títulos de seção (##)
        if linha.startswith('##') and not linha.startswith('###'):
            numero_secao += 1
            pdf.ln(2)
            pdf.set_font(pdf.font_family_main, "B", 10)
            pdf.set_text_color(31, 78, 120)
            pdf.set_fill_color(240, 245, 250)
            pdf.rect(18, pdf.get_y(), 174, 8, 'F')
            pdf.cell(0, 8, f"  {numero_secao}. {linha_limpa}", ln=True)
            pdf.ln(1)
        
        # Detectar subtítulos (###)
        elif linha.startswith('###'):
            pdf.set_font(pdf.font_family_main, "B", 9)
            pdf.set_text_color(50, 100, 150)
            pdf.ln(1)
            pdf.cell(0, 6, f"  ► {linha_limpa}", ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(0.5)
        
        # Detectar listas numeradas (1., 2., etc)
        elif linha_limpa and linha_limpa[0].isdigit() and '.' in linha_limpa[:3]:
            pdf.set_font(pdf.font_family_main, "", 8)
            pdf.set_text_color(60, 60, 60)
            linhas_quebradas = quebrar_texto(linha_limpa, 75)
            for i, linha_quebrada in enumerate(linhas_quebradas):
                if i == 0:
                    pdf.cell(0, 5, f"  {linha_quebrada}", ln=True)
                else:
                    pdf.cell(0, 5, f"     {linha_quebrada}", ln=True)
            pdf.ln(0.5)
        
        # Detectar listas com hífen ou asterisco
        elif linha_limpa.startswith('-') or linha_limpa.startswith('*'):
            pdf.set_font(pdf.font_family_main, "", 8)
            pdf.set_text_color(60, 60, 60)
            linhas_quebradas = quebrar_texto(linha_limpa.lstrip('-*').strip(), 72)
            for i, linha_quebrada in enumerate(linhas_quebradas):
                if i == 0:
                    pdf.cell(0, 5, f"  • {linha_quebrada}", ln=True)
                else:
                    pdf.cell(0, 5, f"     {linha_quebrada}", ln=True)
            pdf.ln(0.5)
        
        # Texto normal
        else:
            pdf.set_font(pdf.font_family_main, "", 8)
            pdf.set_text_color(0, 0, 0)
            linhas_quebradas = quebrar_texto(linha_limpa, 75)
            for linha_quebrada in linhas_quebradas:
                pdf.cell(0, 5, linha_quebrada, ln=True)
            pdf.ln(0.5)
    
    # ========== RODAPÉ FINAL ==========
    pdf.ln(8)
    pdf.set_font(pdf.font_family_main, "I", 7)
    pdf.set_text_color(128, 128, 128)
    
    rodape = "Este relatório foi gerado automaticamente pela ferramenta de Análise Inteligente de Anúncios. As recomendações devem ser validadas conforme o contexto específico do seu negócio."
    linhas_rodape = quebrar_texto(rodape, 85)
    for linha in linhas_rodape:
        pdf.cell(0, 3, linha, ln=True)
    
    # Gerar PDF
    output = BytesIO()
    # fpdf2 retorna bytes por padrão no output()
    pdf_content = pdf.output()
    
    if isinstance(pdf_content, str):
        output.write(pdf_content.encode('utf-8'))
    else:
        output.write(pdf_content)
    
    output.seek(0)
    return output
