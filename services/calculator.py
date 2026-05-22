import math

# ─────────────────────────────────────────────────────────────────────────────
# Calculadora de Potencial Construtivo
# Baseado no Plano Diretor de São Paulo (Lei 16.050/2014)
# ─────────────────────────────────────────────────────────────────────────────

# Parâmetros por zona (simplificado para MVP)
PARAMS_ZONA = {
    "ZM":  {"max_andares": 25, "taxa_ocup": 0.70, "recuo_min": 5.0,  "nome": "Zona Mista"},
    "ZR1": {"max_andares": 3,  "taxa_ocup": 0.50, "recuo_min": 5.0,  "nome": "Zona Residencial 1"},
    "ZR2": {"max_andares": 8,  "taxa_ocup": 0.60, "recuo_min": 5.0,  "nome": "Zona Residencial 2"},
    "ZC":  {"max_andares": 20, "taxa_ocup": 0.80, "recuo_min": 3.0,  "nome": "Zona Comercial"},
    "ZEU": {"max_andares": 25, "taxa_ocup": 0.70, "recuo_min": 5.0,  "nome": "Zona de Eixo Urbano"},
}

def calcular_potencial_construtivo(area_terreno: float, zona: str, coef_aproveit: float) -> dict:
    """
    Calcula o potencial construtivo do terreno conforme zoneamento.
    
    Returns:
        dict com: area_construivel, max_andares, unidades_estimadas, 
                  area_media_apto, teto_m2_construido
    """
    params = PARAMS_ZONA.get(zona, PARAMS_ZONA["ZR2"])
    taxa_ocup = params["taxa_ocup"]
    max_andares = params["max_andares"]
    recuo = params["recuo_min"]

    # Área de projeção (footprint) após recuos
    # Simplificação: desconta 15% da área para recuos laterais/frente/fundos
    area_projecao = area_terreno * taxa_ocup * 0.90

    # Área total construível (pelo coeficiente de aproveitamento)
    area_construivel_total = area_terreno * coef_aproveit

    # Andares possíveis (limitado pelo zoneamento)
    andares_pelo_coef = math.ceil(area_construivel_total / area_projecao) if area_projecao > 0 else 1
    andares_reais = min(andares_pelo_coef, max_andares)

    # Recalcula área real com limite de andares
    area_construivel_real = area_projecao * andares_reais

    # Estimativa de unidades por tipologia
    tipologias = {
        "Studio (30m²)":        math.floor(area_construivel_real * 0.75 / 30),
        "1 dormitório (45m²)":  math.floor(area_construivel_real * 0.75 / 45),
        "2 dormitórios (70m²)": math.floor(area_construivel_real * 0.75 / 70),
        "3 dormitórios (100m²)":math.floor(area_construivel_real * 0.75 / 100),
    }

    return {
        "zona_nome": params["nome"],
        "zona_codigo": zona,
        "area_terreno": area_terreno,
        "area_projecao": round(area_projecao, 1),
        "area_construivel_total": round(area_construivel_real, 1),
        "coef_aproveitamento": coef_aproveit,
        "max_andares_zona": max_andares,
        "andares_viáveis": andares_reais,
        "taxa_ocupacao": f"{taxa_ocup*100:.0f}%",
        "tipologias": tipologias,
        "recuo_minimo": recuo,
    }


def calcular_vgv(area_construivel: float, preco_venda_m2: float, 
                  percentual_area_privativa: float = 0.75) -> dict:
    """
    Calcula o VGV (Valor Geral de Vendas) potencial do empreendimento.
    
    percentual_area_privativa: área privativa / área construída total (típico: 70-80%)
    """
    area_privativa = area_construivel * percentual_area_privativa
    vgv_bruto = area_privativa * preco_venda_m2

    # Estimativas de custos (CUB SP + overhead)
    custo_construcao_m2 = 3200   # R$/m² construído (CUB SP referência 2024)
    custo_total_construcao = area_construivel * custo_construcao_m2

    # Margem bruta típica do setor: 30-40%
    margem_estimada = (vgv_bruto - custo_total_construcao) / vgv_bruto if vgv_bruto > 0 else 0

    return {
        "area_privativa": round(area_privativa, 1),
        "vgv_bruto": round(vgv_bruto, 2),
        "custo_construcao": round(custo_total_construcao, 2),
        "margem_bruta_pct": round(margem_estimada * 100, 1),
        "lucro_estimado": round(vgv_bruto - custo_total_construcao, 2),
    }
