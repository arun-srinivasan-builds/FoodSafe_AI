# Hybrid Retrieval Testing

## Objective

The baseline FoodSafe AI RAG pipeline used FAISS semantic similarity search to retrieve relevant chunks from the indexed FSSAI/FoSCoS knowledge base.

Although FAISS successfully retrieved relevant information for many questions, testing showed that semantic similarity alone did not always rank the most useful official chunk highly enough.

The objective of this phase was to improve retrieval by combining:

- FAISS semantic search
- BM25 keyword search

This created a hybrid retrieval system.


## Baseline Retrieval Architecture

Before hybrid retrieval, the search flow was:

```text
User Question
      ↓
OpenAI Query Embedding
      ↓
FAISS Semantic Search
      ↓
Top Matching Chunks
      ↓
Context
      ↓
GPT-4.1
```


## Why FAISS Alone Was Not Enough

FAISS performs semantic similarity search.

The user's question is converted into an embedding and compared with the embeddings of the indexed FSSAI/FoSCoS chunks.

This works well when the meaning of the question and document are semantically similar.

However, baseline testing identified several limitations:

- overlapping chunks could appear in the results
- weaker chunks could sometimes rank above more useful chunks
- exact complaint-related terminology was not always prioritized
- relevant information could exist in the knowledge base but appear lower in the ranking

Therefore, semantic similarity alone was not considered sufficient for the advanced FoodSafe AI retrieval pipeline.


## Why BM25 Was Added

BM25 is a keyword-based ranking algorithm.

Unlike FAISS, BM25 does not use embeddings.

It looks at the occurrence and importance of words within the indexed documents.

This is useful when the user's question contains terminology that also appears directly in the official FSSAI/FoSCoS source.

Examples include:

- complaint
- packaged food
- food recall
- adulteration
- consumer
- grievance
- supporting document

The intention was not to replace FAISS.

Instead, FoodSafe AI combined the strengths of semantic and keyword retrieval.


## FAISS vs BM25

### FAISS

FAISS is useful for questions such as:

> Which information has a meaning similar to the user's question?

It can retrieve relevant information even when the exact same words are not present.


### BM25

BM25 is useful for questions such as:

> Which documents contain important words used in the user's question?

It can strongly reward exact terminology.


### Hybrid Retrieval

Combining them provides:

```text
Semantic Meaning
      +
Keyword Matching
      ↓
Hybrid Retrieval
```


## Hybrid Retrieval Architecture

The retrieval pipeline became:

```text
                User Question
                     ↓
          ┌──────────┴──────────┐
          ↓                     ↓
   FAISS Semantic          BM25 Keyword
      Retrieval              Retrieval
          ↓                     ↓
          └──────────┬──────────┘
                     ↓
          Reciprocal Rank Fusion
                     ↓
          Combined Candidate Pool
```


## Hybrid Retrieval Configuration

The configuration used during testing was:

### FAISS

```text
Search type : Similarity
Top results : 5
```

### BM25

```text
Top results : 5
```

### Ensemble

```text
FAISS weight : 0.5
BM25 weight  : 0.5
```

LangChain's `EnsembleRetriever` was used to combine both retrievers.


## Reciprocal Rank Fusion

The hybrid retriever did not simply concatenate FAISS and BM25 results.

LangChain's ensemble retrieval combined the rankings using reciprocal rank fusion.

This allowed a document that performed well across the two retrieval methods to receive stronger combined importance.

Conceptually:

```text
FAISS Ranking
      +
BM25 Ranking
      ↓
Reciprocal Rank Fusion
      ↓
Combined Ranking
```


## First Implementation Problem

The initial hybrid retrieval implementation attempted to obtain the document chunks using a function named:

```python
split_documents()
```

However, that function was not available through the expected interface.

This caused an import error and prevented the hybrid retriever from starting.


## Diagnosis

