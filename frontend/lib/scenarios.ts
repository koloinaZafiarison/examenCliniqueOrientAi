export type OrientationResponses = {
  matieres_preferees: string
  competences: string
  centres_interet: string
  environnement_souhaite: string
}

export type Scenario = {
  id: string
  label: string
  responses: OrientationResponses
}

export const SCENARIOS: Scenario[] = [
  {
    id: "tech-ia",
    label: "J’aime programmer, la robotique et les sciences",
    responses: {
      matieres_preferees: "Mathématiques, physique, informatique",
      competences: "Programmation, logique, résolution de problèmes",
      centres_interet: "Robotique, intelligence artificielle, jeux vidéo",
      environnement_souhaite: "Laboratoire, startup technologique, projets en équipe",
    },
  },
  {
    id: "gestion",
    label: "Je m’intéresse à la gestion et à l’entrepreneuriat",
    responses: {
      matieres_preferees: "Économie, mathématiques, langues",
      competences: "Organisation, communication, analyse",
      centres_interet: "Entrepreneuriat, commerce, management",
      environnement_souhaite: "Bureau, entreprise, travail en réseau",
    },
  },
  {
    id: "sante-humain",
    label: "Je veux un métier tourné vers le contact humain",
    responses: {
      matieres_preferees: "SVT, français, langues",
      competences: "Écoute, pédagogie, travail d’équipe",
      centres_interet: "Santé, accompagnement, sciences humaines",
      environnement_souhaite: "Établissement de soin, association, terrain",
    },
  },
  {
    id: "sciences-environnement",
    label: "Je veux lier sciences et environnement",
    responses: {
      matieres_preferees: "SVT, physique-chimie, géographie",
      competences: "Observation, analyse de données, rigueur scientifique",
      centres_interet: "Écologie, climat, sciences de la terre",
      environnement_souhaite: "Terrain, laboratoire, organismes publics",
    },
  },
  {
    id: "creation",
    label: "Je préfère les filières créatives et artistiques",
    responses: {
      matieres_preferees: "Arts plastiques, français, histoire",
      competences: "Créativité, expression visuelle, culture générale",
      centres_interet: "Design, audiovisuel, communication",
      environnement_souhaite: "Studio, agence, ateliers collaboratifs",
    },
  },
]

export function getScenarioById(id: string): Scenario | undefined {
  return SCENARIOS.find((scenario) => scenario.id === id)
}

export function toOrientationPayload(scenario: Scenario) {
  return { responses: scenario.responses }
}
