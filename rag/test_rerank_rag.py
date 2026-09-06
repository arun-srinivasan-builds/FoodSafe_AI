from rerank_retriever import retrieve_and_rerank


TEST_QUESTIONS = [
    "Is plastic rice real?",
    "What should I do if I find fungus in packaged food?",
    "How can I complain about unsafe packaged food?",
    "How do I know if a food product has been recalled?",
    "How can I check whether milk is adulterated?"
]


def run_test():

    print("=" * 80)
    print("FOODSAFE AI - HYBRID + FLASHRANK RETRIEVAL EVALUATION")
    print("=" * 80)

    print(f"\nTotal test questions: {len(TEST_QUESTIONS)}")

    for test_number, question in enumerate(
        TEST_QUESTIONS,
        start=1
    ):

        print("\n" + "=" * 80)
        print(f"TEST {test_number}")
        print("=" * 80)

        print("\nQUESTION:")
        print(question)

        results = retrieve_and_rerank(
            question,
            top_n=3
        )

        print("\nFINAL RERANKED CHUNKS:")

        for i, item in enumerate(
            results,
            start=1
        ):

            doc = item["document"]
            score = item["score"]

            print(f"\nChunk {i}")
            print("-" * 70)

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

            print(
                "Rerank Score:",
                score
            )

            preview = (
                doc.page_content[:500]
                .replace("\n", " ")
            )

            print("Preview:")
            print(preview)

    print("\n" + "=" * 80)
    print("HYBRID + FLASHRANK EVALUATION COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    run_test()