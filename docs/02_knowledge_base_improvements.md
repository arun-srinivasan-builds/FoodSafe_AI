# Knowledge Base Improvements

## Objective

The initial FoodSafe AI RAG pipeline was able to retrieve information from official FSSAI sources.

However, baseline testing showed that retrieval quality depends heavily on the quality, relevance, and completeness of the indexed knowledge base.

The objective of this phase was to improve:

- source coverage
- source authenticity
- document structure
- metadata
- text cleaning
- chunk quality
- complaint guidance coverage
- adulteration guidance coverage

before making more advanced retrieval changes.


## Initial Knowledge Base

The early version of FoodSafe AI used a small set of FSSAI webpages.

The initial pipeline was:

```text
FSSAI Website
      ↓
Playwright Scraper
      ↓
Raw Text
      ↓
LangChain Documents
      ↓
Text Splitting
      ↓
OpenAI Embeddings
      ↓
FAISS
```


## Problems Identified in the Initial Corpus

Testing revealed several knowledge-base problems.

These included:

- limited source coverage
- generic FSSAI pages
- navigation and footer noise
- repeated information
- insufficient adulteration guidance
- insufficient complaint guidance
- some important webpage content not captured by the scraper

This demonstrated an important RAG principle:

> A good LLM cannot retrieve information that is missing from the indexed knowledge base.


## Authentic Source Strategy

FoodSafe AI was designed to use only authentic official sources.

The knowledge base therefore uses information from the official:

- FSSAI website
- FoSCoS ecosystem

Random blogs, review websites, social-media posts, and unofficial food-safety websites were intentionally excluded.


## Why Authentic Sources Matter

FoodSafe AI provides guidance related to:

- unsafe food
- packaged food
- adulteration
- food myths
- food recalls
- consumer complaints

These topics require reliable information.

Therefore, retrieved factual guidance should come from official FSSAI/FoSCoS sources rather than general internet information.


## Final Source Categories

The knowledge base was expanded to six targeted official source categories:

1. Food Recall
2. Food Recall Consumer Information
3. Consumer Complaint Guidance
4. Food Safety Myth Busters
5. FSSAI Knowledge Hub
6. Check Adulteration at Home


## Official Source URLs

The Playwright scraper used the following official sources:

```python
URLS = [
    {
        "category": "Food Recall",
        "url": "https://fssai.gov.in/food-law/food-recall"
    },
    {
        "category": "Food Recall Consumer Information",
        "url": "https://fssai.gov.in/citizen/about-food-recall"
    },
    {
        "category": "Consumer Complaint Guidance",
        "url": "https://foscos.fssai.gov.in/consumergrievance/faqs"
    },
    {
        "category": "Food Safety Myth Busters",
        "url": "https://fssai.gov.in/myth-buster"
    },
    {
        "category": "FSSAI Knowledge Hub",
        "url": "https://fssai.gov.in/knowledge-hub?tab=books"
    },
    {
        "category": "Check Adulteration at Home",
        "url": "https://fssai.gov.in/citizen/about-check-adulteration"
    }
]
```


## Removing Low-Value Content

The initial corpus contained generic information and website navigation/footer text.

This created unnecessary noise for retrieval.

The scraper and cleaning process were improved to focus on useful page content.

The generic homepage was also removed from the targeted source set.


## Why Cleaning Matters

A RAG system searches the chunks stored in the vector database.

If navigation text, footer text, repeated labels, and unrelated website content are stored as chunks, they can compete with useful food-safety information during retrieval.

Therefore:

```text
Cleaner Documents
      ↓
Cleaner Chunks
      ↓
Better Retrieval Candidates
```


## Structured LangChain Documents

Instead of treating all scraped information as one large text file, each official webpage was represented as a LangChain `Document`.

Each document contained:

```text
page_content
+
metadata
```


## Metadata Improvements

Per-source metadata was added to improve traceability.

The metadata fields included:

```text
source
category
title
source_url
scraped_at
data_type
```


## Why Metadata Was Important

