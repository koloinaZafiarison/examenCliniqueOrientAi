# Orient'AI

Prototype d'orientation académique et professionnelle basé sur un questionnaire synthétique. L'application combine un score ML, une détection d'anomalies, une recommandation KNN et une recherche documentaire RAG.

## Démarrage rapide

```powershell
docker compose up --build
```

API disponible sur `http://localhost:8000/docs`. Le frontend se lance séparément avec `cd frontend; npm install; npm run dev`.

## Structure

- `backend/`: API FastAPI, agent d'orchestration, outils ML, RAG et audit.
- `ml/`: notebooks, données d'exemple et scripts d'entraînement.
- `frontend/`: interface React de conversation et visualisation des traces.

## Limites

Les données fournies sont synthétiques. Le système ne réalise aucun diagnostic médical et ne doit pas être utilisé pour profiler ou discriminer une personne. Les modèles joblib et l'index Qdrant sont à produire localement.
