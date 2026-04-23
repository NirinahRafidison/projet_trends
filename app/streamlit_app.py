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

PAPER_BG = "#081120"
PLOT_BG = "#0b1728"
CARD_BG = "rgba(15,23,42,0.82)"
FONT = "#F8FAFC"
GRID = "rgba(148,163,184,0.12)"


# =========================================================
# STYLE
# =========================================================
st.markdown("""
<style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(37,99,235,0.18), transparent 28%),
            radial-gradient(circle at top right, rgba(14,165,233,0.12), transparent 20%),
            linear-gradient(180deg, #06101d 0%, #0b1220 100%);
        color: #f8fafc;
    }

    .block-container {
        max-width: 1520px;
        padding-top: 1.0rem;
        padding-bottom: 2rem;
        padding-left: 1.8rem;
        padding-right: 1.8rem;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #09111f 0%, #111827 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    h1, h2, h3, h4 {
        color: #ffffff !important;
        letter-spacing: -0.3px;
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

    .card {
        background: rgba(15,23,42,0.76);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 22px;
        padding: 18px 18px 12px 18px;
        box-shadow: 0 10px 28px rgba(0,0,0,0.22);
        backdrop-filter: blur(8px);
        margin-bottom: 18px;
    }

    .kpi {
        background: linear-gradient(145deg, #111827, #1e293b);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 20px;
        padding: 16px 18px;
        min-height: 118px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.26);
    }

    .kpi-label {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-bottom: 8px;
    }

    .kpi-value {
        color: white;
        font-size: 1.85rem;
        font-weight: 800;
        line-height: 1.15;
    }

    .kpi-note {
        color: #cbd5e1;
        font-size: 0.83rem;
        line-height: 1.5;
        margin-top: 6px;
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

    .mini {
        color: #cbd5e1;
        font-size: 0.95rem;
        line-height: 1.7;
        margin-top: 8px;
    }

    .summary {
        background: linear-gradient(145deg, rgba(17,24,39,0.98), rgba(30,41,59,0.98));
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 18px 20px;
        color: #e2e8f0;
        line-height: 1.85;
    }

    .footer-note {
        color: #94a3b8;
        font-size: 0.92rem;
        line-height: 1.7;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPERS
# =========================================================
def validate_columns(df, required_cols, name):
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        st.error(f"Colonnes manquantes dans {name} : {missing}")
        st.stop()


def to_num(series, fill=0):
    return pd.to_numeric(series, errors="coerce").fillna(fill)


def common_layout(fig, height=450, title=None):
    fig.update_layout(
        height=height,
        title=title,
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT),
        margin=dict(l=20, r=20, t=60, b=20),
        legend_title_text="",
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    return fig


def add_metric_columns(df):
    """
    Vraie correction du bug :
    - score_absolu = score brut Google Trends
    - score_normalise = min-max normalization sur le sous-ensemble visible
    - part_du_max = part du meilleur pays visible
    """
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


def get_metric_config(metric_mode):
    if metric_mode == "Score absolu":
        return "score_absolu", "Score Google Trends"
    if metric_mode == "Score normalisé":
        return "score_normalise", "Score normalisé (min-max)"
    return "part_du_max", "Part du maximum (%)"


# =========================================================
# LOAD
# =========================================================
@st.cache_data(show_spinner=False)
def load_data():
    df_time = pd.read_csv(TIME_FILE)
    df_country = pd.read_csv(COUNTRY_FILE)
    df_insights = pd.read_csv(INSIGHTS_FILE)

    validate_columns(df_time, ["date", "mot_cle", "score"], "trends_time_long.csv")
    validate_columns(df_country, ["country", "continent", "iso3", "mot_cle", "score"], "trends_country_enriched.csv")
    validate_columns(df_insights, ["country", "continent", "mot_cle_dominant", "score_max", "score_2eme", "ecart_top2"], "country_insights.csv")

    df_time["date"] = pd.to_datetime(df_time["date"], errors="coerce")
    df_time["score"] = to_num(df_time["score"])

    df_country["country"] = df_country["country"].astype(str).str.strip()
    df_country["continent"] = df_country["continent"].astype(str).str.strip()
    df_country["iso3"] = df_country["iso3"].astype(str).str.strip().str.upper()
    df_country["mot_cle"] = df_country["mot_cle"].astype(str).str.strip()
    df_country["score"] = to_num(df_country["score"])

    df_insights["country"] = df_insights["country"].astype(str).str.strip()
    df_insights["continent"] = df_insights["continent"].astype(str).str.strip()
    df_insights["mot_cle_dominant"] = df_insights["mot_cle_dominant"].astype(str).str.strip()
    df_insights["score_max"] = to_num(df_insights["score_max"])
    df_insights["score_2eme"] = to_num(df_insights["score_2eme"])
    df_insights["ecart_top2"] = to_num(df_insights["ecart_top2"])

    df_country = df_country[df_country["country"].ne("")]
    df_country = df_country[df_country["mot_cle"].ne("")]
    df_country = df_country[df_country["iso3"].ne("NAN")]

    return df_time, df_country, df_insights


df_time, df_country, df_insights = load_data()


# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("Contrôles")

keywords = sorted(df_time["mot_cle"].dropna().unique().tolist())
continents = sorted([c for c in df_country["continent"].dropna().unique().tolist() if c and c.lower() != "nan"])

selected_keyword = st.sidebar.selectbox("Mot-clé principal", keywords)

selected_continents = st.sidebar.multiselect(
    "Continents",
    options=continents,
    default=continents
)

metric_mode = st.sidebar.radio(
    "Métrique d'affichage",
    ["Score absolu", "Score normalisé", "Part du maximum (%)"]
)

top_n = st.sidebar.slider("Top pays", 5, 30, 12, 1)
min_score = st.sidebar.slider("Score minimum", 0, 100, 0, 1)
show_avg_line = st.sidebar.checkbox("Afficher la moyenne globale", value=True)
show_raw = st.sidebar.checkbox("Afficher les données brutes", value=False)


# =========================================================
# FILTERS
# =========================================================
country_filtered = df_country.copy()
insights_filtered = df_insights.copy()

if selected_continents:
    country_filtered = country_filtered[country_filtered["continent"].isin(selected_continents)]
    insights_filtered = insights_filtered[insights_filtered["continent"].isin(selected_continents)]

country_filtered = country_filtered[country_filtered["score"] >= min_score]

selected_country_df = country_filtered[country_filtered["mot_cle"] == selected_keyword].copy()
selected_country_df = add_metric_columns(selected_country_df)

metric_col, metric_label = get_metric_config(metric_mode)

if not selected_country_df.empty:
    selected_country_df = selected_country_df.sort_values(metric_col, ascending=False)

time_keyword_df = df_time[df_time["mot_cle"] == selected_keyword].copy()


# =========================================================
# GLOBAL METRICS
# =========================================================
nb_pays = int(insights_filtered["country"].nunique()) if not insights_filtered.empty else 0

if not insights_filtered.empty:
    dom_counts = insights_filtered["mot_cle_dominant"].value_counts()
    global_top_keyword = dom_counts.idxmax()
    global_top_count = int(dom_counts.max())

    gap_row = insights_filtered.sort_values("ecart_top2", ascending=False).iloc[0]
    strongest_country = gap_row["country"]
    strongest_gap = int(gap_row["ecart_top2"])
else:
    global_top_keyword = "N/A"
    global_top_count = 0
    strongest_country = "N/A"
    strongest_gap = 0

if not selected_country_df.empty:
    top_country = selected_country_df.iloc[0]["country"]
    top_value = float(selected_country_df.iloc[0][metric_col])
    mean_value = float(selected_country_df[metric_col].mean())
    median_value = float(selected_country_df[metric_col].median())
else:
    top_country = "N/A"
    top_value = 0
    mean_value = 0
    median_value = 0


# =========================================================
# HEADER
# =========================================================
st.markdown(f"""
<div class="hero">
    <div class="hero-title">Google Trends Ultra Dashboard</div>
    <div class="hero-sub">
        Dashboard analytique avancé pour comparer des mots-clés selon leur évolution dans le temps,
        leur répartition mondiale et leur intensité relative par pays.
        Mot-clé étudié : <b>{selected_keyword}</b> — métrique affichée : <b>{metric_mode}</b>.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info">
<b>Lecture correcte des scores :</b><br>
• Le <b>score absolu</b> correspond au score Google Trends brut.<br>
• Le <b>score normalisé</b> est recalculé sur les pays visibles après filtres, entre le minimum et le maximum observés.<br>
• La <b>part du maximum</b> mesure le poids d’un pays par rapport au meilleur pays visible.<br>
• Ainsi, ces trois métriques sont maintenant réellement différentes et utilisables.
</div>
""", unsafe_allow_html=True)


# =========================================================
# KPI
# =========================================================
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi">
        <div class="kpi-label">🌍 Pays analysés</div>
        <div class="kpi-value">{nb_pays}</div>
        <div class="kpi-note">Après application des filtres</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi">
        <div class="kpi-label">🏆 Mot-clé dominant global</div>
        <div class="kpi-value">{global_top_keyword}</div>
        <div class="kpi-note">Dominant dans {global_top_count} pays</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi">
        <div class="kpi-label">📌 Leader pour {selected_keyword}</div>
        <div class="kpi-value">{top_country}</div>
        <div class="kpi-note">{metric_label} : {top_value:.1f}</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi">
        <div class="kpi-label">⚡ Plus fort écart top 2</div>
        <div class="kpi-value">{strongest_gap}</div>
        <div class="kpi-note">{strongest_country}</div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "Vue générale",
    "Carte & pays",
    "Comparaisons",
    "Résumé & données"
])


# =========================================================
# TAB 1
# =========================================================
with tab1:
    c_left, c_right = st.columns([1.5, 1])

    with c_left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Évolution temporelle des mots-clés")

        fig_time = px.line(
            df_time.sort_values("date"),
            x="date",
            y="score",
            color="mot_cle",
            line_shape="spline",
            title="Popularité relative dans le temps"
        )

        if show_avg_line:
            avg_curve = df_time.groupby("date", as_index=False)["score"].mean()
            fig_time.add_trace(go.Scatter(
                x=avg_curve["date"],
                y=avg_curve["score"],
                mode="lines",
                name="Moyenne",
                line=dict(width=3, dash="dash")
            ))

        common_layout(fig_time, height=500)
        fig_time.update_layout(hovermode="x unified")
        fig_time.update_xaxes(title="Date")
        fig_time.update_yaxes(title="Score Trends")
        st.plotly_chart(fig_time, use_container_width=True)

        st.markdown("""
        <div class="mini">
        Cette vue permet de repérer les pics d’intérêt, les phases de stabilité et les éventuels décrochages.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(f"Indicateurs — {selected_keyword}")

        if not time_keyword_df.empty:
            latest_date = time_keyword_df["date"].max()
            max_time = float(time_keyword_df["score"].max())
            mean_time = float(time_keyword_df["score"].mean())
            last_value = float(time_keyword_df.sort_values("date").iloc[-1]["score"])
        else:
            latest_date = None
            max_time = mean_time = last_value = 0

        st.metric("Max temporel", f"{max_time:.1f}")
        st.metric("Moyenne temporelle", f"{mean_time:.1f}")
        st.metric("Dernière valeur", f"{last_value:.1f}")
        st.metric("Moyenne géographique", f"{mean_value:.1f}")

        if latest_date is not None:
            st.caption(f"Dernière date observée : {latest_date.strftime('%d/%m/%Y')}")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Répartition par continent")

        if not selected_country_df.empty:
            continent_df = (
                selected_country_df.groupby("continent", as_index=False)[metric_col]
                .mean()
                .sort_values(metric_col, ascending=False)
            )

            fig_cont = px.bar(
                continent_df,
                x="continent",
                y=metric_col,
                text=metric_col,
                color=metric_col,
                color_continuous_scale="Blues",
                title=f"Moyenne continentale — {metric_mode}"
            )
            common_layout(fig_cont, height=360)
            fig_cont.update_layout(coloraxis_showscale=False)
            fig_cont.update_traces(texttemplate="%{text:.1f}", textposition="outside")
            fig_cont.update_xaxes(title="Continent")
            fig_cont.update_yaxes(title=metric_label)
            st.plotly_chart(fig_cont, use_container_width=True)
        else:
            st.warning("Aucune donnée continentale disponible.")

        st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# TAB 2
# =========================================================
with tab2:
    map_col, rank_col = st.columns([1.2, 0.8])

    with map_col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(f"Carte mondiale — {selected_keyword}")

        df_map = selected_country_df.dropna(subset=["iso3"]).copy()

        if not df_map.empty:
            fig_map = px.choropleth(
                df_map,
                locations="iso3",
                color=metric_col,
                hover_name="country",
                hover_data={
                    "iso3": True,
                    "score_absolu": ":.1f",
                    "score_normalise": ":.1f",
                    "part_du_max": ":.1f",
                    "continent": True,
                },
                color_continuous_scale=[
                    [0.00, "#dbeafe"],
                    [0.20, "#93c5fd"],
                    [0.40, "#60a5fa"],
                    [0.60, "#3b82f6"],
                    [0.80, "#2563eb"],
                    [1.00, "#1d4ed8"],
                ],
                projection="natural earth",
                title=f"Répartition mondiale — {metric_mode}"
            )

            fig_map.update_layout(
                height=640,
                paper_bgcolor=PAPER_BG,
                font=dict(color=FONT),
                margin=dict(l=10, r=10, t=60, b=10),
                coloraxis_colorbar=dict(
                    title=metric_label,
                    thickness=14,
                    len=0.75
                ),
                geo=dict(
                    bgcolor="#07111d",
                    showframe=False,
                    showcoastlines=True,
                    coastlinecolor="rgba(255,255,255,0.20)",
                    showcountries=True,
                    countrycolor="rgba(255,255,255,0.20)",
                    showland=True,
                    landcolor="#162235",
                    showocean=True,
                    oceancolor="#04101b",
                    lakecolor="#04101b",
                    projection_type="natural earth"
                )
            )

            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("Carte indisponible.")
        st.markdown('</div>', unsafe_allow_html=True)

    with rank_col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(f"Top {top_n} pays")

        df_bar = selected_country_df.head(top_n).copy()

        if not df_bar.empty:
            fig_bar = px.bar(
                df_bar,
                x=metric_col,
                y="country",
                orientation="h",
                text=metric_col,
                color=metric_col,
                color_continuous_scale="Blues",
                title=f"Classement — {metric_mode}"
            )
            common_layout(fig_bar, height=640)
            fig_bar.update_layout(coloraxis_showscale=False)
            fig_bar.update_yaxes(autorange="reversed", title="Pays")
            fig_bar.update_xaxes(title=metric_label)
            fig_bar.update_traces(texttemplate="%{text:.1f}", textposition="outside")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("Aucun pays à afficher.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Nuage d’analyse : score vs écart de domination")

    if not selected_country_df.empty and not insights_filtered.empty:
        scatter_df = selected_country_df.merge(
            insights_filtered[["country", "ecart_top2", "mot_cle_dominant"]],
            on="country",
            how="left"
        )
        scatter_df["statut"] = np.where(
            scatter_df["mot_cle_dominant"] == selected_keyword,
            "Dominant",
            "Secondaire"
        )

        fig_scatter = px.scatter(
            scatter_df,
            x=metric_col,
            y="ecart_top2",
            size="score_absolu",
            color="continent",
            symbol="statut",
            hover_name="country",
            title="Position des pays selon intensité et domination"
        )
        common_layout(fig_scatter, height=480)
        fig_scatter.update_xaxes(title=metric_label)
        fig_scatter.update_yaxes(title="Écart top 2")
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.warning("Scatter indisponible.")
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# TAB 3
# =========================================================
with tab3:
    left_cmp, right_cmp = st.columns(2)

    with left_cmp:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Nombre de pays dominés par mot-clé")

        if not insights_filtered.empty:
            df_dom = insights_filtered["mot_cle_dominant"].value_counts().reset_index()
            df_dom.columns = ["mot_cle", "nb_pays"]

            fig_dom = px.bar(
                df_dom,
                x="mot_cle",
                y="nb_pays",
                text="nb_pays",
                color="nb_pays",
                color_continuous_scale="Blues",
                title="Dominance géographique"
            )
            common_layout(fig_dom, height=420)
            fig_dom.update_layout(coloraxis_showscale=False)
            fig_dom.update_xaxes(title="Mot-clé")
            fig_dom.update_yaxes(title="Nombre de pays")
            fig_dom.update_traces(textposition="outside")
            st.plotly_chart(fig_dom, use_container_width=True)
        else:
            st.warning("Aucune donnée de dominance.")
        st.markdown('</div>', unsafe_allow_html=True)

    with right_cmp:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Distribution des scores")

        if not country_filtered.empty:
            fig_box = px.box(
                country_filtered,
                x="mot_cle",
                y="score",
                color="mot_cle",
                points="outliers",
                title="Dispersion des scores par mot-clé"
            )
            common_layout(fig_box, height=420)
            fig_box.update_layout(showlegend=False)
            fig_box.update_xaxes(title="Mot-clé")
            fig_box.update_yaxes(title="Score Trends")
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.warning("Aucune distribution disponible.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Heatmap pays × mots-clés")

    heatmap_base = country_filtered.copy()
    top_heat_countries = (
        heatmap_base.groupby("country")["score"]
        .max()
        .sort_values(ascending=False)
        .head(15)
        .index.tolist()
    )
    heatmap_df = heatmap_base[heatmap_base["country"].isin(top_heat_countries)].copy()

    if not heatmap_df.empty:
        pivot = heatmap_df.pivot_table(
            index="country",
            columns="mot_cle",
            values="score",
            aggfunc="mean",
            fill_value=0
        )

        fig_heat = px.imshow(
            pivot,
            text_auto=".0f",
            aspect="auto",
            color_continuous_scale="Blues",
            title="Intensité relative par pays et par mot-clé"
        )
        fig_heat.update_layout(
            height=560,
            paper_bgcolor=PAPER_BG,
            plot_bgcolor=PLOT_BG,
            font=dict(color=FONT),
            margin=dict(l=20, r=20, t=60, b=20)
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.warning("Heatmap indisponible.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(f"Radar des 5 premiers pays — {selected_keyword}")

    radar_df = selected_country_df.head(5).copy()

    if not radar_df.empty:
        labels = radar_df["country"].tolist()
        values = radar_df[metric_col].tolist()

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=labels + [labels[0]],
            fill="toself",
            name=selected_keyword
        ))
        fig_radar.update_layout(
            height=500,
            paper_bgcolor=PAPER_BG,
            plot_bgcolor=PLOT_BG,
            font=dict(color=FONT),
            polar=dict(
                bgcolor=PLOT_BG,
                radialaxis=dict(visible=True, gridcolor=GRID, linecolor=GRID),
                angularaxis=dict(gridcolor=GRID, linecolor=GRID)
            ),
            margin=dict(l=20, r=20, t=60, b=20),
            title=f"Profil des pays — {metric_mode}"
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.warning("Radar indisponible.")
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# TAB 4
# =========================================================
with tab4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Résumé automatique")

    if not selected_country_df.empty:
        if not insights_filtered.empty:
            total_countries = insights_filtered["country"].nunique()
            selected_dom_count = int((insights_filtered["mot_cle_dominant"] == selected_keyword).sum())
            selected_dom_share = (selected_dom_count / total_countries * 100) if total_countries else 0
        else:
            selected_dom_count = 0
            selected_dom_share = 0

        top3 = selected_country_df.head(3)["country"].tolist()
        top3_txt = ", ".join(top3) if top3 else "N/A"

        st.markdown(f"""
        <div class="summary">
        <b>Lecture analytique :</b><br><br>

        • Le mot-clé sélectionné est <b>{selected_keyword}</b>.<br>
        • Le pays leader selon la métrique <b>{metric_mode}</b> est <b>{top_country}</b>, avec une valeur de <b>{top_value:.1f}</b>.<br>
        • Les trois pays les plus associés à ce mot-clé sont <b>{top3_txt}</b>.<br>
        • La moyenne observée sur la métrique choisie est de <b>{mean_value:.1f}</b>, pour une médiane de <b>{median_value:.1f}</b>.<br>
        • Au niveau global, <b>{global_top_keyword}</b> est le mot-clé qui domine le plus de pays, avec <b>{global_top_count}</b> territoires.<br>
        • <b>{selected_keyword}</b> arrive en tête dans <b>{selected_dom_count}</b> pays, soit <b>{selected_dom_share:.1f}%</b> des pays visibles.<br>
        • Le pays présentant la domination la plus nette entre le 1er et le 2e mot-clé est <b>{strongest_country}</b>, avec un écart de <b>{strongest_gap}</b>.<br><br>

        <b>Formulation propre pour l’oral :</b><br>
        “Les résultats montrent des niveaux d’intérêt relatifs. Le score absolu donne la lecture brute de Google Trends,
        le score normalisé permet une comparaison plus lisible dans le sous-ensemble affiché,
        et la part du maximum mesure l’écart au leader. On observe ainsi à la fois la hiérarchie géographique,
        l’intensité relative et la domination comparative par pays.”
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Résumé indisponible.")
    st.markdown('</div>', unsafe_allow_html=True)

    if show_raw:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Données brutes")

        t1, t2, t3, t4 = st.tabs([
            "Séries temporelles",
            "Données pays filtrées",
            "Pays du mot-clé",
            "Insights"
        ])

        with t1:
            st.dataframe(df_time, use_container_width=True, height=320)

        with t2:
            st.dataframe(country_filtered, use_container_width=True, height=320)

        with t3:
            st.dataframe(selected_country_df, use_container_width=True, height=320)

        with t4:
            st.dataframe(insights_filtered, use_container_width=True, height=320)

        st.markdown('</div>', unsafe_allow_html=True)


st.markdown("""
<div class="footer-note">
Les scores Google Trends ne sont pas des volumes absolus. Ils servent à comparer des intensités relatives d’intérêt.
La normalisation ajoutée ici est une transformation analytique interne au dashboard pour améliorer la lecture comparative.
</div>
""", unsafe_allow_html=True)