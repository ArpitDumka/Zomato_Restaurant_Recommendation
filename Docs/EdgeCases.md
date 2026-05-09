# Edge cases and failure modes

This document lists **detailed edge cases** for the Zomato-inspired recommendation project. It aligns with [ProblemStatement.md](./ProblemStatement.md) (workflow, preferences, grounded LLM output) and [PhaseWiseArchitecture.md](./PhaseWiseArchitecture.md) (phases 0–6). Use it for **test design**, **acceptance criteria**, and **incident playbooks**.

**Legend:** Each item suggests **expected behavior** (or a decision to lock in Phase 0). Where behavior is ambiguous, mark **TBD** and resolve in charter/ADR.

---

## 1. User preferences and input (workflow §2; Phase 4, 6)

| ID | Scenario | Risk / symptom | Expected handling (recommended) |
|----|----------|----------------|----------------------------------|
| U-01 | **Empty or all-default preferences** (e.g. no location, no cuisine) | Over-broad results or accidental full-table scan | Define product rule: reject with validation error *or* apply safe defaults *or* require minimum fields (document in Phase 0). |
| U-02 | **Unknown location** (typo, non-existent city, “Delhi ” with trailing space) | Zero results or silent mismatch | Normalize whitespace; consider fuzzy match or explicit “unknown city” error; never pretend a match exists. |
| U-03 | **City alias / colloquial names** (e.g. Bangalore vs Bengaluru) | Missed rows if filter is exact string | Phase 0: define canonical city list or alias map; tests for each alias. |
| U-04 | **Case variants** (`delhi`, `DELHI`) | Inconsistent filtering | Normalize to consistent casing *or* case-insensitive match for location/cuisine. |
| U-05 | **Budget exactly on bucket boundary** | Row classified wrong bucket (low vs medium) | Phase 0: document inclusive/exclusive rules for thresholds; unit tests on boundary values. |
| U-06 | **Min rating equals a restaurant’s rating** | Off-by-one exclusion | Define ≥ vs > for min rating; test equality. |
| U-07 | **Min rating out of range** (negative, > max scale, non-numeric) | Crash or nonsense filter | Validate in Phase 6 API/UI; return 400 with clear message. |
| U-08 | **Cuisine: multi-label in data** (“Italian, Pizza”) vs single user pick (“Italian”) | Over-filter or under-filter | Define substring vs token vs set intersection rule; test multi-label rows. |
| U-09 | **User requests cuisine with no rows in that city** | Empty result set | Valid outcome; surface **empty state** (Phase 6), not an error. |
| U-10 | **“Extras”** (family-friendly, quick service) **not present as structured fields** | LLM invents amenities | Do not pass extras as facts unless in dataset; prompt: “only use provided fields” or map extras to keywords in free-text column if it exists. |
| U-11 | **Conflicting preferences** (e.g. very high min rating + lowest budget in expensive area) | Zero results | Same as U-09; optionally message: “Try relaxing rating or budget.” |
| U-12 | **Malicious or huge payload** (megabyte-long “location” string) | Memory/DoS | Max length per field; reject or truncate with policy; rate limit (Phase 6). |
| U-13 | **Unicode / special characters** in inputs (emoji, quotes) | Encoding errors or broken JSON | UTF-8 end-to-end; escape safely in UI; fuzz tests on strings. |

---

## 2. Data ingestion (workflow §1; Phase 2)

