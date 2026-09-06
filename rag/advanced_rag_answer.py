import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from rag.rerank_retriever import get_reranked_documents


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError(
        "OPENAI_API_KEY was not found. "
        "Please check your .env file."
    )


# =========================================================
# CREATE GPT MODEL
# =========================================================

llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0
)


# =========================================================
# BUILD CONTEXT FROM INTENT-AWARE RERANKED CHUNKS
# =========================================================

def build_reranked_context(question, top_n=3):

    print(
        "\nRetrieving and intent-aware reranking "
        "official FSSAI/FoSCoS information..."
    )

    # Step 25B-6:
    # This now returns LangChain Document objects directly.
    reranked_documents = get_reranked_documents(
        question,
        top_n=top_n
    )

    context_parts = []
    source_documents = []

    for index, document in enumerate(
        reranked_documents,
        start=1
    ):

        source_documents.append(
            document
        )

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
            document.metadata.get(
                "source",
                "Unknown"
            )
        )

        rerank_score = document.metadata.get(
            "rerank_score",
            0
        )

        retrieval_query = document.metadata.get(
            "retrieval_query",
            question
        )

        context_block = f"""
SOURCE {index}

Retrieval Intent:
{retrieval_query}

Category:
{category}

Title:
{title}

Official URL:
{source_url}

Rerank Score:
{rerank_score}

Content:
{document.page_content}
"""

        context_parts.append(
            context_block
        )

    context = "\n\n".join(
        context_parts
    )

    return context, source_documents


# =========================================================
# FORMAT RECENT CONVERSATION HISTORY
# =========================================================

def format_conversation_history(
    conversation_history=None
):

    if not conversation_history:
        return "No previous conversation."

    # Last 6 messages =
    # approximately last 3 user/assistant exchanges
    recent_history = conversation_history[-6:]

    history_parts = []

    for item in recent_history:

        role = item.get(
            "role",
            ""
        )

        content = item.get(
            "content",
            ""
        )

        if role == "user":
            label = "User"

        elif role == "assistant":
            label = "FoodSafe AI"

        else:
            label = role

        history_parts.append(
            f"{label}: {content}"
        )

    return "\n\n".join(
        history_parts
    )


# =========================================================
# GENERATE ADVANCED RAG ANSWER
# =========================================================

def generate_advanced_rag_answer(
    question,
    conversation_history=None
):

    # -----------------------------------------------------
    # Retrieve official FSSAI/FoSCoS evidence
    # -----------------------------------------------------

    context, documents = build_reranked_context(
        question,
        top_n=3
    )


    # -----------------------------------------------------
    # Prepare conversational context
    # -----------------------------------------------------

    history_text = format_conversation_history(
        conversation_history
    )


    # -----------------------------------------------------
    # SYSTEM PROMPT
    # -----------------------------------------------------

    system_prompt = """
You are FoodSafe AI, an assistant that answers food-safety
questions using only the official FSSAI and FoSCoS information
provided in the retrieved context.

You may also receive recent conversation history.

IMPORTANT MEMORY RULE:

Conversation history is ONLY provided to help you understand
what the user is referring to in the current question.

For example, conversation history may help resolve references
such as:

- "it"
- "that product"
- "the same issue"
- "what should I keep?"
- "can I complain about this?"
- "what about the package?"

Conversation history is NOT an authoritative source of
food-safety information.

All factual food-safety guidance must come from the supplied
official FSSAI/FoSCoS context.

Follow these rules strictly:

1. Use only the supplied FSSAI/FoSCoS context for factual
   food-safety guidance.

2. Use conversation history only to understand the user's
   current intent and references.

3. Never treat a previous FoodSafe AI answer as an official
   source.

4. Do not invent food-safety procedures, regulations,
   complaint steps, scientific claims, official requirements,
   or legal interpretations.

5. Do not generalize a rule, regulation, standard, or
   statement from one specific food category to another
   unless the supplied context explicitly supports it.

6. Clearly distinguish between:
   - what the supplied FSSAI context explicitly states
   - what the context does not establish.

7. If retrieved context is relevant but does not fully answer
   the current question, say so clearly.

8. If the currently indexed FSSAI information is insufficient,
   say:

   "I could not fully verify this from the FSSAI information
   currently indexed."

9. When appropriate, direct the user to the relevant official
   FSSAI/FoSCoS source.

10. Keep the answer practical, concise, and easy to understand.

11. Do not use outside knowledge.

12. Prefer cautious wording such as:
    "The retrieved FSSAI information states..."
    instead of extending source information beyond what it says.

13. When the retrieved context contains information about a
    different but related food product, explain that limitation
    instead of treating it as direct evidence.

14. If conversation history clarifies what the user means,
    you may restate that context briefly in the answer, but
    factual guidance must still be supported by the official
    retrieved context.

15. When the retrieved FoSCoS context explicitly provides
    complaint procedures or supporting-document guidance,
    use that information directly and practically in the answer.

16. Do not claim that a specific food product violates a
    particular FSSAI product standard unless the supplied
    context explicitly contains a standard applicable to that
    product.
"""


    # -----------------------------------------------------
    # HUMAN PROMPT
    # -----------------------------------------------------

    human_prompt = f"""
RECENT CONVERSATION HISTORY:

{history_text}


OFFICIAL FSSAI/FoSCoS CONTEXT:

{context}


CURRENT USER QUESTION:

{question}


Use the recent conversation history only to understand what
the user is referring to.

Use only the official FSSAI/FoSCoS context for factual
food-safety guidance.

When the context provides relevant complaint or supporting
document information, include it in the answer.

Answer the current question.
"""


    # -----------------------------------------------------
    # CALL GPT-4.1
    # -----------------------------------------------------

    print(
        "\nSending intent-aware reranked context and "
        "conversation history to GPT-4.1..."
    )


    response = llm.invoke(
        [
            SystemMessage(
                content=system_prompt
            ),
            HumanMessage(
                content=human_prompt
            )
        ]
    )


    return response.content, documents


# =========================================================
# INTERACTIVE TERMINAL TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 80)
    print("FOODSAFE AI - ADVANCED RAG")
    print("INTENT-AWARE HYBRID + FLASHRANK + GPT-4.1")
    print("=" * 80)

    question = input(
        "\nEnter your food safety question: "
    ).strip()

    if not question:

        print(
            "\nPlease enter a valid question."
        )

    else:

        answer, documents = generate_advanced_rag_answer(
            question,
            conversation_history=[]
        )

        print("\n" + "=" * 80)
        print("FOODSAFE AI ANSWER")
        print("=" * 80)

        print(
            answer
        )

        print("\n" + "=" * 80)
        print("OFFICIAL SOURCES USED")
        print("=" * 80)

        seen_urls = set()

        for document in documents:

            source_url = document.metadata.get(
                "source_url",
                document.metadata.get(
                    "source",
                    "Unknown"
                )
            )

            category = document.metadata.get(
                "category",
                "Unknown"
            )

            if source_url not in seen_urls:

                print(
                    f"- {category}: {source_url}"
                )

                seen_urls.add(
                    source_url
                )