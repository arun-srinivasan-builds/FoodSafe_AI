from rag_answer import generate_answer


# ---------------------------------------------------------
# Baseline RAG test questions
# ---------------------------------------------------------
TEST_QUESTIONS = [

    "Is plastic rice real?",

    "What should I do if I find fungus in packaged food?",

    "How can I complain about unsafe packaged food?",

    "How do I know if a food product has been recalled?",

    "How can I check whether milk is adulterated?"
]


# ---------------------------------------------------------
# Run baseline RAG tests
# ---------------------------------------------------------
def run_baseline_tests():

    print("=" * 80)
    print("FOODSAFE AI - BASELINE RAG TEST")
    print("=" * 80)

    print(
        f"\nTotal test questions: "
        f"{len(TEST_QUESTIONS)}"
    )

    for test_number, question in enumerate(
        TEST_QUESTIONS,
        start=1
    ):

        print("\n" + "=" * 80)
        print(
            f"TEST {test_number}"
        )
        print("=" * 80)

        print("\nQUESTION:")
        print(question)

        # -------------------------------------------------
        # Generate answer using current Basic RAG pipeline
        # -------------------------------------------------
        answer, documents = generate_answer(
            question
        )

        print("\nANSWER:")
        print(answer)

        # -------------------------------------------------
        # Display retrieved sources
        # -------------------------------------------------
        print("\nRETRIEVED SOURCES:")

        seen_urls = set()

        for document in documents:

            category = document.metadata.get(
                "category",
                "Unknown"
            )

            source_url = document.metadata.get(
                "source_url",
                ""
            )

            if source_url not in seen_urls:

                seen_urls.add(source_url)

                print(
                    f"\n- {category}"
                )

                print(
                    f"  {source_url}"
                )

        # -------------------------------------------------
        # Display retrieved chunk categories
        # -------------------------------------------------
        print("\nRETRIEVED CHUNKS:")

        for index, document in enumerate(
            documents,
            start=1
        ):

            category = document.metadata.get(
                "category",
                "Unknown"
            )

            preview = document.page_content[
                :250
            ].replace(
                "\n",
                " "
            )

            print(
                f"\nChunk {index}"
            )

            print(
                f"Category: {category}"
            )

            print(
                f"Preview: {preview}..."
            )

    print("\n" + "=" * 80)
    print(
        "BASELINE RAG TEST COMPLETED"
    )
    print("=" * 80)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
if __name__ == "__main__":

    run_baseline_tests()