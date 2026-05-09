"use client";

import { useEffect, useState } from "react";
import LlmStatusBadge from "@/components/LlmStatusBadge";
import PreferencesForm from "@/components/PreferencesForm";
import ResultCard from "@/components/ResultCard";
import { getApiBase, getFilterOptions, recommend } from "@/lib/api";
import {
  FilterOptionsResponseOk,
  RecommendRequestBody,
  RecommendResponse,
} from "@/lib/types";

export default function HomePage() {
  const [options, setOptions] = useState<FilterOptionsResponseOk | null>(null);
  const [loadingOptions, setLoadingOptions] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<RecommendResponse | null>(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const data = await getFilterOptions();
        if (mounted) setOptions(data);
      } catch (e) {
        if (mounted) setError(String(e));
      } finally {
        if (mounted) setLoadingOptions(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  async function submit(body: RecommendRequestBody) {
    setSubmitting(true);
    setError(null);
    setResponse(null);
    try {
      const data = await recommend(body);
      setResponse(data);
      if (!data.ok && data.error) {
        setError(data.error);
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setSubmitting(false);
    }
  }

  const result = response?.result ?? null;
  const llmUsed = submitting ? null : result?.used_llm ?? null;

  return (
    <>
      <header className="header">
        <div className="inner">
          <h1>
            Restaurant recommendations <span className="tag">Next.js</span>
          </h1>
          <p className="lead">
            Full pipeline: Hugging Face data {"->"} filters {"->"} LLM top picks
            (grounded).
          </p>
          <p className="ver">
            Frontend on Next.js · API: {getApiBase()} · LLM{" "}
            <LlmStatusBadge
              usedLlm={llmUsed}
              fallbackReason={result?.fallback_reason}
              loading={submitting}
            />
          </p>
        </div>
      </header>

      <main className="main">
        <section className="card">
          <h2>Your preferences</h2>
          <PreferencesForm
            options={options}
            loadingOptions={loadingOptions}
            submitting={submitting}
            onSubmit={submit}
          />
          <p className="hint">
            The full Hugging Face split is loaded by backend on first request and reused.
          </p>
          {options && (
            <p className="hint muted">
              Options from {options.normalized_row_count.toLocaleString()} rows in{" "}
              {options.scan_seconds}s
            </p>
          )}
        </section>

        <section className="card">
          <h2>Result</h2>
          {error && <p className="error">{error}</p>}
          {response && (
            <p className="muted">
              Matched {response.matched_count} rows · sent {response.capped_count} to model
            </p>
          )}

          {response?.message && <div className="empty">{response.message}</div>}
          {result?.summary && <p className="summary">{result.summary}</p>}

          {result?.picks && result.picks.length > 0 ? (
            <ul className="results">
              {result.picks.map((pick) => (
                <ResultCard key={`${pick.restaurant_id}-${pick.rank}`} pick={pick} />
              ))}
            </ul>
          ) : (
            !submitting &&
            response &&
            !response.message &&
            !error && <div className="empty">No picks returned.</div>
          )}
        </section>
      </main>

      <footer className="footer">
        <a href={`${getApiBase()}/docs`} target="_blank" rel="noreferrer">
          API docs
        </a>{" "}
        ·{" "}
        <a href={`${getApiBase()}/api/health`} target="_blank" rel="noreferrer">
          health
        </a>
      </footer>
    </>
  );
}
