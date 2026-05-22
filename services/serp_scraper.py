import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

# ─────────────────────────────────────────────────────────────────────────────
# Busca de anúncios reais de terrenos via SerpAPI (Google Shopping / Search)
# ─────────────────────────────────────────────────────────────────────────────

def buscar_anuncios_terrenos(bairro: str, area_m2: float) -> list[dict]:
    """
    Busca anúncios reais de terrenos em sites como ZAP, OLX, VivaReal via SerpAPI.
    Em modo demo (sem chave), retorna dados simulados.
    """
    if not SERPAPI_KEY or SERPAPI_KEY.startswith("xxx"):
        return _anuncios_demo(bairro, area_m2)

    query = f"terreno à venda {bairro} São Paulo {int(area_m2)}m2 site:zapimoveis.com.br OR site:vivareal.com.br OR site:olx.com.br"

    params = {
        "engine": "google",
        "q": query,
        "location": "São Paulo, Brazil",
        "hl": "pt-BR",
        "gl": "br",
        "num": 10,
        "api_key": SERPAPI_KEY,
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=15)
        data = response.json()
        resultados = []
        for item in data.get("organic_results", [])[:6]:
            resultados.append({
                "titulo": item.get("title", "Terreno à venda"),
                "link": item.get("link", "#"),
                "snippet": item.get("snippet", ""),
                "fonte": _extrair_fonte(item.get("link", "")),
            })
        return resultados if resultados else _anuncios_demo(bairro, area_m2)
    except Exception:
        return _anuncios_demo(bairro, area_m2)


def _extrair_fonte(url: str) -> str:
    if "zapimoveis" in url: return "ZAP Imóveis"
    if "vivareal" in url: return "VivaReal"
    if "olx" in url: return "OLX"
    if "imovelweb" in url: return "ImovelWeb"
    return "Web"


def _anuncios_demo(bairro: str, area_m2: float) -> list[dict]:
    """Anúncios simulados para demo."""
    return [
        {
            "titulo": f"Terreno em {bairro} - {int(area_m2 * 0.8)}m² - Ótima localização",
            "link": "https://www.zapimoveis.com.br/venda/terrenos/sp+sao-paulo/",
            "snippet": f"Terreno plano em {bairro}, próximo ao metrô, documentação ok.",
            "fonte": "ZAP Imóveis",
        },
        {
            "titulo": f"Vendo terreno {bairro} SP - {int(area_m2)}m² - Ideal construtora",
            "link": "https://www.vivareal.com.br/venda/sp/sao-paulo/terreno_residencial/",
            "snippet": f"Excelente oportunidade de investimento em {bairro}. Zoneamento misto.",
            "fonte": "VivaReal",
        },
        {
            "titulo": f"TERRENO {bairro.upper()} - {int(area_m2 * 1.2)}m² - PERMUTA ACEITA",
            "link": "https://www.olx.com.br/imoveis/venda/terrenos-lotes",
            "snippet": f"Terreno em {bairro} com excelente potencial construtivo. Aceita permuta.",
            "fonte": "OLX",
        },
        {
            "titulo": f"Área residencial {bairro} - {int(area_m2 * 0.6)}m² - Financiável",
            "link": "https://www.imovelweb.com.br/terrenos-venda-sao-paulo.html",
            "snippet": f"Lote em {bairro}, São Paulo. Aceita financiamento bancário.",
            "fonte": "ImovelWeb",
        },
    ]
