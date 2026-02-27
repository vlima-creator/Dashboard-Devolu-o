# Dashboard Vendas x Devoluções

Dashboard web profissional para análise de vendas e devoluções do Mercado Livre (BR) com upload de arquivos Excel, processamento client-side e exportação de resultados.

## 🎯 Funcionalidades

### Upload e Processamento
- ✅ Upload de 2 arquivos Excel (Vendas + Devoluções)
- ✅ Validação automática de formato
- ✅ Botão "Carregar Exemplo" com dados pré-carregados
- ✅ Processamento 100% client-side (sem servidor)

### Análise de Dados
- ✅ **Resumo Executivo**: KPIs principais e qualidade do arquivo
- ✅ **Janelas de Tempo**: Análise por períodos (30, 60, 90, 120, 150, 180 dias)
- ✅ **Matriz vs Full**: Comparação de canais
- ✅ **Frete**: Análise por forma de entrega
- ✅ **Motivos**: Distribuição de motivos de devolução
- ✅ **Ads**: Análise de vendas por publicidade
- ✅ **SKUs**: Ranking de SKUs por risco
- ✅ **Simulador**: Simulação de impacto com redução de taxa

### Métricas Calculadas
- Taxa de devolução
- Impacto financeiro
- Perda total e parcial
- Classificação (Saudável/Crítica/Neutra)
- Qualidade do arquivo
- Score de risco por SKU

### Export
- ✅ Exportar resultados em XLSX
- ✅ Múltiplas abas com dados consolidados
- ✅ Dados brutos para análise adicional

## 🚀 Como Usar

### Localmente

```bash
# Instalar dependências
npm install

# Executar em desenvolvimento
npm run dev

# Build para produção
npm run build

# Preview do build
npm run preview
```

Acesse: `http://localhost:5173`

### Deploy no Vercel

#### Opção 1: Via GitHub (Recomendado)

1. Acesse [Vercel](https://vercel.com)
2. Clique em "New Project"
3. Selecione o repositório `vlima-creator/Dashboard-Devolu-o`
4. Vercel detectará automaticamente:
   - Framework: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
5. Clique em "Deploy"

#### Opção 2: Via CLI

```bash
# Instalar Vercel CLI
npm install -g vercel

# Fazer deploy
vercel

# Deploy em produção
vercel --prod
```

#### Opção 3: Automático

Cada push para `main` fará deploy automático no Vercel.

## 📁 Estrutura do Projeto

```
Dashboard-Devolu-o/
├── src/
│   ├── pages/
│   │   ├── Index.tsx          # Página de upload
│   │   └── Dashboard.tsx      # Dashboard com abas
│   ├── components/
│   │   ├── tabs/              # Componentes das 8 abas
│   │   └── ui/                # Componentes shadcn/ui
│   ├── lib/
│   │   ├── parser.ts          # Parser de Excel
│   │   ├── metricas.ts        # Cálculo de métricas
│   │   └── export.ts          # Export XLSX
│   ├── types/
│   │   └── data.ts            # Tipos TypeScript
│   └── App.tsx
├── public/
│   └── examples/              # Arquivos de exemplo
│       ├── vendas_exemplo.xlsx
│       └── devolucoes_exemplo.xlsx
├── package.json
├── tsconfig.json
├── vite.config.ts
└── vercel.json
```

## 📊 Formato dos Arquivos

### Arquivo de Vendas
Aba: `Vendas BR`

Colunas obrigatórias:
- N.º de venda
- Data da venda
- SKU
- Receita por produtos (BRL)
- Receita por envio (BRL)
- Custo de envio com base nas medidas e peso declarados
- Tarifa de venda e impostos (BRL)
- Venda por publicidade

### Arquivo de Devoluções
Abas: `devoluções vendas matriz` e `devoluções vendas full`

Colunas obrigatórias:
- N.º de venda
- Cancelamentos e reembolsos (BRL)
- Tarifa de venda e impostos (BRL)
- Custo de envio com base nas medidas e peso declarados
- Estado
- Motivo do resultado
- Forma de entrega
- Canal

## 🛠️ Tecnologias

- **React 19** + TypeScript
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI Components
- **Recharts** - Gráficos
- **XLSX** - Leitura/escrita de Excel
- **Wouter** - Roteamento

## 🔒 Privacidade

- ✅ Processamento 100% client-side
- ✅ Nenhum dado é enviado para servidor
- ✅ Nenhuma autenticação necessária
- ✅ Dados não são armazenados

## 📝 Licença

MIT

## 🤝 Contribuições

Contribuições são bem-vindas! Abra uma issue ou pull request.

---

**Desenvolvido com ❤️ para análise de Mercado Livre**
