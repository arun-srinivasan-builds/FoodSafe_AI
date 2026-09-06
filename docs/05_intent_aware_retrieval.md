# Intent-Aware Retrieval and Reranking

## Objective

After improving the knowledge base, adding FAISS + BM25 hybrid retrieval, and introducing FlashRank reranking, FoodSafe AI was performing well for most test scenarios.

However, one important test remained only partially successful:

> I found fungus in packaged bread before the expiry date. What should I do?

The objective of this phase was to determine why the required official complaint guidance existed in the knowledge base but was still not reaching GPT-4.1.

This investigation led to the final advanced retrieval strategy:

> Intent-aware multi-query retrieval + per-intent FlashRank reranking.


# Problem — Fungus Test Still Partial

## Expected Answer Requirements

The fungus-in-packaged-bread question contains more than one information need.

A useful answer may require:

1. information about the food-safety problem
2. packaged-food complaint guidance
3. supporting-document or evidence guidance

Conceptually:

```text
Fungus in Packaged Bread
        ↓
┌─────────────────────────────┐
│ Food Safety Information     │
│ Complaint Procedure         │
│ Supporting Evidence         │
└─────────────────────────────┘
```


## Initial Result

Even after improving the FoSCoS complaint corpus, the fungus question remained:

```text
PARTIAL
```

The final top three reranked chunks were all from:

```text
Food Safety Myth Busters
```

Complaint guidance was not reaching the final GPT-4.1 context.


# Was the Complaint Data Missing?

Before changing the retrieval architecture, the knowledge base was tested directly.

A targeted question was used:

> What evidence should I keep when making a complaint about packaged food?


## Diagnostic Result

For this targeted query, the top results were all from:

```text
Consumer Complaint Guidance
```

Approximate FlashRank scores included:

```text
0.9596
0.9587
```


## What This Proved

This proved that:

- the official FoSCoS complaint information had been scraped
- the information existed in the indexed corpus
- FAISS contained the relevant chunks
- BM25 could retrieve them
- hybrid retrieval could retrieve them
- FlashRank could rank them strongly

Therefore, the remaining problem was not:

```text
Missing Data
```

It was:

```text
Retrieval Intent
```


# Understanding the Multi-Intent Problem

A real user may not ask a carefully structured question.

Users may enter short inputs such as:

```text
fungus bread
```

or:

```text
worm in rice packet
```

However, FoodSafe AI still needs to understand that such a problem may require multiple types of official guidance.

A short question may therefore imply:

```text
Problem Identification
        +
Complaint Guidance
        +
Evidence Guidance
```


# Why the Original Query Was Not Enough

Consider:

```text
fungus bread
```

A semantic or keyword search based only on those two words is naturally likely to prioritize chunks containing:

- fungus
- food contamination
- food myths
- related food-safety terminology

It may not strongly retrieve information containing words such as:

- complaint
- grievance
- supporting document
- image
- bill

even though that information is useful for answering what the consumer should do.


# First Improvement — Deterministic Multi-Query Expansion

FoodSafe AI introduced deterministic query expansion.

Instead of searching only the user's exact question, the system generates additional retrieval queries for relevant intents.


## Example

For:

```text
fungus bread
```

the retrieval queries became approximately:

```text
1. fungus bread

2. packaged food complaint Food Grievance Portal consumer complaint procedure

3. supporting document evidence image product bill packaged food complaint
```


## Purpose of the Three Queries

### Query 1 — Original Problem

```text
fungus bread
```

Purpose:

> Retrieve information directly related to the food-safety problem.


### Query 2 — Complaint Guidance

```text
packaged food complaint Food Grievance Portal consumer complaint procedure
```

Purpose:

> Retrieve official complaint-process information.


### Query 3 — Evidence Guidance

```text
supporting document evidence image product bill packaged food complaint
```

Purpose:

> Retrieve official supporting-document guidance.


# Why Deterministic Expansion Was Chosen

FoodSafe AI did not use another LLM to generate these retrieval queries.

The expansion was rule-based and deterministic.


## Advantages

This avoided:

- another LLM generation call
- additional cost
- additional latency
- unpredictable query generation
- unnecessary complexity for the buildathon MVP