Metadata allowed FoodSafe AI to preserve the origin of every retrieved chunk.

This was useful for:

- identifying which official source produced an answer
- displaying official source links in Streamlit
- debugging retrieval
- comparing retrieval results
- verifying grounding
- deduplicating source references


## Chunking Strategy

The cleaned LangChain Documents were divided into smaller chunks using `RecursiveCharacterTextSplitter`.

The configuration used:

```text
chunk_size    = 750 characters
chunk_overlap = 100 characters
```


## Recursive Separators

The splitter used:

```python
[
    "\n\n",
    "\n",
    ". ",
    " ",
    ""
]
```

This allows LangChain to try to split at more natural boundaries before falling back to smaller separators.


## Why Chunking Was Required

Embedding an entire webpage as one document would make retrieval too broad.

Smaller chunks allow FAISS to retrieve the specific section most relevant to the user's question.

Conceptually:

```text
Large Official Page
      ↓
Smaller Meaningful Chunks
      ↓
Embeddings
      ↓
FAISS Search
```


## Why Chunk Overlap Was Used

A `100` character overlap was retained between neighboring chunks.

This helps preserve context when important information appears near a chunk boundary.

However, baseline testing also showed a trade-off:

> Overlap can cause similar or repeated chunks to appear in retrieval results.

This became one of the later motivations for improving retrieval and reranking.


## Initial Retrieval Improvement

After expanding the corpus and improving cleaning, questions such as the plastic-rice myth and fungus-related queries retrieved more targeted FSSAI information.

For example, fungus-related retrieval began finding the relevant FSSAI Myth Buster content more strongly.

However, one weak result could still appear among the retrieved chunks.

This demonstrated that corpus improvement alone would not solve every retrieval-ranking problem.


# Milk Adulteration Knowledge Gap


## Baseline Problem

One of the five baseline evaluation questions was:

> How can I check whether milk is adulterated?

This was the weakest baseline scenario.

The initial knowledge base did not contain enough detailed adulteration information to answer the question completely.


## Initial Classification

The milk adulteration question was classified approximately as:

```text
Weak
```

The issue was primarily:

> corpus coverage

rather than GPT-4.1 generation quality.


## Investigation of Official DART Material

FSSAI publishes consumer material related to detecting adulteration.

An important official resource identified during investigation was the DART material:

```text
Detect Adulteration with Rapid Test
```

The indexed FSSAI PDF URL was:

```text
https://fssai.gov.in/upload/knowledge_hub/1878035b34b558a3b48DART%20Book.pdf
```

This material contains numerous household-level rapid tests for food adulteration.


## Attempted Direct PDF Ingestion

The initial plan was to download the DART PDF directly using Python and process it as part of the RAG corpus.

However, direct Python requests did not return normal PDF bytes.


## PDF Download Problem

Instead of receiving the actual PDF, the Python request returned approximately:

```text
3,221 bytes
```

The returned content was HTML rather than a valid PDF document.

Therefore, the PDF loader could not process it as expected.


## Investigation of the Older DART Page

The older FSSAI book page was also investigated:

```text
https://www.fssai.gov.in/book-details.php?bkid=201
```

The page itself loaded successfully.

However, Playwright did not find a usable direct `.pdf` link from that page.


## Alternative PDF Test

Another official FSSAI PDF was tested to determine whether the issue was specific to DART.

The Eat Right Handbook URL was:

```text
https://fssai.gov.in/upload/EATRIGHTINDIA/PDF/English%20Eat%20Right%20Handbook_ENGLISH.pdf
```

Direct Python access again returned approximately:

```text
3,221-byte HTML wrapper
```

rather than the expected PDF content.


## Conclusion from PDF Investigation

The issue was not simply a broken DART URL.

The FSSAI website delivery behaviour meant that some publicly indexed PDF URLs did not behave like direct downloadable PDF files when accessed programmatically using the attempted Python method.


## Decision

Rather than spending excessive project time bypassing the website behaviour, FoodSafe AI adapted the ingestion strategy.

