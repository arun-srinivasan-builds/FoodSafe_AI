# FlashRank Reranking Testing

## Objective

Hybrid retrieval improved FoodSafe AI by combining:

- FAISS semantic search
- BM25 keyword search
- reciprocal rank fusion

However, hybrid retrieval could return a relatively large candidate pool containing both strong and weak chunks.

The goal of this phase was to add a second-stage reranker that could select the most relevant chunks before sending context to GPT-4.1.


## Why Reranking Was Needed

Hybrid retrieval improves recall.

Its purpose is to increase the chance that useful information appears somewhere in the candidate pool.

However, not every retrieved candidate should necessarily be included in the final LLM context.

For example, a hybrid search could return approximately seven candidates when only three were needed by GPT-4.1.

Therefore, FoodSafe AI introduced a second stage:

```text
Hybrid Candidates
        ↓
    FlashRank
        ↓
  Top 3 Chunks
        ↓
     GPT-4.1
```


## Why FlashRank Was Chosen

FlashRank provides lightweight local reranking.

It evaluates the relationship between:

- the user query
- each retrieved passage

and produces a relevance score.

This allowed FoodSafe AI to perform reranking locally without requiring another OpenAI generation call.


## Initial Planned Architecture

The advanced retrieval pipeline became:

```text
User Question
      ↓
FAISS Semantic Search
        +
BM25 Keyword Search
      ↓
Reciprocal Rank Fusion
      ↓
Hybrid Candidate Pool
      ↓
FlashRank
      ↓
Top 3 Context Chunks
      ↓
GPT-4.1
```


## First Implementation Problem

The initial implementation attempted to use the LangChain `FlashrankRerank` integration.

This failed with a Pydantic-related error involving the FlashRank `Ranker` type.

Rather than blocking the project on the wrapper integration, the implementation was changed to use FlashRank directly.


## Direct FlashRank Implementation

The direct API used:

```python
from flashrank import Ranker, RerankRequest
```

The hybrid candidate chunks were converted into FlashRank passages.

FlashRank then ranked those passages against the user's question.


## Second Implementation Problem — ONNX Runtime

After moving to direct FlashRank, another technical problem appeared.

ONNX Runtime failed to load because of a Windows DLL dependency issue.

The environment was checked and confirmed to be:

- Python 3.11.9
- 64-bit Python
- AMD64 Windows environment

`onnxruntime==1.20.1` was installed, but the DLL problem remained.


## Root Cause

The Windows system had an older Microsoft Visual C++ runtime installed, but did not have the modern runtime required by the ONNX Runtime package.


## Fix

The official Microsoft Visual C++ 2015–2022 Redistributable (x64) was installed.

After installation, the environment successfully reported:

```text
ONNX Runtime: 1.20.1
FlashRank import successful
```

FlashRank could then be used successfully by FoodSafe AI.


## Reranking Test — Complaint Question

A complaint-related question was tested using the new reranking layer.

The hybrid retriever produced approximately:

```text
7 candidate chunks
```

FlashRank then selected the top three.


## Complaint Reranking Result

The final reranked results included:

1. Food Recall Consumer Information
2. Consumer Complaint Guidance
3. Food Recall

Approximate reranking scores included:

```text
0.0276
0.00514
0.000179
```


## Important Observation

Before FlashRank, hybrid retrieval had ranked the complaint source at:

```text
#1
```

After FlashRank, the same complaint source moved to:

```text
#2
```

Therefore, reranking did not improve this individual ranking.


## Why This Matters

It would be incorrect to claim:

> FlashRank always improves retrieval.

The actual FoodSafe AI testing showed something more useful:

> Reranking can improve final context selection, but its effectiveness depends on the query and candidate set.

This result was preserved rather than hidden.


## Plastic Rice Test

The plastic-rice question produced a much stronger reranking result.

FlashRank placed the direct FSSAI Myth Buster information at the top with an approximate score of:

```text
0.9957
```

This demonstrated that FlashRank could strongly identify a directly relevant chunk when the query and passage aligned well.


## Recall Test

Food-recall testing also produced relevant official recall information after reranking.

This provided additional evidence that the reranker could successfully prioritize useful chunks for some FoodSafe AI use cases.


## Milk Adulteration Test

Milk adulteration remained limited even after reranking.

The main problem was not the reranker.

The indexed adulteration webpage did not contain all of the detailed household testing procedures required for a complete answer.

This reinforced the earlier distinction between:

- retrieval quality
- corpus coverage


## Advanced End-to-End RAG

After FlashRank became operational, the complete advanced RAG pipeline was tested:

```text
User Question
      ↓
FAISS + BM25
      ↓
Reciprocal Rank Fusion
      ↓
FlashRank
      ↓
Top 3 Chunks
      ↓
Context + Original Question
      ↓
GPT-4.1
      ↓
Grounded Answer
```


## Grounding Behaviour

The advanced generation prompt instructed GPT-4.1 to:

- use only retrieved FSSAI/FoSCoS context for factual guidance
- avoid unsupported procedures
- avoid unsupported legal or regulatory interpretations
- distinguish between what the source states and what it does not state
- acknowledge insufficient indexed information
- avoid generalizing standards from one food category to another

This was particularly important for the fungus scenario.

The corpus contained a chocolate standard mentioning fungus, but this could not automatically be treated as a bread standard.


## Result

