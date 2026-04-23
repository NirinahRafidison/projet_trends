import pandas as pd
from pathlib import Path
import unicodedata

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
KAGGLE_DIR = BASE_DIR / "data" / "kaggle"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# FONCTION DE NORMALISATION
# =========================
def normalize_text(text):
    text = str(text).strip().lower()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    text = " ".join(text.split())
    return text

# =========================
# 1. TIME SERIES
# =========================
time_input = RAW_DIR / "trends_time.csv"
time_output = PROCESSED_DIR / "trends_time_long.csv"

df_time = pd.read_csv(time_input)

df_time_long = df_time.melt(
    id_vars=["date"],
    var_name="mot_cle",
    value_name="score"
)

df_time_long.to_csv(time_output, index=False)
print("trends_time_long.csv créé")

# =========================
# 2. COUNTRY DATA
# =========================
country_input = RAW_DIR / "trends_country.csv"
country_output = PROCESSED_DIR / "trends_country_long.csv"

df_country_long = pd.read_csv(country_input)

df_country_long.columns = [c.strip().lower() for c in df_country_long.columns]
df_country_long["country"] = df_country_long["country"].astype(str).str.strip()
df_country_long["mot_cle"] = df_country_long["mot_cle"].astype(str).str.strip()
df_country_long["score"] = pd.to_numeric(df_country_long["score"], errors="coerce").fillna(0)

# mapping FR -> EN
mapping_fr_to_en = {
    "afghanistan": "afghanistan",
    "afrique du sud": "south africa",
    "albanie": "albania",
    "algerie": "algeria",
    "allemagne": "germany",
    "arabie saoudite": "saudi arabia",
    "argentine": "argentina",
    "armenie": "armenia",
    "australie": "australia",
    "autriche": "austria",
    "belgique": "belgium",
    "bielorussie": "belarus",
    "bolivie": "bolivia",
    "bresil": "brazil",
    "bulgarie": "bulgaria",
    "cambodge": "cambodia",
    "cameroun": "cameroon",
    "canada": "canada",
    "chili": "chile",
    "chine": "china",
    "colombie": "colombia",
    "coree du sud": "south korea",
    "croatie": "croatia",
    "danemark": "denmark",
    "egypte": "egypt",
    "emirats arabes unis": "united arab emirates",
    "espagne": "spain",
    "estonie": "estonia",
    "etats-unis": "united states",
    "finlande": "finland",
    "france": "france",
    "grece": "greece",
    "hongrie": "hungary",
    "inde": "india",
    "indonesie": "indonesia",
    "irlande": "ireland",
    "islande": "iceland",
    "israel": "israel",
    "italie": "italy",
    "japon": "japan",
    "kazakhstan": "kazakhstan",
    "kenya": "kenya",
    "luxembourg": "luxembourg",
    "malaisie": "malaysia",
    "maroc": "morocco",
    "mexique": "mexico",
    "nigeria": "nigeria",
    "norvege": "norway",
    "nouvelle-zelande": "new zealand",
    "pakistan": "pakistan",
    "pays-bas": "netherlands",
    "perou": "peru",
    "philippines": "philippines",
    "pologne": "poland",
    "portugal": "portugal",
    "qatar": "qatar",
    "roumanie": "romania",
    "royaume-uni": "united kingdom",
    "russie": "russia",
    "singapour": "singapore",
    "slovaquie": "slovakia",
    "slovenie": "slovenia",
    "suede": "sweden",
    "suisse": "switzerland",
    "taiwan": "taiwan",
    "tchequie": "czechia",
    "thailande": "thailand",
    "tunisie": "tunisia",
    "turquie": "turkey",
    "ukraine": "ukraine",
    "vietnam": "vietnam"
}

df_country_long["country_clean"] = df_country_long["country"].apply(normalize_text)
df_country_long["country_clean"] = df_country_long["country_clean"].replace(mapping_fr_to_en)

df_country_long.to_csv(country_output, index=False)
print("trends_country_long.csv créé")

# =========================
# 3. METADATA
# =========================
metadata_input = KAGGLE_DIR / "country_metadata.csv"
output_enriched = PROCESSED_DIR / "trends_country_enriched.csv"

df_meta = pd.read_csv(metadata_input)
df_meta.columns = [c.strip().lower() for c in df_meta.columns]
df_meta["country"] = df_meta["country"].astype(str).str.strip()
df_meta["country_clean"] = df_meta["country"].apply(normalize_text)

# =========================
# 4. MERGE SUR country_clean
# =========================
df_enriched = df_country_long.merge(
    df_meta[["country_clean", "iso3", "continent"]],
    on="country_clean",
    how="left"
)

df_enriched.to_csv(output_enriched, index=False)

print("\ntrends_country_enriched.csv créé")
print(df_enriched.head(20))

print("\nValeurs manquantes :")
print(df_enriched[["iso3", "continent"]].isna().sum())

# =========================
# 5. PAYS NON MATCHÉS
# =========================
unmatched = (
    df_enriched[df_enriched["iso3"].isna()]["country"]
    .drop_duplicates()
    .sort_values()
)

print("\nPays non matchés (aperçu) :")
print(unmatched.head(50).to_list())
print(f"\nNombre de pays non matchés : {unmatched.shape[0]}")