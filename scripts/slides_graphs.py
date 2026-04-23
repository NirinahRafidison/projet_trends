from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# =========================================================
# PATHS
# =========================================================
BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"
PLOTLY_DIR = OUTPUT_DIR / "figures_premium_dark"
MPL_DIR = OUTPUT_DIR / "figures_academic"

PLOTLY_DIR.mkdir(parents=True, exist_ok=True)
MPL_DIR.mkdir(parents=True, exist_ok=True)

TIME_FILE = PROCESSED_DIR / "trends_time_long.csv"
COUNTRY_FILE = PROCESSED_DIR / "trends_country_enriched.csv"
INSIGHTS_FILE = PROCESSED_DIR / "country_insights.csv"

# =========================================================
# LOAD
# =========================================================
df_time = pd.read_csv(TIME_FILE)
df_country = pd.read_csv(COUNTRY_FILE)
df_insights = pd.read_csv(INSIGHTS_FILE)

# =========================================================
# CLEAN
# =========================================================
df_time["date"] = pd.to_datetime(df_time["date"], errors="coerce")
df_time["score"] = pd.to_numeric(df_time["score"], errors="coerce").fillna(0)

df_country["score"] = pd.to_numeric(df_country["score"], errors="coerce").fillna(0)
df_country["continent"] = df_country["continent"].fillna("Inconnu")
df_country["iso3"] = df_country["iso3"].fillna("")

df_insights["score_max"] = pd.to_numeric(df_insights["score_max"], errors="coerce").fillna(0)
df_insights["score_2eme"] = pd.to_numeric(df_insights["score_2eme"], errors="coerce").fillna(0)
df_insights["ecart_top2"] = pd.to_numeric(df_insights["ecart_top2"], errors="coerce").fillna(0)
df_insights["continent"] = df_insights["continent"].fillna("Inconnu")
df_insights["iso3"] = df_insights["iso3"].fillna("")
df_insights["country"] = df_insights["country"].fillna("Unknown")

# =========================================================
# STYLE
# =========================================================
COLORS = {
    "ChatGPT": "#60A5FA",
    "crypto": "#F87171",
    "Netflix": "#34D399",
    "Tesla": "#A78BFA",
    "intelligence artificielle": "#FB923C"
}

SLIDE_W = 1600
SLIDE_H = 900
DARK_BG = "#0B1020"
CARD_BG = "#121A2B"
GRID = "#263042"
FONT = "#E5E7EB"

def apply_plotly_dark(fig, title, x_title="", y_title=""):
    fig.update_layout(
        title=title,
        title_font_size=26,
        font=dict(size=15, color=FONT, family="Arial"),
        paper_bgcolor=DARK_BG,
        plot_bgcolor=CARD_BG,
        margin=dict(l=70, r=70, t=90, b=70),
        xaxis_title=x_title,
        yaxis_title=y_title,
        hoverlabel=dict(
            bgcolor="#111827",
            font_size=13,
            font_color="white"
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=FONT)
        )
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    return fig

def safe_save_plotly(fig, filename):
    out = PLOTLY_DIR / filename
    try:
        fig.write_image(str(out), width=SLIDE_W, height=SLIDE_H, scale=2)
        print(f"[OK] {filename}")
    except Exception as e:
        print(f"[ERREUR] {filename} -> {e}")

def safe_save_mpl(fig, filename):
    out = MPL_DIR / filename
    try:
        fig.savefig(out, dpi=220, bbox_inches="tight", facecolor="white")
        print(f"[OK] {filename}")
    except Exception as e:
        print(f"[ERREUR] {filename} -> {e}")
    finally:
        plt.close(fig)

# =========================================================
# PREP TIME
# =========================================================
df_line = df_time.sort_values(["mot_cle", "date"]).copy()
df_line["score_lisse"] = (
    df_line.groupby("mot_cle")["score"]
    .transform(lambda s: s.rolling(window=6, min_periods=1).mean())
)

