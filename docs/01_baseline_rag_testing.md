# Baseline RAG Testing

## Objective

The first working version of FoodSafe AI used a basic Retrieval-Augmented Generation (RAG) pipeline.

The objective of baseline testing was to determine:

- whether official FSSAI/FoSCoS information could be retrieved
- whether GPT-4.1 could answer using retrieved context
- whether answers remained grounded
- which questions worked well
- which questions exposed knowledge-base or retrieval limitations
- what improvements were required before building the final application

The baseline was intentionally tested before introducing advanced retrieval techniques such as BM25, hybrid retrieval, FlashRank, or intent-aware retrieval.


## Baseline RAG Architecture

The initial RAG flow was:

```text
User Question
      ↓
OpenAI Query Embedding
      ↓
FAISS Semantic Search
      ↓
Top Relevant Chunks
      ↓
Context Builder
      ↓
Context + Original Question
      ↓
GPT-4.1
      ↓
Grounded Answer
```


## Baseline Components

The baseline pipeline used:

- Python
- LangChain
- Playwright
- OpenAI Embeddings
- FAISS
- GPT-4.1


## Role of Playwright

Playwright was used during the ingestion phase.

Its responsibility was to collect information from official FSSAI/FoSCoS webpages.

Conceptually:

```text
Official FSSAI/FoSCoS Website
          ↓
      Playwright
          ↓
     Scraped Text
```

Playwright was not used for answering every user question.


## Role of LangChain Documents

Scraped webpage information was converted into LangChain `Document` objects.

Each document contained:

```text
page_content
+
metadata
```

This provided a structured representation of the official information before splitting and indexing.


## Document Splitting

Large documents were divided into smaller chunks using LangChain's `RecursiveCharacterTextSplitter`.

The configuration used:

```text
chunk_size    = 750 characters
chunk_overlap = 100 characters
```

The recursive separators were:

```python
[
    "\n\n",
    "\n",
    ". ",
    " ",
    ""
]
```


## Why Chunking Was Required

Retrieving an entire webpage for every question would provide too much unrelated information.

Chunking allowed FoodSafe AI to search smaller pieces of official content.

Conceptually:

```text
Official Webpage
      ↓
Smaller Chunks
      ↓
Individual Embeddings
      ↓
More Focused Retrieval
```


## Why Chunk Overlap Was Used

A small overlap was maintained between neighboring chunks so that important information near a chunk boundary would not lose its surrounding context.

The overlap was:

```text
100 characters
```

This helped preserve continuity.

However, testing later showed that overlapping chunks could also result in similar information appearing more than once in retrieval results.


## Document Embeddings

Each document chunk was converted into a numerical vector representation using:

```text
text-embedding-3-small
```

The embedding represents the semantic meaning of the chunk.


## FAISS Vector Store

The document embeddings were stored in FAISS.

FAISS was used to perform semantic similarity search.

Conceptually:

```text
Document Chunk
      ↓
OpenAI Embedding
      ↓
Vector
      ↓
FAISS
```


## Query Retrieval

When the user entered a question, the question was also converted into an embedding.

Conceptually:

```text
User Question
      ↓
OpenAI Embedding
      ↓
Query Vector
```

FAISS then compared the query vector with the stored document vectors.


## Important FAISS Concept

FAISS does not directly generate an answer.

Its responsibility is retrieval.

It identifies document chunks whose embeddings are semantically similar to the user's question.

The flow is:

```text
Question
   ↓
Embedding
   ↓
FAISS Search
   ↓
Relevant Chunks
```

The retrieved chunks are then passed to GPT-4.1 by the Python/LangChain application.


## Context Builder

A reusable context builder combined the retrieved chunks into a text block that could be supplied to GPT-4.1.

During one plastic-rice test, the context builder produced:

```text
Documents used : 3
Context length : approximately 1,803 characters
```

This confirmed that retrieved documents could successfully be transformed into an LLM-ready context.


## Context and Original Question

FoodSafe AI deliberately passed both:

1. retrieved official context
2. the user's original question

