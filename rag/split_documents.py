from load_documents import load_fssai_documents
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_fssai_documents():
    documents = load_fssai_documents()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=750,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = text_splitter.split_documents(documents)

    return chunks


if __name__ == "__main__":
    chunks = split_fssai_documents()

    print("=" * 70)
    print("TEXT SPLITTING COMPLETED")
    print("=" * 70)

    print(f"\nTotal chunks created: {len(chunks)}")

    print("\nFirst 3 chunks:")
    print("=" * 70)

    for index, chunk in enumerate(chunks[:3], start=1):
        print(f"\nCHUNK {index}")
        print("-" * 70)

        print("Metadata:")
        print(chunk.metadata)

        print("\nContent:")
        print(chunk.page_content)

        print("\nCharacter count:", len(chunk.page_content))