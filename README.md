# 🥗 FoodSafe AI

### Grounded Generative AI Assistant for FSSAI Food-Safety Guidance

FoodSafe AI is a **Retrieval-Augmented Generation (RAG)** application that helps users find and understand food-safety information from authentic **FSSAI and FoSCoS sources**.

Instead of relying only on an LLM's internal knowledge, FoodSafe AI retrieves relevant official information and provides it as context to **GPT-4.1** to generate grounded answers with source transparency.

---

## 🎯 Problem

Official food-safety guidance is available across FSSAI and FoSCoS resources, but users may need to search and interpret multiple sources to find information relevant to their situation.

**FoodSafe AI explores how RAG can make this official information easier to discover and understand while keeping AI-generated answers grounded in retrieved sources.**

➡️ [Read the complete Problem Statement](docs/problem_statement.md)

---

## 📸 Application Preview

### Home Page

![Alt text](https://github.com/arun-srinivasan-builds/FoodSafe_AI/blob/93b1358b6a9695aa66eec6ab32a14eeb80928c7b/assets/foodsafe_ai_home.png)


### Grounded Answer with Official Sources

![Alt text](https://github.com/arun-srinivasan-builds/FoodSafe_AI/blob/93b1358b6a9695aa66eec6ab32a14eeb80928c7b/assets/foodsafe_ai_answer.png)


---

## 🎬 Application Demo

## 🎬 Application Demo

The demo below shows FoodSafe AI working end-to-end — from a consumer food-safety question to a grounded response based on official FSSAI and FoSCoS information.

The demonstration includes:

- Asking ready-made and free-text food-safety questions
- Hybrid retrieval using **FAISS semantic search + BM25 keyword search**
- **FlashRank reranking** to prioritize the most relevant retrieved information
- **GPT-4.1** generating answers using the retrieved official context
- Official source references for transparency and verification
- Session-based conversational memory for follow-up questions
- Knowledge-boundary handling for questions outside the application's food-safety scope

▶️ **[Watch the FoodSafe AI Demo](assets/demo/foodsafe_ai_demo.mp4)**

**Demo duration:** ~1 minute 51 seconds

---

## 🧪 Final Application Testing

**8 functional scenarios tested — 🟢 8 Passed | 🟡 0 Partial | 🔴 0 Failed**

FoodSafe AI was validated across **food myths, unsafe packaged food, complaints, food recalls, adulteration, conversational memory, memory clearing, and official source verification**.

➡️ [View Final Test Results](test_results/final_test_results.md)

---

## 💡 What FoodSafe AI Does

Users can ask natural-language questions about:

- Food-safety problems
- Food adulteration and food myths
- Food recalls
- Consumer complaint guidance

FoodSafe AI retrieves relevant information from its indexed official-source knowledge base, selects supporting context, and uses **GPT-4.1** to generate a grounded response.

When sufficient supporting information is unavailable, the application clearly communicates that limitation rather than inventing an answer.

---

## 📚 Explore the Project

Detailed documentation captures the complete RAG engineering and testing journey.

| Topic | Documentation |
|---|---|
| 🎯 Problem Statement | [Problem Statement](docs/problem_statement.md) |
| 🏗️ Architecture & Design | [Architecture & Design](docs/00_architecture_and_design.md) |
| 🧩 LangChain & RAG Concepts | [LangChain & RAG Concepts](docs/07_langchain_rag_concepts.md) |
| 🧪 Baseline RAG | [Baseline RAG Testing](docs/01_baseline_rag_testing.md) |
| 📚 Knowledge Base | [Knowledge Base Improvements](docs/02_knowledge_base_improvements.md) |
| 🔎 Hybrid Retrieval | [FAISS + BM25 Testing](docs/03_hybrid_retrieval_testing.md) |
| 🎯 Reranking | [FlashRank Reranking Testing](docs/04_reranking_testing.md) |
| 🧠 Intent-Aware Retrieval | [Intent-Aware Retrieval](docs/05_intent_aware_retrieval.md) |
| ✅ Final Testing | [Final Application Testing](docs/06_final_application_testing.md) |
| 📊 Test Evidence | [Final Test Results](test_results/final_test_results.md) |

---

## 🛠️ Technology Stack

| Technology | Role |
|---|---|
| **Python** | Application development |
| **Playwright + BeautifulSoup** | Official-source data collection |
| **LangChain** | RAG framework and component integration |
| **OpenAI `text-embedding-3-small`** | Text embeddings |
| **FAISS** | Semantic vector retrieval |
| **BM25** | Keyword retrieval |
| **LangChain EnsembleRetriever** | Hybrid retrieval |
| **FlashRank** | Retrieved-document reranking |
| **GPT-4.1** | Grounded answer generation |
| **Streamlit** | Web application interface |

---

## 🔄 RAG Flow

```text
User Question
      ↓
Intent-Aware Query Expansion
      ↓
FAISS Semantic Search + BM25 Keyword Search
      ↓
Hybrid Retrieval
      ↓
FlashRank Reranking
      ↓
Relevant Official FSSAI / FoSCoS Context
      ↓
Context + Original Question
      ↓
GPT-4.1
      ↓
Grounded Answer + Official Sources
```

➡️ [Explore the complete Architecture & Design](docs/00_architecture_and_design.md)

➡️ [Understand the LangChain & RAG Concepts](docs/07_langchain_rag_concepts.md)

---

## ▶️ Run the Application

Ensure the required Python packages are installed and your OpenAI API key is configured in the local `.env` file.

From the project root, run:

```bash
streamlit run foodsafe_ai_app.py
```

The FoodSafe AI application will open in your browser.

> **Note:** `.env` and the locally generated FAISS vector store are excluded from the Git repository.

---

## ⚠️ Disclaimer

FoodSafe AI is a **learning and demonstration project** and is not an official FSSAI application.

The application is designed to retrieve and explain information from indexed official sources. Users should refer to the official **FSSAI/FoSCoS platforms** for authoritative and current regulatory guidance.

> **Project maturity:** FoodSafe AI is a production-style RAG prototype. Automated knowledge-base refresh, monitoring, deployment, security hardening, and continuous evaluation are future productionization enhancements.
---

### 📖 Suggested Reading Path

**[Problem Statement](docs/problem_statement.md) → [Architecture & Design](docs/00_architecture_and_design.md) → [LangChain & RAG Concepts](docs/07_langchain_rag_concepts.md) → [Final Application Testing](docs/06_final_application_testing.md)**
