import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"

inp = PROCESSED_DIR / "trends_country_enriched.csv"
out = PROCESSED_DIR / "country_insights.csv"

df = pd.read_csv(inp)

# colonnes utiles
cols = ["country", "iso3", "continent", "mot_cle", "score"]
df = df[cols].copy()

# types
df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0)

# tri + rang par pays
df = df.sort_values(["country", "score"], ascending=[True, False])
df["rank"] = df.groupby("country")["score"].rank(method="first", ascending=False)

# top 1
top1 = df[df["rank"] == 1].copy()
top1 = top1.rename(columns={
    "mot_cle": "mot_cle_dominant",
    "score": "score_max"
})

# top 2
top2 = df[df["rank"] == 2][["country", "score"]].copy()
top2 = top2.rename(columns={"score": "score_2eme"})

# fusion
res = top1.merge(top2, on="country", how="left")

# écart
res["score_2eme"] = res["score_2eme"].fillna(0)
res["ecart_top2"] = res["score_max"] - res["score_2eme"]

# colonnes finales
res = res[
    ["country", "iso3", "continent",
     "mot_cle_dominant", "score_max", "score_2eme", "ecart_top2"]
]

res.to_csv(out, index=False)

print("country_insights.csv créé")
print(res.head(10))
print("\nNb pays :", res["country"].nunique())
print("\nDominance :")
print(res["mot_cle_dominant"].value_counts())