An official FSSAI webpage was added instead:

```text
https://fssai.gov.in/citizen/about-check-adulteration
```

Category:

```text
Check Adulteration at Home
```


## Why This Was a Better Buildathon Decision

The goal of FoodSafe AI was to build a working, grounded RAG application.

The project therefore prioritized:

- authentic FSSAI information
- reliable ingestion
- reproducible scraping
- useful consumer guidance

rather than forcing an unreliable PDF ingestion method.


## Milk Test Result After Corpus Expansion

After adding the official Check Adulteration at Home source and rebuilding the FAISS index, milk adulteration retrieval improved.

The result changed approximately from:

```text
Weak
  ↓
Partial
```


## Why Milk Did Not Become Fully Detailed

The official webpage confirmed that FSSAI provides adulteration checking resources, but the scraped page itself did not contain all detailed household milk-test procedures.

Therefore, GPT-4.1 was instructed not to invent procedures that were not present in the retrieved context.

This was considered correct grounded behaviour.


# Consumer Complaint Knowledge Gap


## Complaint Guidance Source

FoodSafe AI used the official FoSCoS consumer grievance FAQ:

```text
https://foscos.fssai.gov.in/consumergrievance/faqs
```

This source was intended to support questions such as:

- How do I complain about unsafe packaged food?
- What evidence should I keep?
- Can I track my complaint?
- What supporting documents should I upload?


## Initial Scraping Problem

The scraper successfully loaded the FoSCoS FAQ page.

However, inspection of `fssai_documents.json` revealed that only the FAQ question headings had been captured.

The actual answers were missing.


## Root Cause

The FoSCoS FAQ uses expandable/collapsible accordion elements.

The answers are not all exposed through the initial basic visible-text extraction.

Conceptually:

```text
FAQ Question
   ↓
Collapsed Answer
   ↓
Basic Extraction
   ↓
Question Captured
Answer Missing
```


## Why This Was Important

At first glance, the complaint page appeared to be successfully indexed because the FAQ headings were present.

However, the actual guidance required by the RAG system was not available.

For example, FoodSafe AI needed information about:

- what types of complaints can be lodged
- supporting documents
- product images
- retail bills
- complaint tracking

Those details existed on the official webpage but had not entered the RAG corpus.


## Diagnosis

This demonstrated an important ingestion lesson:

> Successfully scraping a webpage does not necessarily mean that all important webpage content has been captured.

Dynamic webpage elements must be tested separately.


## Playwright Accordion Fix

The Playwright scraper was enhanced with logic to expand the FoSCoS FAQ sections before extracting the page text.

A dedicated function was added:

```python
expand_foscos_faqs(page)
```


## Accordion Expansion Strategy

The scraper attempted to click the known FAQ questions and also included fallback selectors for common accordion structures such as:

```text
.panel-heading
.panel-title
.accordion-header
.accordion-button
.card-header
[data-toggle='collapse']
[data-bs-toggle='collapse']
```

After expansion, the scraper waited for the content to become available before extracting the body text.


## Result After Scraper Fix

The FoSCoS document now contained the actual FAQ answers rather than only the headings.

Important official information captured included guidance that complaints can relate to:

- Packaged Food
- Food Premises
- Online Aggregator / Food Delivery platforms


## Complaint Registration Information Captured

The expanded FAQ also provided information about the complaint registration process.

This included using the grievance platform and registering a new complaint.


## Supporting Document Information Captured

One of the most important improvements was capturing the official supporting-document guidance.

The FoSCoS FAQ advises consumers to attach relevant proof such as:

- image of the product
- bill received from the retail shop

The FAQ also identifies supported image formats including:

```text
.jpg
.jpeg
.png
```


## Complaint Tracking Information Captured

The expanded FAQ also provided information about tracking the complaint online and described the complaint-resolution flow.


## Corpus Growth

After expanding the FoSCoS FAQ content and rebuilding the FAISS index, the number of indexed chunks increased from:

```text
24 chunks
```

to:

