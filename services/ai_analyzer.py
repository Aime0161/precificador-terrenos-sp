import os
import json
from dotenv import load_dotenv

load_dotenv()

def _get_client():
    """Cria o cliente OpenAI de forma lazy — só instancia se a chave existir."""
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key.startswith("sk-xxx"):
        return None
    return OpenAI(api_key=api_key)

# ─────────────────────────────────────────────────────────────────────────────
# Análise IA com GPT-4
# ─────────────────────────────────────────────────────────────────────────────

def analisar_terreno_com_ia(
    bairro: str,
    area_m2: float,
    preco_m2_mercado: float,
    preco_m2_ofertado: float,
    zona: str,
    coef_aproveit: float,
    risco_alag: str,
    risco_seg: str,
    valorizacao_aa: float,
) -> dict:
    """
    Chama GPT-4 para gerar análise completa do terreno.
    Retorna dict com: parecer, pontos_positivos, pontos_negativos, veredicto, score
    """
    client = _get_client()
    if client is None:
        return _analise_demo(bairro, area_m2, preco_m2_mercado, preco_m2_ofertado,
                             zona, coef_aproveit, risco_alag, risco_seg, valorizacao_aa)

    diferenca_pct = ((preco_m2_ofertado - preco_m2_mercado) / preco_m2_mercado) * 100
    valor_total = area_m2 * preco_m2_ofertado

    prompt = f"""
Você é um especialista sênior em desenvolvimento imobiliário com 20 anos de experiência no mercado de São Paulo.
Analise o terreno abaixo e forneça uma avaliação profissional detalhada.

DADOS DO TERRENO:
- Localização: {bairro}, São Paulo
- Área: {area_m2:,.0f} m²
- Preço ofertado: R$ {preco_m2_ofertado:,.0f}/m² (Total: R$ {valor_total:,.0f})
- Preço médio de mercado: R$ {preco_m2_mercado:,.0f}/m²
- Diferença em relação ao mercado: {diferenca_pct:+.1f}%
- Zoneamento: {zona}
- Coeficiente de aproveitamento: {coef_aproveit}x
- Risco de alagamento: {risco_alag}
- Risco de segurança: {risco_seg}
- Valorização anual histórica: {valorizacao_aa}% a.a.

Retorne EXCLUSIVAMENTE um JSON válido com esta estrutura:
{{
  "parecer": "Texto de 3-4 parágrafos com análise completa do investimento, contexto de mercado e perspectivas",
  "pontos_positivos": ["ponto 1", "ponto 2", "ponto 3", "ponto 4"],
  "pontos_negativos": ["ponto 1", "ponto 2", "ponto 3"],
  "recomendacao_negociacao": "Texto com estratégia de negociação e preço justo sugerido",
  "veredicto": "OURO" | "BOM NEGÓCIO" | "ATENÇÃO" | "CILADA",
  "score": número de 0 a 100,
  "preco_justo_m2": número com o preço justo sugerido em R$
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=1200,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return _analise_demo(bairro, area_m2, preco_m2_mercado, preco_m2_ofertado,
                             zona, coef_aproveit, risco_alag, risco_seg, valorizacao_aa,
                             erro=str(e))


def _analise_demo(bairro, area, preco_mercado, preco_ofertado, zona,
                  coef, risco_alag, risco_seg, val_aa, erro=None) -> dict:
    """Análise simulada para modo demo (sem chave OpenAI)."""
    diff_pct = ((preco_ofertado - preco_mercado) / preco_mercado) * 100
    score_base = 60

    # Ajuste por preço
    if diff_pct < -10:
        score_base += 20
        veredicto = "OURO"
    elif diff_pct < 0:
        score_base += 10
        veredicto = "BOM NEGÓCIO"
    elif diff_pct < 10:
        score_base += 0
        veredicto = "ATENÇÃO"
    else:
        score_base -= 15
        veredicto = "CILADA"

    # Ajuste por risco
    if risco_alag == "Alto": score_base -= 10
    if risco_seg == "Alto": score_base -= 10
    if val_aa > 8: score_base += 10
    score_base = max(5, min(98, score_base))

    preco_justo = int(preco_mercado * 0.92)

    parecer = (
        f"O terreno em {bairro} apresenta características {'favoráveis' if score_base >= 60 else 'desfavoráveis'} "
        f"para investimento imobiliário. Com {area:,.0f}m² em zona {zona}, o ativo tem potencial construtivo "
        f"com coeficiente de aproveitamento de {coef}x.\n\n"
        f"O preço ofertado de R$ {preco_ofertado:,.0f}/m² está {abs(diff_pct):.1f}% "
        f"{'acima' if diff_pct > 0 else 'abaixo'} da média de mercado para a região, "
        f"que é de R$ {preco_mercado:,.0f}/m². "
        f"A valorização histórica de {val_aa}% a.a. "
        f"{'indica boa perspectiva de ganho de capital.' if val_aa >= 7 else 'está abaixo da média premium de São Paulo.'}\n\n"
        f"{'⚠️ Atenção: o risco de alagamento é ' + risco_alag + ', o que pode impactar o projeto e os custos de fundação.' if risco_alag != 'Baixo' else ''}"
        f"{'⚠️ O índice de segurança do bairro é ' + risco_seg + ', fator que pode afetar a atratividade do produto final.' if risco_seg != 'Baixo' else ''}"
    )

    return {
        "parecer": parecer.strip(),
        "pontos_positivos": [
            f"Localização em {bairro} com demanda aquecida" if score_base >= 60 else f"Preço potencialmente negociável",
            f"Coeficiente de aproveitamento {coef}x permite boa densidade construtiva",
            f"Valorização histórica de {val_aa}% a.a.",
            f"Área de {area:,.0f}m² {'permite projeto de médio/grande porte' if area >= 500 else 'adequada para boutique'}",
        ],
        "pontos_negativos": [
            f"Preço {diff_pct:+.1f}% em relação ao mercado" if diff_pct > 0 else f"Verificar motivo do desconto de {abs(diff_pct):.1f}%",
            f"Risco de alagamento {risco_alag}" if risco_alag != "Baixo" else "Verificar histórico de litigios do imóvel",
            f"Índice de segurança: {risco_seg}" if risco_seg != "Baixo" else "Avaliar concorrência na região",
        ],
        "recomendacao_negociacao": (
            f"Sugerimos negociar o preço para aproximadamente R$ {preco_justo:,.0f}/m², "
            f"um desconto de {((preco_justo - preco_ofertado)/preco_ofertado * -100):.1f}% em relação ao ofertado. "
            f"Solicite due diligence completa, laudo geotécnico e certidões negativas antes de fechar negócio."
        ),
        "veredicto": veredicto,
        "score": score_base,
        "preco_justo_m2": preco_justo,
        "_modo": "demo" + (f" (erro API: {erro})" if erro else ""),
    }
