import streamlit as st
import pandas as pd

# Pretraitement des données
def upload_et_pretraitement_donnes(data) :
    # Modification des balises web
    data.loc[:,"NatureProjet"] = data.loc[:,"NatureProjet"].str.replace("<br>", " ")
    data.loc[:,"NatureProjet"] = data.loc[:,"NatureProjet"].str.replace("&nbsp;", " ")
    data.loc[:,"TypeProjet"] = data.loc[:,"TypeProjet"].str.replace("<br>", " ")
    data.loc[:,"TypeProjet"] = data.loc[:,"TypeProjet"].str.replace("&nbsp;", " ")
    data.loc[:,"MaturiteProjet"] = data.loc[:,"MaturiteProjet"].str.replace("<br>", " ")
    data.loc[:,"MaturiteProjet"] = data.loc[:,"MaturiteProjet"].str.replace("&nbsp;", " ")

    # Inputation par 0 de la colonne estTransmiAuCommercial cosidéré comme non transmis
    data.loc[:,"estTransmiAuCommercial"] = data.loc[:,"estTransmiAuCommercial"].fillna(0)
    
    return data

    

def calcul_score_contact(row):
    """Calcule un score de priorité pour un lead en fonction de ses caractéristiques métier.    
    Le score est une combinaison pondérée de plusieurs variables explicatives :    
            - besoinDeFinancement (20%) : montant du financement demandé, en lien direct avec le chiffre d'affaires que CAFPI peut tirer du contrat 
            - LB_Nature (15%) : type de bien / projet (ancien, neuf, etc.)    
            - MaturiteProjet (35%) : niveau d’avancement du projet
            - typeLead (30%) : qualité estimée du lead (en code couleur)    
    
    Chaque variable est transformée en un sous-score compris entre 0 et 1, reflétant sa contribution à la probabilité de conversion ou à la valeur      business. Le score final est une somme pondérée de ces sous-scores et est également compris entre 0 et 1.    
    Objectif :    
        - Prioriser les leads pour les équipes commerciales    
        - Maximiser le taux de conversion et/ou le chiffre d’affaires    
        
    Remarques :    
        - Il s'agit d’un score heuristique basé sur des règles métier (non calibré comme une probabilité)    
        - Les pondérations reflètent l’importance relative supposée de chaque variable    
        - Le score est principalement utilisé pour du ranking (priorisation), pas pour de la prédiction probabiliste. Par ailleurs pour le rendre             optimal des analyses approfondies sur un grand jeu de données seraient nécessaires
    
    Paramètres    
    ----------    
    row : pandas.Series        Ligne du DataFrame contenant les informations du lead    
    
    Retour    
    -------    
    float        Score compris entre 0 et 1"""

    # initilisation du score global 
    # (en cas de disfonctionnements non détectés sur le jeu fourni, les autres initialisations de score suivent la même logique)
    score = 0

    # initilisation du score et du poids de besoin de financement
    # L'ensemble des poids ont été déterminé de manière arbitraire en se basant sur les liens présumés entre les modalités et la valeur cible (passage à l'étape 4)
    # Plus deux modalités sont différenciantes, plus le poids est élevé. La somme des poids est de 1 pour simplifier les calculs
    poids_bf = 0.2
    score_bf = 0

    # Définitions des règles de calcul
    # Initialement conçu en escalier mais comme la variable est continue j'ai adapté la formule pour permettre un lissage de ce score 
    # et ainsi éviter les concentrations trop importantes
    # Les seuils ont été définis en utilisant les quartiles
    if row["besoinDeFinancement"] < 130000:
        score_bf = 0.1 * (row["besoinDeFinancement"] / 130000)
    
    elif row["besoinDeFinancement"] < 200000:
        score_bf = 0.1 + (0.4 - 0.1) * (row["besoinDeFinancement"] - 130000) / (200000 - 130000)
    
    elif row["besoinDeFinancement"] < 298000:
        score_bf = 0.4 + (0.7 - 0.4) * (row["besoinDeFinancement"] - 200000) / (298000 - 200000)
    
    else:
        score_bf = min(1, 0.7 + 0.3 * (row["besoinDeFinancement"] - 298000) / 200000)

    
    #En ce qui concerne les scores suivants
    # Les regroupement et les valeurs de score ont été déterminée en fonction de l'influence présumé des modalité sur l'arrivée à l'étape 4 du processus

    
    # initilisation du score et du poids de LB_Nature
    poids_LBNAT = 0.15
    score_LBNAT = 0

    # Calcul du score
    if row["LB_Nature"] == "Neuf: V.E.F.A":
        score_LBNAT = 0.6
    elif row["LB_Nature"] == "Ancien":
        score_LBNAT = 0.5
    elif row["LB_Nature"] in ["Neuf: Construction", "Neuf: Clés en main"]:
        score_LBNAT = 0.2
    else :
        score_LBNAT = 0.1

    # initilisation du score et du poids de MaturiteProjet
    poids_MP = 0.35
    score_MP = 0

    # Calcul du score
    if row["MaturiteProjet"] == "J'ai signé un compromis":
        score_MP = 0.6
    elif row["MaturiteProjet"] == "Je suis sur le point de faire une offre":
        score_MP = 0.5
    else :
        score_MP = 0.2

    # initilisation du score et du poids de typeLead
    poids_typeLead = 0.3
    score_typeLead = 0

    # Calcul du score
    if row["typeLead"] == "green":
        score_typeLead = 0.7
    elif row["typeLead"] == "orange":
        score_typeLead = 0.2
    else :
        score_typeLead = 0 # Aucun changement c'est simplement pour être sûr de ne pas oublier

    
    # score = Σ poids * score
    score = poids_typeLead * score_typeLead + poids_MP * score_MP + poids_LBNAT * score_LBNAT + poids_bf * score_bf

    return score
    

