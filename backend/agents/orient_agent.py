from agents.security import validate_input
from agents.tools.anomaly_detector import detect_anomaly
from agents.tools.ml_scorer import score_profile
from agents.tools.recommender import recommend_formations
from rag.retriever import retrieve_context

from agents.security import validate_input
from agents.tools.ml_tools import (
    analyser_et_scorer_profil,
    analyser_personnalite_et_interets
)
from agents.tools.rag_tools import rechercher_informations_ispm


# Chargement des variables d'environnement (.env)
load_dotenv()

class OrientIAAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY est manquante dans les variables d'environnement ou le fichier .env")

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            google_api_key=api_key,  
            temperature=0
        )
        
        self.tools = [
            analyser_et_scorer_profil,
            analyser_personnalite_et_interets,
            rechercher_informations_ispm
        ]
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Tu es ORIENT'IA, l'assistant intelligent d'orientation de l'ISPM.
            - Utilise `rechercher_informations_ispm` pour les questions factuelles sur les formations, cours, matières ou frais de scolarité.
            - Utilise `analyser_et_scorer_profil` quand l'utilisateur partage ses notes scolaires ou ses résultats académiques.
            - Utilise `analyser_personnalite_et_interets` quand l'utilisateur décrit son caractère, sa personnalité, ce qu'il aime ou ses centres d'intérêt.
            - Si l'utilisateur demande une recommandation mais qu'il manque des informations clés (notes ou centres d'intérêt), demande-lui des précisions.
            - Tu dois DISTINGUER clairement dans ta réponse les résultats issus des modèles ML (prédictions) et ceux issus de la recherche RAG (documents officiels ISPM)."""),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    def run(self, user_message: str, chat_history: list = None) -> dict:
        """Point d'entrée sécurisé pour traiter le message utilisateur."""

        # 1. Validation/nettoyage de l'entrée utilisateur contre les injections
        clean_message = validate_input(user_message)
        
        # 2. Exécution de l'agent avec historique de discussion
        result = self.agent_executor.invoke({
            "input": clean_message,
            "chat_history": chat_history or []
        })
        
        return {
            "response": result["output"],
            "status": "success"
        }