# Architecture du système ORIENT'IA

Ce document présente l'architecture globale de la plateforme **ORIENT'IA**, un assistant intelligent d'orientation académique de l'ISPM.

L'architecture est organisée en deux vues complémentaires :

1. **Architecture des données — Data Pipeline (hors ligne)** : collecte, préparation, nettoyage et transformation des données nécessaires au fonctionnement des moteurs RAG et ML.
2. **Architecture logicielle — Runtime (temps réel)** : traitement des requêtes utilisateurs par un agent Gemini capable de sélectionner directement les outils appropriés.

---

# 1. Architecture des données — Data Pipeline

Cette architecture décrit la préparation des différentes sources de données utilisées par ORIENT'IA.

Les données sont principalement utilisées pour construire deux composants :

* une **base documentaire RAG** contenant les informations officielles de l'ISPM ;
* un **modèle ML de recommandation** capable d'analyser le profil d'un candidat et de proposer les filières adaptées.

```mermaid
flowchart TD

    %% =========================
    %% SOURCES
    %% =========================
    subgraph Sources["1. SOURCES DE DONNÉES"]

        S1["SRC-EXCEL-001<br/>Référentiel & offres ISPM<br/>(Excel / Web ISPM)"]

        S2["DATA-001<br/>Réponses enquête terrain<br/>(Google Forms / CSV)"]

        S3["DATA-002<br/>Données synthétiques<br/>(Scripts / CSV)"]

    end

    %% =========================
    %% PREPARATION
    %% =========================
    subgraph Preparation["2. PRÉPARATION DES DONNÉES"]

        P1["Parsing & structuration"]

        P2["Nettoyage & anonymisation"]

        P3["Préparation des données<br/>pour le modèle ML"]

        P4["Préparation du corpus<br/>documentaire"]

    end

    %% =========================
    %% MOTEURS
    %% =========================
    subgraph Moteurs["3. MOTEURS IA"]

        RAG["Base documentaire RAG<br/>Embeddings + Qdrant / ChromaDB"]

        ML["Modèle ML de recommandation<br/>Analyse du profil candidat"]

    end

    %% =========================
    %% FLUX
    %% =========================

    S1 -->|"Informations institutionnelles"| P1

    S2 -->|"Données d'enquête"| P2

    S3 -->|"Données synthétiques"| P3

    P1 --> P4

    P2 --> P3

    P3 -->|"Données d'entraînement"| ML

    P4 -->|"Documents indexés"| RAG
```

# 2. Construction des moteurs IA

Le pipeline de données permet de construire deux moteurs principaux.

```mermaid
flowchart LR

    DONNEES["Données préparées"]

    DONNEES --> RAG["Moteur RAG<br/>Documents officiels ISPM"]

    DONNEES --> ML["Modèle ML<br/>Recommandation de filières"]

    RAG --> OUTIL_RAG["Outil :<br/>rechercher_documents_ispm_rag"]

    ML --> OUTIL_ML["Outil :<br/>analyser_profil_candidat_ml"]
```

## 2.1 Moteur RAG

Le moteur RAG permet à ORIENT'IA de rechercher des informations dans les documents officiels de l'ISPM.

L'utilisateur peut par exemple demander :

* « Quelles sont les matières de cette filière ? »
* « Combien coûtent les études ? »
* « Quels sont les parcours proposés ? »
* « Quelles sont les informations concernant cette formation ? »

Le système utilise alors l'outil :

`rechercher_documents_ispm_rag`

Le résultat est basé sur les documents institutionnels indexés dans la base vectorielle.

---

## 2.2 Modèle ML de recommandation

Le modèle ML est utilisé lorsqu'un utilisateur souhaite obtenir une recommandation de filière à partir de son profil.

Exemple :

> « Je suis une personne sociable, j'aime voyager et communiquer avec les autres. Quelle filière pourrait me convenir ? »

L'agent peut alors utiliser :

`analyser_profil_candidat_ml`

Le modèle analyse les caractéristiques du profil et produit une recommandation.

---

# 3. Architecture logicielle — Runtime

Contrairement à une architecture utilisant un classifieur d'intentions séparé, **ORIENT'IA utilise directement un agent Gemini pour comprendre la demande et choisir l'outil approprié**.

