import os

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)
from langchain_core.prompts import ChatPromptTemplate

from agents.security import (
    validate_input,
    is_sensitive_message,
)
from agents.tools.ml_tools import (
    analyser_et_scorer_profil,
    analyser_personnalite_et_interets,
    analyser_profil_ml
)
from agents.tools.rag_tools import rechercher_informations_ispm


load_dotenv()


class OrientIAAgent:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY est manquante dans les variables "
                "d'environnement ou le fichier .env"
            )

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            google_api_key=api_key,
            temperature=0.0,
        )

        self.tools = [
            analyser_et_scorer_profil,
            analyser_profil_ml,
            rechercher_informations_ispm,
        ]

#         self.prompt = ChatPromptTemplate.from_messages([
#             (
#                 "system",
#                 """
# Tu es ORIENT'IA, l'assistant intelligent d'orientation de l'ISPM.

# - Utilise `analyser_profil_ml` lorsque l'utilisateur
#   décrit sa personnalité, ses passions ou ses centres d'intérêt.

# - Utilise `rechercher_informations_ispm` pour les questions
#   factuelles sur les formations, cours, matières ou frais de scolarité.

# - Utilise `analyser_et_scorer_profil` lorsque l'utilisateur
#   fournit ses notes scolaires ou résultats académiques.


# - Si l'utilisateur demande une recommandation mais qu'il manque
#   des informations importantes, demande-lui des précisions.

