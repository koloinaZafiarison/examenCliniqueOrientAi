from langchain_core.tools import tool

from .retriever import retrieve_context


@tool
def rechercher_informations_ispm(query: str) -> str:
    """
    À utiliser pour répondre aux questions factuelles sur l'ISPM, les cours, les diplômes,
    les prérequis, les frais de scolarité ou les détails d'un parcours.
    """
    try:
        context = retrieve_context(query)
    except FileNotFoundError as e:
        # Le fichier Excel source n'a pas été trouvé : on le signale clairement à l'agent
        # plutôt que de renvoyer un contexte vide qui l'inciterait à halluciner une réponse.
        return f"Erreur : base documentaire ISPM indisponible ({e})"

    return f"Documents officiels ISPM :\n{context}"