| ID | Scenario | Risk / symptom | Expected handling |
|----|----------|----------------|-------------------|
| D-01 | **Hugging Face unavailable** (network, 503) | App won’t start | Clear error; optional **offline cache** path; retry with backoff; document in README. |
| D-02 | **Rate limit or auth failure** on HF | Intermittent load | Surface error; distinguish auth vs throttle; don’t silently empty. |
| D-03 | **Partial download / corrupt local cache** | Parse errors mid-run | Checksum or size validation; delete bad cache and retry; fail loud. |
| D-04 | **Upstream schema change** (column renamed, type changed) | Silent wrong mapping or crash | Phase 2: assert expected columns (or version pin dataset revision); CI smoke load. |
| D-05 | **Empty dataset** (zero rows after load) | Everything returns empty | Startup or health check fails *or* explicit “no data” mode; don’t call LLM. |
| D-06 | **Very large full load** | OOM or slow cold start | Document memory needs; support **streaming / subset** for dev; optional Parquet/SQLite (Phase 3). |
| D-07 | **Duplicate runs / concurrent cache writes** | Corrupted cache file | Idempotent cache (Phase 2 “done when”); file lock or atomic write. |

---

## 3. Normalization and canonical model (Phase 3)

| ID | Scenario | Risk / symptom | Expected handling |
|----|----------|----------------|-------------------|
| N-01 | **Null or missing** name, rating, cost, location | Broken display or filter | Document **drop vs impute** rules; never pass null id to LLM as stable key without fallback. |
| N-02 | **Rating outside plausible range** (e.g. 6 on 0–5 scale, string `"4.5★"`) | Sort/filter wrong | Parse + clamp *or* reject row; log counts of rejected rows. |
| N-03 | **Cost as non-numeric** (“₹500 for two”, “$$$”) | Bucket mapping fails | Explicit parsing rules; unknown → “unknown” bucket excluded from strict budget filter *or* mapped per ADR. |
| N-04 | **Duplicate logical restaurants** (same name + coordinates vs fuzzy dupes) | Duplicate recommendations | Dedup policy in Phase 0; stable **record id** after dedupe. |
| N-05 | **Hash/id collision** if id = hash of subset of fields | Wrong merge | Include enough fields in hash or use source row index + dataset version. |
| N-06 | **Whitespace-only cuisine or city** | Rows that slip through filters | Trim; treat empty as null per N-01. |
| N-07 | **All rows dropped** after normalization | Empty canonical set | Same as D-05; alert in logs. |

---

## 4. Deterministic filter and candidate cap (Phase 4)

| ID | Scenario | Risk / symptom | Expected handling |
|----|----------|----------------|-------------------|
| F-01 | **Zero candidates** after filters | Nothing to rank | Short-circuit: **no LLM call**; return empty list + user message (save cost/latency). |
| F-02 | **Fewer than M candidates** | Cap logic assumes full M | Return all; no padding with fake rows. |
| F-03 | **Exactly M candidates** | Tie-breaking ambiguity | Stable sort (secondary key: name, id); document order. |
| F-04 | **Many rows tie on primary sort key** (same rating) | Flaky ordering across runs | Stable sort; optional deterministic seed if sampling. |
| F-05 | **Location matches multiple distinct regions** (“Springfield”) | Wrong geography | Prefer exact match policy *or* disambiguation in Phase 0; test multi-city names. |
| F-06 | **Cuisine filter too strict** | Zero results | Same as F-01; product copy for “broaden cuisine.” |
| F-07 | **Floating-point rating comparisons** | Borderline include/exclude | Compare with tolerance *or* fixed decimal scale. |

---

## 5. LLM integration (workflow §3–4; Phase 5)