BM25 needed access to the same document chunks that had already been embedded and stored inside FAISS.

Re-running the complete ingestion and splitting pipeline inside the application was unnecessary.

It would also create a risk that FAISS and BM25 might operate on different versions of the chunks.


## Fix

Instead of recreating the chunks, the implementation loaded the exact documents already stored inside the FAISS vector store:

```python
documents = list(vectorstore.docstore._dict.values())
```

BM25 was then constructed using those same documents.


## Why This Fix Was Important

This ensured that:

- FAISS searched the existing embedded chunks
- BM25 searched the exact same chunks
- metadata remained consistent
- the application did not need to repeat document splitting
- the application did not need to recreate document embeddings
- ingestion remained separate from inference


## Final Hybrid Retriever Structure

The main hybrid retriever used the following structure:

```python
def get_hybrid_retriever():
    vectorstore = load_faiss_vectorstore()

    faiss_retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )

    documents = get_faiss_documents(vectorstore)

    bm25_retriever = BM25Retriever.from_documents(documents)
    bm25_retriever.k = 5

    hybrid_retriever = EnsembleRetriever(
        retrievers=[faiss_retriever, bm25_retriever],
        weights=[0.5, 0.5]
    )

    return hybrid_retriever
```


## No Document Re-Embedding During Search

An important design decision was to keep ingestion separate from application inference.

The application loads the existing FAISS index from:

```text
vectorstore/faiss_index
```

It does not:

- scrape FSSAI again
- clean the documents again
- split the documents again
- generate all document embeddings again

whenever the application starts or the user asks a question.


## OpenAI API Usage During Hybrid Search

FAISS semantic search requires the current user query to be converted into an embedding.

Therefore, a semantic query search uses the OpenAI embedding API for the question.

BM25 does not require an OpenAI API call.

Conceptually:

```text
User Question
      ↓
      ├── FAISS → Query Embedding Required
      │
      └── BM25  → No OpenAI API Required
```


## Complaint Retrieval Test

One of the most useful tests involved complaint guidance.

The relevant `Consumer Complaint Guidance` source had previously appeared approximately at:

```text
Baseline FAISS Rank → #3
```

After introducing FAISS + BM25 hybrid retrieval, the relevant complaint source moved to approximately:

```text
Hybrid Rank → #1
```


## Complaint Test Result

This demonstrated that keyword information contributed useful retrieval signals for complaint-related questions.

The result can be summarized as:

```text
Baseline FAISS
Complaint Guidance → approximately #3

          ↓

FAISS + BM25 Hybrid

          ↓

Complaint Guidance → approximately #1
```


## Why the Complaint Test Improved

Complaint-related FSSAI/FoSCoS information contains terminology such as:

- complaint
- consumer
- packaged food
- grievance
- food delivery

BM25 could reward these exact terms while FAISS continued to contribute semantic similarity.

The combination improved the ranking for this tested scenario.


## Hybrid Candidate Pool

Because FAISS and BM25 search differently, combining their results created a broader candidate pool.

For one complaint test, approximately:

```text
7 hybrid candidates
```

were returned.


## Benefit of the Larger Candidate Pool

The larger candidate pool improved recall.

In other words:

> The system had a better chance of finding the required official information somewhere among the retrieved candidates.

This was an improvement over relying on one retrieval method alone.


## New Problem Identified

The larger candidate pool also introduced a new problem.

Not every retrieved candidate was equally useful.

The hybrid results could contain:

- highly relevant chunks
- partially relevant chunks
- overlapping chunks
- weakly related chunks

Therefore:

> Better recall did not automatically mean better final context.


## Example Retrieval Flow

The hybrid system could behave conceptually like this:

```text
FAISS Top 5
      +
BM25 Top 5
      ↓
Reciprocal Rank Fusion
      ↓
Approximately 7 Unique Candidates
```

But GPT-4.1 did not need every candidate.

Sending all candidates could introduce unnecessary context noise.


