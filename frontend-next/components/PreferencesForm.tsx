"use client";

import { FormEvent } from "react";
import { BudgetBand, FilterOptionsResponse, RecommendRequestBody } from "@/lib/types";

type Props = {
  options: FilterOptionsResponse | null;
  loadingOptions: boolean;
  submitting: boolean;
  onSubmit: (body: RecommendRequestBody) => void;
};

const TOP_K_OPTIONS = [1, 2, 3, 4, 5];
const LLM_CAP_OPTIONS = [200, 220, 250, 280, 300];

export default function PreferencesForm({
  options,
  loadingOptions,
  submitting,
  onSubmit,
}: Props) {
  function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const body: RecommendRequestBody = {
      city: toNull(f.get("city")),
      cuisine_query: toNull(f.get("cuisine_query")),
      min_rating: toNumberOrNull(f.get("min_rating")),
      budget_band: toBudgetOrNull(f.get("budget_band")),
      top_k: Number(f.get("top_k") || 5),
      llm_candidate_cap: Number(f.get("llm_candidate_cap") || 250),
    };
    onSubmit(body);
  }

  return (
    <form className="grid" onSubmit={submit}>
      <label>
        City (listed_in)
        <select name="city" disabled={loadingOptions || !options}>
          <option value="">
            {loadingOptions ? "Loading dataset..." : "Any city"}
          </option>
          {(options?.cities ?? []).map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </label>

      <label>
        Cuisine (token)
        <select name="cuisine_query" disabled={loadingOptions || !options}>
          <option value="">
            {loadingOptions ? "Loading dataset..." : "Any cuisine"}
          </option>
          {(options?.cuisines ?? []).map((c) => (
            <option key={c} value={c}>
              {titleCaseWords(c)}
            </option>
          ))}
        </select>
      </label>

      <label>
        Min rating
        <select name="min_rating" disabled={loadingOptions || !options}>
          <option value="">
            {loadingOptions ? "Loading dataset..." : "Any rating"}
          </option>
          {(options?.min_ratings ?? []).map((r) => (
            <option key={String(r)} value={String(r)}>
              {r}+
            </option>
          ))}
        </select>
      </label>

      <label>
        Budget band
        <select name="budget_band" disabled={loadingOptions || !options}>
          <option value="">
            {loadingOptions ? "Loading dataset..." : "Any budget"}
          </option>
          {(options?.budget_options ?? []).map((b) => (
            <option key={b.value} value={b.value}>
              {b.label}
            </option>
          ))}
        </select>
      </label>

      <label>
        Top picks (LLM output)
        <select name="top_k" defaultValue="5">
          {TOP_K_OPTIONS.map((v) => (
            <option key={v} value={v}>
              {v}
            </option>
          ))}
        </select>
      </label>

      <label>
        Shortlist size
        <select name="llm_candidate_cap" defaultValue="250">
          {LLM_CAP_OPTIONS.map((v) => (
            <option key={v} value={v}>
              {v}
            </option>
          ))}
        </select>
      </label>

      <div className="actions">
        <button className="btn primary" type="submit" disabled={submitting || loadingOptions}>
          {submitting ? "Working..." : "Get recommendations"}
        </button>
      </div>
    </form>
  );
}

function titleCaseWords(s: string): string {
  return s
    .split(" ")
    .filter(Boolean)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

function toNull(value: FormDataEntryValue | null): string | null {
  const v = String(value ?? "").trim();
  return v ? v : null;
}

function toNumberOrNull(value: FormDataEntryValue | null): number | null {
  const v = String(value ?? "").trim();
  return v ? Number(v) : null;
}

function toBudgetOrNull(value: FormDataEntryValue | null): BudgetBand | null {
  const v = String(value ?? "").trim();
  if (!v) return null;
  if (v === "low" || v === "medium" || v === "high" || v === "unknown") return v;
  return null;
}
