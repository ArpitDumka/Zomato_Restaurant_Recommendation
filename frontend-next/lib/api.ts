import {
  FilterOptionsResponse,
  FilterOptionsResponseOk,
  RecommendRequestBody,
  RecommendResponse,
} from "@/lib/types";

/** Public API origin (no trailing slash). */
export function getApiBase(): string {
  return (
    process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ??
    "http://127.0.0.1:8765"
  );
}

/** Avoid silent misconfig: Vercel UI cannot reach localhost API. */
function assertSensibleApiBase(): void {
  if (typeof window === "undefined") {
    return;
  }
  const base = getApiBase();
  const host = window.location.hostname;
  const looksLikeVercel =
    host.endsWith(".vercel.app") || host.includes("vercel.app");
  const apiIsLocal =
    base.includes("127.0.0.1") || base.includes("localhost");
  if (looksLikeVercel && apiIsLocal) {
    throw new Error(
      "NEXT_PUBLIC_API_BASE_URL is missing or still localhost. In Vercel → Settings → Environment Variables, set it to your Railway API URL (https://…, no trailing slash), then redeploy.",
    );
  }
  if (
    window.location.protocol === "https:" &&
    base.startsWith("http://") &&
    !apiIsLocal
  ) {
    throw new Error(
      "NEXT_PUBLIC_API_BASE_URL must use https:// when the site is served over HTTPS (mixed content blocks the API).",
    );
  }
}

const FILTER_OPTIONS_TIMEOUT_MS = 180_000;
const FILTER_OPTIONS_RETRIES = 3;
const FILTER_OPTIONS_RETRY_DELAY_MS = 2_000;

function sleep(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
}

/** Long timeout + retries for cold Railway / first HF catalog load. */
async function fetchFilterOptionsWithRetry(url: string): Promise<Response> {
  let lastErr: unknown;
  for (let attempt = 1; attempt <= FILTER_OPTIONS_RETRIES; attempt++) {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), FILTER_OPTIONS_TIMEOUT_MS);
    try {
      const r = await fetch(url, { cache: "no-store", signal: ctrl.signal });
      clearTimeout(t);
      return r;
    } catch (e) {
      clearTimeout(t);
      lastErr = e;
      if (attempt < FILTER_OPTIONS_RETRIES) {
        await sleep(FILTER_OPTIONS_RETRY_DELAY_MS);
      }
    }
  }
  throw lastErr;
}

async function readJsonBody<T>(r: Response, context: string): Promise<T> {
  const text = await r.text();
  if (!text.trim()) {
    throw new Error(
      `${context}: empty response (HTTP ${r.status}). Wait for the API to finish starting, open the API /api/health URL once, or check hosting logs.`,
    );
  }
  try {
    return JSON.parse(text) as T;
  } catch {
    throw new Error(
      `${context}: not JSON (HTTP ${r.status}): ${text.slice(0, 240)}`,
    );
  }
}

export async function getFilterOptions(): Promise<FilterOptionsResponseOk> {
  assertSensibleApiBase();
  const API_BASE = getApiBase();
  const url = `${API_BASE}/api/filter-options`;
  let r: Response;
  try {
    r = await fetchFilterOptionsWithRetry(url);
  } catch (e) {
    const hint =
      " Check Railway logs, open the API /api/health in a tab, and set CORS_ORIGIN_REGEX " +
      "(e.g. https://[^/]+\\.vercel\\.app$) plus NEXT_PUBLIC_API_BASE_URL on Vercel.";
    if (e instanceof TypeError) {
      throw new Error(
        `Could not reach the API (${e.message}).${hint}`,
      );
    }
    if (e instanceof DOMException && e.name === "AbortError") {
      throw new Error(
        `Filter options request timed out after ${FILTER_OPTIONS_TIMEOUT_MS / 1000}s.${hint}`,
      );
    }
    throw e;
  }
  const data = await readJsonBody<FilterOptionsResponse>(r, "/api/filter-options");
  if (!data.ok) {
    throw new Error(
      data.error?.trim() ||
        `Could not load filter options (HTTP ${r.status})`,
    );
  }
  if (!r.ok) {
    throw new Error(`Could not load filter options (HTTP ${r.status})`);
  }
  return data;
}

export async function recommend(
  body: RecommendRequestBody,
): Promise<RecommendResponse> {
  assertSensibleApiBase();
  const API_BASE = getApiBase();
  const r = await fetch(`${API_BASE}/api/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return readJsonBody<RecommendResponse>(r, "/api/recommend");
}