to GPT-4.1.

Conceptually:

```text
Retrieved FSSAI Context
          +
Original User Question
          ↓
       GPT-4.1
          ↓
       Answer
```


## Why Both Were Required

The retrieved context tells GPT-4.1:

> What official information is available?

The original question tells GPT-4.1:

> What does the user actually want answered?

The model uses the official context to answer the original question.


## GPT-4.1

GPT-4.1 was used as the final answer-generation model.

Its responsibility was to transform retrieved official information into a clear consumer-friendly answer.


## Temperature Setting

The generation model used:

```text
temperature = 0
```

This was chosen to improve consistency and reduce unnecessary creativity.

For FoodSafe AI, factual grounding was more important than creative variation.


## Grounding Strategy

The prompt instructed GPT-4.1 to answer using the retrieved official context.

If the retrieved FSSAI information did not sufficiently support the requested guidance, the system should acknowledge the limitation rather than invent information.

A limitation message used by the project was:

> I could not fully verify this from the FSSAI information currently indexed.


## Why Grounding Was Important

FoodSafe AI deals with food-safety guidance.

The application should therefore avoid:

- inventing complaint procedures
- inventing adulteration tests
- inventing food standards
- generalizing a standard from one food category to another
- presenting unsupported claims as official FSSAI guidance


# Initial Retrieval Observations


## Plastic Rice Retrieval Test

One of the early retrieval questions involved the plastic-rice myth.

The baseline FAISS retrieval produced:

```text
Result 1 → Excellent direct match
Result 2 → Relevant but overlapping
Result 3 → Weak
```


## What the Plastic Rice Test Showed

The test demonstrated that FAISS semantic retrieval was working.

The relevant official Myth Buster information was successfully retrieved.

However, it also revealed two retrieval-quality issues:

- overlapping chunks
- weak lower-ranked results


## Baseline Retrieval Limitation

This produced an early observation:

> Retrieving some correct information does not mean every retrieved chunk is equally useful.

This later became one reason for adding more advanced retrieval and reranking.


# First End-to-End RAG Test


## End-to-End Flow

After retrieval and context building worked independently, GPT-4.1 was connected to create the first complete FoodSafe AI RAG flow:

```text
Question
   ↓
FAISS
   ↓
Retrieved Chunks
   ↓
Context Builder
   ↓
Context + Question
   ↓
GPT-4.1
   ↓
Answer
```


## First Generation Result

The first end-to-end answer demonstrated that:

- FAISS could retrieve official information
- the context could be formatted correctly
- GPT-4.1 could use that context
- the generated response could remain grounded
- official sources could be preserved for verification

This established the first functional FoodSafe AI RAG baseline.


# Baseline Evaluation


## Why Formal Baseline Testing Was Performed

Testing only one successful question would not provide enough evidence that the RAG pipeline was reliable.

Therefore, five fixed questions representing different FoodSafe AI use cases were selected.


## Baseline Test Questions

The five questions were:

### Test 1 — Food Myth

> Is plastic rice real?


### Test 2 — Unsafe Packaged Food

> What should I do if I find fungus in packaged food?


### Test 3 — Consumer Complaint

> How can I complain about unsafe packaged food?


### Test 4 — Food Recall

> How do I know if a food product has been recalled?


### Test 5 — Food Adulteration

> How can I check whether milk is adulterated?


# Baseline Test Results


## Overall Result

The five baseline questions produced:

```text
Strong  : 2 / 5
Partial : 2 / 5
Weak    : 1 / 5
```


## Useful / Grounded Answers

Approximately:

```text
Useful or grounded : 4 / 5
```


## Unsupported Hallucinations

The baseline evaluation identified:

```text
Unsupported hallucinations : 0 / 5
```

This was an important result.

The baseline was not complete, but the grounding strategy helped prevent unsupported answers.


# Test-by-Test Analysis


## Test 1 — Plastic Rice

Question:

> Is plastic rice real?

### Result

```text
Strong
```

### Why

The FSSAI Myth Buster information contained directly relevant material.