| ID | Scenario | Risk / symptom | Expected handling |
|----|----------|----------------|-------------------|
| L-01 | **Model cites a restaurant not in candidate payload** | Breaks “grounded only” success criterion | Post-validate every `restaurant_id` against allowed set; strip invalid entries; **fallback** to Phase 4 order. |
| L-02 | **Duplicate or missing `restaurant_id` in JSON** | Broken ranking | Reject parse; fallback; log parse failure reason (no secrets). |
| L-03 | **Ranks non-contiguous or duplicated** (two `rank: 1`) | Confusing UI | Normalize ranks server-side: sort by given rank, re-assign 1..K. |
| L-04 | **Valid JSON but empty explanations** | Weak UX | Fallback text per item: “Matches your filters.” *or* retry once with stricter prompt (policy TBD). |
| L-05 | **Markdown code fences** or prose around JSON | Parse failure | Strip fences in parser; fallback on failure. |
| L-06 | **Timeout / provider 5xx / rate limit** | Hung or failed request | Bounded timeout; fallback to deterministic list + generic explanation; surface “AI unavailable” in Phase 6. |
| L-07 | **Invalid API key / quota exhausted** | 401/429 | Fail fast with actionable config message; don’t loop forever. |
| L-08 | **Prompt exceeds context limit** (even after cap M) | Provider error | Reduce M dynamically *or* truncate fields per row with documented priority; log truncated byte count. |
| L-09 | **Unsafe or policy-violating model output** | Legal/brand risk | Optional content filter; escape HTML in UI; no `eval` of model output. |
| L-10 | **Same input, different rank order across calls** | “Not repeatable” narrative | Success criterion allows LLM variance for **order** if ids are grounded; document for stakeholders *or* set `temperature=0` if provider supports. |
| L-11 | **Explanation leaks other users’ data** | Should not happen with stateless prompt | Never put cross-user history in prompt; audit templates. |

---

## 6. API, UI, and output display (workflow §5; Phase 6)

| ID | Scenario | Risk / symptom | Expected handling |
|----|----------|----------------|-------------------|
| O-01 | **Missing display fields** (name null in edge row) | Broken card layout | Placeholder “Unknown name”; still show id for debug if internal. |
| O-02 | **Very long restaurant name or explanation** | Layout break | CSS/text clamp *or* expand; max height with “read more.” |
| O-03 | **XSS** if name/cuisine contain `<script>` | Security | Encode output; React default escaping; no `dangerouslySetInnerHTML` for model text without sanitize. |
| O-04 | **Empty state** (F-01) | Blank screen | Explicit “No restaurants match” + suggestions to relax filters. |
| O-05 | **Loading state** slow (LLM) | User double-submits | Disable button; debounce; idempotent request id optional. |
| O-06 | **Partial success** (filter OK, LLM failed) | Inconsistent UX | Use L-06 fallback; show banner “Ranked by rating; AI summary unavailable.” |

---

## 7. Observability, security, and operations (cross-phase)

| ID | Scenario | Risk / symptom | Expected handling |
|----|----------|----------------|-------------------|
| OP-01 | **Secrets in logs** (API keys, full prompts with PII) | Credential leak | Redact keys; structured logging; avoid logging full user query in production *or* scrub. |
| OP-02 | **Logs contain full restaurant dataset** | Noise, GDPR-style concerns | Log counts/ids only unless debug flag. |
| OP-03 | **Non-reproducible demos** (dataset not pinned) | “Works on my machine” | Document dataset revision / cache date (Phase 0/2). |
| OP-04 | **Clock skew / TLS issues** on provider | Auth failures | Document NTP; system time check in troubleshooting. |

---

## 8. Traceability to phases

| Phase | Primary edge-case sections |
|-------|----------------------------|
| 0 | U-01–U-06, U-10, N-04, F-05, L-10 (policy decisions) |
| 2 | D-01–D-07 |
| 3 | N-01–N-07 |
| 4 | F-01–F-07 |
| 5 | L-01–L-11 |
| 6 | U-07, U-12, U-13, O-01–O-06, OP-01–OP-02 |

---

## 9. Suggested test buckets (non-exhaustive)

1. **Contract tests:** API validation (U-07, U-12), JSON schema for recommendation response.  
2. **Property tests:** Normalization never produces negative ratings; filter is idempotent on same input.  
3. **Golden files:** Small CSV fixtures for Phase 4 (F-01–F-03).  
4. **Resilience tests:** HF down (D-01), LLM timeout (L-06), malformed LLM JSON (L-05).  
5. **Grounding tests:** Injected fake restaurant id in model output must be rejected (L-01).

---

## References

- [ProblemStatement.md](./ProblemStatement.md) — workflow, preferences, success criteria.  
- [PhaseWiseArchitecture.md](./PhaseWiseArchitecture.md) — phased scope and exit criteria.
