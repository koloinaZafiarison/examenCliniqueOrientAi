import os

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)
from langchain_core.prompts import ChatPromptTemplate

from agents.security import validate_input
from agents.tools.ml_tools import (
    analyser_et_scorer_profil,
    analyser_personnalite_et_interets,
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
            model="gemini-3.5-flash",
            google_api_key=api_key,
            temperature=0,
        )

        self.tools = [
            analyser_et_scorer_profil,
            analyser_personnalite_et_interets,
            rechercher_informations_ispm,
        ]

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
Tu es ORIENT'IA, l'assistant intelligent d'orientation de l'ISPM.

- Utilise `rechercher_informations_ispm` pour les questions
  factuelles sur les formations, cours, matières ou frais de scolarité.

- Utilise `analyser_et_scorer_profil` lorsque l'utilisateur
  fournit ses notes scolaires ou résultats académiques.

- Utilise `analyser_personnalite_et_interets` lorsque l'utilisateur
  décrit sa personnalité, ses passions ou ses centres d'intérêt.

- Si l'utilisateur demande une recommandation mais qu'il manque
  des informations importantes, demande-lui des précisions.

- Distingue clairement les résultats issus des modèles ML
  des informations issues de la recherche RAG.
                """,
            ),
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

        # Validation de l'entrée utilisateur
        clean_message = validate_input(user_message)

        # Exécution de l'agent
        result = self.agent_executor.invoke({
            "input": clean_message,
            "chat_history": chat_history or [],
        })

        return {
            "response": result["output"],
            "status": "success",
        }