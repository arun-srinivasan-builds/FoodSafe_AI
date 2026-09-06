from advanced_rag_answer import generate_advanced_rag_answer


TEST_QUESTIONS = [
    "Is plastic rice real?",
    "What should I do if I find fungus in packaged food?",
    "How can I complain about unsafe packaged food?",
    "How do I know if a food product has been recalled?",
    "How can I check whether milk is adulterated?"
]


def run_test():

    print("=" * 80)
    print("FOODSAFE AI - ADVANCED RAG END-TO-END EVALUATION")
    print("FAISS + BM25 + FLASHRANK + GPT-4.1")
    print("=" * 80)

    print(f"\nTotal test questions: {len(TEST_QUESTIONS)}")

    for test_number, question in enumerate(TEST_QUESTIONS, start=1):

        print("\n" + "=" * 80)
        print(f"TEST {test_number}")
        print("=" * 80)

        print("\nQUESTION:")
        print(question)

        answer, documents = generate_advanced_rag_answer(question)

        print("\n" + "-" * 80)
        print("FOODSAFE AI ANSWER")
        print("-" * 80)

        print(answer)

        print("\nOFFICIAL SOURCES USED:")

        seen_urls = set()

        for document in documents:

            source_url = document.metadata.get(
                "source_url",
                "Unknown"
            )

            category = document.metadata.get(
                "category",
                "Unknown"
            )

            if source_url not in seen_urls:

                print(f"- {category}: {source_url}")
                seen_urls.add(source_url)

    print("\n" + "=" * 80)
    print("ADVANCED RAG END-TO-END EVALUATION COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    run_test()