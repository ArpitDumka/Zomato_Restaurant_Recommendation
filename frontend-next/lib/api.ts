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
      "NEXT_PUBLIC_API_BASE_URL is missing or still localhost. In Vercel → Settings → Environment Variables, set it to your Render API URL (https://…, no trailing slash), then redeploy.",
    );
  }
}

async function readJsonBody<T>(r: Response, context: string): Promise<T> {
  const text = await r.text();
  if (!text.trim()) {
    throw new Error(
      `${context}: empty response (HTTP ${r.status}). If the API is on Render free tier, wait for cold start, open the API URL once, or check Render logs.`,
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
  const r = await fetch(`${API_BASE}/api/filter-options`, {
    cache: "no-store",
  });
  const data = await readJsonBody<FilterOptionsResponse>(
    r,
    "/api/filter-options",
  );
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
