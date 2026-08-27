# QUICKSILVER 🤖

## Institut Supérieur Polytechnique de Madagascar : http://www.ispm-edu.com/
Membre de l'équipe **(IGGLIA 5)** et le rôle respectif de chacun: 
  * **RANDRIANOELINA Liantsoa Harimisa                       ,n°14** : Collecte de données RAG et  implémentation de l'agent routeur.
  * **ZAFIARISON Koloina Emile                               ,n°16** : Collecte de données synthétique et le Front-End de l'application.
  * **RANDIMBINIRINA RAKOTOMANANA Yusha Andry Ny Aina        ,n°19** : Mise en place des données sur les Enquetes et création des Endpoints du backend.
  * **RASOLONJATOVO Zo Heriniaina                            ,n°23** : Collecte de données synthétique et création du modèle Machine Learning.

# Orient'AI

Prototype d'orientation académique et professionnelle basé sur un questionnaire synthétique. L'application combine un score ML, une détection d'anomalies, une recommandation KNN et une recherche documentaire RAG.

## Lien déploiement Front-End : https://examen-clinique-orient-ai.vercel.app/ 

API disponible sur `http://localhost:8000/docs`. Le frontend se lance séparément avec `cd frontend; npm install; npm run dev`.

## Structure

- `backend/`: API FastAPI, agent d'orchestration, outils ML, RAG et audit.
- `ml/`: notebooks, données d'exemple et scripts d'entraînement.
- `frontend/`: interface React de conversation et visualisation des traces.

## Limites

Les données fournies sont synthétiques. Le système ne réalise aucun diagnostic médical et ne doit pas être utilisé pour profiler ou discriminer une personne. Les modèles joblib et l'index Qdrant sont à produire localement.

## Livrables

- ### **Livrable 1** : Le code source complet est disponible dans le dépôt, avec l’ensemble des modules :

  notebooks/Modèle_orientation_ML_.ipynb – Notebook complet d’EDA, preprocessing, modélisation et évaluation.

  agents/orient_agent.py – Agent conversationnel (LangChain) intégrant les outils ML et RAG.

  agents/tools/ml_tools.py – Outil analyser_profil_ml avec chargement du modèle, prétraitement, prédiction et recommandation.

  agents/tools/rag_tools.py – Outil rechercher_informations_ispm (à compléter avec le vrai RAG).

  agents/tools/ml_scorer.py – Scorer basé sur les notes (modèle HF).

  agents/tools/recommender.py – Agrégation des scores par filière.

  agents/security.py – Validation des entrées (anti‑injection).

  agents/anomaly_detector.py – Détection d’anomalies (placeholder).

  agents/__init__.py – Package initialisé.

- ### **Livrable 2** : Le fichier se trouve dans la répertoire racine nommée livrable-2-instructions-installation-éxécution.md

- ### **Livrable 3** : Le mécanisme de collecte est documenté dans le notebook et dans le rapport.

  Les données utilisées sont :

  *  donnees_synthetiques_finales_CORRIGE.csv (1000 lignes) – générées synthétiquement selon des règles définies dans le notebook.

  *  Réponse enquête - Réponses au formulaire 1.csv (36 lignes) – collectées via un questionnaire en ligne (Google Forms).

  Le questionnaire d’enquête, les Datasets est inclus dans le dossier ml/data/.
  Le notebook contient le code pour charger, nettoyer et harmoniser les deux sources.

- ### **Livrable 4** : Le registre des sources se trouve dans le fichier SOURCES_REGISTRY.json du répertoire racine.

- ### **Livrable 5** : Jeu de données utilisé pour le Machine Learning

  Le jeu d’entraînement est donnees_synthetiques_finales_CORRIGE.csv (1000 lignes, 18 colonnes).
  Il est disponible dans le dossier ml/data/.

- ### **Livrable 6** : Questionnaire d’enquête, registre de collecte et réponses anonymisées

  Le questionnaire est dans ce lien : https://docs.google.com/forms/d/e/1FAIpQLSfosiDuUvDLgrUEFyjyY_7Zx9Z4D6et14cQrVVRVrj3bayiXQ/viewform .

  Le registre de collecte est inclus dans le notebook (cellules dédiées).

  Les réponses anonymisées sont dans ml/data/Réponse enquête - Réponses au formulaire 1.csv.

- ### **Livrable 7** : Notebooks d’analyse et d’entraînement

  Le notebook dans le dossier ml/notebooks/Modèle_orientation_ML_.ipynb contient :

   * Analyse exploratoire (EDA) des données synthétiques et réelles.

   * Preprocessing (nettoyage, encodage, normalisation).

   * Entraînement de trois modèles (Logistic Regression, Random Forest, XGBoost).

   * Sélection du meilleur modèle (Logistic Regression).

   * Évaluation (métriques Top‑1/3/5, F1, MRR, NDCG).

   * Analyse des erreurs et des biais.

   * Sauvegarde des artefacts (modèle, encodeurs, scaler, métadonnées).

- **Livrable 8** : Modèle entraîné

   * Le modèle entraîné (model.pkl) et ses artefacts (encoders.pkl, scaler.pkl, metadata.json) sont dans ml/models/.

   * Le notebook permet de reproduire l’entraînement en exécutant toutes les cellules.
 
- **Livrable 9** : Jeu d’évaluation

    Le jeu d’évaluation est le sous‑ensemble de test (100 échantillons) extrait du dataset synthétique par split 80/10/10.
    Les données sont intégrées dans le notebook et ne sont pas fournies comme fichier séparé (car elles sont issues du même fichier source).
    Les métriques sont calculées dans le notebook.

- ### **Livrable 10** : Résultats d’évaluation

  Les résultats d’évaluation sont présentés dans le notebook (cellule 12) et dans le rapport final.

| Métrique | Score |
|----------|-------|
| **Top‑1 Accuracy** | 59,0 % |
| **Top‑3 Accuracy** | 89,0 % |
| **Top‑5 Accuracy** | 99,0 % |
| **F1‑macro** | 0,592 |
| **MRR** (Mean Reciprocal Rank) | 0,747 |
| **NDCG@5** | 0,807 |

La matrice de confusion et l’analyse des erreurs sont également fournies.

---

### ***Livrable 11*** : Schéma d’architecture

Un schéma d’architecture est disponible dans ARCHITECTURE.md du dossier racine.  
Il illustre les composants du système :

- **Utilisateur** ↔ **Agent LLM** (Gemini).
- **Agent** ↔ **Outils** :
  - `analyser_profil_ml` (modèle ML)
  - `analyser_et_scorer_profil` (scoring par notes)
  - `rechercher_informations_ispm` (RAG)
- **Modèle ML** ↔ **Artefacts** (model.pkl, encoders, scaler).
- **RAG** ↔ **Base vectorielle** (documents ISPM).
- **Réponse** → retour à l’utilisateur.

Une description textuelle est également disponible dans le fichier ARCHITECTURE.md.

---

### **Livrable 12** :  Note présentant les limites, les biais et les risques se trouve dans le fichier SECURITY_BIAS_LOG.md dans le répertoire racine.


---

 ### **Livrable 13** : Vidéo de présentation de 3 à 5 minutes

Une vidéo de démonstration (format MP4) est disponible dans ` `.  
Elle montre le système en fonctionnement :

- Lancement de l’agent.
- Cas d’usage : demande de recommandation avec profil complet.
- Cas d’usage : profil incomplet → l’agent pose des questions complémentaires.
- Cas d’usage : question factuelle sur l’ISPM (RAG).
- Présentation des résultats (recommandations, scores, points forts, confiance).

---


