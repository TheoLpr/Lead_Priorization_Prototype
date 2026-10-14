import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# CONFIGURATION DE LA PAGE
# ============================================================

st.set_page_config(
    page_title="Lead Prioritization",
    page_icon="🎯",
    layout="wide"
)


# ============================================================
# PRÉTRAITEMENT DES DONNÉES
# ============================================================

def upload_et_pretraitement_donnes(data):

    data = data.copy()

    # Nettoyage des balises web
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

    # Une valeur vide est considérée comme non transmise
    data.loc[:, "estTransmiAuCommercial"] = (
        data.loc[:, "estTransmiAuCommercial"]
        .fillna(0)
    )

    return data


# ============================================================
# CALCUL DU SCORE
# ============================================================

def calcul_score_contact(row):

    """
    Calcule un score de priorité pour un prospect.

    Le score repose sur quatre dimensions métier :

    - Besoin de financement : 20 %
    - Nature du projet : 15 %
    - Maturité du projet : 35 %
    - Type de lead : 30 %

    La variable PassageEtapeSignature_4 n'est jamais utilisée
    dans le calcul du score.

    Elle sert uniquement à évaluer a posteriori la qualité
    de la priorisation.
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
# CHARGEMENT DES DONNÉES
# ============================================================

try:

    df = pd.read_excel("Prospects.xlsx")

except FileNotFoundError:

    st.error(
        "Le fichier Prospects.xlsx est introuvable. "
        "Vérifiez qu'il est bien présent dans le dépôt GitHub."
    )

    st.stop()


# Prétraitement
df = upload_et_pretraitement_donnes(df)


# Calcul du score
df.loc[:, "score"] = [
    calcul_score_contact(row)
    for _, row in df.iterrows()
]


# Score présenté sur 100 dans l'interface
df.loc[:, "score_priorite"] = (
    df["score"] * 100
).round(1)


# ============================================================
# EN-TÊTE
# ============================================================

st.title("🎯 Lead Prioritization")

st.caption(
    "Scoring et priorisation des prospects à potentiel commercial"
)

st.write(
    """
    Ce prototype a été développé à partir d'un exercice technique
    avec un objectif volontairement ouvert : **exploiter un dataset
    de prospects afin d'en tirer une solution business pertinente.**

    L'approche retenue consiste à construire un système de scoring
    permettant d'aider les équipes commerciales à identifier
    **les prospects à contacter en priorité**.
    """
)


# ============================================================
# PROBLÉMATIQUE
# ============================================================

st.divider()

st.subheader("Le problème")

st.write(
    """
    Les équipes commerciales disposent d'un volume important de prospects,
    mais tous ne présentent pas le même potentiel de conversion.

    L'objectif est donc de **concentrer l'effort commercial sur les leads
    présentant le meilleur potentiel**, plutôt que de traiter l'ensemble
    des prospects de manière indifférenciée.
    """
)


st.info(
    """
    🎯 **Métrique cible : PassageEtapeSignature_4**

    Cette variable indique si le prospect a atteint l'étape 4
    du tunnel commercial : **la signature**.

    Elle n'intervient jamais dans le calcul du score.

    Elle est utilisée uniquement après le scoring afin de mesurer
    si les prospects considérés comme prioritaires ont effectivement
    davantage converti historiquement.
    """
)


# ============================================================
# USAGE MÉTIER
# ============================================================

st.subheader("Du prototype à l'usage métier")

st.write(
    """
    Cette démonstration utilise directement le dataset historique
    ayant servi au développement du prototype.

    Dans un environnement opérationnel, l'outil pourrait être connecté
    au **CRM ou à la base de prospects de l'entreprise** afin de recalculer
    régulièrement le scoring et de fournir aux commerciaux une liste
    actualisée des prospects à contacter en priorité.
    """
)


# ============================================================
# CALCUL DES INDICATEURS GLOBAUX
# ============================================================

nb_prospects = len(df)

nb_signatures = int(
    df["PassageEtapeSignature_4"].sum()
)

taux_signature_global = (
    df["PassageEtapeSignature_4"].mean()
)


# Prospects transmis au commercial
df_transmis = df[
    df["estTransmiAuCommercial"] == 1
].copy()


nb_transmis = len(df_transmis)


taux_signature_transmis = (
    df_transmis["PassageEtapeSignature_4"].mean()
)


# ============================================================
# VUE D'ENSEMBLE
# ============================================================

st.divider()

st.subheader("Vue d'ensemble")

col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Prospects",
    f"{nb_prospects:,}".replace(",", " ")
)


col2.metric(
    "Transmis au commercial",
    f"{nb_transmis:,}".replace(",", " ")
)


col3.metric(
    "Signatures",
    f"{nb_signatures:,}".replace(",", " ")
)


col4.metric(
    "Taux de signature",
    f"{taux_signature_transmis:.1%}"
)


st.caption(
    """
    Le taux de signature de référence est calculé sur les prospects
    ayant effectivement été transmis aux équipes commerciales.
    """
)


# ============================================================
# PRIORISATION COMMERCIALE
# ============================================================

st.divider()

st.subheader("Priorisation commerciale")

st.write(
    """
    Sélectionnez la population à analyser et le nombre de prospects
    que l'équipe commerciale est en capacité de traiter.

    Les prospects sont automatiquement classés du score
    de priorité le plus élevé au plus faible.
    """
)


# ============================================================
# FILTRES
# ============================================================

col_filtre, col_nombre = st.columns([1, 2])


with col_filtre:

    filtre_transmis = st.selectbox(
        "Population",
        options=[
            "Transmis",
            "Non Transmis",
            "Tous"
        ],
        help=(
            "Les prospects transmis permettent d'évaluer "
            "historiquement le scoring. Les non transmis "
            "correspondent à son usage opérationnel."
        )
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
    ].copy()


# ============================================================
# TRI DES PROSPECTS
# ============================================================

df_filtered = (
    df_filtered
    .sort_values(
        by=[
            "score",
            "besoinDeFinancement"
        ],
        ascending=False
    )
    .reset_index(drop=True)
)


# ============================================================
# SLIDER TOP N
# ============================================================

max_leads = len(df_filtered)


with col_nombre:

    if max_leads >= 10:

        nombre_lignes = st.slider(
            "Nombre de prospects à prioriser",
            min_value=10,
            max_value=max_leads,
            value=min(50, max_leads),
            step=10
        )

    else:

        nombre_lignes = max_leads

        st.write(
            f"{max_leads} prospects disponibles"
        )


# ============================================================
# SÉLECTION TOP N
# ============================================================

df_selection = (
    df_filtered
    .head(nombre_lignes)
    .copy()
)


# ============================================================
# PERFORMANCE DE LA SÉLECTION
# ============================================================

st.markdown("### Performance de la sélection")


# ------------------------------------------------------------
# CAS 1 : PROSPECTS TRANSMIS
# ------------------------------------------------------------

if filtre_transmis == "Transmis":

    taux_selection = (
        df_selection[
            "PassageEtapeSignature_4"
        ].mean()
    )


    gain_ciblage = (
        taux_selection / taux_signature_transmis
        if taux_signature_transmis > 0
        else 0
    )


    difference = (
        taux_selection
        - taux_signature_transmis
    )


    col1, col2, col3 = st.columns(3)


    col1.metric(
        "Taux de signature de référence",
        f"{taux_signature_transmis:.1%}"
    )


    col2.metric(
        f"Taux de signature — Top {nombre_lignes}",
        f"{taux_selection:.1%}",
        delta=f"{difference:+.1%}"
    )


    col3.metric(
        "Gain de ciblage",
        f"× {gain_ciblage:.2f}"
    )


    st.success(
        f"""
        Parmi les **{nombre_lignes} prospects les mieux classés**,
        **{taux_selection:.1%} ont historiquement atteint la signature**,
        contre **{taux_signature_transmis:.1%}** pour l'ensemble
        des prospects transmis.
        """
    )


# ------------------------------------------------------------
# CAS 2 : PROSPECTS NON TRANSMIS
# ------------------------------------------------------------

elif filtre_transmis == "Non Transmis":

    score_moyen = (
        df_selection["score_priorite"].mean()
    )


    col1, col2, col3 = st.columns(3)


    col1.metric(
        "Prospects disponibles",
        f"{len(df_filtered):,}".replace(",", " ")
    )


    col2.metric(
        "Prospects à contacter",
        len(df_selection)
    )


    col3.metric(
        "Score moyen de la sélection",
        f"{score_moyen:.1f} / 100"
    )


    st.info(
        """
        💡 Ces prospects n'ont pas encore été transmis au commercial.

        Leur taux de signature ne peut donc pas encore être utilisé
        pour mesurer leur performance.

        Le scoring joue ici son rôle opérationnel :
        **identifier les prospects à contacter en priorité.**
        """
    )


# ------------------------------------------------------------
# CAS 3 : TOUS LES PROSPECTS
# ------------------------------------------------------------

else:

    taux_selection = (
        df_selection[
            "PassageEtapeSignature_4"
        ].mean()
    )


    score_moyen = (
        df_selection[
            "score_priorite"
        ].mean()
    )


    col1, col2, col3 = st.columns(3)


    col1.metric(
        "Conversion globale",
        f"{taux_signature_global:.1%}"
    )


    col2.metric(
        f"Taux de signature — Top {nombre_lignes}",
        f"{taux_selection:.1%}"
    )


    col3.metric(
        "Score moyen de la sélection",
        f"{score_moyen:.1f} / 100"
    )


# ============================================================
# PERFORMANCE DU SCORING
# ============================================================

if filtre_transmis == "Transmis":

    st.divider()

    st.subheader("Performance du scoring")

    st.write(
        """
        Le graphique ci-dessous montre comment évolue le taux
        de signature lorsque l'on augmente progressivement
        le nombre de prospects sélectionnés.

        Plus la courbe se situe au-dessus de la baseline,
        plus le scoring concentre efficacement les signatures
        dans les premières positions du classement.
        """
    )


    performances = []


    for n in range(
        10,
        len(df_filtered) + 1,
        10
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


    # Ajout du dernier point si nécessaire
    if len(df_filtered) % 10 != 0:

        performances.append(
            {
                "Nombre de prospects": len(df_filtered),
                "Taux de signature": (
                    df_filtered[
                        "PassageEtapeSignature_4"
                    ].mean()
                )
            }
        )


    df_performance = pd.DataFrame(
        performances
    )


    fig = px.line(
        df_performance,
        x="Nombre de prospects",
        y="Taux de signature",
        title=(
            "Taux de signature selon "
            "le nombre de prospects priorisés"
        )
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


# ============================================================
# TABLEAU DES PROSPECTS PRIORITAIRES
# ============================================================

st.divider()

st.subheader(
    f"Top {nombre_lignes} prospects prioritaires"
)


st.caption(
    """
    Le classement ci-dessous constitue la liste de travail
    proposée aux équipes commerciales.
    """
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


# Pour les prospects déjà transmis,
# on peut afficher le résultat historique.
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
            help=(
                "Score métier utilisé pour "
                "prioriser les prospects."
            ),
            min_value=0,
            max_value=100,
            format="%.1f"
        ),

        "typeLead": "Type de lead",

        "MaturiteProjet": "Maturité du projet",

        "LB_Nature": "Nature du bien",

        "NatureProjet": "Projet",

        "besoinDeFinancement": (
            st.column_config.NumberColumn(
                "Financement",
                format="%.0f €"
            )
        ),

        "Apport": (
            st.column_config.NumberColumn(
                "Apport",
                format="%.0f €"
            )
        ),

        "estTransmiAuCommercial": "Transmis",

        "PassageEtapeSignature_4": "Signature"
    }
)


# ============================================================
# MÉTHODOLOGIE
# ============================================================

st.divider()


with st.expander(
    "🧠 Comprendre la méthodologie de scoring"
):

    st.markdown(
        """
        ### Construction du score

        Le score est un **scoring métier heuristique**.

        Il combine quatre dimensions :

        | Variable | Pondération |
        |---|---:|
        | Maturité du projet | 35 % |
        | Type de lead | 30 % |
        | Besoin de financement | 20 % |
        | Nature du bien | 15 % |

        Les pondérations ont été définies à partir de l'analyse
        exploratoire du dataset et de l'influence supposée des
        différentes caractéristiques sur la conversion.

        ---

        ### Pourquoi ne pas utiliser directement la signature ?

        La variable `PassageEtapeSignature_4` constitue la
        **variable cible d'évaluation**.

        Elle n'est jamais utilisée pour calculer le score.

        Une fois les prospects classés, elle permet en revanche
        de mesurer si les prospects les mieux scorés ont
        historiquement davantage atteint la signature.

        Cette séparation permet d'éviter d'intégrer directement
        le résultat commercial dans la règle de priorisation.

        ---

        ### Limites et prochaines étapes

        Ce score est un outil de **ranking et d'aide à la décision**,
        et non une probabilité individuelle de conversion.

        Avec davantage de données historiques, l'approche pourrait
        être prolongée par :

        - une validation sur une période indépendante ;
        - une optimisation statistique des pondérations ;
        - la comparaison avec un modèle de classification supervisée ;
        - l'intégration du scoring directement dans un CRM ;
        - le suivi du taux de conversion réel après déploiement.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    """
    Projet portfolio — Prototype de scoring et de priorisation commerciale
    développé à partir d'un exercice technique.
    """
)
