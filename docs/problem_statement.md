# FoodSafe AI — Problem Statement

> Making official food-safety guidance easier to find, understand, and use through a grounded Generative AI application.

---

## 📚 Project Navigation

- 🏠 [Project Home](../README.md)
- 🏗️ [Architecture & Design](00_architecture_and_design.md)
- 🧩 [LangChain & RAG Concepts](07_langchain_rag_concepts.md)
- ✅ [Final Application Testing](06_final_application_testing.md)
- 📊 [Final Test Results](../test_results/final_test_results.md)

---

## Problem

Consumers may encounter food-safety concerns such as **fungus or foreign objects in food, suspected adulteration, misleading food claims, recalled products, or uncertainty about how to make a complaint**.

Official guidance is available through **FSSAI and FoSCoS**, but relevant information can be spread across different webpages, FAQs, consumer resources, and recall information. A user may therefore need to search and interpret multiple official sources to understand what applies to their situation.

At the same time, relying only on a general-purpose LLM for such questions can produce information that is not supported by the official sources.

---

## Objective

Build a **Generative AI food-safety assistant using Retrieval-Augmented Generation (RAG)** that:

- retrieves relevant information from authentic FSSAI/FoSCoS sources,
- answers users' natural-language food-safety questions,
- keeps responses grounded in retrieved official information,
- provides official source links for transparency,
- and clearly acknowledges when the indexed information is insufficient.

---

## Proposed Solution

**FoodSafe AI** combines official-source ingestion, LangChain, OpenAI embeddings, FAISS, BM25 hybrid retrieval, FlashRank reranking, intent-aware retrieval, GPT-4.1, and Streamlit.

```text
User Question
      ↓
Retrieve Relevant Official Information
      ↓
Select the Best Supporting Context
      ↓
GPT-4.1
      ↓
Grounded Guidance + Official Sources
```

The goal is not to replace FSSAI or professional advice, but to make relevant official food-safety information **easier for users to discover and understand**.

---

## Success Criteria

The application should:

- retrieve relevant official information for supported food-safety scenarios,
- avoid unsupported claims when evidence is unavailable,
- preserve official source traceability,
- understand simple conversational follow-up questions,
- and provide a clear, usable response through the Streamlit interface.

Final validation achieved:

> **🟢 8 functional scenarios tested — 8 Passed | 0 Partial | 0 Failed**

➡️ [View Final Test Results](../test_results/final_test_results.md)