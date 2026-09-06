# Intent-Aware Retrieval Results

## Result Summary

Intent-aware retrieval was introduced because global reranking could discard important secondary intents such as **complaint guidance** and **supporting evidence**.

| Test Area | Result |
|---|---|
| Multi-Query Expansion | 🟢 **PASS** |
| Hybrid Retrieval Per Intent | 🟢 **PASS** |
| FlashRank Per Intent | 🟢 **PASS** |
| Multi-Intent Preservation | 🟢 **PASS** |
| Fungus Scenario | 🟡 **PARTIAL** → 🟢 **PASS** |

---

## Problem Test

Short user input:

> fungus bread

FoodSafe AI expanded the question into three retrieval needs:

```text
1. Food-safety problem
2. Packaged-food complaint guidance
3. Supporting evidence guidance
```

Hybrid retrieval returned:

| Intent | Candidates |
|---|---:|
| Problem | 8 |
| Complaint | 7 |
| Evidence | 6 |
| Combined | **21** |
| Unique | **15** |

The required information was present, but globally reranking all candidates against only **"fungus bread"** returned three Myth Buster results.

The complaint and evidence intents were lost.

---

## Intent-Aware Fix

Instead of globally reranking everything against the original question, each intent was reranked against its **own retrieval query**.

```text
Problem Query ─────→ Hybrid → FlashRank → Best Problem Document

Complaint Query ───→ Hybrid → FlashRank → Best Complaint Document

Evidence Query ────→ Hybrid → FlashRank → Best Evidence Document
```

### Final Retrieval Evidence

| Intent | Selected Source | Approx. Score |
|---|---|---:|
| Problem | Food Safety Myth Busters | 0.0000327 |
| Complaint | Consumer Complaint Guidance | 0.99946 |
| Evidence | Consumer Complaint Guidance | 0.97164 |

The final context therefore preserved all three information needs:

```text
Food-Safety Problem
        +
Complaint Guidance
        +
Evidence Guidance
```

---

## Final Fungus Test

**Question:**

> I found fungus in packaged bread before the expiry date. What should I do?

**Before:** 🟡 **PARTIAL**  
**After intent-aware retrieval:** 🟢 **PASS**

The final answer:

- used official packaged-food complaint guidance,
- included supported evidence such as **product images and the retail bill**,
- provided the official complaint source,
- and avoided inventing a bread-specific fungus standard that was not present in the retrieved FSSAI information.

This was the final retrieval improvement needed to move the application to **8/8 passing functional tests**.

---

## Key Learning

The test demonstrated an important RAG principle:

> **Retrieving the correct document is not enough if a later ranking stage removes an important user intent.**

The final retrieval strategy became:

```text
User Question
      ↓
Deterministic Multi-Query Expansion
      ↓
FAISS + BM25 Per Intent
      ↓
FlashRank Per Intent
      ↓
Best Unique Documents
      ↓
GPT-4.1
```

---

## Detailed Analysis

➡️ [Intent-Aware Retrieval and Reranking](../docs/05_intent_aware_retrieval.md)

### Related Evidence

← [FlashRank Reranking Results](reranking_results.md)

→ [Final Application Results](final_test_results.md)