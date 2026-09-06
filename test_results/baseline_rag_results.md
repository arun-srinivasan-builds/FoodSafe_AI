# Baseline RAG Results

## Result Summary

The initial FoodSafe AI RAG pipeline used **FAISS semantic retrieval + GPT-4.1**.

Five representative food-safety questions were tested to establish a baseline before introducing knowledge-base and retrieval improvements.

| Metric | Result |
|---|---:|
| Questions Tested | **5** |
| Strong | 🟢 **2** |
| Partial | 🟡 **2** |
| Weak | 🔴 **1** |
| Useful / Grounded | 🟢 **4 / 5** |
| Unsupported Hallucinations | 🟢 **0 / 5** |

---

## Test Results

| # | Question | Result | Key Finding |
|---|---|---|---|
| 1 | Is plastic rice real? | 🟢 **STRONG** | Direct FSSAI Myth Buster information was retrieved |
| 2 | What should I do if I find fungus in packaged food? | 🟡 **PARTIAL** | Relevant information was found, but complaint/evidence guidance was insufficient |
| 3 | How can I complain about unsafe packaged food? | 🟡 **PARTIAL** | Complaint information existed, but retrieval ranking needed improvement |
| 4 | How do I know if a food product has been recalled? | 🟢 **STRONG** | Dedicated FSSAI recall information was retrieved successfully |
| 5 | How can I check whether milk is adulterated? | 🔴 **WEAK** | Initial corpus lacked sufficient adulteration information |

---

## Key Findings

The baseline proved that the core RAG pipeline was working:

```text
User Question
      ↓
FAISS Retrieval
      ↓
Retrieved Context
      ↓
Context + Original Question
      ↓
GPT-4.1
      ↓
Grounded Answer
```

Two main areas needed improvement:

1. **Knowledge coverage** — especially adulteration and complaint guidance.
2. **Retrieval quality** — overlapping or weaker chunks sometimes appeared among the top results.

Importantly:

```text
🟢 Unsupported Hallucinations : 0 / 5
```

This showed that the grounding approach was already working.

The next priority was therefore to improve the **knowledge base and retrieval quality**, rather than replace the generation model.

---

## Baseline Verdict

```text
🟢 Core RAG Pipeline  : WORKING
🟢 Grounding          : WORKING
🟡 Knowledge Coverage : NEEDS IMPROVEMENT
🟡 Retrieval Quality  : NEEDS IMPROVEMENT
```

---

## Improvement Direction

The baseline findings led to the following improvements:

```text
Baseline FAISS RAG
        ↓
Improve Official FSSAI/FoSCoS Corpus
        ↓
Improve Retrieval
        ↓
FAISS + BM25 Hybrid Search
```

---

## Detailed Analysis

For the complete baseline testing, architecture, observations, and lessons learned:

➡️ [Baseline RAG Testing](../docs/01_baseline_rag_testing.md)

For the knowledge-base improvements identified from these tests:

➡️ [Knowledge Base Improvements](../docs/02_knowledge_base_improvements.md)

### Next Test Result

➡️ [Hybrid Retrieval Results](hybrid_retrieval_results.md)