from flashrank import Ranker, RerankRequest

from rag.hybrid_retriever import get_hybrid_retriever


# ============================================================
# FLASHRANK MODEL
# ============================================================

_flashrank_model = None


def get_flashrank_model():
    """
    Load FlashRank once and reuse it.
    """

    global _flashrank_model

    if _flashrank_model is None:
        print("Loading FlashRank model...")

        _flashrank_model = Ranker()

        print("FlashRank model ready.")

    return _flashrank_model


# ============================================================
# QUERY EXPANSION
# ============================================================

def build_retrieval_queries(question):
    """
    Build multiple retrieval-oriented queries from the user's
    original question.

    Supports:
    - full natural questions
    - short / vague inputs
    - packaged-food issues
    - restaurant issues
    - online delivery issues
    - evidence questions
    """

    question = question.strip()
    question_lower = question.lower()

    queries = [question]


    # ========================================================
    # FOOD-SAFETY PROBLEM TERMS
    # ========================================================

    problem_terms = [
        "fungus",
        "mould",
        "mold",
        "worm",
        "worms",
        "insect",
        "insects",
        "bug",
        "bugs",
        "foreign object",
        "foreign material",
        "hair",
        "stone",
        "stones",
        "plastic",
        "glass",
        "metal",
        "spoiled",
        "spoilt",
        "stale",
        "rotten",
        "bad smell",
        "smells bad",
        "foul smell",
        "contaminated",
        "contamination",
        "unsafe",
        "expired",
        "expiry",
        "damaged",
        "leaking",
        "swollen",
        "discoloured",
        "discolored",
    ]

    has_food_problem = any(
        term in question_lower
        for term in problem_terms
    )


    # ========================================================
    # PACKAGED FOOD TERMS
    # ========================================================

    packaged_terms = [
        "packaged",
        "packet",
        "pack",
        "sealed",
        "bread",
        "biscuit",
        "biscuits",
        "rice",
        "milk",
        "milk packet",
        "chocolate",
        "snack",
        "chips",
        "juice",
        "drink",
        "food product",
        "product",
        "expiry",
        "expired",
        "batch",
        "manufacturer",
        "label",
        "wrapper",
        "container",
        "bottle",
        "tin",
        "can",
    ]

    is_packaged_food = any(
        term in question_lower
        for term in packaged_terms
    )


    # ========================================================
    # FOOD PREMISES TERMS
    # ========================================================

    premises_terms = [
        "restaurant",
        "hotel",
        "cafe",
        "canteen",
        "food premises",
        "outlet",
        "qsr",
        "shop",
        "bakery",
        "stall",
        "mess",
    ]

    is_food_premises = any(
        term in question_lower
        for term in premises_terms
    )


    # ========================================================
    # ONLINE FOOD DELIVERY TERMS
    # ========================================================

    delivery_terms = [
        "delivery",
        "food delivery",
        "ordered online",
        "online food",
        "online aggregator",
        "swiggy",
        "zomato",
    ]

    is_delivery = any(
        term in question_lower
        for term in delivery_terms
    )


    # ========================================================
    # ACTION / COMPLAINT INTENT
    # ========================================================

    action_terms = [
        "what should i do",
        "what do i do",
        "what can i do",
        "what action",
        "next step",
        "next steps",
        "complaint",
        "complain",
        "report",
        "report this",
        "how to report",
        "how do i complain",
        "how can i complain",
        "issue",
        "problem",
        "help",
    ]

    has_action_intent = any(
        term in question_lower
        for term in action_terms
    )


    # ========================================================
    # EVIDENCE INTENT
    # ========================================================

    evidence_terms = [
        "evidence",
        "proof",
        "document",
        "documents",
        "supporting",
        "photo",
        "photos",
        "photograph",
        "photographs",
        "image",
        "images",
        "receipt",
        "bill",
        "invoice",
        "keep",
        "retain",
    ]

    has_evidence_intent = any(
        term in question_lower
        for term in evidence_terms
    )


    # ========================================================
    # PACKAGED FOOD
    # ========================================================

    if is_packaged_food and (
        has_food_problem
        or has_action_intent
        or has_evidence_intent
    ):

        queries.append(
            "packaged food complaint "
            "Food Grievance Portal "
            "consumer complaint procedure"
        )

        queries.append(
            "supporting document evidence "
            "image product bill "
            "packaged food complaint"
        )


    # ========================================================
    # RESTAURANT / FOOD PREMISES
    # ========================================================

    elif is_food_premises and (
        has_food_problem
        or has_action_intent
        or has_evidence_intent
    ):

        queries.append(
            "food premises restaurant complaint "
            "Food Grievance Portal "
            "consumer complaint procedure"
        )

        queries.append(
            "supporting document evidence "
            "image bill "
            "food premises complaint"
        )


    # ========================================================
    # ONLINE FOOD DELIVERY
    # ========================================================

    elif is_delivery and (
        has_food_problem
        or has_action_intent
        or has_evidence_intent
    ):

        queries.append(
            "online aggregator food delivery complaint "
            "Food Grievance Portal "
            "consumer complaint procedure"
        )

        queries.append(
            "supporting document evidence "
            "image bill "
            "food delivery complaint"
        )


    # ========================================================
    # GENERAL EVIDENCE QUESTION
    # ========================================================

    elif has_evidence_intent:

        queries.append(
            "supporting document evidence "
            "image product bill "
            "Food Grievance Portal complaint"
        )


    # ========================================================
    # GENERAL FOOD-SAFETY PROBLEM
    # ========================================================

    elif has_food_problem:

        queries.append(
            "food safety consumer complaint "
            "Food Grievance Portal"
        )


    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    unique_queries = []
    seen = set()

    for query in queries:

        normalized = query.lower().strip()

        if normalized not in seen:
            seen.add(normalized)
            unique_queries.append(query)


    return unique_queries[:3]


