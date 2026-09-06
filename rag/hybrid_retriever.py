import os

from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever


# ------------------------------------------------------------------
# PROJECT PATHS
# ------------------------------------------------------------------

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

VECTORSTORE_PATH = os.path.join(
    PROJECT_ROOT,
    "vectorstore",
    "faiss_index"
)

ENV_PATH = os.path.join(
    PROJECT_ROOT,
    ".env"
)


# ------------------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# ------------------------------------------------------------------

load_dotenv(ENV_PATH)


# ------------------------------------------------------------------
# LOAD FAISS VECTOR STORE
# ------------------------------------------------------------------

def load_faiss_vectorstore():

    print("Loading OpenAI embedding model...")

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    print("Loading existing FAISS index...")

    vectorstore = FAISS.load_local(
        VECTORSTORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectorstore


# ------------------------------------------------------------------
# GET DOCUMENTS ALREADY STORED INSIDE FAISS
# ------------------------------------------------------------------

def get_faiss_documents(vectorstore):

    """
    Get the exact document chunks that were used
    when the FAISS vector store was built.

    This ensures BM25 and FAISS search the same chunks.
    """

    documents = list(
        vectorstore.docstore._dict.values()
    )

    return documents


# ------------------------------------------------------------------
# CREATE HYBRID RETRIEVER
# ------------------------------------------------------------------

def get_hybrid_retriever():

    print("\nCreating hybrid retriever...")

    # --------------------------------------------------------------
    # STEP 1 - Load existing FAISS
    # --------------------------------------------------------------

    vectorstore = load_faiss_vectorstore()

    # --------------------------------------------------------------
    # STEP 2 - Create FAISS semantic retriever
    # --------------------------------------------------------------

    print("Creating FAISS semantic retriever...")

    faiss_retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 5
        }
    )

    # --------------------------------------------------------------
    # STEP 3 - Get same chunks already indexed in FAISS
    # --------------------------------------------------------------

    documents = get_faiss_documents(vectorstore)

    print(
        f"Total chunks available for hybrid search: "
        f"{len(documents)}"
    )

    # --------------------------------------------------------------
    # STEP 4 - Create BM25 keyword retriever
    # --------------------------------------------------------------

    print("Creating BM25 keyword retriever...")

    bm25_retriever = BM25Retriever.from_documents(
        documents
    )

    bm25_retriever.k = 5

    # --------------------------------------------------------------
    # STEP 5 - Combine FAISS + BM25
    # --------------------------------------------------------------

    print("Combining FAISS + BM25...")

    hybrid_retriever = EnsembleRetriever(
        retrievers=[
            faiss_retriever,
            bm25_retriever
        ],
        weights=[
            0.5,
            0.5
        ]
    )

    print("Hybrid retriever ready.")

    return hybrid_retriever


# ------------------------------------------------------------------
# TEST
# ------------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 75)
    print("FOODSAFE AI - HYBRID RETRIEVER TEST")
    print("=" * 75)

    retriever = get_hybrid_retriever()

    question = input(
        "\nEnter your food safety question: "
    ).strip()

    if not question:

        print("\nPlease enter a valid question.")

    else:

        print("\n" + "=" * 75)
        print("QUESTION")
        print("=" * 75)

        print(question)

        print("\nSearching using FAISS + BM25...")

        documents = retriever.invoke(question)

        print("\n" + "=" * 75)
        print("HYBRID RETRIEVAL RESULTS")
        print("=" * 75)

        for i, doc in enumerate(
            documents,
            start=1
        ):

            print(f"\nRESULT {i}")
            print("-" * 75)

            print(
                "Category:",
                doc.metadata.get(
                    "category",
                    "Unknown"
                )
            )

            print(
                "Title:",
                doc.metadata.get(
                    "title",
                    "Unknown"
                )
            )

            print(
                "Source:",
                doc.metadata.get(
                    "source_url",
                    "Unknown"
                )
            )

            preview = (
                doc.page_content[:500]
                .replace("\n", " ")
            )

            print("\nPreview:")
            print(preview)

        print("\n" + "=" * 75)

        print(
            "Total hybrid results returned:",
            len(documents)
        )

        print("=" * 75)