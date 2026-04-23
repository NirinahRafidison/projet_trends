import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Google Trends Ultra Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
TIME_FILE = PROCESSED_DIR / "trends_time_long.csv"
COUNTRY_FILE = PROCESSED_DIR / "trends_country_enriched.csv"
INSIGHTS_FILE = PROCESSED_DIR / "country_insights.csv"

COLORS = {
    "ChatGPT":                "#4285F4",
    "crypto":                 "#EA4335",
    "Netflix":                "#34A853",
    "Tesla":                  "#FBBC05",
    "artificial intelligence":"#8AB4F8"
}

# =========================================================
# CSS DARK THEME
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@300;400;500&display=swap');

* { box-sizing: border-box; }

.stApp {
    background: #0b1220;
    font-family: 'Google Sans', 'Roboto', sans-serif;
    color: #f8fafc;
}

.hero {
    background: linear-gradient(135deg, rgba(37,99,235,0.20), rgba(14,165,233,0.10));
    border: 1px solid rgba(96,165,250,0.16);
    border-radius: 24px;
    padding: 24px;
    margin-bottom: 18px;
    box-shadow: 0 12px 40px rgba(0,0,0,0.28);
}
.hero-title {
    font-size: 2.1rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 8px;
}
.hero-sub {
    font-size: 1rem;
    line-height: 1.7;
    color: #dbeafe;
}

.info {
    background: rgba(30,41,59,0.70);
    border-left: 4px solid #60a5fa;
    padding: 15px 18px;
    border-radius: 14px;
    color: #dbeafe;
    line-height: 1.7;
    margin-bottom: 18px;
}

.metrics-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    padding: 24px 0;
}
.metric-card {
    padding: 20px 24px;
    border-radius: 12px;
    background: #111827;
    border: 1px solid rgba(255,255,255,0.07);
    transition: box-shadow 0.2s;
}
.metric-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
.metric-label { font-size: 0.8rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
.metric-value { font-size: 1.9rem; font-weight: 700; color: #f8fafc; line-height: 1.1; }
.metric-note { font-size: 0.82rem; color: #94a3b8; margin-top: 4px; }
.metric-badge {
    display: inline-block;
    background: rgba(66,133,244,0.2);
    color: #8ab4f8;
    border-radius: 12px; padding: 2px 10px;
    font-size: 0.78rem; font-weight: 600; margin-top: 6px;
}

.section-header { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; }
.section-title { font-size: 1.15rem; font-weight: 600; color: #f8fafc; }
.section-badge {
    background: rgba(66,133,244,0.2);
    color: #8ab4f8;
    border-radius: 8px; padding: 3px 10px;
    font-size: 0.78rem; font-weight: 600;
}

.gt-card {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    transition: box-shadow 0.2s;
}
.gt-card:hover { box-shadow: 0 6px 24px rgba(0,0,0,0.5); }

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.05); }
}
.live-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(234,67,53,0.15); color: #f28b82;
    border-radius: 12px; padding: 4px 12px;
    font-size: 0.8rem; font-weight: 600;
}
.live-dot {
    width: 7px; height: 7px;
    background: #f28b82; border-radius: 50%;
    animation: pulse 1.5s ease-in-out infinite;
}

.insight-box {
    background: rgba(66,133,244,0.12);
    border-left: 4px solid #4285F4;
    border-radius: 0 8px 8px 0;
    padding: 14px 18px; font-size: 0.9rem;
    color: #cbd5e1; line-height: 1.6; margin: 12px 0;
}

