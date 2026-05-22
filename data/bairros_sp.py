import pandas as pd
import numpy as np
import random

# ─────────────────────────────────────────────────────────────────────────────
# Base de dados demo: bairros de São Paulo com preços médios de m² de terreno
# Fonte referência: FIPE ZAP Índices (2024), IPTU SP (dados abertos prefeitura)
# ─────────────────────────────────────────────────────────────────────────────

BAIRROS_SP = {
    # Zona Sul
    "Itaim Bibi":         {"preco_m2": 18500, "zona": "ZM",  "coef_aproveit": 4.0, "risco_alag": "Baixo",  "risco_seg": "Baixo",  "valorizacao_aa": 8.5,  "lat": -23.5874, "lon": -46.6764},
    "Moema":              {"preco_m2": 16800, "zona": "ZM",  "coef_aproveit": 4.0, "risco_alag": "Baixo",  "risco_seg": "Baixo",  "valorizacao_aa": 7.8,  "lat": -23.6019, "lon": -46.6675},
    "Vila Olímpia":       {"preco_m2": 17200, "zona": "ZM",  "coef_aproveit": 4.0, "risco_alag": "Baixo",  "risco_seg": "Baixo",  "valorizacao_aa": 9.2,  "lat": -23.5966, "lon": -46.6877},
    "Santo André":        {"preco_m2": 5200,  "zona": "ZR2", "coef_aproveit": 2.0, "risco_alag": "Médio",  "risco_seg": "Médio",  "valorizacao_aa": 5.1,  "lat": -23.6639, "lon": -46.5383},
    "Campo Belo":         {"preco_m2": 12400, "zona": "ZM",  "coef_aproveit": 4.0, "risco_alag": "Baixo",  "risco_seg": "Baixo",  "valorizacao_aa": 7.2,  "lat": -23.6205, "lon": -46.6683},
    "Saúde":              {"preco_m2": 9800,  "zona": "ZM",  "coef_aproveit": 2.5, "risco_alag": "Baixo",  "risco_seg": "Baixo",  "valorizacao_aa": 6.4,  "lat": -23.6204, "lon": -46.6300},
    "Jabaquara":          {"preco_m2": 6500,  "zona": "ZM",  "coef_aproveit": 2.5, "risco_alag": "Médio",  "risco_seg": "Médio",  "valorizacao_aa": 5.3,  "lat": -23.6608, "lon": -46.6425},

    # Zona Oeste
    "Pinheiros":          {"preco_m2": 19200, "zona": "ZM",  "coef_aproveit": 4.0, "risco_alag": "Alto",   "risco_seg": "Baixo",  "valorizacao_aa": 10.1, "lat": -23.5648, "lon": -46.6958},
    "Perdizes":           {"preco_m2": 15600, "zona": "ZM",  "coef_aproveit": 4.0, "risco_alag": "Baixo",  "risco_seg": "Baixo",  "valorizacao_aa": 8.0,  "lat": -23.5397, "lon": -46.6631},
    "Lapa":               {"preco_m2": 9400,  "zona": "ZM",  "coef_aproveit": 2.5, "risco_alag": "Alto",   "risco_seg": "Médio",  "valorizacao_aa": 6.8,  "lat": -23.5252, "lon": -46.7062},
    "Butantã":            {"preco_m2": 8200,  "zona": "ZR2", "coef_aproveit": 2.0, "risco_alag": "Médio",  "risco_seg": "Médio",  "valorizacao_aa": 5.9,  "lat": -23.5665, "lon": -46.7278},
    "Alto de Pinheiros":  {"preco_m2": 14800, "zona": "ZR1", "coef_aproveit": 1.0, "risco_alag": "Baixo",  "risco_seg": "Baixo",  "valorizacao_aa": 7.5,  "lat": -23.5481, "lon": -46.7186},
    "Vila Madalena":      {"preco_m2": 16400, "zona": "ZM",  "coef_aproveit": 4.0, "risco_alag": "Baixo",  "risco_seg": "Baixo",  "valorizacao_aa": 9.8,  "lat": -23.5555, "lon": -46.6918},

    # Zona Norte
    "Santana":            {"preco_m2": 7800,  "zona": "ZM",  "coef_aproveit": 2.5, "risco_alag": "Médio",  "risco_seg": "Médio",  "valorizacao_aa": 5.6,  "lat": -23.5007, "lon": -46.6281},
    "Tucuruvi":           {"preco_m2": 5400,  "zona": "ZR2", "coef_aproveit": 2.0, "risco_alag": "Médio",  "risco_seg": "Médio",  "valorizacao_aa": 4.8,  "lat": -23.4740, "lon": -46.6094},
    "Tremembé":           {"preco_m2": 4100,  "zona": "ZR1", "coef_aproveit": 1.0, "risco_alag": "Alto",   "risco_seg": "Alto",   "valorizacao_aa": 3.5,  "lat": -23.4353, "lon": -46.6469},
    "Casa Verde":         {"preco_m2": 5800,  "zona": "ZR2", "coef_aproveit": 2.0, "risco_alag": "Médio",  "risco_seg": "Médio",  "valorizacao_aa": 4.9,  "lat": -23.5035, "lon": -46.6581},

    # Zona Leste
    "Tatuapé":            {"preco_m2": 8600,  "zona": "ZM",  "coef_aproveit": 2.5, "risco_alag": "Médio",  "risco_seg": "Baixo",  "valorizacao_aa": 6.9,  "lat": -23.5381, "lon": -46.5762},
    "Mooca":              {"preco_m2": 7200,  "zona": "ZM",  "coef_aproveit": 2.5, "risco_alag": "Alto",   "risco_seg": "Médio",  "valorizacao_aa": 6.1,  "lat": -23.5490, "lon": -46.6008},
    "Penha":              {"preco_m2": 4800,  "zona": "ZR2", "coef_aproveit": 2.0, "risco_alag": "Médio",  "risco_seg": "Alto",   "valorizacao_aa": 4.2,  "lat": -23.5258, "lon": -46.5353},
    "Itaquera":           {"preco_m2": 3200,  "zona": "ZR2", "coef_aproveit": 2.0, "risco_alag": "Médio",  "risco_seg": "Alto",   "valorizacao_aa": 3.8,  "lat": -23.5432, "lon": -46.4581},
    "Guaianases":         {"preco_m2": 2600,  "zona": "ZR1", "coef_aproveit": 1.0, "risco_alag": "Baixo",  "risco_seg": "Alto",   "valorizacao_aa": 3.1,  "lat": -23.5412, "lon": -46.3998},

    # Centro
    "Consolação":         {"preco_m2": 11200, "zona": "ZM",  "coef_aproveit": 4.0, "risco_alag": "Baixo",  "risco_seg": "Médio",  "valorizacao_aa": 6.0,  "lat": -23.5500, "lon": -46.6575},
    "Bela Vista":         {"preco_m2": 10400, "zona": "ZM",  "coef_aproveit": 4.0, "risco_alag": "Baixo",  "risco_seg": "Médio",  "valorizacao_aa": 5.8,  "lat": -23.5580, "lon": -46.6450},
    "Liberdade":          {"preco_m2": 9200,  "zona": "ZM",  "coef_aproveit": 4.0, "risco_alag": "Baixo",  "risco_seg": "Médio",  "valorizacao_aa": 5.5,  "lat": -23.5594, "lon": -46.6353},
    "Sé":                 {"preco_m2": 7600,  "zona": "ZM",  "coef_aproveit": 4.0, "risco_alag": "Baixo",  "risco_seg": "Alto",   "valorizacao_aa": 4.5,  "lat": -23.5475, "lon": -46.6361},
    "Brás":               {"preco_m2": 6800,  "zona": "ZM",  "coef_aproveit": 2.5, "risco_alag": "Alto",   "risco_seg": "Alto",   "valorizacao_aa": 5.0,  "lat": -23.5414, "lon": -46.6178},

    # Premium
    "Jardins":            {"preco_m2": 24000, "zona": "ZR1", "coef_aproveit": 1.0, "risco_alag": "Baixo",  "risco_seg": "Baixo",  "valorizacao_aa": 7.0,  "lat": -23.5706, "lon": -46.6676},
    "Brooklin":           {"preco_m2": 14200, "zona": "ZM",  "coef_aproveit": 4.0, "risco_alag": "Baixo",  "risco_seg": "Baixo",  "valorizacao_aa": 8.8,  "lat": -23.6166, "lon": -46.6981},
    "Alphaville":         {"preco_m2": 6800,  "zona": "ZR1", "coef_aproveit": 1.0, "risco_alag": "Baixo",  "risco_seg": "Baixo",  "valorizacao_aa": 9.5,  "lat": -23.4826, "lon": -46.8524},
    "Morumbi":            {"preco_m2": 13500, "zona": "ZR1", "coef_aproveit": 1.0, "risco_alag": "Baixo",  "risco_seg": "Baixo",  "valorizacao_aa": 7.3,  "lat": -23.6183, "lon": -46.7176},
    "Higienópolis":       {"preco_m2": 17800, "zona": "ZM",  "coef_aproveit": 4.0, "risco_alag": "Baixo",  "risco_seg": "Baixo",  "valorizacao_aa": 8.1,  "lat": -23.5445, "lon": -46.6566},
}

