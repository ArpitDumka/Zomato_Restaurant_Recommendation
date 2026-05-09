export type BudgetBand = "low" | "medium" | "high" | "unknown";

export type FilterOptionsResponseOk = {
  ok: true;
  cities: string[];
  cuisines: string[];
  min_ratings: number[];
  budget_options: { value: BudgetBand; label: string }[];
  cost_for_two_inr_min: number | null;
  cost_for_two_inr_max: number | null;
  normalized_row_count: number;
  scan_seconds: number;
};

export type FilterOptionsResponse =
  | FilterOptionsResponseOk
  | { ok: false; error?: string; traceback?: string };

export type RecommendRequestBody = {
  city: string | null;
  cuisine_query: string | null;
  min_rating: number | null;
  budget_band: BudgetBand | null;
  top_k: number;
  llm_candidate_cap: number;
};

export type RankedPick = {
  restaurant_id: string;
  rank: number;
  explanation: string;
  name: string;
  branch?: string | null;
  cuisine: string;
  rating: number | null;
  cost_for_two_inr: number | null;
};

export type RecommendResult = {
  picks: RankedPick[];
  summary: string | null;
  used_llm: boolean;
  fallback_reason: string | null;
  latency_ms: number | null;
};

export type RecommendResponse = {
  ok: boolean;
  error?: string;
  matched_count: number;
  capped_count: number;
  message: string | null;
  result: RecommendResult | null;
};