# ============================================================
# DOCUMENT KEY
# ============================================================

def get_document_key(document):
    """
    Stable key for deduplicating chunks.
    """

    source = document.metadata.get(
        "source_url",
        document.metadata.get("source", "")
    )

    category = document.metadata.get(
        "category",
        ""
    )

    content = document.page_content.strip()

    return (
        source,
        category,
        content
    )


# ============================================================
# RERANK ONE QUERY
# ============================================================

def rerank_for_query(
    query,
    documents,
    top_n=1
):
    """
    Rerank candidates specifically against THIS retrieval query.

    This is the key Step 25B-6 improvement.
    """

    if not documents:
        return []


    passages = []
    document_lookup = {}


    for index, document in enumerate(documents):

        passage_id = str(index)

        passages.append(
            {
                "id": passage_id,
                "text": document.page_content,
            }
        )

        document_lookup[
            passage_id
        ] = document


    rerank_request = RerankRequest(
        query=query,
        passages=passages
    )


    ranker = get_flashrank_model()

    ranked_results = ranker.rerank(
        rerank_request
    )


    final_documents = []


    for result in ranked_results[:top_n]:

        passage_id = str(
            result["id"]
        )

        document = document_lookup.get(
            passage_id
        )

        if document is None:
            continue


        document.metadata[
            "rerank_score"
        ] = float(
            result.get(
                "score",
                0
            )
        )

        document.metadata[
            "retrieval_query"
        ] = query


        final_documents.append(
            document
        )


    return final_documents


# ============================================================
# INTENT-AWARE RETRIEVAL
# ============================================================

