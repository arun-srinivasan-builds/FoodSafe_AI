from pathlib import Path
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
VECTORSTORE_DIR = BASE_DIR / "vectorstore" / "faiss_index"

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")


# ---------------------------------------------------------
# Load FAISS vector store
# ---------------------------------------------------------
def load_vectorstore():

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    vectorstore = FAISS.load_local(
        str(VECTORSTORE_DIR),
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectorstore


# ---------------------------------------------------------
# Create reusable retriever
# ---------------------------------------------------------
def get_retriever():

    vectorstore = load_vectorstore()

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 3
        }
    )

    return retriever


# ---------------------------------------------------------
# Test retriever interactively
# ---------------------------------------------------------
if __name__ == "__main__":

    print("=" * 70)
    print("FOODSAFE AI - RETRIEVER TEST")
    print("=" * 70)

    # Create retriever
    retriever = get_retriever()

    # Get question from user instead of hard coding it
    question = input(
        "\nEnter your food safety question: "
    ).strip()

    if not question:

        print("\nPlease enter a valid question.")

    else:

        # Retrieve relevant FSSAI chunks
        documents = retriever.invoke(question)

        print("\n" + "=" * 70)
        print("QUESTION")
        print("=" * 70)

        print(question)

        print(
            f"\nRetrieved documents: "
            f"{len(documents)}"
        )

        # Display retrieved documents
        for index, document in enumerate(
            documents,
            start=1
        ):

            print("\n" + "=" * 70)
            print(f"RESULT {index}")
            print("=" * 70)

            print("\nSource:")
            print(
                document.metadata.get(
                    "source",
                    "Unknown"
                )
            )

            print("\nCategory:")
            print(
                document.metadata.get(
                    "category",
                    "Unknown"
                )
            )

            print("\nTitle:")
            print(
                document.metadata.get(
                    "title",
                    "Unknown"
                )
            )

            print("\nSource URL:")
            print(
                document.metadata.get(
                    "source_url",
                    ""
                )
            )

            print("\nContent:")
            print(
                document.page_content
            )

        print("\n" + "=" * 70)
        print("RETRIEVER TEST COMPLETED")
        print("=" * 70)