import {
  FilterOptionsResponse,
  RecommendRequestBody,
  RecommendResponse,
} from "@/lib/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8765";

async function parseJson<T>(r: Response): Promise<T> {
  const data = (await r.json()) as T;
  return data;
}

export async function getFilterOptions(): Promise<FilterOptionsResponse> {
  const r = await fetch(`${API_BASE}/api/filter-options`, {
    cache: "no-store",
  });
  const data = await parseJson<FilterOptionsResponse>(r);
  if (!r.ok || !data.ok) {
    throw new Error("Could not load filter options");
  }
  return data;
}

export async function recommend(
  body: RecommendRequestBody,
): Promise<RecommendResponse> {
  const r = await fetch(`${API_BASE}/api/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return parseJson<RecommendResponse>(r);
}
