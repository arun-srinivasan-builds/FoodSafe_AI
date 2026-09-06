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

▶️ **[Watch the FoodSafe AI Demo](https://github.com/arun-srinivasan-builds/FoodSafe_AI/blob/6d040afb2f50b6c5d6e3b853344ef433fc6da493/assets/demo/foodsafe_ai_demo.mp4)**

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

## ▶️ Run the Application

FoodSafe AI can be run locally using the processed FSSAI/FoSCoS knowledge base included in this repository.

### 1. Clone the Repository

```bash
git clone https://github.com/arun-srinivasan-builds/FoodSafe_AI.git
cd FoodSafe_AI
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**macOS / Linux**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Your OpenAI API Key

Create a file named `.env` in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
```

Replace `your_openai_api_key` with your own OpenAI API key.

> **Security:** Never commit your API key to GitHub. The `.env` file is excluded from this repository through `.gitignore`.

### 5. Build the FAISS Vector Store

The processed FSSAI/FoSCoS knowledge base required by the application is already included in:

```text
data/fssai_documents.json
```

Build the local FAISS vector index:

```bash
python rag/build_vectorstore.py
```

This performs:

**Load Documents → Split into Chunks → Create OpenAI Embeddings → Build FAISS Index**

The generated index is stored under:

```text
vectorstore/faiss_index/
```

The `vectorstore/` directory is intentionally excluded from Git because it can be regenerated locally from the included source data.

### 6. Launch FoodSafe AI

```bash
streamlit run foodsafe_ai_app.py
```

Streamlit will start the application and provide a local browser URL.

### Optional: Refresh the FSSAI/FoSCoS Knowledge Base

The repository already contains the processed data needed to run the application, so **Playwright is not required for normal application startup**.

If you want to re-scrape the official FSSAI/FoSCoS sources, first install the Playwright Chromium browser:

```bash
playwright install chromium
```

Then run the scraper:

```bash
python scraper/scrape_fssai.py
```

After refreshing the source data, rebuild the FAISS vector store before launching the application again:

```bash
python rag/build_vectorstore.py
```

### Quick Start Summary

```text
Clone Repository
      ↓
Create & Activate Virtual Environment
      ↓
pip install -r requirements.txt
      ↓
Create .env with your own OPENAI_API_KEY
      ↓
python rag/build_vectorstore.py
      ↓
streamlit run foodsafe_ai_app.py
      ↓
FoodSafe AI
```

> **Note:** `.env` and the locally generated FAISS vector store are excluded from the Git repository.

---

## ⚠️ Disclaimer

FoodSafe AI is a **learning and demonstration project** and is not an official FSSAI application.

The application is designed to retrieve and explain information from indexed official sources. Users should refer to the official **FSSAI/FoSCoS platforms** for authoritative and current regulatory guidance.

> **Project maturity:** FoodSafe AI is a production-style RAG prototype. Automated knowledge-base refresh, monitoring, deployment, security hardening, and continuous evaluation are future productionization enhancements.
---

### 📖 Suggested Reading Path

**[Problem Statement](docs/problem_statement.md) → [Architecture & Design](docs/00_architecture_and_design.md) → [LangChain & RAG Concepts](docs/07_langchain_rag_concepts.md) → [Final Application Testing](docs/06_final_application_testing.md)**