```text
30 chunks
```


## Before → Problem → Improvement → Result

### Before

The FoSCoS complaint webpage was included in the source list.

### Problem

Only FAQ headings were captured because the answers were inside collapsed accordion sections.

### Improvement

Playwright was enhanced to interact with and expand the FAQ elements before text extraction.

### Result

The knowledge base gained the actual official complaint guidance.

The indexed corpus increased:

```text
24 chunks → 30 chunks
```


# Fungus Test After Knowledge Base Improvement


## Expected Improvement

After the complaint FAQ answers were successfully indexed, the fungus-in-packaged-bread test was run again.

The expectation was that the answer could now combine:

- fungus-related food-safety information
- packaged-food complaint guidance
- supporting-document evidence


## Unexpected Result

Despite the improved corpus, the final fungus test remained:

```text
PARTIAL
```

The final reranked top three chunks were still all from:

```text
Food Safety Myth Busters
```

The newly indexed complaint guidance was not reaching the final GPT-4.1 context.


## Important Diagnostic Question

To determine whether complaint data was actually available, a targeted question was tested:

> What evidence should I keep when making a complaint about packaged food?


## Diagnostic Result

For the targeted evidence question, the final top results were all from:

```text
Consumer Complaint Guidance
```

The top reranking scores were approximately:

```text
0.9596
0.9587
```


## What the Diagnostic Test Proved

The diagnostic test proved that:

- the FoSCoS answers had been scraped successfully
- the complaint chunks existed in the corpus
- the FAISS index contained them
- hybrid retrieval could find them
- FlashRank could rank them strongly

Therefore, the remaining fungus problem was no longer a missing-data problem.


## Two Different Problems Identified

This phase produced an important distinction.

### Before the Accordion Fix

The problem was:

```text
Knowledge Coverage Problem
```

The required complaint answers were not present in the indexed corpus.


### After the Accordion Fix

The problem became:

```text
Retrieval Intent Problem
```

The complaint information existed, but the fungus question did not preserve the complaint/evidence intent strongly enough through the complete retrieval pipeline.


## Why Adding More Documents Was Not the Answer

At this point, adding more documents would not necessarily solve the fungus test.

The required official complaint information was already available.

The system needed a better way to retrieve information for multiple user intents.


## Key RAG Learning

This produced one of the most important lessons from the FoodSafe AI build:

> More data does not automatically mean better RAG.

A RAG failure can occur at several different stages:

```text
Source
  ↓
Scraping
  ↓
Cleaning
  ↓
Chunking
  ↓
Embedding / Indexing
  ↓
Retrieval
  ↓
Reranking
  ↓
Generation
```

The correct fix depends on identifying where the failure occurs.


## Knowledge Base Diagnosis Framework

The FoodSafe AI testing process evolved into the following diagnostic approach:

### Question 1

Does the official source contain the required information?

If no:

```text
Source / Corpus Coverage Problem
```

### Question 2

Did the scraper capture the information?

If no:

```text
Ingestion Problem
```

### Question 3

Does the indexed corpus contain the relevant chunk?

If no:

```text
Chunking / Indexing Problem
```

### Question 4

Can a targeted query retrieve the chunk?

If yes, but the real user question cannot:

```text
Retrieval / Intent Problem
```

### Question 5

Is the right chunk retrieved but removed later?

If yes:

```text
Reranking Problem
```

### Question 6

Does GPT-4.1 receive the correct context but still provide unsupported information?

If yes:

```text
Generation / Grounding Problem
```


## Before → Problem → Improvement → Result Summary

### Stage 1 — Initial Corpus

```text
Problem:
Limited source coverage and noisy generic content

Improvement:
Added targeted official FSSAI/FoSCoS sources and improved cleaning

Result:
More relevant retrieval
```


### Stage 2 — Milk Adulteration

```text
Problem:
Insufficient adulteration guidance

Attempt:
Direct FSSAI PDF ingestion

Problem:
PDF URLs returned HTML wrappers to Python

Improvement:
Added official Check Adulteration at Home webpage through Playwright

Result:
Milk test improved from Weak → Partial
```