## API Impact

The original basic FAISS pipeline required approximately one semantic query embedding for one user question.

With three retrieval queries, FAISS semantic retrieval can require approximately:

```text
Up to 3 query embedding calls
```

However, the application still uses only:

```text
1 final GPT-4.1 generation call
```

BM25 does not require an OpenAI API call.


# Multi-Query Retrieval Architecture

The first multi-query design became:

```text
                User Question
                     ↓
          Deterministic Expansion
                     ↓
        ┌────────────┼────────────┐
        ↓            ↓            ↓
     Query 1      Query 2      Query 3
        ↓            ↓            ↓
     Hybrid       Hybrid       Hybrid
   Retrieval     Retrieval     Retrieval
        ↓            ↓            ↓
        └────────────┼────────────┘
                     ↓
             Combine Candidates
                     ↓
                 Deduplicate
                     ↓
             Global FlashRank
                     ↓
                Top 3 Chunks
```


# First Implementation Problem

During the first integration of multi-query retrieval, the new code attempted to import:

```python
create_hybrid_retriever
```

However, the actual hybrid retriever module exposed:

```python
get_hybrid_retriever
```


## Result

The integration failed because the function name did not match the existing module interface.


## Fix

The import was corrected to use:

```python
from hybrid_retriever import get_hybrid_retriever
```

This restored compatibility with the existing hybrid retrieval implementation.


## Engineering Learning

When improving one layer of a RAG pipeline, the interfaces between components must remain consistent.

The retrieval architecture may be logically correct but still fail if integration contracts are not aligned.


# Testing the First Multi-Query Design

The short input:

```text
fungus bread
```

was tested.


## Retrieval Results

The three queries returned approximately:

```text
Query 1 → 8 candidates
Query 2 → 7 candidates
Query 3 → 6 candidates
```

Total before deduplication:

```text
21 candidates
```

After deduplication:

```text
15 unique candidates
```


## Initial Interpretation

This was a positive result.

The expanded queries successfully retrieved information across different intents.

The candidate pool contained both:

- food-safety information
- complaint-related information


# Unexpected Failure — Global Reranking

After retrieving and combining the candidates, FlashRank globally reranked all candidates against the original user query:

```text
fungus bread
```

This caused a new problem.


## Global Reranking Result

The final top three chunks were all:

```text
Food Safety Myth Busters
```

The complaint and evidence chunks were removed from the final context.


## Why This Happened

FlashRank was asked:

> Which passages are most relevant to "fungus bread"?

Naturally, fungus-related passages scored more strongly than complaint-procedure passages.

The reranker did not know that the application intentionally generated other queries representing secondary intents.


# Second Vague Query Test

To confirm that this was not specific to fungus, another short query was tested:

```text
worm in rice packet
```


## Expanded Retrieval

The system again generated approximately:

```text
1. worm in rice packet

2. packaged food complaint Food Grievance Portal consumer complaint procedure

3. supporting document evidence image product bill packaged food complaint
```


## Candidate Results

The combined searches produced approximately:

```text
21 candidates before deduplication
16 unique candidates after deduplication
```


## Final Global Reranking Result

Despite successfully retrieving complaint-related candidates, the final top three were again all:

```text
Food Safety Myth Busters
```


# Critical Finding

The two tests demonstrated an important advanced RAG problem:

> Multi-query retrieval successfully improved recall, but global reranking against the original short question removed the secondary intents.

Conceptually:

```text
Multi-Query Retrieval
        ↓
Problem Information      ✓
Complaint Information    ✓
Evidence Information     ✓
        ↓
Combine Everything
        ↓
Rerank Against Only:
"fungus bread"
        ↓
Problem Information      ✓
Complaint Information    ✗
Evidence Information     ✗
```


# Why Multi-Query Retrieval Alone Was Not Enough

The retrieval stage was working correctly.

The required documents were being found.

The problem occurred later in the pipeline.

This demonstrated that:

> A later RAG stage can undo an improvement made by an earlier stage.


# Alternative Considered — Increase Top-N

One possible solution was to increase the number of final chunks.

For example:

```text
Top 3 → Top 5
```

