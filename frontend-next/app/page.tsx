"use client";

import { useCallback, useEffect, useState } from "react";
import SpiceHero from "@/components/SpiceHero";
import SpicePreferencesForm from "@/components/SpicePreferencesForm";
import SpiceResultBoard from "@/components/SpiceResultBoard";
import SpiceTopBar from "@/components/SpiceTopBar";
import { ShortlistItem } from "@/components/SpicePickCard";
import { getApiBase, getFilterOptions, recommend } from "@/lib/api";
import {
  FilterOptionsResponseOk,
  RecommendRequestBody,
  RecommendResponse,
} from "@/lib/types";

const SHORTLIST_KEY = "zomato_shortlist_v1";

function readShortlist(): ShortlistItem[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(SHORTLIST_KEY);
    const data = raw ? JSON.parse(raw) : [];
    return Array.isArray(data) ? data : [];
  } catch {
    return [];
  }
}

function writeShortlist(items: ShortlistItem[]) {
  localStorage.setItem(SHORTLIST_KEY, JSON.stringify(items));
}

export default function HomePage() {
  const [options, setOptions] = useState<FilterOptionsResponseOk | null>(null);
  const [loadingOptions, setLoadingOptions] = useState(true);
  const [optionsError, setOptionsError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [recommendError, setRecommendError] = useState<string | null>(null);
  const [response, setResponse] = useState<RecommendResponse | null>(null);
  const [boardVisible, setBoardVisible] = useState(false);
  const [activeNav, setActiveNav] = useState<"discover" | "shortlist">("discover");
  const [shortlist, setShortlist] = useState<ShortlistItem[]>([]);

  useEffect(() => {
    setShortlist(readShortlist());
  }, []);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        setOptionsError(null);
        const data = await getFilterOptions();
        if (mounted) setOptions(data);
      } catch (e) {
        if (mounted) setOptionsError(String(e));
      } finally {
        if (mounted) setLoadingOptions(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  const result = response?.result ?? null;
  const llmUsed = submitting ? null : result?.used_llm ?? null;

  const isShortlisted = useCallback(
    (id: string) => shortlist.some((x) => x.restaurant_id === id),
    [shortlist],
  );

  const toggleShortlist = useCallback((item: ShortlistItem) => {
    const current = readShortlist();
    const idx = current.findIndex((x) => x.restaurant_id === item.restaurant_id);
    let next: ShortlistItem[];
    if (idx >= 0) {
      next = [...current.slice(0, idx), ...current.slice(idx + 1)];
    } else {
      next = [item, ...current].slice(0, 20);
    }
    writeShortlist(next);
    setShortlist(next);
  }, []);

  const onNavigate = useCallback((target: "discover" | "shortlist") => {
    setActiveNav(target);
    if (target === "shortlist") {
      setBoardVisible(true);
      requestAnimationFrame(() => {
        document.getElementById("results-board")?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      });
    } else {
      requestAnimationFrame(() => {
        document.getElementById("discover")?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      });
    }
    if (typeof window !== "undefined") {
      const hash = target === "shortlist" ? "shortlist" : "discover";
      window.history.replaceState(null, "", `#${hash}`);
    }
  }, []);

  async function submit(body: RecommendRequestBody) {
    setSubmitting(true);
    setRecommendError(null);
    setResponse(null);
    setBoardVisible(true);
    try {
      const data = await recommend(body);
      setResponse(data);
      if (!data.ok && data.error) {
        setRecommendError(data.error);
      }
    } catch (e) {
      setRecommendError(String(e));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page-root">
      <SpiceTopBar
        activeNav={activeNav}
        onNavigate={onNavigate}
        usedLlm={llmUsed}
        fallbackReason={result?.fallback_reason}
        llmLoading={submitting}
      />
      <main className="main">
        <SpiceHero />
        <section className="layout">
          <SpicePreferencesForm
            options={options}
            loadingOptions={loadingOptions}
            submitting={submitting}
            optionsError={optionsError}
            onSubmit={submit}
          />
          <SpiceResultBoard
            visible={boardVisible}
            submitting={submitting}
            response={response}
            recommendError={recommendError}
            shortlist={shortlist}
            onToggleShortlist={toggleShortlist}
            isShortlisted={isShortlisted}
          />
        </section>
      </main>
      <footer className="footer">
        <a href={`${getApiBase()}/docs`} target="_blank" rel="noreferrer">
          API Docs
        </a>{" "}
        ·{" "}
        <a href={`${getApiBase()}/api/health`} target="_blank" rel="noreferrer">
          System Health
        </a>{" "}
        · <a href="#privacy">Privacy</a>
        <span className="footer-note">
          Visual design is Zomato-inspired for this demo only — not affiliated with{" "}
          <a href="https://www.zomato.com/" target="_blank" rel="noreferrer">
            Zomato
          </a>
          .
        </span>
      </footer>
      <section className="legal">
        <div className="legal-inner">
          <div id="privacy" className="legal-item">
            <strong>Privacy</strong>: We do not store personal profile data in this UI;
            recommendations are computed from your current session inputs.
          </div>
        </div>
      </section>
    </div>
  );
}
