"use client";

import { useState } from "react";
import {
  ArrowUp,
  BookOpen,
  Check,
  ChevronDown,
  ChevronRight,
  CircleHelp,
  ShieldCheck,
  Sparkles,
  UserRound,
  X,
  Wrench,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  getScenarioById,
  toOrientationPayload,
  type Scenario,
} from "@/lib/scenarios";

import Image from 'next/image'
import imageLogo from "../public/logoISPM.jpg"

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";
const API_URL = "https://examen-clinique-orient-ai-4pyd.vercel.app/"
type Recommendation = {
  formation: string;
  reason: string;
};

// --- Types correspondant au format de retour du backend ---
type BackendResponseBlock = {
  type: string; // "text" (peut potentiellement en avoir d'autres plus tard)
  text: string;
  index: number;
  extras?: Record<string, unknown>;
};

type BackendChatResponse = {
  response: BackendResponseBlock[];
  status: "success" | "error";
  recommendations?: Recommendation[];
};

// Historique envoyé au backend à chaque requête
type ChatHistoryEntry = {
  role: "user" | "assistant";
  content: string;
};

type ChatEntry = {
  id: string;
  role: "assistant" | "user";
  content: string;
  isError?: boolean;
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

/**
 * Petit rendu Markdown "maison" pour le texte renvoyé par le backend.
 * Gère : **gras**, listes à puces (* ou -), et paragraphes séparés par \n\n.
 * Volontairement minimal — pas de lib externe pour rester léger.
 */
function renderInlineMarkdown(text: string, keyPrefix: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g).filter(Boolean);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={`${keyPrefix}-b-${i}`}>{part.slice(2, -2)}</strong>;
    }
    return <span key={`${keyPrefix}-t-${i}`}>{part}</span>;
  });
}

export function MarkdownText({ text }: { text: string }) {
  const blocks = text.split(/\n\n+/);

  return (
    <>
      {blocks.map((block, blockIndex) => {
        const lines = block.split("\n").filter((l) => l.trim() !== "");
        const isList = lines.length > 0 && lines.every((l) => /^\s*[*-]\s+/.test(l));

        if (isList) {
          return (
            <ul key={`block-${blockIndex}`} className="message-list">
              {lines.map((line, lineIndex) => (
                <li key={`item-${blockIndex}-${lineIndex}`}>
                  {renderInlineMarkdown(
                    line.replace(/^\s*[*-]\s+/, ""),
                    `li-${blockIndex}-${lineIndex}`,
                  )}
                </li>
              ))}
            </ul>
          );
        }

        return (
          <p key={`block-${blockIndex}`}>
            {lines.map((line, lineIndex) => (
              <span key={`line-${blockIndex}-${lineIndex}`}>
                {renderInlineMarkdown(line, `line-${blockIndex}-${lineIndex}`)}
                {lineIndex < lines.length - 1 && <br />}
              </span>
            ))}
          </p>
        );
      })}
    </>
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

export function TypingIndicator() {
  return (
    <article className="message assistant">
      <div className="message-avatar" aria-hidden="true">
        <Sparkles />
      </div>
      <div className="message-body">
        <div className="message-meta">
          ORIENT'IA <span>En train d'écrire…</span>
        </div>
        <div className="message-content">
          <div className="recommendation-line">
            <span />
            <span />
            <span />
          </div>
        </div>
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
  const [chatEntries, setChatEntries] = useState<ChatEntry[]>([]);
  const [chatHistory, setChatHistory] = useState<ChatHistoryEntry[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string | null>(
    null,
  );
  const [isSending, setIsSending] = useState(false);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);

  function appendEntry(entry: ChatEntry) {
    setChatEntries((current) => [...current, entry]);
  }

  // --- Appel générique au backend de chat ---
  async function sendChatMessage(message: string) {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        chat_history: chatHistory,
      }),
    });

    if (!response.ok) {
      throw new Error(`Le serveur a répondu ${response.status}`);
    }

    return (await response.json()) as BackendChatResponse;
  }

  async function sendOrientation(scenario: Scenario) {
    const payload = toOrientationPayload(scenario);
    const response = await fetch(`${API_BASE_URL}/orient`, {
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
    appendEntry({
      id: `${scenario.id}-user-${Date.now()}`,
      role: "user",
      content: scenario.label,
    });

    try {
      const data = await sendOrientation(scenario);
      const nextRecommendations = data.recommendations ?? [];
      setRecommendations(nextRecommendations);

      const summary =
        nextRecommendations.length > 0
          ? nextRecommendations
              .map((item) => `**${item.formation}** — ${item.reason}`)
              .join("\n\n")
          : "Aucune recommandation n'a été renvoyée pour ce profil.";

      appendEntry({
        id: `${scenario.id}-assistant-${Date.now()}`,
        role: "assistant",
        content: summary,
      });
    } catch {
      appendEntry({
        id: `${scenario.id}-error-${Date.now()}`,
        role: "assistant",
        content:
          "Impossible d'obtenir une orientation pour le moment. Vérifiez que l'API est disponible, puis réessayez.",
        isError: true,
      });
    } finally {
      setIsSending(false);
    }
  }

  async function sendMessage() {
    const text = draft.trim();
    if (!text || isSending) return;

    const userEntryId = `user-${Date.now()}`;
    appendEntry({ id: userEntryId, role: "user", content: text });
    setDraft("");
    setIsSending(true);

    try {
      const data = await sendChatMessage(text);

      if (data.status !== "success") {
        throw new Error("Statut d'erreur renvoyé par le backend");
      }

      // Concatène tous les blocs de type "text" de la réponse
      const assistantText = data.response
        .filter((block) => block.type === "text")
        .map((block) => block.text)
        .join("\n\n");

      appendEntry({
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: assistantText || "(Réponse vide)",
      });

      // Met à jour l'historique envoyé au backend au prochain tour
      setChatHistory((current) => [
        ...current,
        { role: "user", content: text },
        { role: "assistant", content: assistantText },
      ]);

      if (data.recommendations) {
        setRecommendations(data.recommendations);
      }
    } catch (error) {
      appendEntry({
        id: `error-${Date.now()}`,
        role: "assistant",
        content:
          "Une erreur est survenue lors de la communication avec ORIENT'IA. Merci de réessayer.",
        isError: true,
      });
    } finally {
      setIsSending(false);
    }
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
      <div className="">
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
                {chatEntries.map((entry) => (
                  <ChatMessage key={entry.id} role={entry.role}>
                    <MarkdownText text={entry.content} />
                  </ChatMessage>
                ))}
                {isSending && <TypingIndicator />}
              </div>
              <div className="composer">
                <textarea
                  value={draft}
                  onChange={(event) => setDraft(event.target.value)}
                  placeholder="Écrivez votre réponse…"
                  aria-label="Votre réponse"
                  onKeyDown={(event) => {
                    if (
                      event.key === "Enter" &&
                      !event.shiftKey &&
                      !event.nativeEvent.isComposing
                    ) {
                      event.preventDefault();
                      sendMessage();
                    }
                  }}
                />
                <Button
                  size="icon"
                  onClick={sendMessage}
                  disabled={!draft.trim() || isSending}
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
        {/*<aside className="right-column">
          <RecommendationCard recommendations={recommendations} />
          <ComparisonView />
        </aside>*/}
      </div>
    </main>
  );
}