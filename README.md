# QUICKSILVER 🤖

## Institut Supérieur Polytechnique de Madagascar : http://www.ispm-edu.com/
Membre de l'équipe **(IGGLIA 5)** et le rôle respectif de chacun: 
  * **RANDRIANOELINA Liantsoa Harimisa                       ,n°14** 
  * **ZAFIARISON Koloina Emile                               ,n°16**
  * **RANDIMBINIRINA RAKOTOMANANA Yusha Andry Ny Aina        ,n°19**
  * **RASOLONJATOVO Zo Heriniaina                            ,n°23**

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