## Need for a Second-Stage Ranker

This led to the next engineering question:

> From the broader hybrid candidate pool, which chunks should actually be sent to GPT-4.1?

The hybrid retriever was good at discovering potentially relevant information.

A second stage was needed to prioritize the best candidates.


## Decision

FoodSafe AI retained hybrid retrieval and added a reranking stage.

The planned advanced pipeline became:

```text
User Question
      ↓
FAISS Semantic Retrieval
        +
BM25 Keyword Retrieval
      ↓
Reciprocal Rank Fusion
      ↓
Hybrid Candidate Pool
      ↓
Reranker
      ↓
Best Context Chunks
      ↓
GPT-4.1
```


## Before → Problem → Improvement → Result

### Before

FoodSafe AI relied primarily on FAISS semantic similarity retrieval.

### Problem

Relevant official chunks could sometimes appear below overlapping or less useful results.

### Improvement

BM25 keyword retrieval was added and combined with FAISS using reciprocal rank fusion.

### Result

For the tested complaint scenario:

```text
Relevant Complaint Source

Baseline → approximately Rank #3
Hybrid   → approximately Rank #1
```

Hybrid retrieval therefore improved the ranking for this test.

However, the larger candidate pool also introduced noise.


## Important Testing Principle

The hybrid test demonstrated an important principle used throughout FoodSafe AI:

> Retrieval improvements should be measured rather than assumed.

The project does not claim that hybrid retrieval makes every query better.

Instead, the implementation was retained because testing showed that semantic and keyword retrieval provided complementary signals and improved important scenarios such as complaint guidance.


## Key Learning — FAISS

FAISS answers a question similar to:

> Which indexed chunks are semantically similar to this question?

Its strength is meaning-based retrieval.


## Key Learning — BM25

BM25 answers a question similar to:

> Which indexed chunks contain important terms from this question?

Its strength is keyword-based retrieval.


## Key Learning — Hybrid Retrieval

Hybrid retrieval combines:

```text
Meaning
   +
Keywords
   ↓
Better Candidate Discovery
```

This improves retrieval recall by allowing two different search strategies to contribute candidates.


## Key Learning — Recall vs Precision

This phase also helped distinguish two important retrieval concepts.

### Recall

Did the retriever successfully find the useful information?

### Precision

Are the highest-ranked retrieved results actually the most useful ones?

Hybrid retrieval improved candidate discovery and recall.

However, the broader candidate pool showed that precision still needed improvement.


## Why Reranking Became the Next Step

Hybrid retrieval answered:

> What information might be useful?

But FoodSafe AI still needed another mechanism to answer:

> Which of these candidates is most relevant to the user's question?

This directly motivated the introduction of FlashRank.


## Final Hybrid Retrieval Architecture

At the end of this phase, the architecture was:

```text
User Question
      ↓
┌───────────────────────────────┐
│       Hybrid Retrieval        │
│                               │
│  FAISS Semantic Search        │
│           +                   │
│  BM25 Keyword Search          │
│           ↓                   │
│  Reciprocal Rank Fusion       │
└───────────────┬───────────────┘
                ↓
        Candidate Chunks
                ↓
        FlashRank ← NEXT
                ↓
           GPT-4.1
```


## Conclusion

Hybrid retrieval improved FoodSafe AI by combining semantic search and keyword search.

FAISS provided meaning-based retrieval, while BM25 provided exact-term matching.

For the tested complaint scenario, the relevant complaint guidance improved from approximately rank #3 in the baseline retrieval to rank #1 after hybrid retrieval.

The implementation also revealed that improving recall creates another challenge: selecting the best information from a broader candidate pool.

Rather than sending all retrieved information directly to GPT-4.1, FoodSafe AI therefore introduced a second-stage reranking mechanism.

This directly led to FlashRank reranking, documented in:

```text
docs/04_reranking_testing.md
```