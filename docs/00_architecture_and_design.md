# FoodSafe AI — Architecture & Design

> Technical architecture of the final FoodSafe AI application, covering knowledge ingestion, RAG retrieval, grounded generation, conversation memory, and the Streamlit application layer.

---

## 📚 Documentation Navigation

| Topic | Documentation |
|---|---|
| 🏗️ **Architecture & Design** | **You are here** |
| 🧪 Baseline RAG | [Baseline RAG Testing](01_baseline_rag_testing.md) |
| 📚 Knowledge Base | [Knowledge Base Improvements](02_knowledge_base_improvements.md) |
| 🔎 Hybrid Retrieval | [FAISS + BM25 Testing](03_hybrid_retrieval_testing.md) |
| 🎯 Reranking | [FlashRank Reranking Testing](04_reranking_testing.md) |
| 🧠 Intent-Aware Retrieval | [Intent-Aware Retrieval](05_intent_aware_retrieval.md) |
| ✅ Final Testing | [Final Application Testing](06_final_application_testing.md) |
| 📊 Test Evidence | [Final Test Results](../test_results/final_test_results.md) |
| 🏠 Project Home | [README](../README.md) |

---

## 🧭 On This Page

- [1. Purpose](#1-purpose)
- [2. High-Level Architecture](#2-high-level-architecture)
- [3. Offline Knowledge Ingestion](#3-offline-knowledge-ingestion)
- [4. LangChain Documents](#4-langchain-documents)
- [5. Text Splitting](#5-text-splitting)
- [6. Embeddings and FAISS](#6-embeddings-and-faiss)
- [7. BM25 Keyword Retrieval](#7-bm25-keyword-retrieval)
- [8. Hybrid Retrieval](#8-hybrid-retrieval)
- [9. Intent-Aware Query Expansion](#9-intent-aware-query-expansion)
- [10. Intent-Aware FlashRank Reranking](#10-intent-aware-flashrank-reranking)
- [11. Context + Original Question](#11-context--original-question)
- [12. GPT-4.1 Grounded Generation](#12-gpt-41-grounded-generation)
- [13. Conversation Memory](#13-conversation-memory)
- [14. Grounding and Source Transparency](#14-grounding-and-source-transparency)
- [15. Streamlit Application Layer](#15-streamlit-application-layer)
- [16. Ingestion and Inference Are Separate](#16-ingestion-and-inference-are-separate)
- [17. Technology Responsibilities](#17-technology-responsibilities)
- [18. Final Retrieval Architecture](#18-final-retrieval-architecture)
- [19. Design Principles](#19-design-principles)

---

## 1. Purpose

FoodSafe AI is a **Generative AI application built using Retrieval-Augmented Generation (RAG)**.

It helps users ask food-safety questions in natural language and receive grounded guidance based on information retrieved from official **FSSAI and FoSCoS sources**.

The application supports questions related to:

- unsafe or suspicious food
- packaged-food problems
- food adulteration
- food myths and misinformation
- food recalls
- consumer complaints and supporting evidence

The core design principle is:

> **Retrieve relevant official information first, then allow GPT-4.1 to generate the answer from that context.**

---

## 2. High-Level Architecture

FoodSafe AI separates the system into two major flows:

1. **Offline Knowledge Ingestion**
2. **Online Question Answering**

```text
                    FOODSAFE AI

        OFFLINE KNOWLEDGE INGESTION
        ────────────────────────────

Official FSSAI / FoSCoS Sources
              ↓
          Playwright
              ↓
     Clean Structured Content
              ↓
      LangChain Documents
              ↓
RecursiveCharacterTextSplitter
              ↓
        Document Chunks
              ↓
 OpenAI text-embedding-3-small
              ↓
             FAISS
              ↓
       Saved Vector Store


        ONLINE QUESTION ANSWERING
        ──────────────────────────

          User Question
               ↓
    Intent-Aware Query Expansion
               ↓
        ┌──────┴──────┐
        ↓             ↓
      FAISS           BM25
   Semantic Search  Keyword Search
        ↓             ↓
        └──────┬──────┘
               ↓
      Hybrid Candidate Results
               ↓
     FlashRank Per Intent
               ↓
      Best Unique Documents
               ↓
        Retrieved Context
               +
        Original Question
               +
 Recent Conversation History
   (reference resolution only)
               ↓
            GPT-4.1
               ↓
       Grounded Response
               +
       Official Sources
               ↓
          Streamlit UI
```

---

## 3. Offline Knowledge Ingestion

The ingestion pipeline prepares official food-safety information before the application is used.

```text
FSSAI / FoSCoS
      ↓
Playwright
      ↓
Cleaning
      ↓
LangChain Documents
      ↓
Text Splitting
      ↓
Embeddings
      ↓
FAISS
```

### Why Playwright?

Some official FSSAI/FoSCoS pages contain dynamically rendered content.

For example, the FoSCoS consumer grievance page contains FAQ answers inside expandable accordions.

Basic page-text extraction initially captured only the FAQ headings.

Playwright allows FoodSafe AI to:

- open the official page,
- interact with dynamic elements,
- expand FAQ sections,
- and extract the actual guidance.

This ensures that the knowledge base contains the information visible to users on the official website.

---

## 4. LangChain Documents

Scraped information is converted into LangChain `Document` objects.

Each document contains:

```text
page_content
+
metadata
```

Metadata includes information such as:

```text
source
category
title
source_url
scraped_at
data_type
```

This allows retrieved information to retain its connection to the original official source.

---

## 5. Text Splitting

Large documents are divided into smaller chunks using:

```text
RecursiveCharacterTextSplitter
```

Configuration:

```text
chunk_size    = 750
chunk_overlap = 100
```

Separators:

```python
["\n\n", "\n", ". ", " ", ""]
```

Chunking allows the retriever to locate the specific part of an official document that is relevant to the user's question.

The overlap helps preserve context across chunk boundaries.

---

## 6. Embeddings and FAISS

Each document chunk is converted into a vector using:

```text
OpenAI text-embedding-3-small
```

The vectors are stored in:

```text
FAISS
```

FAISS provides **semantic retrieval**.

This means the user's wording does not need to exactly match the wording used by FSSAI.

Conceptually:

```text
Document Chunk
      ↓
Embedding Model
      ↓
Vector
      ↓
FAISS
```

When a user asks a question:

```text
User Question
      ↓
Query Embedding
      ↓
FAISS Similarity Search
      ↓
Semantically Relevant Chunks
```

---

## 7. BM25 Keyword Retrieval

Semantic search alone may not always prioritize important exact terminology.

FoodSafe AI therefore also uses:

```text
BM25
```

BM25 performs keyword-based retrieval.

The two retrieval methods complement each other:

| Retriever | Strength |
|---|---|
| FAISS | Semantic meaning |
| BM25 | Exact terms and keywords |

BM25 searches the **same LangChain document chunks stored in the FAISS docstore**, preventing differences between the two retrieval collections.

---

## 8. Hybrid Retrieval

FoodSafe AI combines FAISS and BM25 using LangChain's:

```text
EnsembleRetriever
```

Configuration:

```text
FAISS k = 5
BM25 k  = 5

FAISS weight = 0.5
BM25 weight  = 0.5
```

The results are combined using reciprocal rank fusion.

```text
                 User Query
                     ↓
             ┌───────┴───────┐
             ↓               ↓
           FAISS            BM25
         Semantic          Keyword
             ↓               ↓
             └───────┬───────┘
                     ↓
             Hybrid Candidates
```

Hybrid retrieval improves the chance that useful information is present in the candidate set.

---

## 9. Intent-Aware Query Expansion

Real users do not always ask complete questions.

They may type:

```text
fungus bread
```

or:

```text
worm in rice packet
```

A single short query may actually contain several information needs.

For example:

```text
fungus bread
      ↓
Food-Safety Problem
      +
Complaint Procedure
      +
Supporting Evidence
```

FoodSafe AI therefore performs **deterministic multi-query expansion**.

Depending on the detected problem, the system can create retrieval queries for:

1. the original food-safety problem,
2. complaint guidance,
3. supporting evidence.

This expansion is rule-based and does **not require another LLM call**.

---

## 10. Intent-Aware FlashRank Reranking

Hybrid retrieval generates candidate documents.

FoodSafe AI then uses:

```text
FlashRank
```

to improve document selection.

A key design decision is that documents are reranked **per retrieval intent** rather than globally against only the original user question.

```text
Problem Query
      ↓
Hybrid Retrieval
      ↓
FlashRank
      ↓
Best Problem Document


Complaint Query
      ↓
Hybrid Retrieval
      ↓
FlashRank
      ↓
Best Complaint Document


Evidence Query
      ↓
Hybrid Retrieval
      ↓
FlashRank
      ↓
Best Evidence Document
```

The best unique documents are then combined into the final context.

This prevents an important secondary intent—such as complaint or evidence guidance—from being removed simply because it is less similar to a short original query.

---

## 11. Context + Original Question

The retriever does **not** directly answer the user.

Instead, Python/LangChain constructs the information that will be sent to GPT-4.1.

```text
Retrieved Official Documents
            ↓
          Context

             +

      Original Question

             ↓
          GPT-4.1
```

The two components have different purposes.

### Context

Tells GPT-4.1:

> **What official information is available?**

### Original Question

Tells GPT-4.1:

> **What does the user actually want to know?**

GPT-4.1 uses the retrieved context to formulate a natural-language response to the original question.

FAISS does **not** communicate directly with GPT-4.1.

The application retrieves the documents, builds the prompt, and then sends the resulting context and question to the model.

---

## 12. GPT-4.1 Grounded Generation

GPT-4.1 is used for the final natural-language answer.

The generation layer receives:

```text
Retrieved Official Context
+
Original User Question
+
Recent Conversation History
```

The prompt instructs the model to answer using the retrieved FSSAI/FoSCoS information.

When the indexed information does not fully support an answer, the application is designed to acknowledge that limitation rather than invent missing guidance.

Example:

> **I could not fully verify this from the FSSAI information currently indexed.**

This grounding strategy is especially important for food-safety information.

---

## 13. Conversation Memory

FoodSafe AI supports follow-up questions during the current Streamlit session.

Example:

```text
User:
I found worms in the rice packet.

User:
What evidence should I keep?
```

The application can understand that the second question refers to the previous rice-packet issue.

Recent messages are stored using:

```text
Streamlit Session State
```

The recent conversation history is provided to GPT-4.1 for **reference resolution**.

However:

> **Conversation history is not treated as a factual food-safety source.**

Official retrieved FSSAI/FoSCoS context remains the source of truth.

Memory is session-only and can be removed using:

```text
Clear conversation
```

---

## 14. Grounding and Source Transparency

FoodSafe AI follows a source-first design.

```text
User Question
      ↓
Retrieve Official Information
      ↓
Generate Answer
      ↓
Show Official Sources
```

The application displays the source documents used for the response so that users can continue to the relevant official FSSAI/FoSCoS information.

The system avoids presenting unsupported information as official guidance.

---

## 15. Streamlit Application Layer

Streamlit provides the user-facing application.

The interface includes:

- natural-language question input,
- common-question shortcuts,
- generated guidance,
- official source links,
- conversation memory,
- clear-conversation control,
- and a simple explanation of the retrieval process.

The application layer calls the existing RAG pipeline rather than rebuilding the knowledge base.

---

## 16. Ingestion and Inference Are Separate

An important architectural decision is to keep ingestion separate from live question answering.

### Ingestion

Performed when official knowledge needs to be collected or refreshed:

```text
Scrape
  ↓
Clean
  ↓
Chunk
  ↓
Embed
  ↓
Save FAISS
```

### Inference

Performed whenever the user asks a question:

```text
Load Existing FAISS
        ↓
Retrieve
        ↓
Rerank
        ↓
Generate Answer
```

Therefore, opening Streamlit does **not**:

- scrape FSSAI again,
- clean the documents again,
- split all documents again,
- or regenerate all document embeddings.

This makes the application faster and avoids unnecessary OpenAI embedding usage.

---

## 17. Technology Responsibilities

| Technology | Role in FoodSafe AI |
|---|---|
| **Python** | Main application language |
| **Playwright** | Extract official web content, including dynamic pages |
| **BeautifulSoup** | Content-cleaning support |
| **LangChain** | RAG orchestration and document/retriever components |
| **RecursiveCharacterTextSplitter** | Divide source documents into searchable chunks |
| **OpenAI Embeddings** | Convert text into semantic vectors |
| **FAISS** | Semantic vector retrieval |
| **BM25** | Keyword retrieval |
| **EnsembleRetriever** | Combine FAISS and BM25 |
| **FlashRank** | Rerank retrieved candidates |
| **GPT-4.1** | Generate the final grounded response |
| **Streamlit** | User interface and session memory |

---

## 18. Final Retrieval Architecture

The final FoodSafe AI retrieval pipeline is:

```text
User Question
      ↓
Intent Detection / Query Expansion
      ↓
Multiple Retrieval Queries
      ↓
FAISS + BM25 Hybrid Search
      ↓
FlashRank Per Intent
      ↓
Best Unique Official Documents
      ↓
Retrieved Context
      ↓
Context + Original Question
      ↓
GPT-4.1
      ↓
Grounded Answer
```

This architecture was reached through iterative testing rather than selecting advanced RAG techniques only for complexity.

---

## 19. Design Principles

FoodSafe AI follows five main architectural principles.

### 1. Official Sources First

Use authentic FSSAI/FoSCoS information as the knowledge base.

### 2. Retrieve Before Generating

GPT-4.1 receives relevant retrieved context before producing food-safety guidance.

### 3. Combine Semantic and Keyword Search

FAISS and BM25 provide complementary retrieval signals.

### 4. Preserve Multiple User Intents

Intent-aware retrieval prevents complaint or evidence information from being lost when users ask short questions.

### 5. Prefer Grounded Limitations Over Unsupported Answers

If the indexed official information is insufficient, the system should state the limitation rather than fabricate missing details.

## Production Readiness

FoodSafe AI is a **production-style RAG application prototype** with a complete end-to-end retrieval and generation pipeline.

The current implementation demonstrates official-source ingestion, hybrid retrieval, reranking, grounded generation, source transparency, conversational memory, and functional validation.

It is not yet a production-ready system. Further productionization would include:

- Automated or incremental knowledge-base refresh
- Monitoring, logging, and alerting
- Automated regression and RAG evaluation
- Production-grade secrets and security management
- Scalable deployment and concurrency handling
- Knowledge-base versioning and source-change detection
- Cost, latency, and reliability monitoring

These are considered future enhancements beyond the current MVP.