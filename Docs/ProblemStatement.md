# Problem Statement: AI-Powered Restaurant Recommendation (Zomato-Inspired)

## Context

Build an **AI-powered restaurant recommendation service** modeled on how discovery products like Zomato work. The system should combine **structured restaurant data** with a **Large Language Model (LLM)** so suggestions feel personalized and easy to understand—not just a sorted table of rows.

## Objectives

Design and implement an application that:

1. **Accepts user preferences** — e.g. location, budget band, cuisine, minimum rating, and optional qualifiers (family-friendly, quick service, etc.).
2. **Uses a real restaurant dataset** — grounded in actual listings, not invented venues.
3. **Uses an LLM for the “why”** — ranking, short explanations, and optional summaries in natural language.
4. **Presents results clearly** — scannable, trustworthy, and actionable for the end user.

## System Workflow

### 1. Data ingestion

- Load and preprocess the Zomato-style dataset from Hugging Face: [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation).
- Normalize and retain fields needed for filtering and display (e.g. name, location, cuisine, cost, rating, and any other columns that support relevance or explanations).

### 2. User input

Preferences are collected primarily through a **basic web UI** (per Phase 0 charter; implemented in Phase 6), for example:

| Preference | Examples |
|------------|----------|
| Location | Delhi, Bangalore, … |
| Budget | Low, medium, high |
| Cuisine | Italian, Chinese, … |
| Minimum rating | Numeric threshold |
| Extras | Family-friendly, quick service, … |

### 3. Integration layer

- **Filter** the dataset to a candidate set that matches hard constraints (location, budget, rating floor, cuisine, etc.).
- **Shape** that subset for the model: compact, structured snippets the LLM can reason over (not the entire raw table if it is huge).
- **Prompt** the LLM to rank, compare, and explain within the candidate set—avoid hallucinating restaurants that are not in the provided data.

### 4. Recommendation engine (LLM)

The LLM should:

- **Rank** restaurants from the filtered candidate list.
- **Explain** why each top pick fits the user’s stated preferences.
- **Optionally** provide a short overview or comparison across the top options.

### 5. Output display

Show **top recommendations** in a user-friendly layout, including at minimum:

- Restaurant name  
- Cuisine  
- Rating  
- Estimated cost  
- **AI-generated explanation** (why this match makes sense)

## Success criteria (summary)

- Recommendations are **constrained by real dataset rows** after filtering.
- The UI (or API response) makes **ranking and rationale** obvious.
- The pipeline is **repeatable**: new user inputs produce consistent filtering plus LLM-grounded narratives.

## Delivery roadmap

Phased implementation (0–6) lives in **[PhaseWiseArchitecture.md](./PhaseWiseArchitecture.md)** so this file stays focused on product definition; the architecture doc owns sequencing, scope per phase, and exit criteria.

Edge conditions, failure modes, and suggested tests are catalogued in **[EdgeCases.md](./EdgeCases.md)**.
