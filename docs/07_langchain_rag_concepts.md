# FoodSafe AI — LangChain & RAG Concepts Reference

> A practical reference to the LangChain and Retrieval-Augmented Generation (RAG) concepts implemented in FoodSafe AI, why each concept is used, and where its implementation and testing can be studied in this repository.

---

## 📚 Documentation Navigation

| Topic | Documentation |
|---|---|
| 🏗️ Architecture & Design | [Architecture & Design](00_architecture_and_design.md) |
| 🧪 Baseline RAG | [Baseline RAG Testing](01_baseline_rag_testing.md) |
| 📚 Knowledge Base | [Knowledge Base Improvements](02_knowledge_base_improvements.md) |
| 🔎 Hybrid Retrieval | [FAISS + BM25 Testing](03_hybrid_retrieval_testing.md) |
| 🎯 Reranking | [FlashRank Reranking Testing](04_reranking_testing.md) |
| 🧠 Intent-Aware Retrieval | [Intent-Aware Retrieval](05_intent_aware_retrieval.md) |
| ✅ Final Testing | [Final Application Testing](06_final_application_testing.md) |
| 🧩 **LangChain & RAG Concepts** | **You are here** |
| 📊 Test Evidence | [Final Test Results](../test_results/final_test_results.md) |
| 🏠 Project Home | [README](../README.md) |

---

## 🧭 On This Page

