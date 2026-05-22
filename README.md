# 🏗️ Precificador de Terrenos SP

> **"Em 3 cliques, um investidor sabe se o terreno é ouro ou cilada."**

MVP de análise imobiliária para incorporadores e investidores de São Paulo. Insira um endereço/bairro e receba análise completa de preço, potencial construtivo e riscos em segundos.

![screenshot](https://img.shields.io/badge/status-MVP-blueviolet) ![python](https://img.shields.io/badge/python-3.11+-blue) ![streamlit](https://img.shields.io/badge/streamlit-1.35-red) ![license](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Funcionalidades

| Feature | Descrição |
|---|---|
| 💰 **Preço de Mercado** | Benchmark do m² baseado em dados FIPE ZAP + IPTU SP (2024) |
| 🏗️ **Potencial Construtivo** | Andares, unidades e área construível conforme zoneamento (Plano Diretor SP) |
| 🤖 **Análise GPT-4** | Parecer detalhado, pontos positivos/negativos e veredicto: OURO / BOM NEGÓCIO / ATENÇÃO / CILADA |
| 📊 **Comparação de Mercado** | Bairros similares, transações recentes e evolução de preços |
| 🗺️ **Mapa Interativo** | Localização do terreno e região com Folium |
| 🔍 **Anúncios Reais** | Busca automática no ZAP, VivaReal e OLX via SerpAPI |
| 💼 **VGV Estimado** | Projeção financeira com custo de construção e margem bruta |

---

## 🚀 Como Rodar

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/precificador-terrenos-sp.git
cd precificador-terrenos-sp
```

### 2. Crie e ative o ambiente virtual
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o .env com suas chaves de API
```

| Variável | Onde obter | Obrigatório |
|---|---|---|
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com) | Para análise IA real |
| `SERPAPI_KEY` | [serpapi.com](https://serpapi.com) | Para anúncios reais |

> ⚡ **Modo Demo:** Sem chaves de API, o app roda em modo demo com dados simulados — ideal para apresentações!

### 5. Execute o app
```bash
streamlit run app.py
```

Acesse: **http://localhost:8501**

---

## 🗂️ Estrutura do Projeto

```
precificador/
├── app.py                    # App principal Streamlit
├── requirements.txt          # Dependências Python
├── .env.example              # Template de variáveis de ambiente
├── .streamlit/
│   └── config.toml           # Tema dark purple
├── data/
│   └── bairros_sp.py         # Base de dados: 30+ bairros de SP com preços e riscos
└── services/
    ├── ai_analyzer.py        # Integração GPT-4 para análise de terreno
    ├── calculator.py         # Calculadora de potencial construtivo (Plano Diretor SP)
    └── serp_scraper.py       # Busca de anúncios via SerpAPI
```

---

## 🏙️ Bairros Disponíveis

30+ bairros de São Paulo com dados de:
- Preço médio m² (referência FIPE ZAP 2024)
- Zoneamento (ZM, ZR1, ZR2, ZC, ZEU)
- Coeficiente de aproveitamento
- Risco de alagamento (Baixo/Médio/Alto)
- Índice de segurança (Baixo/Médio/Alto)  
- Valorização histórica anual (% a.a.)

Incluindo: Itaim Bibi, Pinheiros, Vila Madalena, Moema, Jardins, Higienópolis, Tatuapé, Mooca, Santana, e muito mais.

---

## ☁️ Deploy

### Streamlit Cloud (gratuito)
1. Faça fork deste repositório
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte seu GitHub e selecione o repositório
4. Adicione `OPENAI_API_KEY` e `SERPAPI_KEY` em **Secrets**

### Railway / Render
```bash
# Procfile (Railway)
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

---

## 🛠️ Tecnologias

- **[Streamlit](https://streamlit.io)** — Framework Python para apps de dados
- **[OpenAI GPT-4o](https://openai.com)** — Análise inteligente do investimento
- **[SerpAPI](https://serpapi.com)** — Scraping de anúncios em tempo real
- **[Plotly](https://plotly.com)** — Gráficos interativos
- **[Folium](https://folium.readthedocs.io)** — Mapas interativos
- **[Plano Diretor SP](https://gestaourbana.prefeitura.sp.gov.br)** — Base para cálculo de zoneamento

---

## 📄 Licença

MIT License — use, modifique e distribua livremente.

---

<div align="center">
Feito com ❤️ para o mercado imobiliário brasileiro 🇧🇷
</div>
