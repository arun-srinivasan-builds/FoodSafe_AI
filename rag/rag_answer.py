from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from build_context import build_context


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")


# ---------------------------------------------------------
# Create GPT model
# ---------------------------------------------------------
def get_llm():

    llm = ChatOpenAI(
        model="gpt-4.1",
        temperature=0
    )

    return llm


# ---------------------------------------------------------
# Create RAG prompt
# ---------------------------------------------------------
def get_rag_prompt():

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are FoodSafe AI, a food safety guidance assistant.

Your answers must be based only on the official FSSAI/FoSCoS
information provided in the retrieved context.

Rules:

1. Use only the retrieved official context to answer.
2. Do not invent food safety rules, regulations, procedures,
   complaint steps, recall information, or scientific claims.
3. If the retrieved context does not contain enough information
   to answer the question, clearly say that the available
   FSSAI/FoSCoS information does not provide enough evidence.
4. Do not treat general knowledge as official FSSAI guidance.
5. Give a clear, simple, practical answer.
6. Mention when the retrieved information is specifically about
   a particular product or situation and should not automatically
   be generalized to every food product.
7. Do not claim that a complaint has been filed or that FoodSafe AI
   can submit a complaint on behalf of the user.
8. When relevant, encourage the user to verify information using
   the official FSSAI/FoSCoS source supplied by the application.
"""
            ),
            (
                "human",
                """
OFFICIAL FSSAI/FoSCoS CONTEXT:

{context}


USER QUESTION:

{question}


Answer the user's question using only the official context above.
"""
            )
        ]
    )

    return prompt


# ---------------------------------------------------------
# Generate grounded RAG answer
# ---------------------------------------------------------
def generate_answer(question):

    # Retrieve and build context
    context, documents = build_context(question)

    # Create prompt and model
    prompt = get_rag_prompt()
    llm = get_llm()

    # Build complete prompt
    messages = prompt.invoke(
        {
            "context": context,
            "question": question
        }
    )

    # Send prompt to GPT-4.1
    response = llm.invoke(messages)

    return response.content, documents


# ---------------------------------------------------------
# Interactive test
# ---------------------------------------------------------
if __name__ == "__main__":

    print("=" * 70)
    print("FOODSAFE AI - RAG ANSWER TEST")
    print("=" * 70)

    question = input(
        "\nEnter your food safety question: "
    ).strip()

    if not question:

        print("\nPlease enter a valid question.")

    else:

        answer, documents = generate_answer(
            question
        )

        print("\n" + "=" * 70)
        print("QUESTION")
        print("=" * 70)

        print(question)

        print("\n" + "=" * 70)
        print("FOODSAFE AI ANSWER")
        print("=" * 70)

        print(answer)

        print("\n" + "=" * 70)
        print("OFFICIAL SOURCES USED")
        print("=" * 70)

        seen_urls = set()

        for document in documents:

            source_url = document.metadata.get(
                "source_url",
                ""
            )

            category = document.metadata.get(
                "category",
                "Unknown"
            )

            # Avoid printing duplicate URLs
            if source_url and source_url not in seen_urls:

                seen_urls.add(source_url)

                print(
                    f"\n- {category}"
                )

                print(
                    f"  {source_url}"
                )

        print("\n" + "=" * 70)
        print("RAG TEST COMPLETED")
        print("=" * 70)