def get_bairros_list():
    return sorted(BAIRROS_SP.keys())

def get_bairro_data(bairro: str) -> dict | None:
    return BAIRROS_SP.get(bairro)

def get_similar_bairros(bairro: str, n: int = 5) -> list[dict]:
    """Retorna bairros similares baseado em faixa de preço."""
    target = BAIRROS_SP.get(bairro)
    if not target:
        return []
    preco_alvo = target["preco_m2"]
    similares = []
    for nome, dados in BAIRROS_SP.items():
        if nome == bairro:
            continue
        diff = abs(dados["preco_m2"] - preco_alvo) / preco_alvo
        if diff < 0.35:
            similares.append({"bairro": nome, **dados, "diff_pct": diff * 100})
    similares.sort(key=lambda x: x["diff_pct"])
    return similares[:n]

def get_transacoes_recentes(bairro: str, n: int = 8) -> pd.DataFrame:
    """Gera transações simuladas para demonstração."""
    random.seed(hash(bairro) % 10000)
    base = BAIRROS_SP.get(bairro, {}).get("preco_m2", 8000)
    registros = []
    meses = ["Jan/24", "Fev/24", "Mar/24", "Abr/24", "Mai/24", "Jun/24", "Jul/24", "Ago/24"]
    for mes in meses:
        variacao = random.uniform(-0.12, 0.12)
        area = random.choice([200, 300, 400, 500, 600, 800, 1000, 1200])
        preco_m2 = int(base * (1 + variacao))
        registros.append({
            "Mês": mes,
            "Área (m²)": area,
            "Preço/m²": f"R$ {preco_m2:,.0f}",
            "Valor Total": f"R$ {(preco_m2 * area):,.0f}",
            "Tipo": random.choice(["Residencial", "Comercial", "Misto"]),
        })
    return pd.DataFrame(registros)
