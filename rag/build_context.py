from retriever import get_retriever


# ---------------------------------------------------------
# Build context from retrieved FSSAI documents
# ---------------------------------------------------------
def build_context(question):

    # Get the reusable FAISS retriever
    retriever = get_retriever()

    # Retrieve relevant documents for the user question
    documents = retriever.invoke(question)

    context_parts = []

    # -----------------------------------------------------
    # Convert each retrieved LangChain Document
    # into a readable context block
    # -----------------------------------------------------
    for index, document in enumerate(
        documents,
        start=1
    ):

        category = document.metadata.get(
            "category",
            "Unknown"
        )

        title = document.metadata.get(
            "title",
            "Unknown"
        )

        source_url = document.metadata.get(
            "source_url",
            ""
        )

        content = document.page_content

        context_part = f"""
SOURCE {index}

Category:
{category}

Title:
{title}

Official Source:
{source_url}

Content:
{content}
"""

        context_parts.append(context_part)

    # Combine all retrieved chunks
    context = "\n".join(context_parts)

    return context, documents


# ---------------------------------------------------------
# Interactive test
# ---------------------------------------------------------
if __name__ == "__main__":

    print("=" * 70)
    print("FOODSAFE AI - CONTEXT BUILD TEST")
    print("=" * 70)

    # User enters a question
    question = input(
        "\nEnter your food safety question: "
    ).strip()

    if not question:

        print(
            "\nPlease enter a valid question."
        )

    else:

        # Build context from retrieved FSSAI documents
        context, documents = build_context(
            question
        )

        print("\n" + "=" * 70)
        print("ORIGINAL USER QUESTION")
        print("=" * 70)

        print(question)

        print("\n" + "=" * 70)
        print("RETRIEVED FSSAI CONTEXT")
        print("=" * 70)

        print(context)

        print("\n" + "=" * 70)
        print("CONTEXT BUILD COMPLETED")
        print("=" * 70)

        print(
            f"\nDocuments used: "
            f"{len(documents)}"
        )

        print(
            f"Total context characters: "
            f"{len(context):,}"
        )