### Stage 3 — Complaint Guidance

```text
Problem:
FoSCoS FAQ questions indexed but answers missing

Diagnosis:
Answers hidden inside dynamic accordion elements

Improvement:
Enhanced Playwright to expand FAQ sections before extraction

Result:
Actual official complaint guidance indexed
24 chunks → 30 chunks
```


### Stage 4 — Fungus Retest

```text
Problem:
Fungus test still PARTIAL

Diagnosis:
Targeted evidence query retrieved complaint chunks strongly

Conclusion:
Knowledge base was now sufficient
Remaining issue was retrieval intent
```


## Important Engineering Lesson

The knowledge-base phase demonstrated that RAG development should not follow:

```text
Bad Answer
   ↓
Add More Documents
```

Instead, FoodSafe AI used:

```text
Bad Answer
   ↓
Inspect Retrieved Context
   ↓
Check Official Source
   ↓
Check Scraped Data
   ↓
Check Indexed Chunks
   ↓
Run Targeted Retrieval Test
   ↓
Identify Exact Failure Stage
   ↓
Apply Focused Fix
```


## Authenticity and Grounding Principle

Even when the indexed source was incomplete, FoodSafe AI did not use unsupported outside knowledge to fill the gap.

The generation layer was designed to state a limitation when the indexed official information was insufficient.

For example:

> I could not fully verify this from the FSSAI information currently indexed.

This helped maintain the project's official-source-only grounding strategy.


## Final Knowledge Base Status

At the end of this phase:

```text
Official source pages        : 6
Indexed chunks               : 30
Source metadata              : Added
Navigation/footer noise      : Reduced
Complaint FAQ answers        : Captured
Adulteration source          : Added
FAISS index                  : Rebuilt
Authentic-source strategy    : Preserved
```


## Decision

The knowledge base was considered sufficient for the buildathon MVP.

The remaining problems were increasingly related to retrieval quality rather than missing official data.

Therefore, the next development focus moved from:

```text
Knowledge Base Expansion
```

to:

```text
Retrieval Improvement
```


## Next Improvement

The next step was to combine:

```text
FAISS Semantic Search
        +
BM25 Keyword Search
```

using hybrid retrieval.

This is documented in:

```text
docs/03_hybrid_retrieval_testing.md
```


## Key Learnings

1. **RAG quality depends on corpus quality.**  
   GPT-4.1 cannot retrieve information that was never indexed.

2. **Official source availability does not guarantee successful ingestion.**  
   Dynamic accordions and PDF delivery behaviour required different ingestion strategies.

3. **Playwright was valuable for dynamic official webpages.**  
   It allowed FoodSafe AI to interact with FoSCoS FAQ elements before extracting content.

4. **More documents do not automatically produce better answers.**  
   After the complaint information was indexed, retrieval still had to be improved.

5. **Failures should be diagnosed by pipeline stage.**  
   Corpus, ingestion, retrieval, reranking, and generation problems require different fixes.

6. **Grounding is more important than pretending to have a complete answer.**  
   When official indexed information was insufficient, FoodSafe AI preserved the limitation rather than inventing guidance.


## Conclusion

The FoodSafe AI knowledge base evolved from a small collection of official webpages into a more structured and targeted FSSAI/FoSCoS corpus.

The project improved source selection, cleaning, metadata, chunking, adulteration coverage, and complaint guidance.

Two important ingestion challenges were discovered and addressed:

- FSSAI PDF URLs returning HTML wrappers during direct Python access
- FoSCoS FAQ answers being hidden inside dynamic accordion elements

The FoSCoS scraper improvement increased the corpus from 24 to 30 chunks and successfully added official complaint and supporting-document guidance.

However, the fungus test remaining partial after this improvement demonstrated that knowledge-base expansion alone was not enough.

That finding directly motivated the next phase of FoodSafe AI:

> improving retrieval using FAISS + BM25 hybrid search.