The advanced pipeline produced useful grounded answers while retaining limitations when the indexed information was insufficient.

This was more important than optimizing a single reranking score.


## Before → Problem → Improvement → Result

### Before

Hybrid retrieval produced a broader candidate pool.

### Problem

Not every hybrid candidate was suitable for inclusion in the final GPT-4.1 context.

### Improvement

FlashRank was introduced as a second-stage reranker.

### Technical Challenges

1. LangChain FlashRank wrapper produced a Pydantic integration error.
2. Direct FlashRank then encountered an ONNX Runtime DLL problem.
3. The Windows runtime dependency was diagnosed and corrected.

### Result

FlashRank became operational and could reduce the hybrid candidate pool to the most relevant context chunks.

Some queries, such as plastic rice, showed very strong reranking.

Other queries demonstrated that reranking does not universally improve every result.


## Key Learning

Retrieval and reranking have different responsibilities.

### Hybrid Retrieval

Optimizes primarily for:

> Finding potentially useful information.

### Reranking

Optimizes primarily for:

> Deciding which retrieved information should be prioritized.

However, a reranker is not automatically correct.

Its output must still be evaluated using real application questions.


## New Limitation Discovered Later

During final fungus testing, a deeper limitation became visible.

The short question:

```text
fungus bread
```

was expanded into multiple retrieval intents including:

1. the original food-safety problem
2. packaged-food complaint guidance
3. supporting-document evidence

The expanded hybrid searches successfully produced a broader candidate pool.

For example:

```text
Retrieval queries:

1. fungus bread
2. packaged food complaint Food Grievance Portal consumer complaint procedure
3. supporting document evidence image product bill packaged food complaint
```

The three searches returned:

```text
Query 1 → 8 candidates
Query 2 → 7 candidates
Query 3 → 6 candidates

Combined candidates before deduplication → 21
Unique candidates after deduplication → 15
```

This proved that multi-query retrieval itself was working.


## Global Reranking Problem

Despite successfully retrieving candidates for all three intents, the combined candidate pool was globally reranked against only the original short query:

```text
fungus bread
```

FlashRank therefore prioritized chunks that contained information closely related to fungus and bread.

The final top three were all:

```text
Food Safety Myth Busters
```

The Consumer Complaint Guidance chunks did not survive into the final GPT-4.1 context.


## Second Vague Query Test

The same behaviour was observed with:

```text
worm in rice packet
```

The retrieval layer correctly generated:

```text
1. worm in rice packet
2. packaged food complaint Food Grievance Portal consumer complaint procedure
3. supporting document evidence image product bill packaged food complaint
```

The combined searches produced:

```text
21 candidates before deduplication
16 unique candidates after deduplication
```

However, after global reranking, all three final results were again:

```text
Food Safety Myth Busters
```


## Significance of the Vague Query Tests

These tests demonstrated that:

> Multi-query retrieval can improve candidate recall while a later global reranking stage can still remove important secondary intents.

The problem was therefore no longer simply:

> Do we have the right document?

It became:

> Are we preserving all of the user's relevant intents through the complete retrieval pipeline?


## Why Increasing Top-N Was Not Chosen

One possible workaround would have been to increase the number of chunks sent to GPT-4.1.

For example:

```text
Top 3 → Top 5 or Top 10
```

This was not selected as the primary solution.

Increasing the context size would not guarantee that each required intent was represented.

It could also introduce additional irrelevant information and increase context noise.


## Decision

FoodSafe AI therefore moved from global reranking to:

> Intent-aware reranking.

Instead of merging every candidate first and asking FlashRank to rank them all against the original short question, each retrieval query would be handled independently.

The new strategy became:

```text
Original Question
      ↓
Intent-Aware Query Expansion
      ↓
Query 1 → Hybrid Retrieval → FlashRank using Query 1
Query 2 → Hybrid Retrieval → FlashRank using Query 2
Query 3 → Hybrid Retrieval → FlashRank using Query 3
      ↓
Select Best Unique Result Per Intent
      ↓
Final Context
      ↓
GPT-4.1
```


## Why Intent-Aware Reranking Was Better

For a vague input such as:

```text
fungus bread
```

FoodSafe AI could preserve different useful information:

```text
Intent 1
Food-safety / fungus information

Intent 2
Packaged-food complaint procedure

Intent 3
Supporting-document evidence
```

This prevented the strongest lexical match for the original short query from eliminating all complaint-related information.


## Transition to Next Improvement

FlashRank itself was retained.

The problem was not that FlashRank was unusable.

The problem was how it was being applied across multiple different retrieval intents.

Therefore, the next improvement reused:

- FAISS
- BM25
- reciprocal rank fusion
- FlashRank

but changed the orchestration around reranking.

The final intent-aware implementation and its successful test results are documented in:

```text
docs/05_intent_aware_retrieval.md
```


## Conclusion

FlashRank provided a useful second-stage ranking mechanism for FoodSafe AI, but testing showed why reranking should be treated as an engineering component rather than a guaranteed improvement.

The project retained FlashRank because it performed strongly for several scenarios and provided a useful ranking layer.

At the same time, actual testing showed two important limitations:

1. reranking did not improve every individual query
2. global reranking could remove secondary intents introduced through multi-query retrieval

Rather than hiding these limitations, FoodSafe AI used them to improve the architecture.

This directly led to the final intent-aware retrieval and reranking strategy.