Le système ne possède donc pas de composant `CLASSIFIER` dédié.

Le modèle Gemini agit comme **orchestrateur intelligent**.

```mermaid
flowchart LR

    %% =========================
    %% INTERFACE
    %% =========================

    UI["Frontend React"]

    %% =========================
    %% API
    %% =========================

    API["Backend FastAPI"]

    %% =========================
    %% SECURITE
    %% =========================

    SEC["Sécurité & Guardrails"]

    %% =========================
    %% AGENT
    %% =========================

    AGENT["Agent ORIENT'IA<br/>Gemini"]

    %% =========================
    %% OUTILS
    %% =========================

    RAG["rechercher_documents_ispm_rag<br/>Moteur RAG"]

    ML["analyser_profil_candidat_ml<br/>Modèle ML"]

    %% =========================
    %% AUDIT
    %% =========================

    DB[("PostgreSQL<br/>Audit & historique")]

    %% =========================
    %% FLUX
    %% =========================

    UI -->|"Requête HTTP / JSON"| API

    API --> SEC

    SEC -->|"Requête validée"| AGENT

    AGENT -->|"Question factuelle"| RAG

    AGENT -->|"Demande de recommandation<br/>avec profil"| ML

    RAG -->|"Informations issues<br/>des documents officiels"| AGENT

    ML -->|"Résultats de recommandation"| AGENT

    AGENT -->|"Journalisation"| DB

    AGENT -->|"Réponse"| SEC

    SEC -->|"Réponse filtrée"| API

    API -->|"Réponse HTTP / JSON"| UI
```

---

# 4. Rôle de l'agent Gemini

L'agent Gemini constitue le cœur de l'architecture temps réel.

Il reçoit directement la question de l'utilisateur et détermine, à partir des instructions du système et des outils disponibles, quelle action effectuer.

```mermaid
flowchart TD

    USER["Question utilisateur"]

    GEMINI["Agent Gemini<br/>ORIENT'IA"]

    DECISION{"Quelle action<br/>est nécessaire ?"}

    RAG["Outil RAG<br/>rechercher_documents_ispm_rag"]

    ML["Outil ML<br/>analyser_profil_candidat_ml"]

    CLARIF["Demande de précisions"]

    RESPONSE["Réponse finale"]

    USER --> GEMINI

    GEMINI --> DECISION

    DECISION -->|"Information factuelle"| RAG

    DECISION -->|"Recommandation + profil suffisant"| ML

    DECISION -->|"Informations insuffisantes"| CLARIF

    RAG --> RESPONSE

    ML --> RESPONSE

    CLARIF --> RESPONSE
```

## 4.1 Décision basée sur les outils

La sélection de l'outil n'est pas réalisée par un classifieur d'intentions externe.

Elle est effectuée directement par Gemini grâce au **tool calling**.

Les outils disponibles sont :

```python
tools = [
    analyser_profil_candidat_ml,
    rechercher_documents_ispm_rag
]
```

L'agent dispose donc de deux capacités principales :

| Outil                           | Utilisation                                                     |
| ------------------------------- | --------------------------------------------------------------- |
| `rechercher_documents_ispm_rag` | Rechercher des informations officielles dans les documents ISPM |
| `analyser_profil_candidat_ml`   | Analyser le profil d'un candidat et recommander des filières    |

Lorsque les informations fournies par l'utilisateur sont insuffisantes pour effectuer une recommandation, l'agent peut demander des précisions avant d'appeler le modèle ML.

---

# 5. Prompt et règles de l'agent

Le comportement de l'agent est défini par un prompt système.

Les principales règles sont :

* utiliser le RAG pour les questions factuelles concernant les formations ;
* utiliser le modèle ML lorsqu'une recommandation est demandée et que le profil est suffisamment renseigné ;
* demander des précisions lorsque le profil fourni est insuffisant ;
* indiquer systématiquement la provenance des informations utilisées.

Le principe est donc :