FAISS retrieved the relevant source successfully.

### Learning

When the corpus contains a strong direct match, basic semantic retrieval can work very well.


## Test 2 — Fungus in Packaged Food

Question:

> What should I do if I find fungus in packaged food?

### Result

```text
Partial
```

### Why

The knowledge base contained fungus-related FSSAI information.

However, it did not yet provide enough complaint/evidence guidance in the final retrieved context to give a complete consumer-action answer.

### Learning

A question can require multiple types of information:

```text
Food Safety Problem
      +
Complaint Guidance
      +
Evidence Guidance
```

A single semantic match may not cover every intent.


## Test 3 — Unsafe Packaged-Food Complaint

Question:

> How can I complain about unsafe packaged food?

### Result

```text
Partial
```

### Why

Complaint-related information existed, but retrieval quality and knowledge coverage still required improvement.

The relevant complaint source was not always the highest-ranked result.

### Learning

Exact complaint terminology suggested that keyword retrieval could complement semantic search.


## Test 4 — Food Recall

Question:

> How do I know if a food product has been recalled?

### Result

```text
Strong
```

### Why

The corpus contained dedicated official FSSAI food-recall information.

The question aligned well with the indexed recall content.

### Learning

Dedicated, targeted official source pages improve RAG performance.


## Test 5 — Milk Adulteration

Question:

> How can I check whether milk is adulterated?

### Result

```text
Weak
```

### Why

The initial corpus did not contain enough detailed adulteration guidance to answer the question completely.

### Learning

This was primarily a:

```text
Corpus Coverage Problem
```

rather than an LLM problem.


# Two Main Problem Categories Identified


## 1. Retrieval Quality Problems

Some required information existed in the corpus but was not always ranked optimally.

Examples included:

- overlapping chunks
- weak lower-ranked results
- relevant complaint information appearing below other results

This indicated a need to improve retrieval.


## 2. Corpus Coverage Problems

Some required information was not sufficiently represented in the indexed data.

The clearest example was:

```text
Milk Adulteration
```

This indicated a need to improve the knowledge base.


## Why This Distinction Was Important

Without this distinction, every weak answer could incorrectly be treated as a model problem.

Instead, FoodSafe AI used the following reasoning:

```text
Weak Answer
    ↓
Is the required information in the corpus?
    ↓
YES                         NO
 ↓                           ↓
Retrieval Problem       Corpus Problem
```


# Baseline Before → Problem → Improvement Direction


## Before

FoodSafe AI had a functioning baseline RAG pipeline:

```text
Official Sources
      ↓
Playwright
      ↓
LangChain Documents
      ↓
Chunks
      ↓
Embeddings
      ↓
FAISS
      ↓
GPT-4.1
```


## Problem

Baseline evaluation showed:

```text
Strong  : 2
Partial : 2
Weak    : 1
```

The main issues were:

- limited corpus coverage
- overlapping retrieval results
- weaker chunks in top results
- complaint information not always highly ranked
- insufficient adulteration information


## Improvement Direction

The baseline results led to a structured improvement plan:

1. improve official source coverage
2. improve document metadata
3. clean unnecessary webpage content
4. add adulteration guidance
5. improve complaint guidance
6. add BM25 keyword retrieval
7. combine BM25 with FAISS
8. add reranking
9. test final answer quality


# Why the Baseline Was Preserved

The baseline was not discarded after advanced RAG was implemented.

It was documented because it provided a measurable reference point.

Without baseline testing, later claims such as:

> retrieval improved

would have little supporting evidence.

The baseline made it possible to show how FoodSafe AI evolved through testing.


# Baseline vs Advanced RAG Direction

At this stage, the architecture was:

```text
BASELINE

Question
   ↓
FAISS
   ↓
Top Chunks
   ↓
GPT-4.1
```

The planned advanced direction became:

```text
ADVANCED

Question
   ↓
FAISS + BM25
   ↓
Hybrid Retrieval
   ↓
Reranking
   ↓
Better Context
   ↓
GPT-4.1
```


# Important API Understanding


## Document Embedding Calls

