from pathlib import Path
import time
import pandas as pd
from pytrends.request import TrendReq

KEYWORDS = [
    "intelligence artificielle",
    "crypto",
    "Netflix",
    "Tesla",
    "ChatGPT"
]

TIMEFRAME = "2023-01-01 2026-01-01"
TIMEFRAME_COUNTRY = "2025-01-01 2026-01-01"
GEO = ""
HL = "fr-FR"

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

TIME_OUTPUT = RAW_DIR / "trends_time.csv"
COUNTRY_OUTPUT = RAW_DIR / "trends_country.csv"


def connect_trends():
    return TrendReq(hl=HL, tz=360)


def fetch_interest_over_time(pytrends, keywords):
    pytrends.build_payload(
        kw_list=keywords,
        cat=0,
        timeframe=TIMEFRAME,
        geo=GEO,
        gprop=""
    )

    df_time = pytrends.interest_over_time()

    if df_time.empty:
        raise ValueError("Aucune donnée temporelle récupérée.")

    if "isPartial" in df_time.columns:
        df_time = df_time.drop(columns=["isPartial"])

    df_time = df_time.reset_index()
    return df_time


def fetch_interest_by_country(pytrends, keywords):
    all_country_data = []

    for keyword in keywords:
        print(f"Récupération des données pays pour : {keyword}")

        pytrends.build_payload(
            kw_list=[keyword],
            cat=0,
            timeframe=TIMEFRAME_COUNTRY,
            geo=GEO,
            gprop=""
        )

        df_country = pytrends.interest_by_region(
            resolution="COUNTRY",
            inc_low_vol=True,
            inc_geo_code=False
        )

        if df_country.empty:
            print(f"Aucune donnée pour {keyword}")
            continue

        df_country = df_country.reset_index()

        first_col = df_country.columns[0]
        df_country = df_country.rename(columns={first_col: "country"})

        if keyword not in df_country.columns:
            print(f"Colonne introuvable pour {keyword}")
            continue

        df_country = df_country.rename(columns={keyword: "score"})
        df_country["mot_cle"] = keyword
        df_country = df_country[["country", "mot_cle", "score"]]

        all_country_data.append(df_country)

        time.sleep(3)

    if not all_country_data:
        raise ValueError("Aucune donnée géographique récupérée.")

    final_df = pd.concat(all_country_data, ignore_index=True)
    return final_df


def save_csv(df, output_path):
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Fichier enregistré : {output_path}")


def main():
    try:
        pytrends = connect_trends()

        print("Récupération des données temporelles...")
        df_time = fetch_interest_over_time(pytrends, KEYWORDS)
        save_csv(df_time, TIME_OUTPUT)

        time.sleep(3)

        print("Récupération des données par pays...")
        df_country = fetch_interest_by_country(pytrends, KEYWORDS)
        save_csv(df_country, COUNTRY_OUTPUT)

        print("\nCollecte terminée.")
        print("\nAperçu trends_time :")
        print(df_time.head())

        print("\nAperçu trends_country :")
        print(df_country.head())

    except Exception as e:
        print("Erreur pendant la collecte :", e)


if __name__ == "__main__":
    main()