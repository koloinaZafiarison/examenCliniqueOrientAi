"use client";

import { useState } from "react";
import {
  ArrowUp,
  BookOpen,
  Check,
  ChevronDown,
  ChevronRight,
  CircleHelp,
  Clock3,
  FileText,
  FlaskConical,
  GraduationCap,
  Info,
  Menu,
  PanelRight,
  Pencil,
  Search,
  ShieldCheck,
  Sparkles,
  UserRound,
  X,
  Wrench,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScenarioDropdown } from "@/components/ui/scenario-dropdown";
import {
  getScenarioById,
  toOrientationPayload,
  type Scenario,
} from "@/lib/scenarios";

import Image from 'next/image'
import imageLogo from "../public/logoISPM.jpg"

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Recommendation = {
  formation: string;
  reason: string;
};

const profileFields = [
  { label: "Matières préférées", value: null },
  { label: "Compétences", value: null },
  { label: "Centres d'intérêt", value: null },
  { label: "Environnement souhaité", value: null },
];

export function SourceCitation({
  number,
  title,
  origin,
  date,
}: {
  number: number;
  title?: string;
  origin?: string;
  date?: string;
}) {
  return (
    <button
      className="source-citation"
      aria-label={`Source ${number}: ${title ?? "à renseigner"}`}
    >
      <span>[{number}]</span> {title ?? "Source à renseigner"}{" "}
      <ChevronRight aria-hidden="true" />
      {(origin || date) && (
        <small>
          {origin} · consultée le {date}
        </small>
      )}
    </button>
  );
}

export function ChatMessage({
  role,
  children,
}: {
  role: "assistant" | "user";
  children: React.ReactNode;
}) {
  return (
    <article className={`message ${role}`}>
      <div className="message-avatar" aria-hidden="true">
        {role === "assistant" ? <Sparkles /> : <UserRound />}
      </div>
      <div className="message-body">
        <div className="message-meta">
          {role === "assistant" ? "ORIENT'IA" : "Vous"}{" "}
          <span>{role === "assistant" ? "Texte généré" : "Message"}</span>
        </div>
        <div className="message-content">{children}</div>
      </div>
    </article>
  );
}

export function RecommendationCard({
  recommendations = [],
}: {
  recommendations?: Recommendation[];
}) {
  const [expanded, setExpanded] = useState(false);
  const hasRecommendations = recommendations.length > 0;
  return (
    <section
      className="recommendation-card"
      aria-label="Recommandations de parcours"
    >
      <div className="card-heading">
        <div className="icon-box">
          
        </div>
        <div>
          <p className="eyebrow">Recommandations</p>
          <h2>
            {hasRecommendations
              ? "Parcours proposés"
              : "Vos parcours apparaîtront ici"}
          </h2>
        </div>
      </div>
      {hasRecommendations ? (
        <div className="empty-recommendation">
          {recommendations.map((item) => (
            <p key={item.formation}>
              <strong>{item.formation}</strong>
              <br />
              {item.reason}
            </p>
          ))}
          <Button
            variant="outline"
            size="sm"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? "Masquer les détails" : "Voir le fonctionnement"}{" "}
            <ChevronDown />
          </Button>
        </div>
      ) : (
        <div className="empty-recommendation">
          <div className="recommendation-line">
            <span />
            <span />
            <span />
          </div>
          <p>
            Après quelques échanges, ORIENT’IA vous proposera des parcours adaptés
            à votre profil et expliquera chaque recommandation.
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? "Masquer les détails" : "Voir le fonctionnement"}{" "}
            <ChevronDown />
          </Button>
        </div>
      )}
      {expanded && (
        <div className="explanation">
          <Check /> Chaque score sera accompagné de facteurs explicatifs et de
          sources vérifiables.
        </div>
      )}
    </section>
  );
}

export function ComparisonView() {
  return (
    <section className="comparison-card">
      <div className="card-heading">
        <div className="icon-box muted-icon">
          <BookOpen />
        </div>
        <div>
          <p className="eyebrow">Comparateur</p>
          <h2>Comparer des parcours</h2>
        </div>
      </div>
      <div className="comparison-empty">
        <CircleHelp />
        <p>
          Sélectionnez 2 à 3 parcours pour comparer les matières, prérequis et
          débouchés côte à côte.
        </p>
        <Button variant="outline" size="sm" disabled>
          Comparer des parcours
        </Button>
      </div>
    </section>
  );
}


