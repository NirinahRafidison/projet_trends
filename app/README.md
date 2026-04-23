Voici une version propre, claire et directement réutilisable dans ton `README.md`.

---

# Google Trends Ultra Dashboard

## Présentation

Cette application Streamlit permet d’explorer et de comparer plusieurs mots-clés issus de Google Trends selon trois angles d’analyse :

* l’évolution temporelle de leur popularité
* leur répartition géographique par pays
* leur domination relative par rapport aux autres mots-clés

L’objectif du dashboard est de produire une visualisation lisible, analytique et exploitable dans un cadre académique, professionnel ou de soutenance.

---

## Objectif du projet

Le projet vise à transformer des données Google Trends en un tableau de bord interactif permettant :

* d’identifier les mots-clés les plus dominants selon les pays
* de repérer les zones géographiques les plus réceptives à un mot-clé
* de comparer les dynamiques d’intérêt entre plusieurs thèmes
* de proposer une lecture visuelle et interprétative des résultats

Attention : les scores Google Trends sont des indices relatifs et non des volumes absolus de recherche.

---

## Structure générale du code

Le code est organisé en plusieurs blocs logiques :

### 1. Configuration de la page

```python
st.set_page_config(...)
```

Cette partie définit :

* le titre de l’application
* l’icône affichée dans l’onglet
* la largeur de mise en page
* l’état initial de la sidebar

Cela permet d’obtenir une interface plus propre et adaptée à un dashboard.

---

### 2. Définition des chemins des fichiers

```python
BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
```

Ces lignes servent à localiser les fichiers CSV nécessaires au dashboard :

* `trends_time_long.csv`
* `trends_country_enriched.csv`
* `country_insights.csv`

Le code suppose que les données traitées sont stockées dans un dossier `data/processed`.

---

### 3. Personnalisation visuelle avec CSS

Le bloc `st.markdown("""<style>...</style>""", unsafe_allow_html=True)` permet de styliser l’application.

Il sert à :

* changer le fond global
* styliser les cartes KPI
* améliorer la sidebar
* rendre les sections plus modernes
* créer une apparence “dashboard premium”

Cette partie ne modifie pas la logique métier, mais améliore fortement l’expérience utilisateur.

---

### 4. Fonctions utilitaires

Le code contient plusieurs fonctions pour rendre l’application plus propre et plus robuste.

#### `validate_columns(df, required_cols, name)`

Cette fonction vérifie que les colonnes attendues existent bien dans chaque fichier CSV.

Elle évite les erreurs silencieuses en affichant un message clair si une colonne manque.

#### `to_num(series, fill=0)`

Cette fonction convertit une colonne en valeur numérique.

Elle remplace les valeurs invalides par `0`.

#### `common_layout(fig, height=450, title=None)`

Cette fonction applique un style commun à tous les graphiques Plotly :

* couleurs de fond
* police
* marges
* grille
* cohérence visuelle globale

Cela évite de répéter le même code sur tous les graphiques.

#### `add_metric_columns(df)`

C’est une fonction importante.

Elle crée trois métriques différentes à partir du score initial :

* `score_absolu` : score Google Trends brut
* `score_normalise` : score recalculé entre le minimum et le maximum visibles
* `part_du_max` : part du score du meilleur pays affiché

Cette fonction corrige le problème classique où “score absolu” et “score normalisé” semblent identiques.

#### `get_metric_config(metric_mode)`

Cette fonction associe le choix utilisateur dans la sidebar à :

* la colonne à utiliser
* le libellé à afficher dans les graphiques

Exemple :

* `"Score absolu"` → `score_absolu`
* `"Score normalisé"` → `score_normalise`
* `"Part du maximum (%)"` → `part_du_max`

---

### 5. Chargement des données

```python
@st.cache_data(show_spinner=False)
def load_data():
```

Cette fonction charge les trois fichiers CSV et prépare les données.

Elle effectue plusieurs traitements :