or:

```text
Top 3 → Top 10
```


## Why This Was Not Preferred

Increasing the number of chunks would not guarantee that every intent was represented.

It could also:

- introduce more noise
- increase context size
- send less relevant information to GPT-4.1
- hide the actual retrieval-design problem

Therefore, FoodSafe AI did not solve the issue simply by increasing context size.


# Final Improvement — Intent-Aware Reranking

The architecture was changed so that each retrieval intent was reranked independently.

Instead of:

```text
All Candidates
      ↓
FlashRank Against Original Query
```

FoodSafe AI now uses:

```text
Query 1 Candidates
      ↓
FlashRank Against Query 1

Query 2 Candidates
      ↓
FlashRank Against Query 2

Query 3 Candidates
      ↓
FlashRank Against Query 3
```


# Final Intent-Aware Architecture

The final retrieval pipeline became:

```text
                     User Question
                          ↓
              Deterministic Query Expansion
                          ↓
          ┌───────────────┼───────────────┐
          ↓               ↓               ↓
       Intent 1         Intent 2         Intent 3
       Problem          Complaint        Evidence
          ↓               ↓               ↓
     FAISS + BM25     FAISS + BM25     FAISS + BM25
          ↓               ↓               ↓
      FlashRank        FlashRank        FlashRank
     vs Intent 1      vs Intent 2      vs Intent 3
          ↓               ↓               ↓
      Best Doc         Best Doc         Best Doc
          └───────────────┼───────────────┘
                          ↓
                Best Unique Documents
                          ↓
                    Final Context
                          ↓
              Context + Original Question
                          ↓
                       GPT-4.1
                          ↓
                   Grounded Answer
```


# Best Unique Document Per Intent

After reranking each intent independently, FoodSafe AI selects the best document for that intent.

The selected documents are also deduplicated.

This helps prevent the same document from occupying all available context positions.


## Why This Matters

The final context can now preserve multiple information needs.

For example:

```text
Document 1 → Food-safety problem
Document 2 → Complaint process
Document 3 → Supporting evidence
```


# Intent-Aware Test — Fungus Bread

The short query was tested again:

```text
fungus bread
```


## Intent 1

Query:

```text
fungus bread
```

Hybrid candidates:

```text
8
```

Selected category:

```text
Food Safety Myth Busters
```

Approximate rerank score:

```text
3.267209103796631e-05
```


## Intent 2

Query:

```text
packaged food complaint Food Grievance Portal consumer complaint procedure
```

Hybrid candidates:

```text
7
```

Selected category:

```text
Consumer Complaint Guidance
```

Approximate rerank score:

```text
0.9994555115699768
```


## Intent 3

Query:

```text
supporting document evidence image product bill packaged food complaint
```

Hybrid candidates:

```text
6
```

Selected category:

```text
Consumer Complaint Guidance
```

Approximate rerank score:

```text
0.9716382622718811
```


# Final Selected Categories

The final context now contained:

```text
1. Food Safety Myth Busters
2. Consumer Complaint Guidance
3. Consumer Complaint Guidance
```

This was the intended result.

The food-safety issue and complaint/evidence guidance were now preserved together.


# Why This Solved the Problem

Previously:

```text
All intents
   ↓
Global rerank against "fungus bread"
   ↓
All top results = Myth Busters
```

After the improvement:

```text
Problem intent
   ↓
Rerank against problem query
   ↓
Problem document

Complaint intent
   ↓
Rerank against complaint query
   ↓
Complaint document

Evidence intent
   ↓
Rerank against evidence query
   ↓
Evidence document
```


# Minor Debugging Metadata Issue

During intent-aware testing, a minor debugging issue was observed.

The same LangChain `Document` object could be reused across retrieval queries.

Temporary metadata such as:

```text
retrieval_query
```

could therefore be overwritten during later reranking operations.


## Example

A document selected for the complaint intent could later display the evidence retrieval query in debugging output if the same document object was encountered again.


## Impact

This did not affect:

- the document content
- the official source
- the final retrieval quality
- the GPT-4.1 answer

It affected only temporary debugging metadata.


## Possible Future Cleanup