# =========================================================
# FIGURE 1 - LINE
# =========================================================
try:
    fig1 = px.line(
        df_line,
        x="date",
        y="score_lisse",
        color="mot_cle",
        color_discrete_map=COLORS
    )
    fig1.update_traces(line=dict(width=4))
    fig1 = apply_plotly_dark(fig1, "Search Momentum", "Date", "Smoothed score")
    fig1.update_layout(hovermode="x unified")

    last_points = (
        df_line.sort_values("date")
        .groupby("mot_cle", as_index=False)
        .tail(1)
    )
    for _, row in last_points.iterrows():
        fig1.add_annotation(
            x=row["date"],
            y=row["score_lisse"],
            text=row["mot_cle"],
            showarrow=False,
            xshift=10,
            font=dict(size=12, color=COLORS.get(row["mot_cle"], FONT))
        )

    safe_save_plotly(fig1, "01_search_momentum_dark.png")
except Exception as e:
    print(f"[ERREUR FIG1] {e}")

# =========================================================
# FIGURE 2 - HEATMAP
# =========================================================
try:
    df_heat = df_time.copy()
    df_heat["year_month"] = df_heat["date"].dt.to_period("M").astype(str)
    df_heat = df_heat.groupby(["mot_cle", "year_month"], as_index=False)["score"].mean()
    heat_pivot = df_heat.pivot(index="mot_cle", columns="year_month", values="score").fillna(0)

    fig2 = go.Figure(
        data=go.Heatmap(
            z=heat_pivot.values,
            x=heat_pivot.columns,
            y=heat_pivot.index,
            colorscale="YlOrRd"
        )
    )
    fig2 = apply_plotly_dark(fig2, "Monthly Heatmap", "Month", "Keyword")
    fig2.update_xaxes(tickangle=-45)

    safe_save_plotly(fig2, "02_monthly_heatmap_dark.png")
except Exception as e:
    print(f"[ERREUR FIG2] {e}")

# =========================================================
# FIGURE 3 - MAP
# =========================================================
try:
    df_map = df_insights[df_insights["iso3"].str.len() == 3].copy()

    fig3 = px.choropleth(
        df_map,
        locations="iso3",
        color="mot_cle_dominant",
        hover_name="country",
        hover_data=["score_max", "score_2eme", "ecart_top2"],
        color_discrete_map=COLORS,
        projection="natural earth"
    )
    fig3 = apply_plotly_dark(fig3, "World Leaders")

    fig3.update_layout(
        geo=dict(
            bgcolor=DARK_BG,
            showframe=False,
            showcoastlines=True,
            coastlinecolor="#475569",
            showcountries=True,
            countrycolor="#334155"
        )
    )

    safe_save_plotly(fig3, "03_world_leaders_dark.png")
except Exception as e:
    print(f"[ERREUR FIG3] {e}")

# =========================================================
# FIGURE 4 - SCATTER
# =========================================================
try:
    fig4 = px.scatter(
        df_insights,
        x="score_max",
        y="ecart_top2",
        color="mot_cle_dominant",
        hover_name="country",
        size="score_max",
        size_max=26,
        color_discrete_map=COLORS
    )
    fig4 = apply_plotly_dark(fig4, "Popularity vs Dominance", "Top score", "Gap vs second")
    fig4.update_traces(marker=dict(line=dict(width=1, color="white"), opacity=0.82))

    safe_save_plotly(fig4, "04_popularity_vs_dominance_dark.png")
except Exception as e:
    print(f"[ERREUR FIG4] {e}")

# =========================================================
# FIGURE 5 - CONTINENT LEADERS
# =========================================================
try:
    df_cont = (
        df_country.groupby(["continent", "mot_cle"], as_index=False)["score"]
        .mean()
    )
    idx = df_cont.groupby("continent")["score"].idxmax()
    df_cont_leaders = df_cont.loc[idx].copy().sort_values("score", ascending=True)

    fig5 = px.bar(
        df_cont_leaders,
        x="score",
        y="continent",
        orientation="h",
        text="score",
        color="mot_cle",
        color_discrete_map=COLORS
    )
    fig5 = apply_plotly_dark(fig5, "Continental Leaders", "Average score", "Continent")
    fig5.update_traces(texttemplate="%{text:.1f}", textposition="outside")

    safe_save_plotly(fig5, "05_continental_leaders_dark.png")
except Exception as e:
    print(f"[ERREUR FIG5] {e}")

print("\nTerminé.")