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
        self.set_font("Helvetica", "B", 18)
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
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(31, 78, 120)
        self.ln(4)
        self.cell(0, 7, title, ln=True)
        
        # Linha separadora
        self.set_draw_color(200, 200, 200)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(2)
    
    def subsection_title(self, title):
        """Adiciona um subtítulo"""
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(50, 50, 50)
        self.ln(1)
        self.cell(0, 5, title, ln=True)
        self.ln(1)
    
    def add_text(self, text, size=9, color=(0, 0, 0), bold=False):
        """Adiciona texto com quebra de linha automática"""
        self.set_font("Helvetica", "B" if bold else "", size)
        self.set_text_color(*color)
        # Usar cell ao invés de multi_cell para evitar problemas de espaço
        self.multi_cell(0, 4, text)
        self.ln(1)
    
    def add_info_box(self, label, value):
        """Adiciona uma caixa de informação"""
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(31, 78, 120)
        
        # Limitar o tamanho do valor para evitar overflow
        value_str = str(value)[:100]
        
        self.cell(45, 5, label + ":", ln=False)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 5, value_str)
        self.ln(0.5)

def limpar_texto(texto: str) -> str:
    """Remove caracteres especiais e emojis do texto"""
    # Remover caracteres especiais comuns
    texto = texto.replace('**', '')
    texto = texto.replace('##', '')
    texto = texto.replace('###', '')
    
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
    
    try:
        pdf = PDFRelatorioAnuncio()
        pdf.add_page()
        
        # ========== SEÇÃO 1: INFORMAÇÕES DO ANÚNCIO ==========
        pdf.section_title("Informacoes do Anuncio")
        
        # Dados do anúncio - com limite de caracteres
        pdf.add_info_box("Titulo", limpar_texto(str(dados_anuncio.get('titulo', 'Nao extraido')))[:80])
        pdf.add_info_box("Preco", limpar_texto(str(dados_anuncio.get('preco', 'Nao extraido')))[:50])
        pdf.add_info_box("Vendedor", limpar_texto(str(dados_anuncio.get('vendedor', 'Nao extraido')))[:60])
        pdf.add_info_box("Avaliacoes", limpar_texto(str(dados_anuncio.get('avaliacoes', 'Nao extraido')))[:50])
        pdf.add_info_box("URL", url[:80])
        
        # Descrição
        if dados_anuncio.get('descricao'):
            pdf.ln(2)
            pdf.subsection_title("Descricao:")
            descricao_limpa = limpar_texto(str(dados_anuncio.get('descricao')))[:300]
            pdf.add_text(descricao_limpa, size=8)
        
        # Aviso se foi bloqueado
        if dados_anuncio.get('status') == 'bloqueado':
            pdf.ln(2)
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(200, 100, 0)
            mensagem = limpar_texto(str(dados_anuncio.get('mensagem', 'Dados parcialmente extraidos')))[:100]
            pdf.multi_cell(0, 4, f"Nota: {mensagem}")
            pdf.ln(1)
        
        # ========== SEÇÃO 2: ANÁLISE DA IA ==========
        pdf.add_page()
        pdf.section_title("Analise Detalhada da IA")
        
        # Processar a análise para melhor formatação
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(0, 0, 0)
        
        # Dividir a análise em linhas e adicionar ao PDF
        linhas = analise_ia.split('\n')
        
        for linha in linhas:
            linha_limpa = limpar_texto(linha.strip())
            
            if not linha_limpa or len(linha_limpa) == 0:
                pdf.ln(1)
                continue
            
            # Limitar o tamanho da linha para evitar overflow
            linha_limpa = linha_limpa[:170]
            
            # Detectar títulos de seção
            if linha.count('#') >= 2 and not linha.count('#') >= 3:
                pdf.section_title(linha_limpa)
            # Detectar subtítulos
            elif linha.count('#') >= 3:
                pdf.subsection_title(linha_limpa)
            # Detectar listas
            elif linha_limpa.startswith('-') or linha_limpa.startswith('*'):
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(0, 4, f"  {linha_limpa}")
            # Detectar listas numeradas
            elif linha_limpa and linha_limpa[0].isdigit() and '.' in linha_limpa[:3]:
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(0, 4, f"  {linha_limpa}")
            # Texto normal
            else:
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(0, 4, linha_limpa)
        
        # ========== RODAPÉ FINAL ==========
        pdf.ln(5)
        pdf.set_font("Helvetica", "I", 7)
        pdf.set_text_color(128, 128, 128)
        pdf.multi_cell(0, 3, 
            "Este relatorio foi gerado automaticamente pela ferramenta de Analise Inteligente de Anuncios. "
            "As recomendacoes sao baseadas em analise de IA e devem ser validadas conforme o contexto especifico do seu negocio.")
        
        # Retornar o PDF como BytesIO
        output = BytesIO()
        pdf_bytes = pdf.output(dest='S').encode('latin-1') if isinstance(pdf.output(dest='S'), str) else pdf.output(dest='S')
        output.write(pdf_bytes)
        output.seek(0)
        
        return output
        
    except Exception as e:
        # Se houver erro, criar um PDF simples com a mensagem de erro
        print(f"Erro ao gerar PDF: {str(e)}")
        raise
