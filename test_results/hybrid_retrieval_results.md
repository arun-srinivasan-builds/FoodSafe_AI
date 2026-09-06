# Hybrid Retrieval Results

## Result Summary

FoodSafe AI introduced **FAISS + BM25 hybrid retrieval** to improve retrieval limitations identified during baseline testing.

| Metric | Result |
|---|---|
| FAISS Retrieval | 🟢 **PASS** |
| BM25 Retrieval | 🟢 **PASS** |
| Hybrid Integration | 🟢 **PASS** |
| Complaint Retrieval | 🟢 **IMPROVED** |
| Candidate Recall | 🟢 **IMPROVED** |
| Final Precision | 🟡 **NEEDED RERANKING** |

---

## Key Test

**Question:**

> How can I complain about unsafe packaged food?

| Retrieval Method | Relevant Complaint Source |
|---|---|
| FAISS only | Approximately **Rank #3** |
| FAISS + BM25 | Approximately **Rank #1** |

### 🟢 Result: Improved

The relevant official complaint guidance improved from approximately **#3 → #1** after introducing hybrid retrieval.

---

## Hybrid Configuration

```text
FAISS k       : 5
BM25 k        : 5
FAISS Weight  : 0.5
BM25 Weight   : 0.5
```

Results were combined using LangChain's **EnsembleRetriever** with reciprocal rank fusion.

```text
User Question
      ↓
 ┌────┴────┐
 ↓         ↓
FAISS     BM25
 ↓         ↓
 └────┬────┘
      ↓
Hybrid Candidate Pool
```

BM25 used the **same documents stored in the FAISS docstore**, ensuring both retrieval methods searched the same chunks.

---

## Key Finding

Hybrid retrieval improved **recall**, but the complaint test produced approximately **7 candidates**, including some weaker results.

```text
FAISS + BM25
     ↓
Better Recall
     ↓
Larger Candidate Pool
     ↓
Need Better Final Ranking
```

This demonstrated an important RAG principle:

> **Better recall does not automatically mean better final ranking.**

The result led directly to the next improvement: **FlashRank reranking**.

---

## Detailed Analysis

➡️ [Hybrid Retrieval Testing](../docs/03_hybrid_retrieval_testing.md)

### Related Evidence

← [Baseline RAG Results](baseline_rag_results.md)

→ [FlashRank Reranking Results](reranking_results.md)