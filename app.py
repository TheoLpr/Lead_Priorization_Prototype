import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Lead Prioritization",
    page_icon="🎯",
    layout="wide"
)


# ============================================================
# IDENTITÉ VISUELLE
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 2.2rem 2.4rem;
        border-radius: 20px;
        background: linear-gradient(
            135deg,
            #111827 0%,
            #1f2937 100%
        );
        color: white;
        margin-bottom: 2rem;
    }

    .hero h1 {
        font-size: 2.4rem;
        margin-bottom: 0.5rem;
    }

    .hero p {
        font-size: 1.05rem;
        color: #d1d5db;
        max-width: 850px;
        margin-bottom: 0;
    }

    .info-box {
        padding: 1.3rem 1.5rem;
        border-radius: 14px;
        background-color: #f8fafc;
        border: 1px solid #e5e7eb;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
    }

    .small-text {
        font-size: 0.9rem;
        color: #6b7280;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PRÉTRAITEMENT
# ============================================================

def upload_et_pretraitement_donnes(data):

    data = data.copy()

    colonnes_texte = [
        "NatureProjet",
        "TypeProjet",
        "MaturiteProjet"
    ]

    for colonne in colonnes_texte:

        data.loc[:, colonne] = (
            data.loc[:, colonne]
            .str.replace("<br>", " ", regex=False)
            .str.replace("&nbsp;", " ", regex=False)
        )

    # Un prospect sans information de transmission
    # est considéré comme non transmis.
    data.loc[:, "estTransmiAuCommercial"] = (
        data.loc[:, "estTransmiAuCommercial"]
        .fillna(0)
    )

    return data


# ============================================================
# SCORING
# ============================================================

def calcul_score_contact(row):

    """
    Calcule un score de priorité commercial compris entre 0 et 1.

    Le score repose sur quatre dimensions :

    - besoin de financement : 20 %
    - nature du projet : 15 %
    - maturité du projet : 35 %
    - qualité du lead : 30 %

    La variable PassageEtapeSignature_4 n'est jamais utilisée
    dans le calcul du score. Elle sert uniquement à évaluer
    a posteriori la qualité de la priorisation.
    """

    # --------------------------------------------------------
    # BESOIN DE FINANCEMENT
    # --------------------------------------------------------

    poids_bf = 0.20
    score_bf = 0

    if row["besoinDeFinancement"] < 130000:

        score_bf = (
            0.1
            * (row["besoinDeFinancement"] / 130000)
        )

    elif row["besoinDeFinancement"] < 200000:

        score_bf = (
            0.1
            + (0.4 - 0.1)
            * (
                row["besoinDeFinancement"] - 130000
            )
            / (200000 - 130000)
        )

    elif row["besoinDeFinancement"] < 298000:

        score_bf = (
            0.4
            + (0.7 - 0.4)
            * (
                row["besoinDeFinancement"] - 200000
            )
            / (298000 - 200000)
        )

    else:

        score_bf = min(
            1,
            0.7
            + 0.3
            * (
                row["besoinDeFinancement"] - 298000
            )
            / 200000
        )


    # --------------------------------------------------------
    # NATURE DU PROJET
    # --------------------------------------------------------

    poids_LBNAT = 0.15
    score_LBNAT = 0

    if row["LB_Nature"] == "Neuf: V.E.F.A":

        score_LBNAT = 0.6

    elif row["LB_Nature"] == "Ancien":

        score_LBNAT = 0.5

    elif row["LB_Nature"] in [
        "Neuf: Construction",
        "Neuf: Clés en main"
    ]:

        score_LBNAT = 0.2

    else:

        score_LBNAT = 0.1


    # --------------------------------------------------------
    # MATURITÉ DU PROJET
    # --------------------------------------------------------

    poids_MP = 0.35
    score_MP = 0

    if row["MaturiteProjet"] == "J'ai signé un compromis":

        score_MP = 0.6

    elif row["MaturiteProjet"] == (
        "Je suis sur le point de faire une offre"
    ):

        score_MP = 0.5

    else:

        score_MP = 0.2


    # --------------------------------------------------------
    # TYPE DE LEAD
    # --------------------------------------------------------

    poids_typeLead = 0.30
    score_typeLead = 0

    if row["typeLead"] == "green":

        score_typeLead = 0.7

    elif row["typeLead"] == "orange":

        score_typeLead = 0.2

    else:

        score_typeLead = 0


    # --------------------------------------------------------
    # SCORE FINAL
    # --------------------------------------------------------

    score = (
        poids_typeLead * score_typeLead
        + poids_MP * score_MP
        + poids_LBNAT * score_LBNAT
        + poids_bf * score_bf
    )

    return score


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">

        <h1>🎯 Lead Prioritization</h1>

        <p>
        Un outil d'aide à la décision conçu pour aider les équipes
        commerciales à identifier les prospects à contacter en priorité
        grâce à un scoring métier explicable.
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PRÉSENTATION DU PROJET
# ============================================================

st.markdown("### Le problème")

st.write(
    """
    Les équipes commerciales disposent d'un volume important de prospects,
    mais tous ne présentent pas le même potentiel de conversion.

    L'objectif de ce projet est donc simple :
    **identifier les prospects à traiter en priorité afin de concentrer
    l'effort commercial sur les leads présentant le meilleur potentiel.**
    """
)

st.markdown(
    """
    <div class="info-box">

    <b>🎯 Métrique cible : PassageEtapeSignature_4</b><br><br>

    Cette variable indique si le prospect a atteint l'étape 4 du tunnel
    commercial : <b>la signature</b>.

    <br><br>

    Elle n'intervient pas dans le calcul du score.
    Elle est utilisée uniquement après le scoring afin d'évaluer
    sa capacité à identifier les prospects ayant historiquement converti.

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

st.markdown("### Données")

col_demo, col_upload = st.columns(2)

with col_demo:

    st.markdown("#### Dataset de démonstration")

    st.caption(
        "Utilisez directement le dataset ayant servi "
        "à construire ce projet."
    )

    charger_demo = st.button(
        "🚀 Charger les données de démonstration",
        use_container_width=True,
        type="primary"
    )


with col_upload:

    st.markdown("#### Votre propre fichier")

    st.caption(
        "Vous pouvez également tester l'outil "
        "avec un fichier Excel compatible."
    )

    uploaded_file = st.file_uploader(
        "Importer un fichier Excel",
        type=["xlsx"],
        label_visibility="collapsed"
    )


# ============================================================
# MÉMORISATION DU CHOIX
# ============================================================

if charger_demo:

    st.session_state["utiliser_demo"] = True


if uploaded_file is not None:

    st.session_state["utiliser_demo"] = False


# ============================================================
# LECTURE DES DONNÉES
# ============================================================

df = None

if uploaded_file is not None:

    df = pd.read_excel(uploaded_file)


elif st.session_state.get("utiliser_demo", False):

    try:

        df = pd.read_excel("Prospects.xlsx")

    except FileNotFoundError:

        st.error(
            "Le fichier Prospects.xlsx doit être placé "
            "dans le même dossier que l'application."
        )


# ============================================================
# APPLICATION
# ============================================================

if df is not None:

    df = upload_et_pretraitement_donnes(df)

    # Calcul du score
    df.loc[:, "score"] = [
        calcul_score_contact(row)
        for _, row in df.iterrows()
    ]

    # Score plus lisible pour l'utilisateur
    df.loc[:, "score_priorite"] = (
        df["score"] * 100
    ).round(1)


    # ========================================================
    # INDICATEURS DATASET
    # ========================================================

    nb_prospects = len(df)

    nb_signatures = int(
        df["PassageEtapeSignature_4"].sum()
    )

    taux_signature_total = (
        df["PassageEtapeSignature_4"].mean()
    )

    df_transmis = df[
        df["estTransmiAuCommercial"] == 1
    ]

    taux_signature_transmis = (
        df_transmis["PassageEtapeSignature_4"].mean()
    )


    st.divider()

    st.markdown("### Vue d'ensemble")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Prospects",
        f"{nb_prospects:,}".replace(",", " ")
    )

    col2.metric(
        "Signatures",
        f"{nb_signatures:,}".replace(",", " ")
    )

    col3.metric(
        "Conversion globale",
        f"{taux_signature_total:.1%}"
    )

    col4.metric(
        "Conversion après transmission",
        f"{taux_signature_transmis:.1%}"
    )


    st.caption(
        "La conversion après transmission constitue la baseline "
        "de référence pour évaluer la performance du scoring."
    )


    # ========================================================
    # PARAMÉTRAGE
    # ========================================================

    st.divider()

    st.markdown("### Priorisation commerciale")

    st.write(
        """
        Sélectionnez la population à analyser puis le nombre de prospects
        que l'équipe commerciale est en capacité de traiter.
        """
    )


    col_filtre, col_nombre = st.columns([1, 2])


    with col_filtre:

        filtre_transmis = st.selectbox(
            "Population",
            options=[
                "Transmis",
                "Non Transmis",
                "Tous"
            ]
        )


    filtre_corres = {
        "Transmis": 1,
        "Non Transmis": 0
    }


    df_filtered = df.copy()


    if filtre_transmis != "Tous":

        df_filtered = df_filtered[
            df_filtered["estTransmiAuCommercial"]
            == filtre_corres[filtre_transmis]
        ]


    # Tri avant sélection du Top N
    df_filtered = df_filtered.sort_values(
        by=[
            "score",
            "besoinDeFinancement"
        ],
        ascending=False
    ).reset_index(drop=True)


    with col_nombre:

        max_leads = len(df_filtered)

        nombre_lignes = st.slider(
            "Nombre de prospects à prioriser",
            min_value=10,
            max_value=max_leads,
            value=min(50, max_leads),
            step=10
        )


    # ========================================================
    # TOP N
    # ========================================================

    df_selection = (
        df_filtered
        .head(nombre_lignes)
        .copy()
    )


    # ========================================================
    # KPI DYNAMIQUES
    # ========================================================

    st.markdown("#### Performance de la sélection")


    if filtre_transmis == "Transmis":

        taux_selection = (
            df_selection[
                "PassageEtapeSignature_4"
            ].mean()
        )

        gain_ciblage = (
            taux_selection
            / taux_signature_transmis
            if taux_signature_transmis > 0
            else 0
        )


        col1, col2, col3 = st.columns(3)


        col1.metric(
            "Taux de signature de référence",
            f"{taux_signature_transmis:.1%}"
        )


        col2.metric(
            f"Taux de signature — Top {nombre_lignes}",
            f"{taux_selection:.1%}",
            delta=(
                f"{(taux_selection - taux_signature_transmis):+.1%}"
            )
        )


        col3.metric(
            "Gain de ciblage",
            f"× {gain_ciblage:.2f}"
        )


        st.caption(
            f"Historiquement, {taux_selection:.1%} des "
            f"{nombre_lignes} prospects les mieux classés ont atteint "
            "l'étape de signature."
        )


    elif filtre_transmis == "Non Transmis":

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Prospects disponibles",
            len(df_filtered)
        )

        col2.metric(
            "Prospects à contacter",
            len(df_selection)
        )

        col3.metric(
            "Score moyen du Top",
            f"{df_selection['score_priorite'].mean():.1f} / 100"
        )


        st.info(
            "💡 Ces prospects n'ont pas encore été transmis au commercial. "
            "Leur taux de signature historique ne peut donc pas être utilisé "
            "pour évaluer leur performance. Le scoring sert ici à déterminer "
            "les prospects à contacter en priorité."
        )


    else:

        taux_selection = (
            df_selection[
                "PassageEtapeSignature_4"
            ].mean()
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Conversion globale",
            f"{taux_signature_total:.1%}"
        )

        col2.metric(
            f"Top {nombre_lignes}",
            f"{taux_selection:.1%}"
        )

        col3.metric(
            "Score moyen",
            f"{df_selection['score_priorite'].mean():.1f} / 100"
        )


    # ========================================================
    # COURBE DE PERFORMANCE
    # ========================================================

    if filtre_transmis == "Transmis":

        st.divider()

        st.markdown("### Performance du scoring")

        st.write(
            """
            Cette courbe mesure le taux de signature historique lorsque
            l'on augmente progressivement le nombre de prospects sélectionnés.
            """
        )


        performances = []

        pas = 10

        for n in range(
            pas,
            len(df_filtered) + 1,
            pas
        ):

            top_n = df_filtered.head(n)

            taux = (
                top_n[
                    "PassageEtapeSignature_4"
                ].mean()
            )

            performances.append(
                {
                    "Nombre de prospects": n,
                    "Taux de signature": taux
                }
            )


        df_performance = pd.DataFrame(
            performances
        )


        fig = px.line(
            df_performance,
            x="Nombre de prospects",
            y="Taux de signature",
            title="Taux de signature selon le nombre de prospects priorisés"
        )


        fig.add_hline(
            y=taux_signature_transmis,
            line_dash="dash",
            annotation_text=(
                f"Baseline : "
                f"{taux_signature_transmis:.1%}"
            )
        )


        fig.update_yaxes(
            tickformat=".0%"
        )


        fig.update_layout(
            xaxis_title="Nombre de prospects sélectionnés",
            yaxis_title="Taux de signature",
            hovermode="x unified"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # ========================================================
    # TABLEAU DES PROSPECTS
    # ========================================================

    st.divider()

    st.markdown(
        f"### Top {nombre_lignes} prospects prioritaires"
    )


    colonnes_affichage = [
        "id",
        "score_priorite",
        "typeLead",
        "MaturiteProjet",
        "LB_Nature",
        "NatureProjet",
        "besoinDeFinancement",
        "Apport",
        "estTransmiAuCommercial"
    ]


    # En mode validation, on affiche également le résultat réel.
    if filtre_transmis == "Transmis":

        colonnes_affichage.append(
            "PassageEtapeSignature_4"
        )


    st.dataframe(
        df_selection[colonnes_affichage],
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": "ID",
            "score_priorite": st.column_config.ProgressColumn(
                "Score de priorité",
                help="Score métier utilisé pour prioriser les prospects.",
                min_value=0,
                max_value=100,
                format="%.1f"
            ),
            "typeLead": "Type de lead",
            "MaturiteProjet": "Maturité du projet",
            "LB_Nature": "Nature du bien",
            "NatureProjet": "Projet",
            "besoinDeFinancement": st.column_config.NumberColumn(
                "Financement",
                format="%.0f €"
            ),
            "Apport": st.column_config.NumberColumn(
                "Apport",
                format="%.0f €"
            ),
            "estTransmiAuCommercial": "Transmis",
            "PassageEtapeSignature_4": "Signature"
        }
    )


    # ========================================================
    # MÉTHODOLOGIE
    # ========================================================

    st.divider()

    with st.expander(
        "🧠 Comment fonctionne le scoring ?"
    ):

        st.markdown(
            """
            Le score est un **scoring métier heuristique** compris entre
            0 et 1 puis présenté dans l'interface sur une échelle de 0 à 100.

            Il combine quatre dimensions :

            - **Maturité du projet — 35 %**
            - **Type de lead — 30 %**
            - **Besoin de financement — 20 %**
            - **Nature du bien — 15 %**

            Les pondérations ont été définies à partir de l'analyse
            exploratoire du dataset et de l'influence supposée de ces
            caractéristiques sur la conversion.

            **La variable cible `PassageEtapeSignature_4` n'est jamais
            utilisée pour calculer le score.**

            Elle intervient uniquement après le classement afin de mesurer
            la capacité du scoring à concentrer les signatures historiques.

            Ce scoring constitue donc une approche de priorisation
            explicable et non un modèle probabiliste de machine learning.
            Une validation sur un historique plus important permettrait
            ensuite de calibrer ou d'entraîner un modèle prédictif.
            """
        )
