from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from split_documents import split_fssai_documents


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
VECTORSTORE_DIR = BASE_DIR / "vectorstore" / "faiss_index"

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")


def build_vectorstore():

    print("=" * 70)
    print("BUILDING FOODSAFE AI VECTOR STORE")
    print("=" * 70)

    # -----------------------------------------------------
    # Step 1: Get the chunks created in Step 7
    # -----------------------------------------------------
    chunks = split_fssai_documents()

    print(f"\nChunks received: {len(chunks)}")

    # -----------------------------------------------------
    # Step 2: Create OpenAI embedding model
    # -----------------------------------------------------
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    print("\nEmbedding model: text-embedding-3-small")
    print("Creating embeddings...")

    # -----------------------------------------------------
    # Step 3: Convert chunks to embeddings and store in FAISS
    # -----------------------------------------------------
    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    print("Embeddings created successfully.")

    # -----------------------------------------------------
    # Step 4: Save FAISS index locally
    # -----------------------------------------------------
    VECTORSTORE_DIR.parent.mkdir(parents=True, exist_ok=True)

    vectorstore.save_local(str(VECTORSTORE_DIR))

    print("\nFAISS vector store created successfully.")
    print(f"Saved to: {VECTORSTORE_DIR}")

    return vectorstore


if __name__ == "__main__":
    build_vectorstore()