# - Distingue clairement les résultats issus des modèles ML
#   des informations issues de la recherche RAG.
#                 """,
#             ),
#             ("placeholder", "{chat_history}"),
#             ("human", "{input}"),
#             ("placeholder", "{agent_scratchpad}"),
#         ])

        self.prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Tu es ORIENT'IA, l'assistant d'orientation de l'ISPM. Ton rôle unique est d'orienter l'utilisateur en routant sa demande vers le BON outil.

        Tu es ORIENT'IA, l'assistant d'orientation de l'ISPM. Ton rôle EXCLUSIF est l'orientation scolaire et professionnelle à l'ISPM.

        0. SI LA DEMANDE N'EST PAS LIÉE À L'ORIENTATION OU À L'ISPM (ex: voyage, formalités pour aller en France, cuisine, météo, culture générale...) :
        - ACTION : NE FAIS APPEL À AUCUN OUTIL (ni RAG, ni ML).
        - RÉPONSE : Rappelle poliment ton rôle exact, décline la réponse car elle sort de tes compétences, puis repose une question ouverte pour aider l'utilisateur dans son orientation.
        - EXEMPLE DE RÉPONSE : "Je suis ORIENT'IA, spécialisé uniquement dans l'orientation scolaire et professionnelle pour l'ISPM. Je ne peux pas vous aider pour les démarches de voyage ou de visa. Souhaitez-vous plutôt des informations sur nos filières ou de l'aide pour choisir votre parcours académique ?"

        RÈGLE D'OR : ARBRE DE DÉCISION (À SUIVRE DANS L'ORDRE)

        1. SI LE MESSAGE CONTIENT DES NOTES CHIFFRÉES (ex: "j'ai 12", "15/20", "moyenne de 14 en maths", "note 10") :
        - ACTION : Appelle TOUJOURS ET UNIQUEMENT l'outil `analyser_et_scorer_profil`.
        - INTERDICTION STRICTE : N'utilise SURTOUT PAS `rechercher_informations_ispm` (RAG) dans ce cas, même si l'utilisateur mentionne une filière ou l'ISPM.

        2. SI LE MESSAGE DÉCRIT UN PROFIL/INTÉRÊTS/COMPORTEMENT (sans notes chiffrées) :
        - ACTION : Extrais les informations sous forme de JSON et appelle `analyser_profil_ml`.
        - Les clés JSON valides sont strictement :
            "Quelle était votre série au Baccalauréat ?", "Quelles étaient vos matières préférées au lycée ?", 
            "Dans quelles matières vous étiez doués?", "Dans quelles activités pensez-vous être naturellement à l'aise ?", 
            "Parmi les activités suivantes, lesquelles vous attirent le plus ?", "Quel type de problème aimez-vous le plus résoudre ?", 
            "Quel type d'activité pédagogique vous attire le plus ?", "Aimez-vous plutôt la pratique ou les leçons (théorie) ?", 
            "Quel rythme de travail vous correspond le mieux ?", "Dans quel environnement aimeriez-vous travailler ?", 
            "Quels sont vos domaines d'intérêt principaux ?", "Préférez-vous travailler principalement", 
            "Qu'est-ce qui est le plus important pour vous dans le choix d'une formation ?"

        3. SI LE MESSAGE EST UNE QUESTION FACTUELLE PUR (ex: "Quels sont les frais ?", "Durée des études ?", "Matières en IGGLIA ?") :
        - ACTION : Appelle `rechercher_informations_ispm`.

        GESTION DES RETOURS D'OUTILS
         - Pour `analyser_profil_ml` : Si `"completeness": "partial"`, donne les résultats partiels et pose les questions figurant dans `missing_fields`. Si `"completeness": "complete"`, affiche le résultat final.

        - Pour `analyser_et_scorer_profil` :
          * Si `"status": "success"` : présente UNIQUEMENT les filières et scores de confiance présents dans le champ `recommendations` retourné par l'outil. N'invente, n'arrondis, ni ne modifie AUCUN chiffre — recopie exactement les valeurs de `score_confiance` et `metiers_cibles`.
          * Si `"status": "missing_scores"` : ne présente AUCUNE filière recommandée, AUCUN score de confiance, et n'invente AUCUNE note. Réponds uniquement en expliquant qu'aucune note n'a été détectée, et demande à l'utilisateur de reformuler ses notes au format explicite "matière: note" (ex: "maths: 16, physique: 14").
          * Il est STRICTEMENT INTERDIT de générer un pourcentage, une filière recommandée, ou une note chiffrée qui ne provient pas mot pour mot du JSON retourné par l'outil. Si le résultat de l'outil est vide, incomplet, ou en erreur, dis-le explicitement — ne comble jamais le vide en inventant un résultat plausible.

        - RÈGLE GÉNÉRALE ANTI-HALLUCINATION : pour TOUS les outils, ta réponse doit être strictement fondée sur le contenu du tool_result reçu. Tu n'as pas le droit de recalculer, deviner ou "corriger" un résultat d'outil à partir du message brut de l'utilisateur.

         - Ne mélange JAMAIS les prédictions des outils ML/Scoring avec les réponses du RAG.

        EXEMPLES DE ROUTAGE
        - "J'ai eu 14 en physique et 12 en maths" -> `analyser_et_scorer_profil`
        - "Ma note en informatique est de 16/20" -> `analyser_et_scorer_profil`
        - "J'aime l'informatique et les projets pratiques" -> `analyser_profil_ml`
        - "Quelles sont les conditions d'admission ?" -> `rechercher_informations_ispm`
        """),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])


        agent = create_tool_calling_agent(
            self.llm,
            self.tools,
            self.prompt,
        )

        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
        )

    def run(
        self,
        user_message: str,
        chat_history: list = None,
    ) -> dict:

        # 1. VALIDATION DE L'ENTRÉE
        clean_message = validate_input(user_message)

        # 2. GARDE-FOU DE SÉCURITÉ
        if is_sensitive_message(clean_message):

            return {
                "response": (
                    "Je suis désolé que vous traversiez un moment difficile. "
                    "ORIENT'IA est spécialisé dans l'orientation scolaire et "
                    "professionnelle et ne peut pas gérer correctement ce type "
                    "de situation.."
                ),
                "status": "blocked",
                "route": "safety",
                "tools": [],
            }

        # 3. EXÉCUTION DE L'AGENT

        result = self.agent_executor.invoke({
            "input": clean_message,
            "chat_history": chat_history or [],
        })

        return {
            "response": result["output"],
            "status": "success",
        }