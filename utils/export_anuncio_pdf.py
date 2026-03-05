"""
Módulo para exportar análises de anúncios para PDF
Abordagem minimalista e robusta - sem multi_cell problemático.
"""

from fpdf import FPDF
from io import BytesIO
from datetime import datetime
from typing import Dict, Any

def limpar_texto_pdf(texto: str, max_len: int = 500) -> str:
    """Limpa o texto para ser compatível com PDF"""
    if not texto:
        return ""
    
    # Converter para string se não for
    texto = str(texto)
    
    # Remover caracteres especiais e emojis
    texto = texto.replace('**', '').replace('##', '').replace('###', '')
    texto = texto.replace('*', '-').replace('`', '')
    
    # Remover caracteres não-latin1
    try:
        texto = texto.encode('latin-1', 'ignore').decode('latin-1')
    except:
        texto = texto.encode('ascii', 'ignore').decode('ascii')
    
    # Limitar tamanho
    return texto[:max_len]

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
    Gera um PDF com a análise completa do anúncio.
    Abordagem minimalista usando apenas cell() para evitar problemas de espaço.
    """
    
    # Criar PDF com margens seguras
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Cores
    cor_titulo = (31, 78, 120)
    cor_texto = (0, 0, 0)
    cor_cinza = (128, 128, 128)
    
    # ========== CABEÇALHO ==========
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*cor_titulo)
    pdf.cell(0, 10, "Relatorio de Analise", ln=True, align="C")
    pdf.set_text_color(*cor_cinza)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 5, f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    pdf.ln(5)
    
    # ========== SEÇÃO 1: DADOS DO ANÚNCIO ==========
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*cor_titulo)
    pdf.cell(0, 8, "1. Informacoes do Anuncio", ln=True)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)
    
    # Função para adicionar linha de dados
    def add_data_line(label: str, value: str):
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*cor_titulo)
        pdf.cell(35, 6, label + ":", ln=False)
        
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*cor_texto)
        
        # Quebrar valor em linhas se muito longo
        valor_limpo = limpar_texto_pdf(value, 100)
        linhas_valor = quebrar_texto(valor_limpo, 70)
        
        for i, linha in enumerate(linhas_valor):
            if i == 0:
                pdf.cell(0, 6, linha, ln=True)
            else:
                pdf.cell(35, 6, "", ln=False)  # Espaço para indentação
                pdf.cell(0, 6, linha, ln=True)
        
        pdf.ln(1)
    
    # Adicionar dados
    add_data_line("Titulo", str(dados_anuncio.get('titulo', 'Nao extraido')))
    add_data_line("Preco", str(dados_anuncio.get('preco', 'Nao extraido')))
    add_data_line("Vendedor", str(dados_anuncio.get('vendedor', 'Nao extraido')))
    add_data_line("Avaliacoes", str(dados_anuncio.get('avaliacoes', 'Nao extraido')))
    add_data_line("URL", url[:80])
    
    # Descrição (se existir)
    if dados_anuncio.get('descricao'):
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*cor_titulo)
        pdf.cell(0, 6, "Descricao:", ln=True)
        
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*cor_texto)
        desc = limpar_texto_pdf(str(dados_anuncio.get('descricao')), 300)
        linhas_desc = quebrar_texto(desc, 75)
        
        for linha in linhas_desc:
            pdf.cell(0, 5, linha, ln=True)
        
        pdf.ln(2)
    
    # ========== SEÇÃO 2: ANÁLISE DA IA ==========
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*cor_titulo)
    pdf.cell(0, 8, "2. Analise Detalhada da IA", ln=True)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)
    
    # Processar análise linha por linha
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*cor_texto)
    
    linhas_analise = analise_ia.split('\n')
    
    for linha in linhas_analise:
        linha_limpa = limpar_texto_pdf(linha.strip(), 150)
        
        if not linha_limpa:
            pdf.ln(2)
            continue
        
        # Detectar títulos de seção
        if linha.startswith('##') and not linha.startswith('###'):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*cor_titulo)
            pdf.cell(0, 6, linha_limpa, ln=True)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(*cor_texto)
        # Detectar subtítulos
        elif linha.startswith('###'):
            pdf.ln(1)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(50, 50, 50)
            pdf.cell(0, 5, linha_limpa, ln=True)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(*cor_texto)
        # Linhas normais ou com lista
        else:
            # Quebrar linhas muito longas
            linhas_quebradas = quebrar_texto(linha_limpa, 80)
            for i, linha_quebrada in enumerate(linhas_quebradas):
                if i == 0 and (linha.startswith('-') or linha.startswith('*')):
                    pdf.cell(0, 4, "  - " + linha_quebrada, ln=True)
                else:
                    pdf.cell(0, 4, linha_quebrada, ln=True)
    
    # ========== RODAPÉ ==========
    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*cor_cinza)
    rodape = "Este relatorio foi gerado automaticamente. As recomendacoes devem ser validadas conforme o contexto do seu negocio."
    linhas_rodape = quebrar_texto(rodape, 85)
    for linha in linhas_rodape:
        pdf.cell(0, 3, linha, ln=True)
    
    # Gerar PDF
    output = BytesIO()
    pdf_content = pdf.output(dest='S')
    
    if isinstance(pdf_content, str):
        output.write(pdf_content.encode('latin-1'))
    else:
        output.write(pdf_content)
    
    output.seek(0)
    return output
