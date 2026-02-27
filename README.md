# Dashboard de Devoluções BlueWorks

Dashboard profissional em **Streamlit** para análise de devoluções vs vendas com dados de 180 dias.

## 📊 Funcionalidades

O dashboard oferece 6 visualizações principais:

### 1. **📈 Resumo Executivo**
- KPIs principais: Total de Vendas, Taxa de Devolução, Impacto Financeiro, Custo de Devolução
- Gráfico de tendência de devoluções por período
- Classificação de devoluções (Saudável, Crítica, Neutra)

### 2. **🎯 Análise por Período**
- Seletor de período (30, 60, 90, 120, 150, 180 dias)
- Comparação: Vendas vs Devoluções
- Análise de impacto financeiro
- Tabela completa de detalhes

### 3. **📦 SKUs em Risco**
- Top 10 SKUs por risco financeiro
- Filtro por período de análise (30 a 180 dias)
- Métricas de taxa de devolução e impacto

### 4. **🔍 Motivos de Devolução**
- Distribuição dos 11 motivos de devolução
- Gráfico de barras com percentuais
- Tabela detalhada de motivos

### 5. **🚚 Canais de Entrega**
- Análise por forma de entrega (Correios, Mercado Envios, etc.)
- Taxa de devolução por canal
- Comparação Full vs Matriz
- Impacto financeiro por canal

### 6. **💰 Impacto Financeiro**
- Top 10 SKUs por impacto financeiro
- Top 10 SKUs por taxa de devolução
- Detalhamento de perdas financeiras

## 🚀 Como Usar

### Instalação Local

1. **Clone o repositório:**
```bash
git clone https://github.com/vlima-creator/Dashboard-Devolu-o.git
cd Dashboard-Devolu-o
```

2. **Instale as dependências:**
```bash
pip install streamlit pandas openpyxl plotly numpy
```

3. **Execute o dashboard:**
```bash
streamlit run app.py
```

4. **Acesse no navegador:**
```
http://localhost:8501
```

### Deploy no Streamlit Cloud

1. **Faça push para o GitHub** (já feito ✓)

2. **Acesse [Streamlit Cloud](https://streamlit.io/cloud)**

3. **Clique em "New app"** e selecione:
   - Repository: `vlima-creator/Dashboard-Devolu-o`
   - Branch: `main`
   - Main file path: `app.py`

4. **Deploy automático!** 🎉

## 📁 Estrutura de Arquivos

```
Dashboard-Devolu-o/
├── app.py                                          # Aplicação Streamlit
├── Analise_Devolucoes_x_Vendas_BlueWorks_6m.xlsx # Dados (15 abas)
├── README.md                                       # Este arquivo
└── ... (arquivos do projeto React anterior)
```

## 📊 Dados

A planilha `Analise_Devolucoes_x_Vendas_BlueWorks_6m.xlsx` contém 15 abas:

- **Resumo_Janelas**: Métricas principais em períodos de 30-180 dias
- **Saudavel_vs_Critica_180d**: Classificação de devoluções
- **Matriz_vs_Full_180d**: Comparação de canais
- **Frete_180d**: Análise por forma de entrega
- **Motivos_180d**: Distribuição de motivos
- **Top10_Devol_Qtd_180d**: Top 10 por quantidade
- **Top10_Taxa_180d**: Top 10 por taxa
- **Top10_Perdas_180d**: Top 10 por perdas financeiras
- **Top10_Risco_180d**: Top 10 por risco
- **Risco_SKU_30d a 180d**: Análise de risco por período

## 🛠️ Tecnologias

- **Streamlit**: Framework web para Python
- **Pandas**: Manipulação de dados
- **Plotly**: Gráficos interativos
- **openpyxl**: Leitura de arquivos Excel

## 📈 Métricas Principais

| Métrica | Valor (180 dias) |
|---------|-----------------|
| Total de Vendas | 7.857 |
| Unidades Vendidas | 8.196 |
| Total de Devoluções | 621 |
| Taxa de Devolução | 7,90% |
| Impacto Financeiro | R$ -41.690,57 |
| Custo de Devolução | R$ -11.783,66 |

## 💡 Dicas de Uso

1. **Navegação**: Use o menu lateral para trocar entre visualizações
2. **Filtros**: Selecione períodos diferentes para análise comparativa
3. **Gráficos**: Interaja com os gráficos (zoom, pan, download)
4. **Tabelas**: Ordene colunas e busque por valores
5. **Exportação**: Baixe dados em CSV diretamente das tabelas

## 📞 Suporte

Para dúvidas ou sugestões, abra uma issue no repositório.

---

**Desenvolvido com ❤️ usando Streamlit**