```text
Question utilisateur
        │
        ▼
   Agent Gemini
        │
        ├──► Information institutionnelle
        │          │
        │          ▼
        │       RAG ISPM
        │
        ├──► Demande de recommandation
        │          │
        │          ▼
        │       Modèle ML
        │
        └──► Informations insuffisantes
                   │
                   ▼
             Demande de précisions
```

---

# 6. Architecture complète

La combinaison du pipeline de données et de l'architecture runtime donne la vue globale suivante :

```mermaid
flowchart TB

    %% ====================================
    %% PIPELINE HORS LIGNE
    %% ====================================

    subgraph OFFLINE["A. PIPELINE DE DONNÉES — HORS LIGNE"]

        SOURCES["Sources de données<br/>ISPM + Enquêtes + Données synthétiques"]

        PREP["Nettoyage<br/>Structuration<br/>Anonymisation"]

        RAG_DATA["Corpus documentaire"]

        ML_DATA["Dataset ML"]

        RAG_ENGINE["Base vectorielle RAG"]

        ML_ENGINE["Modèle ML de recommandation"]

        SOURCES --> PREP

        PREP --> RAG_DATA

        PREP --> ML_DATA

        RAG_DATA --> RAG_ENGINE

        ML_DATA --> ML_ENGINE

    end

    %% ====================================
    %% RUNTIME
    %% ====================================

    subgraph RUNTIME["B. APPLICATION — TEMPS RÉEL"]

        FRONT["Frontend React"]

        API["Backend FastAPI"]

        SECURITY["Sécurité & Guardrails"]

        AGENT["Agent Gemini<br/>ORIENT'IA"]

        TOOL_RAG["Outil RAG"]

        TOOL_ML["Outil ML"]

        AUDIT[("PostgreSQL<br/>Audit & historique")]

        FRONT -->|"HTTP / JSON"| API

        API --> SECURITY

        SECURITY --> AGENT

        AGENT --> TOOL_RAG

        AGENT --> TOOL_ML

        TOOL_RAG --> AGENT

        TOOL_ML --> AGENT

        AGENT --> AUDIT

        AGENT --> SECURITY

        SECURITY --> API

        API --> FRONT

    end

    %% ====================================
    %% LIEN OFFLINE / RUNTIME
    %% ====================================

    RAG_ENGINE -.->|"Base de connaissances"| TOOL_RAG

    ML_ENGINE -.->|"Modèle entraîné"| TOOL_ML
```

---

# 7. Résumé de l'architecture

L'architecture ORIENT'IA repose sur trois composants intelligents principaux :

### 1. Agent Gemini

Il constitue le **cerveau de l'application**.

Il comprend la demande de l'utilisateur et décide directement quel outil utiliser grâce au mécanisme de **tool calling**.

### 2. Moteur RAG

Il fournit des réponses basées sur les **documents officiels de l'ISPM**.

Il est utilisé pour les demandes nécessitant des informations factuelles et vérifiables.

### 3. Modèle ML

Il analyse le **profil du candidat** afin de produire des recommandations de filières.

Cette séparation permet de distinguer :

* les informations provenant des **documents institutionnels** ;
* les recommandations provenant du **modèle ML**.

L'agent Gemini assure l'orchestration entre ces deux capacités.

---

# 8. Flux global d'une requête

```text
┌─────────────────────┐
│    Utilisateur      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Frontend React   │
└──────────┬──────────┘
           │ HTTP / JSON
           ▼
┌─────────────────────┐
│    Backend FastAPI  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Sécurité & Guardrails│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Agent Gemini     │
│    ORIENT'IA        │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
┌─────────┐  ┌─────────┐
│   RAG   │  │   ML    │
│ ISPM    │  │Profil   │
└────┬────┘  └────┬────┘
     │            │
     └──────┬─────┘
            ▼
   ┌─────────────────┐
   │ Réponse finale  │
   └────────┬────────┘
            ▼
   ┌─────────────────┐
   │ Frontend React  │
   └─────────────────┘
```

**Principe architectural :**

> **Gemini ne prédit pas une intention prédéfinie : il raisonne sur la demande et choisit directement l'outil adapté.**

Cela simplifie l'architecture en supprimant la couche de classification d'intentions et permet d'ajouter ultérieurement de nouveaux outils à l'agent sans devoir modifier un classifieur d'intentions.