A future implementation could copy the LangChain `Document` before adding temporary reranking metadata.

This was not required for the buildathon MVP because answer quality was unaffected.


# Integration Problem After Intent-Aware Retrieval

After the new retrieval function was implemented, Streamlit failed to start.

The error was caused by the generation layer still importing the older retrieval interface:

```python
retrieve_and_rerank
```


## Root Cause

The new reranking module exposed:

```python
get_reranked_documents
```

but `advanced_rag_answer.py` still expected the previous function.


## Fix

The generation layer was updated to use:

```python
from rerank_retriever import get_reranked_documents
```


## Context Builder Update

`advanced_rag_answer.py` was also updated so that its context-building function could directly accept the LangChain `Document` objects returned by the new intent-aware retriever.

It could read metadata such as:

```text
rerank_score
retrieval_query
```

while preserving the official source information.


## Streamlit Impact

The Streamlit user interface did not require architectural redesign.

The integration layer was corrected while preserving:

- the existing UI
- conversation memory
- source display
- official links
- answer generation


# Final End-to-End Fungus Test

After integrating intent-aware retrieval into the complete application, the original fungus scenario was tested again.

Question:

> I found fungus in packaged bread before the expiry date. What should I do?


## Final Answer Behaviour

The final answer correctly explained that:

- packaged-food complaints can be lodged through the official FSSAI/FoSCoS grievance mechanism
- relevant proof can be attached
- an image of the product is useful supporting evidence
- the retail bill is useful supporting evidence
- supported image formats include `.jpg`, `.jpeg`, and `.png`
- the complaint can be tracked
- the indexed information did not specifically establish a bread-specific fungus standard


## Important Grounding Behaviour

The answer did not incorrectly apply fungus-related standards from another food category to bread.

Instead, it explicitly acknowledged the limitation.

This prevented an unsupported regulatory generalization.


# Final Fungus Result

Before intent-aware retrieval:

```text
PARTIAL
```

After intent-aware retrieval:

```text
PASS
```


# Improvement Summary

```text
Initial Fungus Test
        ↓
PARTIAL
        ↓
Inspect Corpus
        ↓
FoSCoS FAQ Answers Missing
        ↓
Expand Dynamic Accordions
        ↓
24 Chunks → 30 Chunks
        ↓
Retest
        ↓
Still PARTIAL
        ↓
Targeted Evidence Query
        ↓
Complaint Chunks Retrieved Strongly
        ↓
Corpus Confirmed Correct
        ↓
Multi-Query Expansion
        ↓
Complaint Candidates Retrieved
        ↓
Global Reranking Removes Them
        ↓
Intent-Aware Per-Query Reranking
        ↓
Problem + Complaint + Evidence Preserved
        ↓
GPT-4.1 Grounded Answer
        ↓
PASS
```


# Before → Problem → Improvement → Result

## Before

The advanced pipeline used:

```text
FAISS + BM25
      ↓
Hybrid Candidate Pool
      ↓
Global FlashRank
      ↓
Top 3
```


## Problem

A short multi-intent question could retrieve the required complaint information, but global reranking against the original query removed secondary intents.


## First Improvement

Deterministic multi-query expansion was added.


## First Improvement Result

Recall improved, but global reranking still removed complaint/evidence candidates.


## Final Improvement

Each retrieval intent was reranked independently against its own query.


## Final Result

The final context preserved:

```text
Food Safety Information
        +
Complaint Guidance
        +
Evidence Guidance
```

The fungus test improved:

```text
PARTIAL → PASS
```


# Final Advanced Retrieval Pipeline

At the end of this phase, FoodSafe AI used:

```text
User Question
      ↓
Deterministic Intent-Aware Query Expansion
      ↓
Multiple Retrieval Queries
      ↓
FAISS + BM25 Hybrid Retrieval Per Query
      ↓
FlashRank Per Intent
      ↓
Best Unique Document Per Intent
      ↓
Final Retrieved Context
      ↓
Recent Conversation History
(Reference Resolution Only)
      ↓
Context + Original Question
      ↓
GPT-4.1
      ↓
Grounded Answer
      ↓
Official Source Links
```


# Role of Conversation Memory

