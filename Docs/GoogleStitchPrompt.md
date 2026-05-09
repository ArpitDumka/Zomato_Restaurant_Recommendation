# Google Stitch prompt for Next.js frontend + UI images

Use the prompt below directly in Google Stitch.

```text
You are a senior product designer + frontend engineer.
Create a modern, production-ready frontend for an AI restaurant recommendation app.
The implementation framework must be Next.js (App Router) with TypeScript and Tailwind CSS.

Product context:
- App name: Restaurant recommendations (Zomato-inspired)
- Users choose preferences, then see top restaurant recommendations with short AI explanations.
- Data comes from backend APIs (already built separately).

Required UX flow:
1) Landing / Home view with headline and short supporting text.
2) "Your preferences" form with these controls (all as dropdowns/selects where applicable):
   - City
   - Cuisine
   - Min rating
   - Budget band (low/medium/high/unknown)
   - Top picks (1-5)
   - Shortlist size (200-300)
   - Primary CTA: "Get recommendations"
3) Result section/cards showing:
   - Rank
   - Restaurant name
   - Cuisine
   - Rating
   - Cost for two
   - AI explanation text (2-3 lines)
4) Status states:
   - Loading state while recommendations are being fetched
   - Empty state ("No matches. Try broader filters.")
   - Error state
   - LLM status badge in header (Idle / ON / OFF)
5) Secondary links:
   - API docs
   - Health

Design direction:
- Dark modern food-tech aesthetic
- Clean spacing, rounded cards, strong hierarchy
- Mobile-first responsive design, then tablet and desktop
- Accessible colors/contrast and keyboard-friendly controls
- Keep UI natural and practical (not overly fancy)

Output I want from you:
A) UI images/screens (high fidelity) for:
   - Desktop home + form + results
   - Mobile home + form + results
   - Loading and empty/error examples
B) Next.js code structure suggestion:
   - app/page.tsx
   - components/PreferencesForm.tsx
   - components/ResultCard.tsx
   - components/LlmStatusBadge.tsx
   - lib/api.ts
   - app/globals.css
C) A ready-to-use sample Next.js page implementation with mock data and mocked API calls.
D) Keep code easy to plug into real backend endpoints:
   - GET /api/filter-options
   - POST /api/recommend

API contract assumptions (frontend side):
- GET /api/filter-options returns:
  { cities, cuisines, min_ratings, budget_options, normalized_row_count, scan_seconds, ... }
- POST /api/recommend body includes:
  { city, cuisine_query, min_rating, budget_band, top_k, llm_candidate_cap }
- POST /api/recommend response includes:
  { ok, matched_count, capped_count, message, result }
- result includes:
  { picks: [{rank, name, cuisine, rating, cost_for_two_inr, explanation}], summary, used_llm, fallback_reason }

Important constraints:
- Use only Next.js + TypeScript + Tailwind CSS.
- Do not add backend code.
- Do not use a component library dependency unless explicitly justified.
- Keep naming clean and scalable.
- Add brief comments only where necessary.

Finally, provide a short "integration checklist" describing how to connect this frontend to an existing backend running on http://127.0.0.1:8765.
```

## Optional quick variant (if you only want UI images first)

```text
Create high-fidelity UI mockups (desktop + mobile) for a Next.js restaurant recommendation app with:
- dark modern theme
- dropdown-based preference form (city, cuisine, rating, budget, top picks, shortlist size)
- results cards with rank/name/cuisine/rating/cost/AI explanation
- states: loading, empty, error
- LLM status badge (Idle/ON/OFF)

No backend screens. Focus on clean, realistic product UI and export-ready assets.
```