During offline ingestion, OpenAI embeddings were used to convert document chunks into vectors.

These vectors were saved in FAISS.

They did not need to be regenerated for every user question.


## Query Embedding Call

When a user asks a new question, FAISS semantic search requires the question to be converted into an embedding.

Therefore:

```text
New Question
    ↓
Query Embedding
    ↓
FAISS Search
```


## GPT-4.1 Generation Call

After retrieval, GPT-4.1 receives:

```text
Retrieved Context
       +
Original Question
```

and generates the final answer.

Therefore, embeddings and GPT-4.1 perform different jobs:

```text
Embedding Model
      ↓
Helps FIND information

GPT-4.1
      ↓
Helps EXPLAIN information
```


# Important Architecture Principle


## Ingestion Is Separate from Inference

The baseline established an important architectural principle that was retained in the final application.

### Offline Ingestion

```text
FSSAI/FoSCoS
      ↓
Playwright
      ↓
Cleaning
      ↓
Documents
      ↓
Chunks
      ↓
Embeddings
      ↓
FAISS
```


### Online Inference

```text
User Question
      ↓
Load Existing FAISS
      ↓
Retrieve Context
      ↓
GPT-4.1
      ↓
Answer
```


## Why This Matters

The Streamlit application does not need to:

- scrape FSSAI every time it opens
- clean the source pages again
- recreate all chunks
- regenerate all document embeddings

This makes the application faster, cleaner, and more cost-efficient.


# Key Learnings


## 1. A Working RAG Pipeline Is Not Automatically a Good RAG Pipeline

The baseline technically worked, but formal testing exposed weaknesses that were not obvious from a single successful question.


## 2. Retrieval and Generation Are Different Stages

FAISS finds relevant information.

GPT-4.1 explains the retrieved information.

A weak retrieval result can limit the quality of the final answer even when GPT-4.1 is working correctly.


## 3. Corpus Quality Matters

The milk adulteration test demonstrated that missing source information cannot be solved simply by changing the prompt.


## 4. Semantic Retrieval Has Limitations

FAISS successfully found semantically relevant content, but overlapping and weaker chunks could still appear.


## 5. Grounding Should Be Tested Explicitly

The baseline produced:

```text
Unsupported hallucinations : 0 / 5
```

This was an important success even though some answers were incomplete.


## 6. Limitations Are Better Than Unsupported Answers

When indexed FSSAI information was insufficient, the application was designed to acknowledge that limitation rather than invent a procedure.


## 7. Baseline Testing Creates Evidence for Improvement

The baseline results provided a measurable starting point against which later retrieval improvements could be compared.


# Baseline Testing Summary

```text
Questions Tested            : 5

Strong                      : 2
Partial                     : 2
Weak                        : 1

Useful / Grounded           : 4 / 5
Unsupported Hallucinations  : 0 / 5
```


# Decision

The baseline RAG pipeline was considered successfully functional but not yet sufficient for the final FoodSafe AI application.

The next priority was not to change GPT-4.1.

Instead, the first major improvement focused on the information being supplied to it:

> the FSSAI/FoSCoS knowledge base.


# Next Improvement

The next phase focused on:

- expanding authentic official sources
- improving metadata
- cleaning the corpus
- adding adulteration coverage
- improving complaint guidance
- rebuilding the FAISS index

This is documented in:

```text
docs/02_knowledge_base_improvements.md
```


# Conclusion

The baseline FoodSafe AI RAG pipeline successfully demonstrated the complete flow from official FSSAI/FoSCoS information to a GPT-4.1-generated grounded answer.

Testing five representative questions produced:

```text
2 Strong
2 Partial
1 Weak
0 Unsupported Hallucinations
```

The baseline proved that the core RAG architecture worked, while also revealing two separate areas for improvement:

```text
Corpus Coverage
      +
Retrieval Quality
```

Rather than changing the LLM immediately, FoodSafe AI used these findings to systematically improve the knowledge base and retrieval architecture.

This baseline became the reference point for measuring the later evolution of FoodSafe AI.