# Config page
st.set_page_config(
    page_title="Priorisation des Leads",
    layout="wide"
)

st.title("Priorisation des leads à recontacter")

# -------------------------
# Upload fichier
# -------------------------
uploaded_file = st.file_uploader("Upload du fichier Excel", type=["xlsx"])

if uploaded_file is not None:

    # Lecture fichier

    df = pd.read_excel(uploaded_file)
    df = upload_et_pretraitement_donnes(df)

    st.success("Fichier chargé avec succès")

    
    # SCORE 
    df.loc[:,"score"] = [calcul_score_contact(row) for _, row in df.iterrows()]

    # Sidebar filtres
    st.sidebar.header("Filtres")

    # Sélection pour choisir entre une prise de contact et un suivi client
    filtre_transmis = st.sidebar.selectbox(
        "estTransmiAuCommercial",
        options=["Tous", "Transmis", "Non Transmis"]
    )

    # Traduction en data
    filtre_corres = {"Transmis" : 1, "Non Transmis" : 0}

    # création de la copie pour garder l'original en cas de changements
    df_filtered = df.copy()
    
    # Sélection du nouveau DataFrame
    if filtre_transmis != "Tous":
        df_filtered = df_filtered[
            df_filtered["estTransmiAuCommercial"] == filtre_corres[filtre_transmis]
        ]

    # Sélection du nombre de leads
    nombre_lignes = st.sidebar.select_slider(
    "Nombre de clients à recontacter",
    options=[i+1 for i in range(100)],
    value = 25
    )

    # Tri par score et sélection du nombre de lignes
    if "score" in df_filtered.columns:
        df_filtered = df_filtered.sort_values(
            by=["score","besoinDeFinancement"],
            ascending=False
        ).head(nombre_lignes).reset_index(drop=True)

    # Affichage
    st.subheader("Données triées par score")

    st.dataframe(
        df_filtered,
        use_container_width=True
    )