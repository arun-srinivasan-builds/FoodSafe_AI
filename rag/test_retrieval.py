from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

BASE_DIR = Path(__file__).resolve().parent.parent
VECTORSTORE_DIR = BASE_DIR / "vectorstore" / "faiss_index"

load_dotenv(BASE_DIR / ".env")


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


def test_search(question):
    vectorstore = load_vectorstore()

    print("=" * 70)
    print("FOODSAFE AI - FAISS RETRIEVAL TEST")
    print("=" * 70)

    print(f"\nQuestion:\n{question}")

    results = vectorstore.similarity_search(
        question,
        k=3
    )

    print(f"\nRetrieved documents: {len(results)}")

    for index, document in enumerate(results, start=1):
        print("\n" + "=" * 70)
        print(f"RESULT {index}")
        print("=" * 70)

        print("\nMetadata:")
        print(document.metadata)

        print("\nRetrieved content:")
        print(document.page_content)


if __name__ == "__main__":
    test_question = "What should I do if I find fungus in packaged food?"

    test_search(test_question)