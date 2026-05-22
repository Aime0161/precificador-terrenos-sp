import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from data.bairros_sp import get_bairros_list, get_bairro_data, get_similar_bairros, get_transacoes_recentes
from services.calculator import calcular_potencial_construtivo, calcular_vgv
from services.ai_analyzer import analisar_terreno_com_ia
from services.serp_scraper import buscar_anuncios_terrenos

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Precificador de Terrenos SP",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS Custom ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: linear-gradient(135deg, #0f0c29 0%, #141428 50%, #0d1117 100%); }

/* Hero */
.hero-box {
    background: linear-gradient(135deg, #1a1a3e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.hero-box::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(ellipse at top, rgba(99,102,241,0.15) 0%, transparent 70%);
}
.hero-title {
    font-size: 2.8rem; font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0; line-height: 1.2;
}
.hero-sub { color: #94a3b8; font-size: 1.1rem; margin-top: 0.5rem; }

/* Metric Cards */
.metric-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
}
.metric-card:hover { border-color: rgba(99,102,241,0.5); transform: translateY(-2px); }
.metric-value { font-size: 1.8rem; font-weight: 700; color: #a78bfa; }
.metric-label { font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

/* Verdict */
.verdict-ouro    { background: linear-gradient(135deg,#f59e0b,#fbbf24); color:#000; }
.verdict-bom     { background: linear-gradient(135deg,#10b981,#34d399); color:#000; }
.verdict-atencao { background: linear-gradient(135deg,#f97316,#fb923c); color:#000; }
.verdict-cilada  { background: linear-gradient(135deg,#ef4444,#f87171); color:#fff; }

.verdict-box {
    border-radius: 16px; padding: 1.5rem 2rem;
    text-align: center; margin: 1.5rem 0;
}
.verdict-box h2 { font-size: 2rem; font-weight: 800; margin: 0; }
.verdict-box p  { margin: 0.3rem 0 0; font-size: 1rem; opacity: 0.85; }

/* Pro/Con */
.pro-item  { background:rgba(16,185,129,0.1); border-left:3px solid #10b981; border-radius:8px; padding:0.6rem 1rem; margin:0.4rem 0; color:#d1fae5; }
.con-item  { background:rgba(239,68,68,0.1);  border-left:3px solid #ef4444;  border-radius:8px; padding:0.6rem 1rem; margin:0.4rem 0; color:#fee2e2; }

/* Ad cards */
.ad-card {
    background: rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);
    border-radius: 12px; padding: 1rem 1.2rem; margin: 0.5rem 0;
    transition: all 0.2s;
}
.ad-card:hover { border-color: rgba(99,102,241,0.4); }
.ad-fonte { font-size:0.7rem; color:#6366f1; font-weight:600; text-transform:uppercase; }
.ad-title { color:#e2e8f0; font-weight:500; font-size:0.9rem; margin:0.2rem 0; }
.ad-snippet { color:#64748b; font-size:0.8rem; }

/* Section title */
.section-title { color:#a78bfa; font-size:1.1rem; font-weight:700; text-transform:uppercase; letter-spacing:2px; margin:1.5rem 0 1rem; }

/* Sidebar */
[data-testid="stSidebar"] { background: rgba(15,12,41,0.95) !important; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-box">
    <div class="hero-title">🏗️ Precificador de Terrenos</div>
    <div class="hero-sub">Em 3 cliques, saiba se o terreno é <strong>ouro</strong> ou <strong>cilada</strong> · São Paulo · MVP v1.0</div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar – Inputs ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📍 Dados do Terreno")
    bairros = get_bairros_list()
    bairro_sel = st.selectbox("Bairro / Região", bairros, index=bairros.index("Pinheiros"))

    area_m2 = st.number_input("Área do terreno (m²)", min_value=50, max_value=50000,
                               value=500, step=50)

    dados = get_bairro_data(bairro_sel)
    preco_mercado = dados["preco_m2"]

    preco_ofertado = st.number_input(
        "Preço ofertado (R$/m²)",
        min_value=500, max_value=100000,
        value=preco_mercado, step=100,
        help="Digite o preço que o vendedor está pedindo"
    )

    preco_venda_apto = st.number_input(
        "Preço venda apartamento (R$/m²)",
        min_value=3000, max_value=50000,
        value=int(preco_mercado * 1.8), step=500,
        help="Preço de venda estimado dos imóveis construídos"
    )

    st.markdown("---")
    usar_ia = st.toggle("🤖 Análise com IA (GPT-4)", value=True,
                         help="Requer OPENAI_API_KEY no arquivo .env")
    buscar_anuncios = st.toggle("🔍 Buscar anúncios reais", value=True,
                                 help="Requer SERPAPI_KEY no arquivo .env")

    analisar = st.button("🚀 ANALISAR TERRENO", use_container_width=True, type="primary")

# ── Main ──────────────────────────────────────────────────────────────────────
if not analisar:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("**1️⃣ Selecione o bairro** e informe a área do terreno na barra lateral")
    with c2:
        st.info("**2️⃣ Informe o preço** sendo pedido pelo vendedor (R$/m²)")
    with c3:
        st.info("**3️⃣ Clique em Analisar** e receba o diagnóstico completo em segundos")
    st.markdown("---")
    st.markdown("#### 📊 Base de Dados: Bairros Disponíveis")
    from data.bairros_sp import BAIRROS_SP
    df_all = pd.DataFrame([
        {"Bairro": k, "Preço m²": f"R$ {v['preco_m2']:,.0f}", "Zona": v["zona"],
         "Valoriz. a.a.": f"{v['valorizacao_aa']}%", "Seg.": v["risco_seg"], "Alag.": v["risco_alag"]}
        for k, v in BAIRROS_SP.items()
    ])
    st.dataframe(df_all, use_container_width=True, hide_index=True)
    st.stop()

# ── Análise ───────────────────────────────────────────────────────────────────
with st.spinner("🔍 Analisando terreno..."):
    potencial = calcular_potencial_construtivo(area_m2, dados["zona"], dados["coef_aproveit"])
    vgv_data  = calcular_vgv(potencial["area_construivel_total"], preco_venda_apto)
    anuncios  = buscar_anuncios_terrenos(bairro_sel, area_m2) if buscar_anuncios else []
    
    analise_ia = {}
    if usar_ia:
        analise_ia = analisar_terreno_com_ia(
            bairro=bairro_sel, area_m2=area_m2,
            preco_m2_mercado=preco_mercado, preco_m2_ofertado=preco_ofertado,
            zona=dados["zona"], coef_aproveit=dados["coef_aproveit"],
            risco_alag=dados["risco_alag"], risco_seg=dados["risco_seg"],
            valorizacao_aa=dados["valorizacao_aa"],
        )

# ── Row 1: KPIs ──────────────────────────────────────────────────────────────
diff_pct = ((preco_ofertado - preco_mercado) / preco_mercado) * 100
valor_total = area_m2 * preco_ofertado

c1, c2, c3, c4, c5 = st.columns(5)
kpis = [
    (f"R$ {preco_mercado:,.0f}", "Preço Médio Mercado"),
    (f"{diff_pct:+.1f}%", "vs Mercado"),
    (f"R$ {valor_total/1e6:.2f}M", "Valor Total"),
    (f"{potencial['andares_viáveis']} and.", "Potencial Construtivo"),
    (f"R$ {vgv_data['vgv_bruto']/1e6:.1f}M", "VGV Estimado"),
]
for col, (val, lbl) in zip([c1,c2,c3,c4,c5], kpis):
    with col:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{val}</div><div class="metric-label">{lbl}</div></div>', unsafe_allow_html=True)

st.markdown("")

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🤖 Análise IA", "🏗️ Potencial", "📊 Mercado", "🗺️ Mapa", "🔍 Anúncios"])

# ─ TAB 1: IA ─────────────────────────────────────────────────────────────────
with tab1:
    if not analise_ia:
        st.warning("Ative o toggle '🤖 Análise com IA' na barra lateral.")
    else:
        veredicto = analise_ia.get("veredicto", "ATENÇÃO")
        score     = analise_ia.get("score", 50)
        cls_map   = {"OURO": "ouro", "BOM NEGÓCIO": "bom", "ATENÇÃO": "atencao", "CILADA": "cilada"}
        cls       = cls_map.get(veredicto, "atencao")
        emoji_map = {"OURO": "🥇", "BOM NEGÓCIO": "✅", "ATENÇÃO": "⚠️", "CILADA": "🚨"}
        emoji     = emoji_map.get(veredicto, "⚠️")

        st.markdown(f"""
        <div class="verdict-box verdict-{cls}">
            <h2>{emoji} {veredicto}</h2>
            <p>Score de investimento: {score}/100</p>
        </div>""", unsafe_allow_html=True)

        # Score gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={"x":[0,1],"y":[0,1]},
            gauge={
                "axis":{"range":[0,100],"tickcolor":"#64748b"},
                "bar":{"color":"#a78bfa"},
                "steps":[
                    {"range":[0,40],"color":"rgba(239,68,68,0.3)"},
                    {"range":[40,65],"color":"rgba(251,146,60,0.3)"},
                    {"range":[65,80],"color":"rgba(16,185,129,0.3)"},
                    {"range":[80,100],"color":"rgba(245,158,11,0.3)"},
                ],
                "threshold":{"line":{"color":"white","width":3},"thickness":0.8,"value":score},
            },
            title={"text":"Score de Investimento","font":{"color":"#94a3b8"}},
            number={"font":{"color":"#a78bfa","size":48}},
        ))
        fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                 font_color="#94a3b8", height=300)
        
        col_g, col_p = st.columns([1,2])
        with col_g:
            st.plotly_chart(fig_gauge, use_container_width=True)
        with col_p:
            st.markdown("**📋 Parecer do Analista IA**")
            st.markdown(f'<div style="background:rgba(255,255,255,0.03);border-radius:12px;padding:1rem;color:#cbd5e1;line-height:1.7">{analise_ia.get("parecer","")}</div>', unsafe_allow_html=True)

        st.markdown("")
        c_pos, c_neg = st.columns(2)
        with c_pos:
            st.markdown('<div class="section-title">✅ Pontos Positivos</div>', unsafe_allow_html=True)
            for p in analise_ia.get("pontos_positivos", []):
                st.markdown(f'<div class="pro-item">👍 {p}</div>', unsafe_allow_html=True)
        with c_neg:
            st.markdown('<div class="section-title">⚠️ Pontos de Atenção</div>', unsafe_allow_html=True)
            for p in analise_ia.get("pontos_negativos", []):
                st.markdown(f'<div class="con-item">⚠️ {p}</div>', unsafe_allow_html=True)

        if analise_ia.get("recomendacao_negociacao"):
            st.markdown("---")
            preco_justo = analise_ia.get("preco_justo_m2", preco_mercado)
            st.info(f"💡 **Estratégia de Negociação** | Preço justo sugerido: **R$ {preco_justo:,.0f}/m²** — {analise_ia['recomendacao_negociacao']}")
        
        if "_modo" in analise_ia:
            st.caption(f"ℹ️ Modo: {analise_ia['_modo']}")

# ─ TAB 2: Potencial Construtivo ───────────────────────────────────────────────
with tab2:
    st.markdown(f'<div class="section-title">Zoneamento: {potencial["zona_nome"]} ({potencial["zona_codigo"]})</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    cards2 = [
        (f"{potencial['andares_viáveis']} andares", "Andares Viáveis"),
        (f"{potencial['area_construivel_total']:,.0f} m²", "Área Construível"),
        (potencial["taxa_ocupacao"], "Taxa de Ocupação"),
        (f"{potencial['coef_aproveitamento']}x", "Coef. Aproveitamento"),
    ]
    for col, (val, lbl) in zip([c1,c2,c3,c4], cards2):
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{val}</div><div class="metric-label">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("")
    col_tip, col_vgv = st.columns(2)

    with col_tip:
        st.markdown("#### 🏠 Unidades por Tipologia")
        tip = potencial["tipologias"]
        fig_bar = px.bar(
            x=list(tip.keys()), y=list(tip.values()),
            labels={"x":"Tipologia","y":"Unidades"},
            color=list(tip.values()),
            color_continuous_scale=["#6366f1","#a78bfa","#34d399","#fbbf24"],
        )
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               font_color="#94a3b8", showlegend=False, coloraxis_showscale=False, height=320)
        fig_bar.update_traces(marker_line_color="rgba(0,0,0,0)")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_vgv:
        st.markdown("#### 💰 Projeção Financeira (VGV)")
        labels = ["VGV Bruto", "Custo Construção", "Lucro Estimado"]
        values = [vgv_data["vgv_bruto"], vgv_data["custo_construcao"], vgv_data["lucro_estimado"]]
        colors = ["#6366f1","#ef4444","#10b981"]
        fig_fin = go.Figure(go.Bar(x=labels, y=values, marker_color=colors,
                                    text=[f"R$ {v/1e6:.1f}M" for v in values], textposition="outside"))
        fig_fin.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               font_color="#94a3b8", height=320,
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
        st.plotly_chart(fig_fin, use_container_width=True)
        st.metric("Margem Bruta Estimada", f"{vgv_data['margem_bruta_pct']}%",
                   delta="Referência setor: 30-40%")

# ─ TAB 3: Mercado ─────────────────────────────────────────────────────────────
with tab3:
    similares = get_similar_bairros(bairro_sel, 6)
    transacoes = get_transacoes_recentes(bairro_sel)

    col_sim, col_trans = st.columns([1,1])

    with col_sim:
        st.markdown("#### 🔍 Bairros Similares")
        if similares:
            nomes  = [s["bairro"] for s in similares] + [bairro_sel]
            precos = [s["preco_m2"] for s in similares] + [preco_ofertado]
            cores  = ["#6366f1"] * len(similares) + ["#fbbf24"]
            fig_sim = go.Figure(go.Bar(
                x=nomes, y=precos, marker_color=cores,
                text=[f"R${p:,.0f}" for p in precos], textposition="outside"
            ))
            fig_sim.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                   font_color="#94a3b8", height=350,
                                   yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                   xaxis=dict(tickangle=-30))
            st.plotly_chart(fig_sim, use_container_width=True)
    
    with col_trans:
        st.markdown("#### 📈 Transações Recentes (Simulado)")
        st.dataframe(transacoes, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### ⚠️ Análise de Riscos")
    rc1, rc2, rc3 = st.columns(3)
    risk_color = {"Baixo":"#10b981","Médio":"#f97316","Alto":"#ef4444"}
    with rc1:
        c = risk_color[dados["risco_alag"]]
        st.markdown(f"**🌊 Risco Alagamento**")
        st.markdown(f'<span style="color:{c};font-size:1.4rem;font-weight:700">{dados["risco_alag"]}</span>', unsafe_allow_html=True)
    with rc2:
        c = risk_color[dados["risco_seg"]]
        st.markdown(f"**🔒 Segurança**")
        st.markdown(f'<span style="color:{c};font-size:1.4rem;font-weight:700">{dados["risco_seg"]}</span>', unsafe_allow_html=True)
    with rc3:
        va = dados["valorizacao_aa"]
        c = "#10b981" if va >= 7 else "#f97316" if va >= 5 else "#ef4444"
        st.markdown(f"**📈 Valorização Histórica**")
        st.markdown(f'<span style="color:{c};font-size:1.4rem;font-weight:700">{va}% a.a.</span>', unsafe_allow_html=True)

# ─ TAB 4: Mapa ────────────────────────────────────────────────────────────────
with tab4:
    lat, lon = dados["lat"], dados["lon"]
    m = folium.Map(location=[lat, lon], zoom_start=14,
                   tiles="CartoDB dark_matter")

    # Ponto principal
    folium.CircleMarker(
        location=[lat, lon], radius=16,
        color="#a78bfa", fill=True, fill_color="#a78bfa", fill_opacity=0.8,
        popup=folium.Popup(f"<b>{bairro_sel}</b><br>R$ {preco_mercado:,.0f}/m²<br>Valorização: {dados['valorizacao_aa']}% a.a.", max_width=200),
        tooltip=bairro_sel,
    ).add_to(m)

    # Bairros similares
    for s in similares:
        folium.CircleMarker(
            location=[s["lat"], s["lon"]], radius=8,
            color="#6366f1", fill=True, fill_color="#6366f1", fill_opacity=0.5,
            popup=folium.Popup(f"<b>{s['bairro']}</b><br>R$ {s['preco_m2']:,.0f}/m²", max_width=150),
            tooltip=s["bairro"],
        ).add_to(m)

    st_folium(m, height=500, use_container_width=True)

# ─ TAB 5: Anúncios ────────────────────────────────────────────────────────────
with tab5:
    if not anuncios:
        st.info("Ative '🔍 Buscar anúncios reais' na barra lateral.")
    else:
        st.markdown(f"#### 🔍 Anúncios encontrados para terrenos em **{bairro_sel}**")
        for ad in anuncios:
            st.markdown(f"""
            <div class="ad-card">
                <div class="ad-fonte">{ad['fonte']}</div>
                <div class="ad-title"><a href="{ad['link']}" target="_blank" style="color:#a78bfa;text-decoration:none">{ad['titulo']}</a></div>
                <div class="ad-snippet">{ad['snippet']}</div>
            </div>""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#374151;font-size:0.8rem">'
    '🏗️ Precificador de Terrenos SP · MVP v1.0 · Dados: FIPE ZAP, IPTU SP (referência 2024) · '
    '<a href="https://github.com" style="color:#6366f1">GitHub</a>'
    '</div>',
    unsafe_allow_html=True
)