export default function OrientiaWorkspace() {
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<React.ReactNode[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string | null>(
    null,
  );
  const [isSending, setIsSending] = useState(false);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);

  function appendMessages(...nodes: React.ReactNode[]) {
    setMessages((current) => [...current, ...nodes]);
  }

  async function sendOrientation(scenario: Scenario) {
    const payload = toOrientationPayload(scenario);
    const response = await fetch(`${API_BASE_URL}/api/orient`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(`Le serveur a répondu ${response.status}`);
    }
    return response.json() as Promise<{ recommendations?: Recommendation[] }>;
  }

  async function submitScenario(scenarioId: string) {
    const scenario = getScenarioById(scenarioId);
    if (!scenario || isSending) return;

    setSelectedScenarioId(scenarioId);
    setIsSending(true);
    appendMessages(
      <ChatMessage key={`${scenario.id}-user-${Date.now()}`} role="user">
        {scenario.label}
      </ChatMessage>,
    );

    try {
      const data = await sendOrientation(scenario);
      const nextRecommendations = data.recommendations ?? [];
      setRecommendations(nextRecommendations);
      appendMessages(
        <ChatMessage
          key={`${scenario.id}-assistant-${Date.now()}`}
          role="assistant"
        >
          {nextRecommendations.length > 0 ? (
            nextRecommendations.map((item) => (
              <p key={item.formation}>
                <strong>{item.formation}</strong> — {item.reason}
              </p>
            ))
          ) : (
            <p>Aucune recommandation n’a été renvoyée pour ce profil.</p>
          )}
        </ChatMessage>,
      );
    } catch {
      appendMessages(
        <ChatMessage
          key={`${scenario.id}-error-${Date.now()}`}
          role="assistant"
        >
          <p>
            Impossible d’obtenir une orientation pour le moment. Vérifiez que
            l’API est disponible, puis réessayez.
          </p>
        </ChatMessage>,
      );
    } finally {
      setIsSending(false);
    }
  }

  //TODO: Send message to the server
  function sendMessage() {
    if (!draft.trim()) return;
    setMessages((current) => [
      ...current,
      <ChatMessage key={current.length} role="user">
        {draft}
      </ChatMessage>,
    ]);
    setDraft("");
  }

  return (
    <main className="orientia-shell">
      <header className="topbar">
        <div className="ml-10 brand ">
          <Image className="h-20 w-20" src={imageLogo} alt="logo"/>
          <div>
            <strong>ORIENT'IA</strong>
          </div>
        </div>
        <div className="top-actions">
          <span className="secure-status">
            <ShieldCheck /> Données protégées
          </span>
        </div>
      </header>
      <div className="workspace-grid">
        <section className="main-column">
            <div className="chat-screen">
              <div className="chat-heading">
                <div>
                  <p className="eyebrow">
                    Session d’orientation · Nouvelle conversation
                  </p>
                  <h1>Parlons de votre avenir.</h1>
                </div>
              </div>
              <div className="conversation">
                <ChatMessage role="assistant">
                  <p>
                    Bonjour, je suis ORIENT’IA. Je vais vous aider à clarifier
                    votre projet d’avenir, étape par étape.
                  </p>
                </ChatMessage>
                {messages}
              </div>
              <div className="composer">
                <div className="composer-scenarios">
                  <ScenarioDropdown
                    value={selectedScenarioId}
                    disabled={isSending}
                    onValueChange={submitScenario}
                  />
                </div>
                <textarea
                  value={draft}
                  onChange={(event) => setDraft(event.target.value)}
                  placeholder="Écrivez votre réponse…"
                  aria-label="Votre réponse"
                  onKeyDown={(event) => {
                    if (
                      event.key === "Enter" &&
                      !event.shiftKey &&
                      !event.nativeEvent.isComposing &&
                      event.key !== "Enter"
                    ) {
                      event.preventDefault();
                      sendMessage();
                    }
                  }}
                />
                <Button
                  size="icon"
                  onClick={sendMessage}
                  disabled={!draft.trim()}
                  aria-label="Envoyer"
                >
                  <ArrowUp />
                </Button>
                <small>
                  Entrée pour envoyer · Maj + Entrée pour une nouvelle ligne
                </small>
              </div>
            </div>
        </section>
        <aside className="right-column">
          <RecommendationCard recommendations={recommendations} />
          <ComparisonView />
        </aside>
      </div>
    </main>
  );
}
