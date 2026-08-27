from collections import defaultdict

# Base de connaissances ISPM (filiere -> nom + metiers)
filieres_ispm = {
    "IGGLIA": {"nom": "Informatique et Télécommunication", "metiers": ["Développeur d'applications", "Ingénieur en systèmes d'information", "Chef de projet IT", "Analyste fonctionnel"]},
    "ISAIA": {"nom": "Informatique et Télécommunication", "metiers": ["Data analyst", "Chargé d'études statistiques", "Data scientist junior", "Actuaire junior"]},
    "CAA": {"nom": "Techniques des Affaires", "metiers": ["Responsable marketing", "Chargé de clientèle", "Chef des ventes", "Entrepreneur / créateur d'entreprise"]},
    "FIC": {"nom": "Techniques des Affaires", "metiers": ["Comptable", "Contrôleur de gestion", "Analyste financier", "Auditeur junior"]},
    "IAA": {"nom": "Biotechnologie et Agronomie", "metiers": ["Ingénieur agroalimentaire", "Responsable qualité", "Technicien de production", "Responsable R&D"]},
    "PIP": {"nom": "Biotechnologie et Agronomie", "metiers": ["Assistant de recherche pharmaceutique", "Technicien de laboratoire pharmaceutique", "Responsable qualité en industrie pharmaceutique"]},
    "AEE": {"nom": "Biotechnologie et Agronomie", "metiers": ["Technicien agricole", "Responsable d'exploitation agricole", "Conseiller agricole", "Entrepreneur en agribusiness"]},
    "EMII": {"nom": "Génie Industriel et Génie Civil", "metiers": ["Ingénieur maintenance industrielle", "Technicien automaticien", "Responsable de production", "Ingénieur projet électrique"]},
    "GCA": {"nom": "Génie Industriel et Génie Civil", "metiers": ["Ingénieur BTP", "Architecte", "Conducteur de travaux", "Urbaniste", "Métreur"]},
    "TEE": {"nom": "Techniques du Tourisme", "metiers": ["Guide touristique / écotouristique", "Agent de valorisation du patrimoine", "Chargé de mission environnement-tourisme"]},
    "TEH": {"nom": "Techniques du Tourisme", "metiers": ["Manager d'établissement hôtelier", "Chef de cuisine", "Responsable réception", "Agent de voyage"]},
    "ESIIA": {"nom": "Informatique et Télécommunication", "metiers": ["Ingénieur électronique", "Ingénieur systèmes embarqués", "Technicien réseaux et télécommunications", "Ingénieur support informatique"]},
    "IMTICIA": {"nom": "Informatique et Télécommunication", "metiers": ["Développeur multimédia", "Intégrateur web", "Administrateur réseaux/télécoms junior", "Technicien audiovisuel numérique", "Chargé de communication digitale"]},
    "DTJA": {"nom": "Techniques des Affaires", "metiers": ["Juriste d'entreprise", "Assistant juridique", "Chargé de conformité", "Conseiller juridique junior", "Technicien du droit"]},
    "EMP": {"nom": "Techniques des Affaires", "metiers": ["Économiste junior", "Chargé d'études économiques", "Analyste économique", "Chargé de projet", "Consultant junior en économie"]},
    "ICMP": {"nom": "Génie Industriel et Génie Civil", "metiers": ["Ingénieur procédés junior", "Technicien chimiste", "Technicien minier", "Technicien pétrolier", "Responsable HSE junior"]},
}

tous_les_codes = list(filieres_ispm.keys())

career_vers_filieres = {
    "Software Engineer": ["IGGLIA"],
    "Business Owner": ["CAA"],
    "Banker": ["FIC"],
    "Lawyer": ["DTJA"],
    "Accountant": ["FIC"],
    "Real Estate Developer": ["GCA"],
    "Stock Investor": ["FIC"],
    "Construction Engineer": ["GCA"],
    "Game Developer": ["IMTICIA"],
    "Government Officer": ["DTJA"],
    "Scientist": ["ISAIA"],
    "Social Network Studies": ["IMTICIA"],
    "Doctor": ["PIP"],           
    "Designer": ["IMTICIA"],     
    "Writer": ["DTJA"],          
    "Teacher": tous_les_codes,   
}


def recommend_formations(profile_dict: dict, score_result: dict, n: int = 3) -> dict:
    """
    Agrège les probabilités par métier pour calculer les scores par filière ISPM 
    et conserve les métiers prédits.
    """
    if not score_result.get("has_scores"):
        return {"error": "Impossible d'agréger les filières sans notes chiffrées."}

    proba_par_carriere = score_result.get("probas_carriere", {})

    proba_par_filiere = defaultdict(float)
    metiers_par_filiere = defaultdict(list)

    # Agrégation et répartition équitable
    for carriere, proba in proba_par_carriere.items():
        filieres = career_vers_filieres.get(carriere, [])
        if not filieres:
            continue
        
        proba_repartie = proba / len(filieres)
        
        for code_filiere in filieres:
            proba_par_filiere[code_filiere] += proba_repartie
            metiers_par_filiere[code_filiere].append((carriere, proba))

    # Tri par probabilité décroissante
    filieres_triees = sorted(proba_par_filiere.items(), key=lambda x: x[1], reverse=True)[:n]

    recommendations = {}
    for code, proba in filieres_triees:
        jobs_tries = sorted(metiers_par_filiere[code], key=lambda x: x[1], reverse=True)
        
        recommendations[code] = {
            "nom_filiere": filieres_ispm.get(code, {}).get("nom", "Filière inconnue"),
            "score_confiance": f"{round(proba * 100, 1)}%",
            "metiers_cibles": [job for job, p in jobs_tries[:3]]
        }

    return recommendations