* lecture des fichiers
* vérification des colonnes
* conversion des dates
* conversion des scores en numérique
* nettoyage des chaînes de caractères
* suppression de certaines valeurs vides

L’utilisation de `@st.cache_data` améliore les performances en évitant de recharger les fichiers à chaque interaction.

---

## Description des jeux de données

### `df_time`

Contient les données temporelles.

Colonnes principales :

* `date`
* `mot_cle`
* `score`

Ce fichier sert à tracer l’évolution des mots-clés dans le temps.

---

### `df_country`

Contient les scores par pays.

Colonnes principales :

* `country`
* `continent`
* `iso3`
* `mot_cle`
* `score`

Ce fichier sert à alimenter :

* la carte mondiale
* les classements de pays
* la heatmap
* les analyses géographiques

---

### `df_insights`

Contient les indicateurs de domination par pays.

Colonnes principales :

* `country`
* `continent`
* `mot_cle_dominant`
* `score_max`
* `score_2eme`
* `ecart_top2`

Ce fichier sert à analyser quel mot-clé domine dans chaque pays et avec quelle intensité.

---

## Sidebar et filtres interactifs

La sidebar permet à l’utilisateur de contrôler le dashboard.

### Filtres disponibles

* choix du mot-clé principal
* sélection des continents
* choix de la métrique affichée
* nombre de pays à afficher
* score minimum
* affichage ou non de la moyenne globale
* affichage ou non des données brutes

### Intérêt

Ces filtres rendent l’analyse plus souple et interactive.

L’utilisateur peut ainsi adapter la lecture des résultats selon ses besoins.

---

## Préparation des données filtrées

Après lecture des filtres, le code construit plusieurs sous-ensembles :

* `country_filtered`
* `insights_filtered`
* `selected_country_df`
* `time_keyword_df`

Ces DataFrames sont utilisés dans les différentes visualisations.

Le DataFrame `selected_country_df` est particulièrement important car il contient uniquement les pays associés au mot-clé choisi, enrichis avec les métriques calculées.

---

## KPI principaux

Le dashboard affiche quatre indicateurs clés :

* nombre de pays analysés
* mot-clé dominant global
* pays leader pour le mot-clé sélectionné
* plus fort écart entre le premier et le deuxième mot-clé

Ces KPI donnent une lecture rapide et synthétique de la situation.

---

## Organisation du dashboard en onglets

L’application est divisée en quatre onglets.

---

### 1. Vue générale

Cet onglet contient :

#### a. Une courbe temporelle globale

Elle compare l’évolution des mots-clés dans le temps.

Optionnellement, une moyenne globale peut être affichée pour mieux situer les tendances.

#### b. Des indicateurs complémentaires

On y retrouve par exemple :

* le score maximal dans le temps
* la moyenne temporelle
* la dernière valeur observée
* la moyenne géographique

#### c. Un graphique par continent

Il montre, pour le mot-clé choisi, le score moyen observé sur chaque continent.

---

### 2. Carte & pays

Cet onglet se concentre sur l’analyse géographique.

#### a. Carte mondiale

La carte choroplèthe affiche les pays colorés selon la métrique choisie.

Elle utilise les codes ISO3 pour positionner correctement les pays.

#### b. Classement Top pays

Un bar chart horizontal présente les pays les plus associés au mot-clé sélectionné.

#### c. Nuage d’analyse

Un scatter plot croise :

* la métrique choisie
* l’écart entre le premier et le deuxième mot-clé

Cela permet d’identifier les pays où un mot-clé est fort et clairement dominant.

---

### 3. Comparaisons

Cet onglet permet une analyse transversale entre tous les mots-clés.

#### a. Nombre de pays dominés par mot-clé

Ce graphique montre dans combien de pays chaque mot-clé arrive en première position.

#### b. Distribution des scores

Le boxplot montre la dispersion des scores géographiques pour chaque mot-clé.

#### c. Heatmap pays × mots-clés

