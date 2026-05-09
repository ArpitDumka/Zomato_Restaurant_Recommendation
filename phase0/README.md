# Phase 0 deliverables

Implements **Phase 0** from [PhaseWiseArchitecture.md](../Docs/PhaseWiseArchitecture.md): charter, dataset spike, field mapping, and runtime/LLM ADR. **No application** beyond throwaway scripts.

**Charter note:** user preferences are defined for a **basic web UI** as the main input surface (see [FieldMapping.md](./FieldMapping.md) and [ADR-0001-runtime-and-llm.md](./ADR-0001-runtime-and-llm.md)); Phase 6 implements that UI on top of the backend.

## Contents

| Artifact | Purpose |
|----------|---------|
| [FieldMapping.md](./FieldMapping.md) | User preference ↔ dataset columns; grounded-only rule; recommendation JSON shape. |
| [ADR-0001-runtime-and-llm.md](./ADR-0001-runtime-and-llm.md) | Python + default LLM provider decision. |
| [dataset_spike.py](./dataset_spike.py) | Loads `ManikaSaini/zomato-restaurant-recommendation` (streaming) and writes [DatasetSpikeReport.md](./DatasetSpikeReport.md). |
| [DatasetSpikeReport.md](./DatasetSpikeReport.md) | Generated schema, null rates, value samples (re-run script to refresh). |
| [requirements.txt](./requirements.txt) | Minimal deps for the spike only. |

## Run the spike

```powershell
cd path\to\Zomato_1
pip install -r phase0/requirements.txt
python phase0/dataset_spike.py
```

Requires internet access to Hugging Face Hub. Optional: set `HF_TOKEN` for higher rate limits.

## Exit criteria (Phase 0)

- [x] Field-mapping table exists (`FieldMapping.md`).
- [x] Dataset sample analyzed; schema/nulls/examples documented (`DatasetSpikeReport.md`).
- [x] Runtime + LLM choice recorded (`ADR-0001-runtime-and-llm.md`).

Next: **Phase 1** repository scaffold in [`phase1/`](../phase1/README.md) (see architecture doc).
