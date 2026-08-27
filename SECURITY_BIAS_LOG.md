# Journal de Sécurité, Biais et Limites

## 1. Principes Généraux
- Le système propose uniquement des recommandations indicatives.
- Aucune donnée sensible (genre, origine, situation sociale) n'est utilisée.
- Les décisions finales d'orientation restent entièrement entre les mains des humains.

## 2. Limites du Système
- **Modèle de Notes** : L'extraction par Regex peut rater des notes si le format du texte est inhabituel.
- **Modèle de Personnalité** : Les résultats reposent sur des déclarations spontanées qui peuvent varier selon l'humeur.
- **Base RAG** : Le RAG répond uniquement à partir des documents officiels enregistrés pour l'ISPM.
- **Imputation** : Les notes manquantes sont devinées par calcul, ce qui peut masquer certains points forts.

## 3. Biais Identifiés
- **Désirabilité sociale** : L'utilisateur peut surévaluer ses notes ou adapter la description de son caractère.
- **Stéréotypes** : Le modèle peut lier certains traits de caractère à des métiers précis.
- **Conflits de sources** : La recommandation des modèles ML peut parfois différer des détails trouvés par le RAG.

## 4. Risques et Solutions

| Risque | Description | Solution |
| :--- | :--- | :--- |
| **Surconfiance** | Croire aveuglément au résultat. | R rappeler toujours le caractère indicatif du score. |
| **Profilage** | Étiqueter rigidement un étudiant. | Ne pas stocker de profil psychologique nominatif. |
| **Hallucination** | Erreurs sur les cours de l'ISPM. | Bloquer le LLM sur la base documentaire officielle. |

## 5. Gouvernance
- Un entretien avec un conseiller d'orientation reste indispensable.
- L'étudiant peut demander à voir les critères utilisés pour sa recommandation.
