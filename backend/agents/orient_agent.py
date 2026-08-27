import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

from backend.agents.security import validate_input
from backend.agents.tools.ml_tools import analyser_et_scorer_profil
from backend.agents.tools.rag_tools import rechercher_informations_ispm

# Charge le fichier .env si les variables ne sont pas déjà dans l'environnement
load_dotenv()

class OrientIAAgent:
    def __init__(self):
        # Récupération de la clé API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY est manquante dans les variables d'environnement ou le fichier .env")

        # Initialisation du LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            google_api_key=api_key,  
            temperature=0
        )
        
        # Enregistrement des outils métiers
        self.tools = [analyser_et_scorer_profil, rechercher_informations_ispm]
        
        # System Prompt avec les consignes strictes du sujet
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Tu es ORIENT'IA, l'assistant intelligent d'orientation de l'ISPM.
            - Utilise `rechercher_informations_ispm` pour les questions factuelles sur les formations, cours ou frais.
            - Utilise `analyser_et_scorer_profil` quand l'utilisateur partage son profil, ses notes ou veut une recommandation.
            - Si l'utilisateur demande une recommandation mais qu'il manque des informations clés (notes, intérêts), demande des précisions.
            - Tu dois DISTINGUER clairement dans ta réponse les résultats venant du modèle ML et ceux des documents RAG."""),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    def run(self, user_message: str, chat_history: list = None) -> dict:
        """Point d'entrée sécurisé pour traiter le message utilisateur."""
        # 1. Couche de sécurité
        clean_message = validate_input(user_message)
        
        # 2. Exécution de l'agent avec routing dynamique (RAG vs ML)
        result = self.agent_executor.invoke({
            "input": clean_message,
            "chat_history": chat_history or []
        })
        
        return {
            "response": result["output"],
            "status": "success"
        }