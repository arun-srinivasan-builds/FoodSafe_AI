# FlashRank Reranking Results

## Result Summary

FlashRank was added after hybrid retrieval to improve the ordering of the larger **FAISS + BM25 candidate pool**.

| Test Area | Result |
|---|---|
| FlashRank Integration | 🟢 **PASS** |
| Plastic Rice | 🟢 **STRONG** |
| Food Recall | 🟢 **STRONG** |
| Packaged-Food Complaint | 🟡 **MIXED** |
| Milk Adulteration | 🟡 **LIMITED BY CORPUS** |

---

## Key Test Results

### Plastic Rice

The direct FSSAI Myth Buster result received an approximate FlashRank score of:

```text
0.9957
```

🟢 **STRONG** — the directly relevant Myth Buster content was strongly prioritized.

### Packaged-Food Complaint

Hybrid retrieval produced approximately **7 candidates**.

After FlashRank reranking:

| Rank | Source | Approx. Score |
|---|---|---:|
| 1 | Food Recall Consumer Information | 0.0276 |
| 2 | Consumer Complaint Guidance | 0.00514 |
| 3 | Food Recall | 0.000179 |

The complaint source had been approximately **#1 after hybrid retrieval**, but moved to **#2 after reranking**.

🟡 **MIXED** — reranking worked technically, but did not improve the ordering for every question.

---

## Implementation Issues Resolved

Two technical problems were encountered while adding FlashRank:

```text
LangChain FlashRank Wrapper
        ↓
Pydantic Ranker Error
        ↓
Use FlashRank Directly
```

Then:

```text
FlashRank
    ↓
ONNX Runtime DLL Error
    ↓
Install Microsoft Visual C++ 2015–2022 x64 Runtime
    ↓
ONNX Runtime 1.20.1
    ↓
FlashRank Working
```

These fixes successfully enabled local FlashRank reranking.

---

## Key Finding

FlashRank provided strong ranking for some queries, particularly **plastic rice**, but testing showed that reranking was **not a universal improvement**.

Later tests with short user questions such as:

```text
fungus bread
worm in rice packet
```

revealed that globally reranking all candidates against the original short question could discard useful **complaint and evidence** information.

This led to the next improvement:

```text
Hybrid Retrieval
      ↓
FlashRank
      ↓
Global Reranking Limitation
      ↓
Intent-Aware Reranking
```

---

## Detailed Analysis

➡️ [FlashRank Reranking Testing](../docs/04_reranking_testing.md)

### Related Evidence

← [Hybrid Retrieval Results](hybrid_retrieval_results.md)

→ [Intent-Aware Retrieval Results](intent_aware_results.md)