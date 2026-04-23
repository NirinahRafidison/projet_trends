# 📊 Analyse Google Trends de 5 mots-clés

## 🎯 Objectif du projet

Ce projet vise à analyser et comparer l’intérêt relatif pour 5 mots-clés à l’échelle mondiale, en combinant :

- des données issues de Google Trends
- un enrichissement par métadonnées pays (type Kaggle)
- des visualisations interactives via Streamlit

L’objectif est de construire une pipeline data complète allant de la collecte à l’interprétation.

---

## 🧠 Problématique

Comment comparer l’intérêt pour différents mots-clés :

- dans le temps  
- selon les pays  
- et selon les zones géographiques  

tout en tenant compte du fait que Google Trends fournit des données relatives (0–100) et non absolues ?

---

## 🏗️ Architecture du projet

bash projet_trends/ │ ├── data/ │   ├── raw/                  # données brutes Google Trends │   ├── processed/            # datasets nettoyés et enrichis │   └── kaggle/               # métadonnées pays │ ├── scripts/ │   ├── collect_trends.py     # collecte Google Trends │   ├── clean_merge.py        # nettoyage + enrichissement │   ├── country_insights.py   # calcul des indicateurs │   └── slides_graphs.py      # génération des graphes │ ├── app/ │   └── streamlit_app.py      # application interactive │ ├── outputs/ │   └── figures/              # graphes pour les slides │ ├── requirements.txt └── README.md 

---

## 🔄 Pipeline de traitement

### 1. Collecte des données

Script : collect_trends.py

- récupération via pytrends
- 5 mots-clés :
  - intelligence artificielle
  - crypto
  - Netflix
  - Tesla
  - ChatGPT

Deux datasets :

- trends_time.csv
  - évolution temporelle (3 ans)

- trends_country.csv
  - distribution géographique (1 an)

---

### 2. Nettoyage et structuration

Script : clean_merge.py

Transformations :

- conversion en format long
- normalisation des noms de pays
- mapping FR → EN
- gestion des valeurs manquantes

---

### 3. Enrichissement des données

Ajout de métadonnées pays :

- code ISO3
- continent
- région

👉 Permet :

- cartes interactives
- agrégations géographiques
- analyses comparatives

---

### 4. Calcul des indicateurs

Script : country_insights.py

Variables créées :

- mot_cle_dominant
- score_max
- score_2eme
- ecart_top2

👉 Permet d’identifier :

- le mot-clé dominant par pays
- l’intensité de domination
- la concurrence entre mots-clés

---

### 5. Visualisation

#### Application Streamlit

L’application permet :

- sélection de mots-clés
- filtrage par continent
- visualisation interactive :
  - courbes temporelles
  - top pays
  - carte mondiale
  - indicateurs clés

---

## 📊 Graphes utilisés pour les slides

1. Search Momentum
→ montre l’évolution globale et les pics d’intérêt dans le temps

2. Monthly Heatmap
→ met en évidence les périodes fortes et les tendances saisonnières

3. World Leaders
→ visualise le mot-clé dominant dans chaque pays

4. Popularity vs Dominance
→ compare la popularité d’un mot-clé et sa domination locale

5. Continental Leaders
→ identifie le mot-clé le plus fort en moyenne par continent


## ⚠️ Limites du projet

- Google Trends fournit un score relatif (0–100)  
- pas de volume absolu de recherche  
- dépendance à une API non officielle (pytrends)  
- qualité variable des données pays  

---

## 🚀 Lancer le projet

### 1. Installer les dépendances

bash pip install -r requirements.txt 

### 2. Collecter les données

bash python scripts/collect_trends.py 

### 3. Nettoyer et enrichir

bash python scripts/clean_merge.py 

### 4. Générer les insights

bash python scripts/country_insights.py 

### 5. Lancer l’application

bash python -m streamlit run app/streamlit_app.py 

---

## 📌 Résultats principaux

- certains mots-clés dominent largement selon les zones géographiques  
- la popularité varie fortement selon les pays  
- certains mots-clés présentent une distribution homogène  
- d’autres sont très localisés  

---

## 🧠 Apports du projet

Ce projet illustre :

- la construction d’une pipeline data complète  
- l’intégration de sources multiples  
- la transformation de données brutes en indicateurs  
- la visualisation et l’interprétation de données  

---

## 🔮 Améliorations possibles

- ajout d’autres mots-clés  
- intégration de nouvelles sources de données  
- analyse de tendances plus avancée  
- prévision (time series)  
- déploiement web de l’application  

---

## 👤 Auteur

Projet réalisé dans le cadre d’un projet académique en data
