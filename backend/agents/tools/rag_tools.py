from langchain_core.tools import tool
#from rag.retriever import retrieve_context

@tool
def rechercher_informations_ispm(query: str) -> str:
    """
    À utiliser pour répondre aux questions factuelles sur l'ISPM, les cours, les diplômes,
    les prérequis, les frais de scolarité ou les détails d'un parcours.
    """
    #context = retrieve_context({"query": query})
    return f"Documents officiels ISPM : {context}"