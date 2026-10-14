# Lead Priorization Prototype

## Présentation du projet

Ce projet explore l'utilisation de données prospects pour répondre à une problématique concrète de performance commerciale : **comment identifier les prospects à contacter en priorité ?**

À partir de données décrivant le profil, le projet et le niveau de maturité des prospects, j'ai développé une méthode de **scoring permettant de les classer selon leur potentiel commercial**.

L'objectif est de transformer les données disponibles en un outil d'aide à la décision capable de fournir aux équipes commerciales une réponse directement exploitable : **sur quels prospects concentrer leurs efforts en priorité ?**

Le projet associe ainsi trois dimensions :

- l'analyse exploratoire des données afin d'identifier les variables pertinentes ;
- la construction d'un scoring métier explicable ;
- le développement d'une application Streamlit permettant d'utiliser le classement et d'en mesurer la performance historique.

## Problématique métier

Lorsqu'un volume important de prospects doit être traité, leur accorder à tous le même niveau de priorité n'est pas nécessairement la stratégie la plus efficace.

L'enjeu consiste à exploiter les informations disponibles en amont de la prise de contact afin de **hiérarchiser le portefeuille de prospects et orienter l'effort commercial vers les profils présentant le meilleur potentiel**.

Le scoring développé dans ce projet répond à cet objectif en attribuant à chaque prospect un score de priorité, utilisé ensuite pour générer une liste de contacts ordonnée.

La pertinence de cette priorisation est évaluée à partir du passage à l'étape de signature observé historiquement.

---

## Métrique cible

La principale métrique utilisée pour évaluer la pertinence du scoring est :

`PassageEtapeSignature_4`

Cette variable indique si un prospect a atteint **l'étape 4 du tunnel commercial, correspondant à la signature**.

Elle n'est **jamais utilisée directement dans le calcul du score**.

Elle a d'abord servi à étudier les relations entre les différentes caractéristiques des prospects et leur conversion, puis elle est utilisée uniquement pour **évaluer a posteriori la qualité du classement obtenu**.

Cette distinction permet de construire le score à partir des caractéristiques connues du prospect, puis de vérifier si les prospects les mieux classés ont effectivement davantage converti historiquement.

---

## Méthodologie de scoring

Chaque prospect reçoit un score de priorité construit à partir de quatre dimensions métier.

| Critère | Pondération |
|---|---:|
| Maturité du projet | 35 % |
| Type de lead | 30 % |
| Besoin de financement | 20 % |
| Nature du bien | 15 % |

Chaque variable est transformée en un sous-score compris entre 0 et 1.

Le score final correspond à la somme pondérée de ces différents sous-scores.

Le besoin de financement étant une variable continue, son sous-score évolue progressivement selon différents seuils définis à partir de la distribution observée dans le dataset.

Le résultat constitue un **score de ranking** : son objectif principal est de comparer et ordonner les prospects entre eux, et non de fournir une probabilité individuelle de conversion.

---

## Résultats

Le dataset contient **3 101 prospects**, dont **2 097 ont été transmis aux équipes commerciales**.

Parmi les prospects transmis, le taux historique de passage à la signature est d'environ :

**12,6 %**

Après classement selon le score développé dans le cadre du projet, le **Top 50 des prospects obtient un taux de signature historique de 24 %**.

La population prioritaire présente donc un taux de signature environ :

**1,9 fois supérieur au taux de référence.**

Ce résultat suggère que le scoring permet de concentrer une proportion plus importante de signatures dans les premières positions du classement et peut ainsi constituer un outil d'aide à la priorisation commerciale.

---

## Fonctionnement de l'application

L'application Streamlit permet d'explorer deux usages complémentaires du scoring.

### Validation historique

Les prospects déjà transmis aux équipes commerciales disposent d'un résultat observable : signature ou non-signature.

Cette population permet donc de mesurer la performance historique du scoring.

L'utilisateur peut choisir le nombre de prospects qu'il souhaite sélectionner. L'application recalcule automatiquement :

- le taux de signature de référence ;
- le taux de signature du Top N sélectionné ;
- le gain de ciblage obtenu grâce à la priorisation.

Une courbe permet également d'observer comment évolue le taux de signature à mesure que le nombre de prospects sélectionnés augmente.

### Priorisation opérationnelle

Pour les prospects qui n'ont pas encore été transmis aux équipes commerciales, le résultat final n'est pas encore connu.

Le scoring est alors utilisé comme un véritable outil opérationnel afin de générer une **liste de prospects à contacter en priorité**.

Dans un environnement de production, cette logique pourrait être connectée directement au CRM ou à la base prospects de l'entreprise afin de recalculer régulièrement le classement.

---

## Fonctionnalités

L'application comprend notamment :

- calcul automatique du score de priorité ;
- classement des prospects ;
- distinction entre prospects transmis et non transmis ;
- sélection dynamique du nombre de prospects à traiter ;
- calcul du taux de signature du Top N ;
- comparaison avec le taux de signature de référence ;
- calcul du gain de ciblage ;
- visualisation de la performance du scoring ;
- génération d'une liste de prospects prioritaires ;
- présentation de la méthodologie directement dans l'interface.

---

## Technologies utilisées

- Python
- Pandas
- Streamlit
- Plotly
- Excel

---

## Limites et perspectives

Le scoring développé ici repose sur une **approche heuristique fondée sur des règles métier et sur l'analyse exploratoire des données**.

Il ne doit pas être interprété comme une probabilité statistiquement calibrée de conversion.

Avec un historique plus important, plusieurs prolongements seraient possibles :

- validation du scoring sur une période indépendante ;
- optimisation statistique des pondérations ;
- comparaison avec un modèle de classification supervisée ;
- analyse de nouvelles variables explicatives ;
- intégration du scoring dans un CRM ;
- suivi de la performance réelle du dispositif après déploiement.

L'objectif de ce prototype était avant tout de montrer comment transformer un dataset commercial en un **outil simple, explicable et directement orienté vers l'action**.

---

## Données

Le jeu de données présenté dans ce projet est anonymisé et utilisé exclusivement à des fins de démonstration et d'illustration de la méthodologie développée.

Les données sont mises à disposition uniquement pour permettre le fonctionnement et la consultation de ce projet portfolio. Leur réutilisation, redistribution ou exploitation dans le cadre d'autres projets n'est pas autorisée.