1. [RAG — The Bigger Picture](#1-rag--the-bigger-picture)
2. [LangChain's Role](#2-langchains-role)
3. [Data Ingestion](#3-data-ingestion)
4. [LangChain Document](#4-langchain-document)
5. [Metadata](#5-metadata)
6. [Text Splitting](#6-text-splitting)
7. [Chunks and Chunk Overlap](#7-chunks-and-chunk-overlap)
8. [Embeddings](#8-embeddings)
9. [Vector Store — FAISS](#9-vector-store--faiss)
10. [Query Embedding](#10-query-embedding)
11. [Retriever](#11-retriever)
12. [Semantic Search](#12-semantic-search)
13. [BM25 Keyword Retrieval](#13-bm25-keyword-retrieval)
14. [Hybrid Retrieval](#14-hybrid-retrieval)
15. [EnsembleRetriever](#15-ensembleretriever)
16. [Reciprocal Rank Fusion](#16-reciprocal-rank-fusion)
17. [Candidate Documents](#17-candidate-documents)
18. [Reranking](#18-reranking)
19. [FlashRank](#19-flashrank)
20. [Multi-Query Expansion](#20-multi-query-expansion)
21. [Intent-Aware Retrieval](#21-intent-aware-retrieval)
22. [Intent-Aware Reranking](#22-intent-aware-reranking)
23. [Context Building](#23-context-building)
24. [Context + Original Question](#24-context--original-question)
25. [Prompt Grounding](#25-prompt-grounding)
26. [GPT-4.1 — Generation](#26-gpt-41--generation)
27. [Conversation Memory](#27-conversation-memory)
28. [Source Attribution](#28-source-attribution)
29. [Offline Ingestion vs Online Inference](#29-offline-ingestion-vs-online-inference)
30. [Complete RAG Mental Model](#30-complete-rag-mental-model)
31. [Concepts by Project Stage](#31-concepts-by-project-stage)
32. [Reusable Learning for Future RAG Projects](#32-reusable-learning-for-future-rag-projects)

---

# 1. RAG — The Bigger Picture

**Retrieval-Augmented Generation (RAG)** is an architecture where an LLM is given relevant information retrieved from an external knowledge source before it generates an answer.

Instead of expecting GPT-4.1 to answer a food-safety question entirely from its built-in knowledge, FoodSafe AI first retrieves relevant official FSSAI/FoSCoS information and provides that information to GPT-4.1.

```text
User Question
      ↓
Retrieve Relevant Information
      ↓
Provide Information to LLM
      ↓
Generate Grounded Answer
```

### Why FoodSafe AI uses it

Food-safety answers should be based on official information rather than relying entirely on the model's general knowledge.

### Study in this project

- [Architecture & Design](00_architecture_and_design.md)
- [Baseline RAG Testing](01_baseline_rag_testing.md)

---

# 2. LangChain's Role

**LangChain is the orchestration layer** used to connect several components of the RAG application.

In FoodSafe AI, LangChain helps work with documents, text splitting, embeddings, FAISS, retrievers, BM25, hybrid retrieval, and the application flow around the LLM.

```text
Documents
   ↓
Splitter
   ↓
Embeddings
   ↓
FAISS
   ↓
Retriever
   ↓
Context
   ↓
Prompt
   ↓
GPT-4.1
```

LangChain does not replace GPT-4.1, FAISS, or the embedding model. It helps the Python application organize and connect these components.

### Study in this project

- [Architecture & Design](00_architecture_and_design.md)
- [Baseline RAG Testing](01_baseline_rag_testing.md)

---

# 3. Data Ingestion

**Data ingestion** is the process of bringing external information into the application's knowledge pipeline.

FoodSafe AI uses Playwright to collect information from official FSSAI/FoSCoS webpages before converting the extracted content into documents.

```text
FSSAI / FoSCoS Website
          ↓
      Playwright
          ↓
   Extracted Content
          ↓
    RAG Knowledge
```

### Why FoodSafe AI uses it

A RAG system can only retrieve information that has first been made available to its knowledge base.

The quality of the RAG application therefore begins with the quality of ingestion.

### Study in this project

- [Architecture & Design](00_architecture_and_design.md)
- [Knowledge Base Improvements](02_knowledge_base_improvements.md)

---

# 4. LangChain Document

A LangChain **`Document`** is a standard structure used to represent information inside the RAG pipeline.

Each document has two important parts:

```text
Document
   │
   ├── page_content
   │
   └── metadata
```

`page_content` contains the actual FSSAI/FoSCoS information.

`metadata` contains information describing where that content came from.

### Why FoodSafe AI uses it

The Document structure allows content and its source information to travel together through splitting, retrieval, testing, and source attribution.

### Study in this project

- [Architecture & Design](00_architecture_and_design.md)
- [Knowledge Base Improvements](02_knowledge_base_improvements.md)

---

# 5. Metadata

**Metadata is information about a document rather than the main document content itself.**

FoodSafe AI stores metadata such as:

```text
source
category
title
source_url
scraped_at
data_type
```

For example:

```text
page_content:
"Relevant FSSAI complaint guidance..."

metadata:
category   = Consumer Complaint Guidance
source_url = Official FoSCoS URL
```

### Why FoodSafe AI uses it

Metadata allows FoodSafe AI to identify **where retrieved information came from**.

It supports:

- source traceability,
- official source attribution,
- document/category identification,
- retrieval debugging,
- testing and evaluation.

For example, during testing we could inspect whether a retrieved chunk came from:

```text
Food Safety Myth Busters
```

or:

```text
Consumer Complaint Guidance
```

This became especially useful when diagnosing why complaint information was or was not reaching the final context.

### Easy way to remember

```text
page_content = the knowledge

metadata = information about the knowledge
```

The document text provides the searchable information, while metadata helps identify and trace that information.

### Study in this project

- [Architecture & Design](00_architecture_and_design.md)
- [Knowledge Base Improvements](02_knowledge_base_improvements.md)
- [Intent-Aware Retrieval](05_intent_aware_retrieval.md)

---

# 6. Text Splitting

**Text splitting** divides large documents into smaller pieces before they are embedded and stored.

FoodSafe AI uses:

```text
RecursiveCharacterTextSplitter
```

with:

```text
chunk_size    = 750
chunk_overlap = 100
```

The configured separators are:

```python
["\n\n", "\n", ". ", " ", ""]
```

### Why FoodSafe AI uses it

Embedding an entire large webpage as one block would make it harder to retrieve only the section relevant to a user's question.

Smaller chunks allow retrieval to locate more focused information.

### Study in this project

- [Architecture & Design](00_architecture_and_design.md)
- [Baseline RAG Testing](01_baseline_rag_testing.md)

---

# 7. Chunks and Chunk Overlap

A **chunk** is one smaller piece of text produced after splitting a larger document.

FoodSafe AI uses an overlap of `100` characters so that information near the end of one chunk can also appear at the beginning of the next.

```text
Chunk 1
-------------------------
               overlap
               ↓↓↓↓↓↓↓
          -------------------------
                   Chunk 2
```

### Why overlap is useful

Without overlap, an important sentence or idea could be divided between two chunks and lose some of its context.

However, overlap can also cause similar chunks to appear in retrieval results. This behaviour was observed during FoodSafe AI's baseline retrieval testing.

### Study in this project

- [Baseline RAG Testing](01_baseline_rag_testing.md)
- [Architecture & Design](00_architecture_and_design.md)

---

# 8. Embeddings

An **embedding** converts text into a numerical vector that represents aspects of its semantic meaning.

FoodSafe AI uses:

```text
OpenAI text-embedding-3-small
```

Conceptually:

```text
"How do I complain about unsafe food?"
                  ↓
          Embedding Model
                  ↓
      Numerical Vector Representation
```

### Why FoodSafe AI uses embeddings

Embeddings allow the system to search based on semantic similarity rather than depending only on exact word matches.

### Easy way to remember

```text
Text
 ↓
Embedding Model
 ↓
Numbers representing meaning
```

### Study in this project

- [Architecture & Design](00_architecture_and_design.md)
- [Baseline RAG Testing](01_baseline_rag_testing.md)

---

# 9. Vector Store — FAISS

A **vector store** stores document vectors and provides a way to search them efficiently.

FoodSafe AI uses:

```text
FAISS
```

The document chunks are converted into embeddings and indexed in FAISS.

```text
Document Chunks
      ↓
Embeddings
      ↓
FAISS Vector Store
```

### Why FoodSafe AI uses FAISS

FAISS allows the application to locate document chunks that are semantically similar to the user's question.

The FAISS index is saved locally and reused by the application.

### Important distinction

```text
Embedding Model → creates vectors

FAISS → stores/searches vectors
```

FAISS itself does not generate the embeddings.

### Study in this project

- [Architecture & Design](00_architecture_and_design.md)
- [Baseline RAG Testing](01_baseline_rag_testing.md)
- [Hybrid Retrieval Testing](03_hybrid_retrieval_testing.md)

---

# 10. Query Embedding

The user's question must also be converted into a vector before FAISS can compare it with the stored document vectors.

```text
User Question
      ↓
Embedding Model
      ↓
Query Vector
      ↓
Compare with FAISS Vectors
```

### Why it matters

The stored document chunks already have vectors.

The incoming question also needs a vector representation so that FAISS can compare their semantic similarity.

### Easy way to remember

```text
Documents → vectors
Question  → vector

FAISS compares them.
```

### Study in this project

- [Architecture & Design](00_architecture_and_design.md)
- [Baseline RAG Testing](01_baseline_rag_testing.md)

---

# 11. Retriever

A **retriever** is the component responsible for finding documents that are relevant to a query.

It sits between the knowledge store and the generation stage.

```text
User Question
      ↓
Retriever
      ↓
Relevant Documents
```

### Why FoodSafe AI uses it

GPT-4.1 should not receive the entire knowledge base for every question.

The retriever selects a smaller set of potentially relevant information.

### Easy way to remember

> **The retriever finds the knowledge. The LLM explains the knowledge.**

### Study in this project

- [Baseline RAG Testing](01_baseline_rag_testing.md)
- [Hybrid Retrieval Testing](03_hybrid_retrieval_testing.md)

---

# 12. Semantic Search

**Semantic search** searches based on similarity in meaning rather than requiring identical keywords.

In FoodSafe AI, FAISS performs semantic retrieval using OpenAI embeddings.

For example, conceptually:

```text
User:
"unsafe packaged food"
```

may retrieve official content containing wording such as:

```text
"consumer grievance relating to packaged food"
```

even though the sentences are not identical.

### Study in this project

- [Baseline RAG Testing](01_baseline_rag_testing.md)
- [Architecture & Design](00_architecture_and_design.md)

---

# 13. BM25 Keyword Retrieval

**BM25** is a traditional keyword-based information retrieval algorithm.

Unlike FAISS semantic search, BM25 gives importance to terms that occur directly in the query and documents.

### Why FoodSafe AI uses it

Some questions contain useful exact terminology that keyword retrieval can identify effectively.

Therefore:

```text
FAISS → semantic similarity

BM25  → keyword relevance
```

Using both provides two complementary ways of finding information.

### Study in this project

- [Hybrid Retrieval Testing](03_hybrid_retrieval_testing.md)
- [Architecture & Design](00_architecture_and_design.md)

---

# 14. Hybrid Retrieval

**Hybrid retrieval combines more than one retrieval method.**

FoodSafe AI combines:

```text
FAISS Semantic Retrieval
          +
BM25 Keyword Retrieval
```

### Why FoodSafe AI uses it

FAISS can find semantically related information while BM25 can identify useful exact terms.

Combining them improves the chance that relevant information appears in the candidate set.

### Important learning

Hybrid retrieval mainly improved **candidate recall**.

It did not mean that every candidate was good enough to send directly to GPT-4.1.

That led to the addition of reranking.

### Study in this project

- [Hybrid Retrieval Testing](03_hybrid_retrieval_testing.md)
- [Architecture & Design](00_architecture_and_design.md)

---

# 15. EnsembleRetriever

FoodSafe AI uses LangChain's:

```text
EnsembleRetriever
```

to combine FAISS and BM25 retrieval results.

The project configuration uses:

```text
FAISS k = 5
BM25 k  = 5

FAISS weight = 0.5
BM25 weight  = 0.5
```

### Why it is used

Instead of choosing either semantic search or keyword search, `EnsembleRetriever` allows both retrievers to contribute to the result set.

### Study in this project

- [Hybrid Retrieval Testing](03_hybrid_retrieval_testing.md)
- [Architecture & Design](00_architecture_and_design.md)

---

# 16. Reciprocal Rank Fusion

**Reciprocal Rank Fusion (RRF)** is a method for combining ranked result lists.

FoodSafe AI uses ranking information from FAISS and BM25 through the ensemble retrieval process.

Conceptually:

```text
FAISS Ranking ──┐
                ├──→ Combined Ranking
BM25 Ranking ───┘
```

### Why it matters

FAISS similarity scores and BM25 scores are produced differently.

RRF allows ranked results to be combined without requiring their raw scores to be directly comparable.

### Study in this project

- [Hybrid Retrieval Testing](03_hybrid_retrieval_testing.md)

---

# 17. Candidate Documents

The initial retrieval stage produces **candidate documents**.

These are documents that may be relevant, but they are not automatically assumed to be the best documents for the final LLM context.

For example:

```text
Hybrid Retrieval
       ↓
~7 Candidate Documents
       ↓
Reranking
       ↓
Best Documents
```

### Why this distinction matters

Retrieval focuses on finding enough potentially useful information.

Reranking focuses on deciding which of those retrieved candidates are strongest for the query.

### Easy way to remember

```text
Retriever = find candidates

Reranker  = prioritize candidates
```

### Study in this project

- [Hybrid Retrieval Testing](03_hybrid_retrieval_testing.md)
- [FlashRank Reranking Testing](04_reranking_testing.md)

---

# 18. Reranking

**Reranking** takes retrieved candidate documents and reorders them based on their relevance to a query.

```text
Retriever
   ↓
Candidate Documents
   ↓
Reranker
   ↓
More Relevant Ordering
```

### Why FoodSafe AI uses it

Hybrid retrieval improves recall but can also return additional noise.

Reranking helps select stronger documents before the final context is constructed.

### Important learning from this project

Reranking did **not automatically improve every query**.

For the packaged-food complaint test, an important complaint document moved from approximately hybrid rank `#1` to reranked rank `#2`.

This became an important lesson:

> **Adding a reranker does not guarantee that every retrieval result becomes better. It must be tested.**

### Study in this project

- [FlashRank Reranking Testing](04_reranking_testing.md)
- [Intent-Aware Retrieval](05_intent_aware_retrieval.md)

---

# 19. FlashRank

FoodSafe AI uses **FlashRank** as the reranking component.

FlashRank receives:

```text
Query
+
Candidate Documents
```

and returns relevance scores that can be used to reorder those candidates.

### Why FoodSafe AI uses it

It provides a dedicated reranking stage without requiring GPT-4.1 to perform document ranking.

### Implementation learning

The project initially attempted the LangChain FlashRank wrapper but encountered an integration issue.

The implementation was changed to use FlashRank directly:

```python
from flashrank import Ranker, RerankRequest
```

The project also required a compatible ONNX Runtime environment and Microsoft Visual C++ runtime.

### Study in this project

- [FlashRank Reranking Testing](04_reranking_testing.md)

---

# 20. Multi-Query Expansion

A single user question can be expanded into multiple retrieval queries representing different information needs.

For example:

```text
fungus bread
```

can lead to retrieval queries covering:

```text
1. Food-safety problem
2. Complaint procedure
3. Supporting evidence
```

### Why FoodSafe AI uses it

Real users often type short or incomplete questions.

A single retrieval query may find information about the immediate food problem while missing related complaint or evidence guidance.

### Important implementation detail

FoodSafe AI's query expansion is:

```text
Deterministic
+
Rule-Based
```

It does **not** require an additional LLM call to generate the retrieval queries.

### Study in this project

- [Intent-Aware Retrieval](05_intent_aware_retrieval.md)
- [Architecture & Design](00_architecture_and_design.md)

---

# 21. Intent-Aware Retrieval

**Intent-aware retrieval recognizes that one user question may contain or imply multiple information needs.**

For example:

```text
"I found fungus in packaged bread."
```

may require:

```text
Problem Information
        +
Complaint Information
        +
Evidence Information
```

### Why FoodSafe AI uses it

Retrieving only information similar to the words `fungus` and `bread` may find the food-safety problem but miss useful complaint guidance.

Intent-aware retrieval deliberately searches for each relevant information need.

### Study in this project

- [Intent-Aware Retrieval](05_intent_aware_retrieval.md)

---

# 22. Intent-Aware Reranking

The first multi-query implementation retrieved documents for multiple intents but then reranked all candidates against the original short question.

For example:

```text
Problem Documents
Complaint Documents
Evidence Documents
        ↓
Global Rerank against "fungus bread"
        ↓
Mostly Problem Documents Survived
```

This meant the multi-query retrieval worked, but the global reranking stage could undo its benefit.

FoodSafe AI therefore changed to **per-intent reranking**.

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

The best unique documents are then combined.

### Why this was important

It preserves different user intents instead of allowing the strongest match to the original wording to dominate the entire final context.

This improvement changed the fungus scenario from:

```text
🟡 PARTIAL
```

to:

```text
🟢 PASS
```

### Study in this project

- [Intent-Aware Retrieval](05_intent_aware_retrieval.md)
- [Final Application Testing](06_final_application_testing.md)

---

# 23. Context Building

After retrieval and reranking, the selected document content is combined into a **context** for GPT-4.1.

```text
Selected Document 1
Selected Document 2
Selected Document 3
        ↓
Combined Context
```

### Why FoodSafe AI uses it

GPT-4.1 needs the retrieved official information in a usable form before it can generate the final response.

Context building therefore acts as the bridge between:

```text
Retrieval
```

and:

```text
Generation
```

### Study in this project

- [Architecture & Design](00_architecture_and_design.md)
- [Baseline RAG Testing](01_baseline_rag_testing.md)

---

# 24. Context + Original Question

FoodSafe AI sends both the **retrieved context** and the **original user question** to GPT-4.1.

They perform different jobs.

### Context

Answers:

> **What official information is available?**

### Original Question

Answers:

> **What does the user actually want to know?**

Together:

```text
Official Retrieved Context
           +
    Original Question
           ↓
        GPT-4.1
           ↓
Relevant Natural-Language Answer
```

### Important understanding

FAISS does **not** directly send documents to GPT-4.1.

The Python/LangChain application:

```text
retrieves documents
        ↓
builds context
        ↓
combines context with the question
        ↓
calls GPT-4.1
```

### Study in this project

- [Architecture & Design](00_architecture_and_design.md)
- [Baseline RAG Testing](01_baseline_rag_testing.md)

---

# 25. Prompt Grounding

**Prompt grounding means instructing the LLM to base its response on the retrieved information rather than freely generating unsupported facts.**

FoodSafe AI instructs GPT-4.1 to use the retrieved official FSSAI/FoSCoS context.

When the indexed information does not fully support an answer, the application is designed to acknowledge that limitation.

Example:

> **I could not fully verify this from the FSSAI information currently indexed.**

### Why FoodSafe AI uses it

Food-safety guidance should not be confidently invented when the indexed official sources do not support the claim.

### Important learning

Good retrieval alone is not enough.

The generation prompt must also tell the LLM how to use the retrieved evidence and what to do when evidence is insufficient.

### Study in this project

- [Baseline RAG Testing](01_baseline_rag_testing.md)
- [Final Application Testing](06_final_application_testing.md)

---

# 26. GPT-4.1 — Generation

GPT-4.1 performs the **generation** part of Retrieval-Augmented Generation.

It receives:

```text
Official Retrieved Context
           +
    Original Question
           +
Recent Conversation History
           ↓
        GPT-4.1
           ↓
 Natural-Language Answer
```

### Important distinction

GPT-4.1 is not the vector database and does not search FAISS itself.

The retrieval pipeline first finds relevant information.

GPT-4.1 then uses that supplied information to create a clear answer for the user.

### Easy way to remember

```text
Retriever → finds

GPT-4.1 → explains
```

### Study in this project

- [Architecture & Design](00_architecture_and_design.md)
- [Final Application Testing](06_final_application_testing.md)

---

# 27. Conversation Memory

FoodSafe AI stores recent conversation messages using:

```text
Streamlit Session State
```

This allows follow-up questions such as:

```text
User:
I found worms in the rice packet.

User:
What evidence should I keep?
```

The second question can be understood as referring to the previous rice-packet problem.

### Critical grounding rule

Conversation history is used for:

```text
Reference Resolution
```

but not as:

```text
Food-Safety Knowledge
```

Official retrieved FSSAI/FoSCoS context remains the factual source of truth.

### Session-only memory

The memory exists only during the current application session.

The user can remove it using:

```text
Clear conversation
```

Both memory retention and memory clearing were tested in the final application.

### Study in this project

- [Architecture & Design](00_architecture_and_design.md)
- [Final Application Testing](06_final_application_testing.md)

---

# 28. Source Attribution

Retrieved documents retain metadata such as:

```text
title
category
source_url
```

FoodSafe AI uses this information to display official sources associated with the generated guidance.

```text
Retrieved Chunk
      ↓
Metadata
      ↓
Official Source URL
      ↓
Displayed to User
```

### Why it matters

Source attribution improves transparency and allows users to verify or continue reading the official FSSAI/FoSCoS information.

It also makes the RAG pipeline easier to debug because retrieved information can be traced back to its source.

### Study in this project

- [Architecture & Design](00_architecture_and_design.md)
- [Knowledge Base Improvements](02_knowledge_base_improvements.md)
- [Final Application Testing](06_final_application_testing.md)

---

# 29. Offline Ingestion vs Online Inference

FoodSafe AI deliberately separates **knowledge preparation** from **live question answering**.

## Offline Ingestion

```text
Official Sources
      ↓
Scrape
      ↓
Clean
      ↓
Create Documents + Metadata
      ↓
Split into Chunks
      ↓
Create Embeddings
      ↓
Build and Save FAISS
```

This is performed when the knowledge base needs to be created or refreshed.

## Online Inference

```text
User Question
      ↓
Load Existing FAISS
      ↓
Query Expansion
      ↓
Hybrid Retrieval
      ↓
Reranking
      ↓
Build Context
      ↓
GPT-4.1
      ↓
Answer
```

This happens while the application is being used.

### Why this matters

FoodSafe AI does not scrape, split, and re-embed the entire knowledge base whenever Streamlit starts.

This provides:

- faster application startup,
- less unnecessary processing,
- fewer unnecessary embedding API calls,
- cleaner separation between data preparation and application usage.

### Study in this project

- [Architecture & Design](00_architecture_and_design.md)

---

# 30. Complete RAG Mental Model

The easiest way to remember the complete FoodSafe AI RAG pipeline is:

```text
SOURCE
   ↓
INGEST
   ↓
DOCUMENT
   ↓
METADATA
   ↓
SPLIT
   ↓
CHUNKS
   ↓
EMBED
   ↓
VECTOR STORE
   ↓
RETRIEVE
   ↓
RERANK
   ↓
BUILD CONTEXT
   ↓
PROMPT
   ↓
LLM
   ↓
GROUNDED ANSWER
```

### Simple meaning of each stage

| Stage | Simple Meaning |
|---|---|
| **Source** | Where does my trusted knowledge come from? |
| **Ingest** | Bring that knowledge into the application |
| **Document** | Put the content into a standard structure |
| **Metadata** | Remember where the content came from |
| **Split** | Break large content into smaller pieces |
| **Chunks** | The searchable pieces of knowledge |
| **Embed** | Convert text meaning into numerical vectors |
| **Vector Store** | Store and search the vectors |
| **Retrieve** | Find information relevant to the question |
| **Rerank** | Prioritize the strongest retrieved information |
| **Context** | Prepare selected knowledge for the LLM |
| **Prompt** | Tell the LLM how to use the information |
| **LLM** | Generate the natural-language response |
| **Grounded Answer** | Answer based on retrieved trusted information |

### FoodSafe AI implementation

The actual project extends the basic RAG flow:

```text
SOURCE
   ↓
Playwright Ingestion
   ↓
LangChain Documents + Metadata
   ↓
Recursive Text Splitting
   ↓
Chunks
   ↓
OpenAI Embeddings
   ↓
FAISS
   ↓
Intent-Aware Query Expansion
   ↓
FAISS + BM25
   ↓
Hybrid Retrieval
   ↓
FlashRank Per Intent
   ↓
Best Unique Documents
   ↓
Context
   ↓
Grounded Prompt
   ↓
GPT-4.1
   ↓
Answer + Official Sources
```

---

# 31. Concepts by Project Stage

This table provides a quick reference when returning to the project later.

| Project Stage | Concepts Used | Main Documentation |
|---|---|---|
| Knowledge Collection | Playwright, ingestion, cleaning | [Knowledge Base](02_knowledge_base_improvements.md) |
| Document Preparation | LangChain Document, `page_content`, metadata | [Architecture](00_architecture_and_design.md) |
| Chunking | RecursiveCharacterTextSplitter, chunk size, overlap | [Baseline RAG](01_baseline_rag_testing.md) |
| Vectorization | OpenAI embeddings, vectors | [Architecture](00_architecture_and_design.md) |
| Semantic Retrieval | FAISS, query embeddings, similarity search | [Baseline RAG](01_baseline_rag_testing.md) |
| Keyword Retrieval | BM25 | [Hybrid Retrieval](03_hybrid_retrieval_testing.md) |
| Hybrid Search | EnsembleRetriever, FAISS + BM25, RRF | [Hybrid Retrieval](03_hybrid_retrieval_testing.md) |
| Candidate Selection | Retrieval candidates | [Hybrid Retrieval](03_hybrid_retrieval_testing.md) |
| Reranking | FlashRank | [Reranking](04_reranking_testing.md) |
| Query Expansion | Deterministic multi-query expansion | [Intent-Aware Retrieval](05_intent_aware_retrieval.md) |
| Multi-Intent Handling | Intent-aware retrieval and per-intent reranking | [Intent-Aware Retrieval](05_intent_aware_retrieval.md) |
| Context Building | Retrieved documents → LLM context | [Architecture](00_architecture_and_design.md) |
| Generation | Context + original question + GPT-4.1 | [Architecture](00_architecture_and_design.md) |
| Grounding | Prompt restrictions and insufficient-evidence handling | [Final Testing](06_final_application_testing.md) |
| Memory | Streamlit Session State, reference resolution | [Final Testing](06_final_application_testing.md) |
| Transparency | Metadata and official source attribution | [Final Testing](06_final_application_testing.md) |

---

# 32. Reusable Learning for Future RAG Projects

FoodSafe AI demonstrates that building a useful RAG application involves more than connecting a vector database to an LLM.

A reusable approach for future projects is:

```text
1. Choose trusted knowledge sources
              ↓
2. Build reliable ingestion
              ↓
3. Create Documents + Metadata
              ↓
4. Choose a chunking strategy
              ↓
5. Create embeddings
              ↓
6. Build the vector store
              ↓
7. Test baseline retrieval
              ↓
8. Identify retrieval vs knowledge gaps
              ↓
9. Improve retrieval only where testing shows a need
              ↓
10. Add reranking when candidate quality requires it
              ↓
11. Build grounded context for the LLM
              ↓
12. Test real user questions
              ↓
13. Diagnose failures
              ↓
14. Improve and retest
```

## Key Lessons from FoodSafe AI

### 1. More data does not automatically mean better RAG

The quality and relevance of the indexed information matter more than simply adding more documents.

### 2. Retrieval problems and knowledge problems are different

If the correct information exists in the knowledge base but is not retrieved, improve retrieval.

If the required information does not exist in the indexed sources, changing the retriever alone will not solve the problem.

### 3. Hybrid retrieval improves recall, not necessarily final precision

FAISS + BM25 helped find a broader set of useful candidates, but reranking was still required to prioritize them.

### 4. Reranking must be tested

Adding a reranker does not guarantee better results for every question.

FoodSafe AI's testing showed that global reranking could sometimes reduce the visibility of an important secondary intent.

### 5. Short questions may contain multiple information needs

Queries such as:

```text
fungus bread
```

may require problem information, complaint guidance, and evidence guidance.

This led to intent-aware retrieval.

### 6. Metadata is important beyond retrieval

Metadata helped with:

```text
Source Attribution
+
Debugging
+
Testing
+
Traceability
```

### 7. Grounding is a complete pipeline responsibility

Grounding does not come only from the prompt.

It depends on:

```text
Trusted Sources
      +
Good Ingestion
      +
Relevant Retrieval
      +
Good Reranking
      +
Correct Context
      +
Grounded Prompt
```

### 8. Memory and knowledge are different

Conversation memory helps understand what the user is referring to.

The retrieved official knowledge determines the factual answer.

### 9. Separate ingestion from inference

The knowledge base should not normally be rebuilt every time a user asks a question or starts the application.

### 10. Build → Test → Diagnose → Improve → Retest

The FoodSafe AI development journey followed:

```text
Baseline RAG
     ↓
Identify Knowledge Gaps
     ↓
Improve Official Source Ingestion
     ↓
Hybrid Retrieval
     ↓
Test
     ↓
FlashRank Reranking
     ↓
Test
     ↓
Identify Multi-Intent Problem
     ↓
Multi-Query Retrieval
     ↓
Test
     ↓
Identify Global Reranking Problem
     ↓
Intent-Aware Per-Query Reranking
     ↓
Retest
     ↓
Grounded Final Application
```

The most reusable lesson from this project is:

> **A strong RAG application is built by improving the quality of the complete pipeline — knowledge, ingestion, chunking, retrieval, reranking, context, grounding, and testing — rather than simply adding more advanced components.**

This **build → test → diagnose → improve → retest** approach can be reused when building future RAG applications in other domains.