Cette visualisation permet de repérer rapidement les contrastes entre pays et mots-clés.

#### d. Radar des 5 premiers pays

Le radar met en évidence le profil des cinq pays les plus réceptifs au mot-clé sélectionné.

---

### 4. Résumé & données

Cet onglet contient :

#### a. Résumé automatique

Le code génère un texte interprétatif à partir des résultats filtrés.

Il résume notamment :

* le pays leader
* les trois premiers pays
* la moyenne observée
* la domination globale
* la part de domination du mot-clé choisi

Cette partie est utile pour l’oral ou la soutenance.

#### b. Données brutes

Si l’utilisateur active l’option correspondante, il peut consulter les tables sous forme de DataFrames.

---

## Logique des métriques

Le dashboard propose trois manières de lire les scores.

### 1. Score absolu

Il s’agit du score Google Trends tel qu’il est fourni dans les données.

Exemple : `42`, `28`, `17`

### 2. Score normalisé

Le score est recalculé entre le minimum et le maximum observés dans le sous-ensemble visible.

Formule :

```python
(score - min) / (max - min) * 100
```

Cela permet de mieux voir les écarts internes entre les pays affichés.

### 3. Part du maximum

Chaque score est exprimé comme une proportion du meilleur score visible.

Formule :

```python
score / score_max * 100
```

Exemple :
si le meilleur pays vaut `42`, alors un pays à `28` obtient environ `66.7%`.

---

## Pourquoi cette distinction est utile

Google Trends fournit déjà des scores relatifs, mais dans un dashboard, il peut être utile d’ajouter des transformations analytiques pour mieux comparer les pays visibles.

Cela améliore :

* la lisibilité
* la hiérarchie visuelle
* l’analyse comparative

---

## Points forts techniques du code

### Robustesse

* vérification des colonnes
* nettoyage des données
* conversion sécurisée des types

### Performance

* mise en cache avec `st.cache_data`
* calculs regroupés
* traitement unique des données

### Lisibilité

* découpage logique du script
* fonctions dédiées
* structure claire

### Design

* interface moderne
* cohérence graphique
* meilleure lisibilité pour l’utilisateur final

---

## Lancer le projet

### Installer les dépendances

```bash
pip install streamlit pandas numpy plotly
```

### Lancer l’application

```bash
streamlit run app/dashboard.py
```

Adapte le chemin selon le nom réel de ton fichier.

---

## Exemple d’interprétation

Pour un mot-clé donné, si la France a un score de `42`, le Maroc `28` et l’Algérie `17`, cela signifie :

* la France est le pays le plus réceptif dans le sous-ensemble observé
* le Maroc présente un niveau d’intérêt inférieur mais significatif
* l’Algérie reste présente, mais plus loin derrière

Cela ne signifie pas :

* 42 recherches en France
* 28 recherches au Maroc
* 17 recherches en Algérie

Il s’agit uniquement d’indices relatifs d’intérêt.

---

## Limites du projet

* Google Trends ne fournit pas de volumes absolus
* les résultats dépendent fortement du mot-clé choisi
* la langue influence la distribution géographique
* les scores dépendent aussi de la période d’observation

---

## Pistes d’amélioration

* ajouter un export CSV ou PNG
* intégrer une comparaison simultanée de plusieurs mots-clés
* générer des commentaires automatiques plus avancés
* ajouter une section “recommandations stratégiques”
* proposer une analyse temporelle filtrable par période

---

## Conclusion

Ce dashboard transforme des données Google Trends en outil d’analyse interactif.
Il permet une lecture claire des dynamiques temporelles, géographiques et comparatives, avec un niveau de présentation adapté à une soutenance ou à un projet de data visualisation.

---

Si tu veux, je peux maintenant te rédiger un `README.md` complet, directement prêt à copier-coller, avec :

* titre
* installation
* structure du projet
* explication du code
* captures à ajouter
* conclusion propre.