Conversation memory was added separately to improve follow-up questions.

For example:

```text
User:
I found worms in the rice packet.

User:
What evidence should I keep?
```

The second question can be understood as referring to the rice-packet problem.


## Important Grounding Rule

Conversation history is not treated as an official factual source.

It is used only to resolve references such as:

- it
- that product
- same issue
- what should I keep?

Factual food-safety guidance must still come from retrieved official FSSAI/FoSCoS context.


# Why Self-RAG Was Not Added

Other advanced RAG approaches were considered, including:

- Self-RAG
- Corrective RAG
- Fusion RAG
- additional retrieval strategies

However, after intent-aware retrieval and grounding improvements, the final application tests were successful.


## Buildathon Decision

Additional RAG complexity was not added simply for the sake of using more techniques.

The project prioritized:

- measurable improvement
- grounded answers
- maintainable architecture
- explainable retrieval
- successful end-to-end testing


# Key Learning — Query Expansion

A short user question may contain more intent than its literal words indicate.

For example:

```text
fungus bread
```

may imply:

```text
What is this problem?
What should I do?
How can I complain?
What evidence should I keep?
```


# Key Learning — Multi-Query Retrieval

Multi-query retrieval can improve recall by searching separately for different information needs.

However:

> Retrieving the right documents is not enough if a later pipeline stage removes them.


# Key Learning — Reranking

Reranking should respect the purpose of the retrieval query that produced the candidate.

Globally reranking all documents against a short original query can over-prioritize one intent.


# Key Learning — Intent Preservation

The final architecture does not merely ask:

> Which three documents are most similar to the original question?

Instead, it also asks:

> Which document best represents each important retrieval intent?


# Key Learning — More Context Is Not Always Better

The solution was not simply to send more chunks to GPT-4.1.

The goal was to send:

> fewer but intentionally selected chunks representing the required information.


# Key Learning — RAG Is a Pipeline

One of the strongest learnings from this phase was:

> An improvement at one stage can be undone by a later stage.

In this case:

```text
Multi-Query Retrieval → Improved Recall

but

Global Reranking → Removed Secondary Intents
```

The final fix required understanding the entire pipeline rather than optimizing one component independently.


# Key Learning — Real User Inputs Matter

Testing only carefully written questions can hide retrieval problems.

Short inputs such as:

```text
fungus bread
worm in rice packet
```

were valuable because they represented how real users may interact with the application.

The final retrieval design became more robust because these vague queries were explicitly tested.


# Final Result

Intent-aware retrieval became the final advanced retrieval strategy for the FoodSafe AI buildathon MVP.

The architecture combined:

- OpenAI query embeddings
- FAISS semantic retrieval
- BM25 keyword retrieval
- reciprocal rank fusion
- deterministic query expansion
- FlashRank
- per-intent reranking
- unique document selection
- GPT-4.1 grounded generation


# Final Outcome

The most important measurable outcome of this phase was:

```text
Fungus Test

Before : PARTIAL
After  : PASS
```

This improvement contributed to the final FoodSafe AI application test result:

```text
PASS    : 8
PARTIAL : 0
FAIL    : 0
```


# Decision

Intent-aware retrieval was frozen as the final retrieval architecture for the FoodSafe AI buildathon MVP.

No additional RAG architecture was added after the final tests passed.


# Next Step

With the retrieval architecture complete, the next phase focused on validating the complete application:

- grounded answers
- complaint guidance
- food recall
- adulteration limitations
- conversational memory
- memory clearing
- official source links
- Streamlit UI

This is documented in:

```text
docs/06_final_application_testing.md
```


# Conclusion

The intent-aware retrieval phase solved the most important remaining retrieval problem in FoodSafe AI.

The required complaint information already existed in the knowledge base, but a short multi-intent question could not preserve that information through global reranking.

Deterministic multi-query expansion improved recall, but testing showed that global reranking could undo that improvement.

The final solution was to rerank each retrieval intent independently and preserve the best unique document for each intent.

This changed the fungus test from:

```text
PARTIAL → PASS
```

and completed the evolution of FoodSafe AI from a basic FAISS RAG pipeline into an intent-aware hybrid retrieval system.