.summary-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.summary-table th {
    background: #1e293b; color: #94a3b8;
    font-weight: 600; font-size: 0.78rem;
    text-transform: uppercase; letter-spacing: 0.5px;
    padding: 12px 16px;
    border-bottom: 2px solid rgba(255,255,255,0.08);
    text-align: left;
}
.summary-table td {
    padding: 12px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    color: #e2e8f0;
}
.summary-table tr:hover td { background: #1e293b; }

.block-container {
    padding-top: 1.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}
header[data-testid="stHeader"] { background: transparent !important; }
div[data-testid="stToolbar"] { display: none; }

.stTabs [data-baseweb="tab-list"] {
    background: #0d1829;
    border-bottom: 2px solid rgba(255,255,255,0.07);
    gap: 0; padding: 0 8px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Google Sans', sans-serif !important;
    font-weight: 500; color: #94a3b8;
    padding: 16px 24px; font-size: 0.92rem;
}
.stTabs [aria-selected="true"] {
    color: #8ab4f8 !important;
    border-bottom: 3px solid #4285F4 !important;
}
.stTabs [data-baseweb="tab-border"] { display: none; }
.stTabs [data-baseweb="tab-panel"] {
    background: #0b1220;
    padding: 24px 8px !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #09111f 0%, #111827 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
.stSelectbox label, .stMultiSelect label, .stSlider label,
.stCheckbox label, .stRadio label {
    color: #f8fafc !important;
    font-family: 'Google Sans', sans-serif !important;
    font-size: 0.9rem !important;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPERS
# =========================================================
def to_num(s, fill=0):
    return pd.to_numeric(s, errors="coerce").fillna(fill)

def gt_layout(fig, height=420, show_legend=True):
    fig.update_layout(
        height=height,
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(family="Google Sans, Roboto, sans-serif", size=13, color="#f8fafc"),
        margin=dict(l=16, r=16, t=48, b=16),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="left", x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=12, color="#f8fafc"),
        ) if show_legend else dict(visible=False),
        showlegend=show_legend,
        hoverlabel=dict(
            bgcolor="#1e293b", font_size=13,
            font_family="Google Sans, sans-serif",
            font_color="#f8fafc", bordercolor="#334155"
        )
    )
    fig.update_xaxes(
        showgrid=True, gridcolor="rgba(255,255,255,0.06)",
        zeroline=False, showline=False,
        tickfont=dict(size=11, color="#94a3b8")
    )
    fig.update_yaxes(
        showgrid=True, gridcolor="rgba(255,255,255,0.06)",
        zeroline=False, showline=False,
        tickfont=dict(size=11, color="#94a3b8")
    )
    return fig

def get_metric_config(metric_mode):
    if metric_mode == "Score absolu":
        return "score_absolu", "Score Google Trends"
    if metric_mode == "Score normalisé":
        return "score_normalise", "Score normalisé (min-max)"
    return "part_du_max", "Part du maximum (%)"

def add_metric_columns(df):
    out = df.copy()
    out["score_absolu"] = to_num(out["score"])
    if out.empty:
        out["score_normalise"] = []
        out["part_du_max"] = []
        return out
    s_min = out["score_absolu"].min()
    s_max = out["score_absolu"].max()
    if pd.isna(s_min) or pd.isna(s_max) or s_max == s_min:
        out["score_normalise"] = 100.0
    else:
        out["score_normalise"] = ((out["score_absolu"] - s_min) / (s_max - s_min) * 100).round(2)
    if s_max == 0 or pd.isna(s_max):
        out["part_du_max"] = 0.0
    else:
        out["part_du_max"] = (out["score_absolu"] / s_max * 100).round(2)
    return out


# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data(show_spinner=False)
def load_data():
    df_time = pd.read_csv(TIME_FILE)
    df_country = pd.read_csv(COUNTRY_FILE)
    df_insights = pd.read_csv(INSIGHTS_FILE)
    df_time["date"] = pd.to_datetime(df_time["date"], errors="coerce")
    df_time["score"] = to_num(df_time["score"])
    df_country["score"] = to_num(df_country["score"])
    df_country["continent"] = df_country["continent"].fillna("Inconnu").astype(str)
    df_country["iso3"] = df_country["iso3"].fillna("").astype(str).str.upper()
    df_country = df_country[df_country["iso3"] != "NAN"]
    df_insights["score_max"] = to_num(df_insights["score_max"])
    df_insights["score_2eme"] = to_num(df_insights["score_2eme"])
    df_insights["ecart_top2"] = to_num(df_insights["ecart_top2"])
    return df_time, df_country, df_insights

df_time, df_country, df_insights = load_data()


# =========================================================
# SIDEBAR ORIGINAL COMPLET
# =========================================================
with st.sidebar:
    st.title("Contrôles")
    keywords = sorted(df_time["mot_cle"].dropna().unique().tolist())
    continents = sorted([c for c in df_country["continent"].dropna().unique() if c.lower() != "nan"])

    selected_kw = st.selectbox("Mot-clé principal", keywords,
        index=keywords.index("ChatGPT") if "ChatGPT" in keywords else 0)

    selected_continents = st.multiselect("Continents", options=continents, default=continents)

    metric_mode = st.radio(
        "Métrique d'affichage",
        ["Score absolu", "Score normalisé", "Part du maximum (%)"]
    )

    top_n = st.slider("Top pays", 5, 30, 12, 1)
    min_score = st.slider("Score minimum", 0, 100, 0, 1)
    show_avg = st.checkbox("Afficher la moyenne globale", value=True)
    show_raw = st.checkbox("Afficher les données brutes", value=False)


# =========================================================
# FILTERS
# =========================================================
df_c_filtered = df_country.copy()
if selected_continents:
    df_c_filtered = df_c_filtered[df_c_filtered["continent"].isin(selected_continents)]
df_c_filtered = df_c_filtered[df_c_filtered["score"] >= min_score]

df_insights_f = df_insights.copy()
if selected_continents:
    df_insights_f = df_insights_f[df_insights_f["continent"].isin(selected_continents)]

df_kw = add_metric_columns(df_c_filtered[df_c_filtered["mot_cle"] == selected_kw].copy())
metric_col, metric_label = get_metric_config(metric_mode)
if not df_kw.empty:
    df_kw = df_kw.sort_values(metric_col, ascending=False)

df_time_kw = df_time[df_time["mot_cle"] == selected_kw]


# =========================================================
# KPIs
# =========================================================
nb_pays = df_insights_f["country"].nunique()
if not df_insights_f.empty:
    dom = df_insights_f["mot_cle_dominant"].value_counts()
    top_kw_global = dom.idxmax()
    top_kw_count = int(dom.max())
    gap_row = df_insights_f.sort_values("ecart_top2", ascending=False).iloc[0]
    strongest_country = gap_row["country"]
    strongest_gap = int(gap_row["ecart_top2"])
else:
    top_kw_global, top_kw_count, strongest_country, strongest_gap = "N/A", 0, "N/A", 0

top_country = df_kw.iloc[0]["country"] if not df_kw.empty else "N/A"
top_score = float(df_kw.iloc[0][metric_col]) if not df_kw.empty else 0
mean_score = float(df_kw[metric_col].mean()) if not df_kw.empty else 0
kw_dom_count = int((df_insights_f["mot_cle_dominant"] == selected_kw).sum()) if not df_insights_f.empty else 0


# =========================================================
# HEADER ORIGINAL
# =========================================================
st.markdown(f"""
<div class="hero">
    <div class="hero-title">Google Trends Ultra Dashboard</div>
    <div class="hero-sub">
        Dashboard analytique avancé pour comparer des mots-clés selon leur évolution dans le temps,
        leur répartition mondiale et leur intensité relative par pays.
        Mot-clé étudié : <b>{selected_kw}</b> — métrique affichée : <b>{metric_mode}</b>.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info">
<b>Lecture correcte des scores :</b><br>
• Le <b>score absolu</b> correspond au score Google Trends brut.<br>
• Le <b>score normalisé</b> est recalculé sur les pays visibles après filtres, entre le minimum et le maximum observés.<br>
• La <b>part du maximum</b> mesure le poids d'un pays par rapport au meilleur pays visible.<br>
• Ainsi, ces trois métriques sont maintenant réellement différentes et utilisables.
</div>
""", unsafe_allow_html=True)


# =========================================================
# METRICS
# =========================================================
st.markdown(f"""
<div class="metrics-row">
    <div class="metric-card">
        <div class="metric-label">🌍 Pays analysés</div>
        <div class="metric-value">{nb_pays}</div>
        <div class="metric-note">Après filtres appliqués</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">🏆 Mot-clé dominant</div>
        <div class="metric-value" style="font-size:1.4rem;color:{COLORS.get(top_kw_global,'#f8fafc')}">{top_kw_global}</div>
        <div class="metric-note">Leader dans {top_kw_count} pays</div>
        <span class="metric-badge">Global</span>
    </div>
    <div class="metric-card">
        <div class="metric-label">📌 Leader — {selected_kw}</div>
        <div class="metric-value" style="font-size:1.35rem">{top_country}</div>
        <div class="metric-note">{metric_label} : {top_score:.1f} | Moy. : {mean_score:.1f}</div>
        <span class="metric-badge">{kw_dom_count} pays dominés</span>
    </div>
    <div class="metric-card">
        <div class="metric-label">⚡ Écart max top 2</div>
        <div class="metric-value">{strongest_gap}</div>
        <div class="metric-note">{strongest_country}</div>
        <span class="metric-badge">Dominance nette</span>
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Tendances temporelles",
    "🗺️ Carte mondiale",
    "📊 Comparaisons",
    "🔍 Données & Résumé"
])


# ==== TAB 1 ====
with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="gt-card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="section-header">
            <span class="section-title">Évolution de l'intérêt dans le temps</span>
            <span class="section-badge">Line chart animé</span>
        </div>
        """, unsafe_allow_html=True)

        df_sorted = df_time.sort_values(["mot_cle", "date"]).copy()
        df_sorted["score_lisse"] = df_sorted.groupby("mot_cle")["score"].transform(
            lambda s: s.rolling(4, min_periods=1).mean()
        )

        dates = sorted(df_sorted["date"].unique())
        step = max(1, len(dates) // min(60, len(dates)))
        frame_dates = dates[::step]

        frames = []
        for fd in frame_dates:
            sub = df_sorted[df_sorted["date"] <= fd]
            frame_traces = []
            for kw in keywords:
                kw_data = sub[sub["mot_cle"] == kw]
                frame_traces.append(go.Scatter(
                    x=kw_data["date"], y=kw_data["score_lisse"],
                    mode="lines", name=kw,
                    line=dict(color=COLORS.get(kw, "#888"), width=2.5)
                ))
            frames.append(go.Frame(data=frame_traces, name=str(fd)))

        fig_time = go.Figure()
        for kw in keywords:
            kw_data = df_sorted[df_sorted["mot_cle"] == kw]
            fig_time.add_trace(go.Scatter(
                x=kw_data["date"], y=kw_data["score_lisse"],
                mode="lines", name=kw,
                line=dict(color=COLORS.get(kw, "#888"), width=2.5),
                hovertemplate=f"<b>{kw}</b><br>%{{x|%b %Y}}<br>Score : %{{y:.0f}}<extra></extra>"
            ))

        if show_avg:
            avg = df_time.groupby("date", as_index=False)["score"].mean()
            fig_time.add_trace(go.Scatter(
                x=avg["date"], y=avg["score"],
                mode="lines", name="Moyenne",
                line=dict(color="#64748b", width=1.5, dash="dot"),
                hovertemplate="Moyenne<br>%{x|%b %Y}<br>%{y:.1f}<extra></extra>"
            ))

        fig_time.frames = frames
        fig_time.update_layout(
            updatemenus=[dict(
                type="buttons", showactive=False,
                y=-0.12, x=0.5, xanchor="center",
                buttons=[dict(
                    label="▶ Rejouer l'animation",
                    method="animate",
                    args=[None, dict(
                        frame=dict(duration=80, redraw=True),
                        fromcurrent=False,
                        transition=dict(duration=0)
                    )]
                )],
                bgcolor="#1a73e8",
                font=dict(color="white", size=13)
            )]
        )
        gt_layout(fig_time, height=460)
        fig_time.update_layout(hovermode="x unified", title="Popularité relative des mots-clés (2023–2026)")
        st.plotly_chart(fig_time, use_container_width=True)

        st.markdown("""
        <div class="insight-box">
            💡 <b>Lecture :</b> ChatGPT explose à partir de Jan 2024, dépassant Netflix dès mi-2024.
            Les scores sont relatifs (0–100) et normalisés par Google Trends sur la période sélectionnée.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="gt-card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="section-header">
            <span class="section-title">Intensité mensuelle</span>
            <span class="section-badge">Heatmap</span>
        </div>
        """, unsafe_allow_html=True)

        df_heat = df_time.copy()
        df_heat["mois"] = df_heat["date"].dt.to_period("M").astype(str)
        pivot_heat = df_heat.groupby(["mot_cle", "mois"])["score"].mean().reset_index()
        pivot_heat = pivot_heat.pivot(index="mot_cle", columns="mois", values="score").fillna(0)

        fig_heat = go.Figure(data=go.Heatmap(
            z=pivot_heat.values,
            x=pivot_heat.columns,
            y=pivot_heat.index,
            colorscale=[[0, "#0d1829"], [0.3, "#1e3a5f"], [0.7, "#2563eb"], [1, "#60a5fa"]],
            showscale=True,
            hovertemplate="%{y}<br>%{x}<br>Score : %{z:.0f}<extra></extra>"
        ))
        gt_layout(fig_heat, height=280, show_legend=False)
        fig_heat.update_layout(title="Score moyen par mois")
        fig_heat.update_xaxes(tickangle=-45, nticks=8)
        st.plotly_chart(fig_heat, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="gt-card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="section-header">
            <span class="section-title">Stats — {selected_kw}</span>
        </div>
        """, unsafe_allow_html=True)

        if not df_time_kw.empty:
            s = df_time_kw["score"]
            stats = {
                "Maximum": f"{s.max():.0f}",
                "Moyenne": f"{s.mean():.1f}",
                "Médiane": f"{s.median():.1f}",
                "Écart-type": f"{s.std():.1f}",
                "Dernière valeur": f"{df_time_kw.sort_values('date').iloc[-1]['score']:.0f}"
            }
            rows = "".join([
                f"<tr><td>{k}</td><td style='font-weight:600;color:#8ab4f8'>{v}</td></tr>"
                for k, v in stats.items()
            ])
            st.markdown(f"<table class='summary-table'>{rows}</table>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ==== TAB 2 ====
with tab2:
    map_col, rank_col = st.columns([1.4, 0.6])

    with map_col:
        st.markdown('<div class="gt-card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="section-header">
            <span class="section-title">Répartition mondiale des mots-clés dominants</span>
            <span class="section-badge">Choroplèthe</span>
        </div>
        """, unsafe_allow_html=True)

        df_map = df_insights_f[df_insights_f["iso3"].str.len() == 3].copy()
        fig_map = px.choropleth(
            df_map, locations="iso3", color="mot_cle_dominant",
            hover_name="country",
            hover_data={"score_max": ":.0f", "ecart_top2": ":.0f"},
            color_discrete_map=COLORS,
            projection="natural earth",
        )
        fig_map.update_layout(
            height=520,
            paper_bgcolor="#111827",
            font=dict(family="Google Sans, sans-serif", color="#f8fafc"),
            margin=dict(l=0, r=0, t=40, b=0),
            title="Mot-clé dominant par pays",
            geo=dict(
                bgcolor="#0b1220",
                showframe=False,
                showcoastlines=True, coastlinecolor="rgba(255,255,255,0.15)",
                showcountries=True, countrycolor="rgba(255,255,255,0.15)",
                showland=True, landcolor="#1e293b",
                showocean=True, oceancolor="#0d1829",
                lakecolor="#0d1829",
            ),
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.08,
                xanchor="center", x=0.5, font=dict(color="#f8fafc")
            )
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown("""
        <div class="insight-box">
            💡 Netflix domine en Europe, Amérique du Sud et Océanie.
            Crypto domine en Russie et Asie Centrale (instabilité monétaire).
            ChatGPT s'impose au Moyen-Orient et Asie du Sud-Est.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with rank_col:
        st.markdown('<div class="gt-card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="section-header">
            <span class="section-title">Top {top_n} pays — {selected_kw}</span>
        </div>
        """, unsafe_allow_html=True)

        if not df_kw.empty:
            df_bar = df_kw.head(top_n)
            fig_bar = px.bar(
                df_bar, x=metric_col, y="country",
                orientation="h", text=metric_col,
                color_discrete_sequence=[COLORS.get(selected_kw, "#4285F4")]
            )
            gt_layout(fig_bar, height=520, show_legend=False)
            fig_bar.update_yaxes(autorange="reversed", title="")
            fig_bar.update_xaxes(title=metric_label)
            fig_bar.update_traces(texttemplate="%{text:.1f}", textposition="outside")
            fig_bar.update_layout(title="Classement pays")
            st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ==== TAB 3 ====
with tab3:
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="gt-card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="section-header">
            <span class="section-title">Distribution des scores</span>
            <span class="section-badge">Box plot</span>
        </div>
        """, unsafe_allow_html=True)
        fig_box = px.box(
            df_time, x="mot_cle", y="score",
            color="mot_cle", color_discrete_map=COLORS,
            points="outliers"
        )
        gt_layout(fig_box, height=400, show_legend=False)
        fig_box.update_layout(title="Variance et médiane par mot-clé")
        fig_box.update_xaxes(title="")
        fig_box.update_yaxes(title="Score (0–100)")
        st.plotly_chart(fig_box, use_container_width=True)
        st.markdown("""
        <div class="insight-box">
            💡 ChatGPT : variance maximale (outliers ~95) → intérêt viral.<br>
            Netflix : boîte compacte → usage quotidien stable.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="gt-card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="section-header">
            <span class="section-title">Matrice de corrélation</span>
            <span class="section-badge">Co-évolutions</span>
        </div>
        """, unsafe_allow_html=True)
        df_pivot_corr = df_time.pivot_table(index="date", columns="mot_cle", values="score").fillna(0)
        corr = df_pivot_corr.corr().round(2)
        fig_corr = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.index.tolist(),
            colorscale=[[0, "#ea4335"], [0.5, "#1e293b"], [1, "#4285F4"]],
            zmin=-1, zmax=1,
            text=corr.values,
            texttemplate="%{text:.2f}",
            showscale=True,
            hovertemplate="%{y} × %{x}<br>r = %{z:.2f}<extra></extra>"
        ))
        gt_layout(fig_corr, height=400, show_legend=False)
        fig_corr.update_layout(title="Corrélation entre mots-clés")
        st.plotly_chart(fig_corr, use_container_width=True)
        st.markdown("""
        <div class="insight-box">
            💡 ChatGPT & Crypto : r = 0.68 → deux sujets médiatiques.<br>
            ChatGPT & AI : r = 0.35 → public cherche l'outil, pas le concept.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="gt-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
        <span class="section-title">Dominance géographique par mot-clé</span>
        <span class="section-badge">Nombre de pays</span>
    </div>
    """, unsafe_allow_html=True)
    col_dom, col_avg = st.columns(2)
    with col_dom:
        if not df_insights_f.empty:
            df_dom = df_insights_f["mot_cle_dominant"].value_counts().reset_index()
            df_dom.columns = ["mot_cle", "nb_pays"]
            fig_dom = px.bar(df_dom, x="mot_cle", y="nb_pays", text="nb_pays",
                color="mot_cle", color_discrete_map=COLORS)
            gt_layout(fig_dom, height=320, show_legend=False)
            fig_dom.update_layout(title="Pays dominés par mot-clé")
            fig_dom.update_traces(textposition="outside")
            fig_dom.update_xaxes(title="")
            fig_dom.update_yaxes(title="Nombre de pays")
            st.plotly_chart(fig_dom, use_container_width=True)
    with col_avg:
        avg_df = df_time.groupby("mot_cle", as_index=False)["score"].mean().sort_values("score")
        fig_avg = px.bar(avg_df, x="score", y="mot_cle", orientation="h", text="score",
            color="mot_cle", color_discrete_map=COLORS)
        gt_layout(fig_avg, height=320, show_legend=False)
        fig_avg.update_layout(title="Score moyen global")
        fig_avg.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_avg.update_xaxes(title="Score moyen")
        fig_avg.update_yaxes(title="")
        st.plotly_chart(fig_avg, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ==== TAB 4 ====
with tab4:
    st.markdown('<div class="gt-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
        <span class="section-title">Résumé analytique automatique</span>
    </div>
    """, unsafe_allow_html=True)

    kw_dom_share = (kw_dom_count / nb_pays * 100) if nb_pays else 0
    top3 = df_kw.head(3)["country"].tolist()
    top3_txt = ", ".join(top3) if top3 else "N/A"

    st.markdown(f"""
    <table class="summary-table">
        <tr><th>Indicateur</th><th>Valeur</th><th>Interprétation</th></tr>
        <tr><td>Mot-clé dominant global</td>
            <td><b style="color:{COLORS.get(top_kw_global,'#f8fafc')}">{top_kw_global}</b></td>
            <td>Leader dans {top_kw_count} pays</td></tr>
        <tr><td>Leader pour {selected_kw}</td>
            <td><b>{top_country}</b></td>
            <td>{metric_label} : {top_score:.1f}</td></tr>
        <tr><td>Top 3 pays — {selected_kw}</td>
            <td><b>{top3_txt}</b></td>
            <td>Pays avec intérêt le plus élevé</td></tr>
        <tr><td>Domination de {selected_kw}</td>
            <td><b>{kw_dom_count} pays</b></td>
            <td>{kw_dom_share:.1f}% des pays analysés</td></tr>
        <tr><td>Écart de domination max</td>
            <td><b>{strongest_gap} pts</b></td>
            <td>{strongest_country} — domination nette</td></tr>
        <tr><td>Score moyen — {selected_kw}</td>
            <td><b>{mean_score:.1f}</b></td>
            <td>Sur l'ensemble des pays filtrés</td></tr>
    </table>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if show_raw:
        st.markdown('<div class="gt-card">', unsafe_allow_html=True)
        st.subheader("Données brutes")
        t1, t2, t3 = st.tabs(["Séries temporelles", "Données pays", "Insights"])
        with t1: st.dataframe(df_time, use_container_width=True, height=300)
        with t2: st.dataframe(df_c_filtered, use_container_width=True, height=300)
        with t3: st.dataframe(df_insights_f, use_container_width=True, height=300)
        st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# FOOTER
# =========================================================
st.markdown("""
<div style="text-align:center;padding:24px 0 16px;color:#475569;font-size:0.82rem;
font-family:'Google Sans',sans-serif;border-top:1px solid rgba(255,255,255,0.06);margin-top:8px;">
    TrendScope · M1 BIDABI 2025–2026 · Données Google Trends via pytrends · Vanilla Savienny & Can Pekgoz
</div>
""", unsafe_allow_html=True)