def get_intent_aware_documents(
    question,
    top_n=3
):
    """
    Step 25B-6

    For each retrieval query:

        query
          ↓
        FAISS + BM25
          ↓
        FlashRank using same query
          ↓
        best result

    Then combine the best result from each intent.
    """

    retriever = get_hybrid_retriever()


    retrieval_queries = build_retrieval_queries(
        question
    )


    print("\nRetrieval queries:")

    for index, query in enumerate(
        retrieval_queries,
        start=1
    ):

        print(
            f"  {index}. {query}"
        )


    selected_documents = []

    seen = set()


    # ========================================================
    # PROCESS EACH INTENT SEPARATELY
    # ========================================================

    for index, query in enumerate(
        retrieval_queries,
        start=1
    ):

        print(
            f"\n{'=' * 70}"
        )

        print(
            f"INTENT {index}"
        )

        print(
            f"{'=' * 70}"
        )

        print(
            f"Query: {query}"
        )


        # ----------------------------------------------------
        # Hybrid retrieval
        # ----------------------------------------------------

        documents = retriever.invoke(
            query
        )


        print(
            f"Hybrid candidates returned: "
            f"{len(documents)}"
        )


        # ----------------------------------------------------
        # Rerank ONLY this intent's candidates
        # ----------------------------------------------------

        reranked_documents = rerank_for_query(
            query=query,
            documents=documents,
            top_n=3
        )


        # ----------------------------------------------------
        # Select best unique result for this intent
        # ----------------------------------------------------

        selected_for_intent = None


        for document in reranked_documents:

            key = get_document_key(
                document
            )

            if key not in seen:

                seen.add(key)

                selected_for_intent = document

                break


        if selected_for_intent is not None:

            selected_documents.append(
                selected_for_intent
            )

            print(
                "Selected category:",
                selected_for_intent.metadata.get(
                    "category",
                    "Unknown"
                )
            )

            print(
                "Selected score:",
                selected_for_intent.metadata.get(
                    "rerank_score",
                    0
                )
            )

        else:

            print(
                "No unique document selected "
                "for this intent."
            )


    # ========================================================
    # SAFETY FALLBACK
    # ========================================================

    # If fewer than requested documents were selected,
    # retrieve from the original question and fill remaining
    # slots using unique results.

    if len(selected_documents) < top_n:

        print(
            "\nAdding fallback documents "
            "from original question..."
        )


        fallback_documents = retriever.invoke(
            question
        )


        fallback_ranked = rerank_for_query(
            query=question,
            documents=fallback_documents,
            top_n=top_n
        )


        for document in fallback_ranked:

            if len(selected_documents) >= top_n:
                break


            key = get_document_key(
                document
            )


            if key not in seen:

                seen.add(key)

                selected_documents.append(
                    document
                )


    return selected_documents[:top_n]


# ============================================================
# PUBLIC RETRIEVER FUNCTION
# ============================================================

def get_reranked_documents(
    question,
    top_n=3
):
    """
    Kept with the same function name so the rest of FoodSafe AI
    does not need to change.

    Internally this now uses intent-aware reranking.
    """

    return get_intent_aware_documents(
        question=question,
        top_n=top_n
    )


# ============================================================
# CONTEXT BUILDER
# ============================================================

def build_reranked_context(
    question,
    top_n=3
):
    """
    Build GPT-ready context.

    Returns:

        context
        documents
    """

    documents = get_reranked_documents(
        question=question,
        top_n=top_n
    )


    context_parts = []


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

        source = document.metadata.get(
            "source_url",
            document.metadata.get(
                "source",
                "Unknown"
            )
        )

        retrieval_query = document.metadata.get(
            "retrieval_query",
            question
        )


        context_part = f"""
SOURCE {index}

Retrieval Intent:
{retrieval_query}

Category:
{category}

Title:
{title}

Official URL:
{source}

Content:
{document.page_content}
""".strip()


        context_parts.append(
            context_part
        )


    context = "\n\n".join(
        context_parts
    )


    return context, documents


# ============================================================
# COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 75)

    print(
        "FOODSAFE AI - INTENT-AWARE HYBRID + FLASHRANK TEST"
    )

    print("=" * 75)


    question = input(
        "\nEnter your food safety question: "
    ).strip()


    if not question:

        print(
            "\nPlease enter a valid question."
        )

    else:

        print(
            "\n" + "=" * 75
        )

        print(
            "QUESTION"
        )

        print(
            "=" * 75
        )

        print(
            question
        )


        documents = get_reranked_documents(
            question=question,
            top_n=3
        )


        print(
            "\n" + "=" * 75
        )

        print(
            "FINAL INTENT-AWARE RESULTS"
        )

        print(
            "=" * 75
        )


        for index, document in enumerate(
            documents,
            start=1
        ):

            print(
                f"\nRESULT {index}"
            )

            print(
                "-" * 75
            )


            print(
                "Retrieval Intent:",
                document.metadata.get(
                    "retrieval_query",
                    "Unknown"
                )
            )


            print(
                "Category:",
                document.metadata.get(
                    "category",
                    "Unknown"
                )
            )


            print(
                "Title:",
                document.metadata.get(
                    "title",
                    "Unknown"
                )
            )


            print(
                "Source:",
                document.metadata.get(
                    "source_url",
                    document.metadata.get(
                        "source",
                        "Unknown"
                    )
                )
            )


            print(
                "Rerank Score:",
                document.metadata.get(
                    "rerank_score",
                    0
                )
            )


            preview = (
                document.page_content[:700]
                .replace(
                    "\n",
                    " "
                )
            )


            print(
                "\nPreview:"
            )

            print(
                preview
            )


        print(
            "\n" + "=" * 75
        )

        print(
            "Total final results:",
            len(documents)
        )

        print(
            "=" * 75
        )