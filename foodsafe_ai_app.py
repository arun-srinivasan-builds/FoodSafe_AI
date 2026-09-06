import html
import streamlit as st

from rag.advanced_rag_answer import generate_advanced_rag_answer


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="FoodSafe AI",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# SESSION STATE
# =========================================================

if "question" not in st.session_state:
    st.session_state.question = ""

if "answer" not in st.session_state:
    st.session_state.answer = ""

if "documents" not in st.session_state:
    st.session_state.documents = []

if "has_answer" not in st.session_state:
    st.session_state.has_answer = False

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
<style>

/* =====================================================
   GLOBAL
===================================================== */

.stApp {
    background:
        radial-gradient(
            circle at top right,
            rgba(213, 238, 224, 0.50),
            transparent 28%
        ),
        #fbfcfa;
    color: #17231c;
}

.block-container {
    max-width: 1180px;
    padding-top: 0.5rem;
    padding-bottom: 2rem;
}

html {
    scroll-behavior: smooth;
}

header[data-testid="stHeader"] {
    background: transparent;
}


/* =====================================================
   TOP BAR
===================================================== */

.top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0 1.1rem 0;
}

.brand {
    font-size: 1.08rem;
    font-weight: 800;
    color: #163d2b;
    letter-spacing: 0.03em;
}

.verified-badge {
    display: inline-block;
    padding: 0.40rem 0.78rem;
    border-radius: 999px;
    background: #edf7f0;
    border: 1px solid #d1e8d8;
    color: #28633f;
    font-size: 0.78rem;
    font-weight: 700;
}


/* =====================================================
   HERO
===================================================== */

.hero {
    padding: 2.1rem 0 2.2rem 0;
    max-width: 900px;
}

.hero-kicker {
    color: #377c52;
    font-size: 0.85rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.13em;
    margin-bottom: 1rem;
}

.hero-title {
    font-size: clamp(3rem, 7vw, 5.7rem);
    line-height: 0.98;
    font-weight: 850;
    color: #14291e;
    letter-spacing: -0.065em;
    margin-bottom: 1.5rem;
}

.hero-highlight {
    color: #2d7549;
}

.hero-description {
    font-size: 1.15rem;
    line-height: 1.75;
    max-width: 720px;
    color: #526159;
    margin-bottom: 1.3rem;
}

.hero-trust {
    font-size: 0.88rem;
    color: #6d7972;
}


/* =====================================================
   SECTION HEADERS
===================================================== */

.section-label {
    color: #36774f;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    font-weight: 800;
    margin-bottom: 0.55rem;
}

.section-title {
    font-size: 2.05rem;
    color: #17291f;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin-bottom: 0.5rem;
}

.section-text {
    color: #69756e;
    max-width: 690px;
    line-height: 1.65;
    margin-bottom: 0.85rem;
}


/* =====================================================
   FEATURE CARDS
===================================================== */

.pillar-card {
    background: rgba(255, 255, 255, 0.84);
    border: 1px solid #e0e9e3;
    border-radius: 18px;
    padding: 1.35rem;
    min-height: 165px;
    transition: all 0.18s ease;
    box-shadow:
        0 7px 22px rgba(25, 62, 41, 0.035);
}

.pillar-card:hover {
    transform: translateY(-3px);
    border-color: #b9d8c3;
    box-shadow:
        0 12px 28px rgba(25, 62, 41, 0.075);
}

.pillar-icon {
    font-size: 1.55rem;
    margin-bottom: 0.7rem;
}

.pillar-title {
    font-size: 1.02rem;
    font-weight: 800;
    color: #1d3928;
    margin-bottom: 0.45rem;
}

.pillar-text {
    color: #6a756f;
    font-size: 0.89rem;
    line-height: 1.5;
}


/* =====================================================
   ASK FOODSAFE PANEL
===================================================== */

.ask-shell {
    margin-top: 0.2rem;
    padding: 1.25rem 1.6rem;
    background: #173d2b;
    border-radius: 24px;
    color: white;
    box-shadow:
        0 20px 55px rgba(20, 61, 42, 0.14);
}

.ask-title {
    font-size: 2.05rem;
    font-weight: 800;
    letter-spacing: -0.035em;
    color: white;
    margin-bottom: 0.55rem;
}

.ask-description {
    color: #c6d9ce;
    font-size: 0.98rem;
    line-height: 1.65;
    max-width: 780px;
}


/* =====================================================
   TEXT AREA
===================================================== */

div[data-testid="stTextArea"] textarea {
    border: 1px solid #d8e5dc !important;
    border-radius: 14px !important;
    padding: 1rem !important;
    font-size: 1rem !important;
    background: white !important;
    color: #17231c !important;
}

div[data-testid="stTextArea"] textarea:focus {
    border-color: #55a571 !important;
    box-shadow:
        0 0 0 3px rgba(75, 150, 100, 0.13) !important;
}


/* =====================================================
   CHAT INPUT
===================================================== */

div[data-testid="stChatInput"] {
    margin-top: 0.15rem !important;
    margin-bottom: 0.05rem !important;
}

div[data-testid="stChatInput"] > div {
    background: #173d2b !important;
    border: 1px solid #4f765f !important;
    border-radius: 14px !important;
}

div[data-testid="stChatInput"] textarea {
    color: white !important;
    -webkit-text-fill-color: white !important;
    caret-color: white !important;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(255, 255, 255, 0.78) !important;
    -webkit-text-fill-color: rgba(255, 255, 255, 0.78) !important;
    opacity: 1 !important;
}

div[data-testid="stChatInput"] button {
    color: white !important;
}


/* =====================================================
   BUTTONS
===================================================== */

.stButton > button {
    width: 100%;
    border-radius: 12px;
    border: 1px solid #d8e5dc;
    background: white;
    color: #234431;
    padding: 0.72rem 0.9rem;
    font-weight: 650;
    transition: all 0.15s ease;
}

.stButton > button:hover {
    border-color: #4e9b69;
    color: #21653d;
    background: #f4faf6;
}

.stButton > button[kind="primary"] {
    background: #48a668;
    color: white;
    border: none;
    font-weight: 750;
    min-height: 47px;
}

.stButton > button[kind="primary"]:hover {
    background: #3e925b;
    color: white;
}


/* =====================================================
   VERTICAL SPACING CLEANUP
===================================================== */

/* Reduce space around the conversation controls row */
div[data-testid="stHorizontalBlock"] {
    row-gap: 0.35rem !important;
}

/* Reduce default spacing between Streamlit blocks */
div[data-testid="stVerticalBlock"] > div {
    gap: 0.4rem;
}

/* Keep buttons compact */
.stButton {
    margin-top: 0.1rem !important;
    margin-bottom: 0.1rem !important;
}

/* Pull the guidance section closer to controls */
.st-key-guidance_card {
    margin-top: 0.2rem !important;
}


/* =====================================================
   GUIDANCE CARD
===================================================== */

.st-key-guidance_card {
    background: #ffffff !important;
    border: 1px solid #d8e5dc !important;
    border-radius: 22px !important;
    padding: 1.05rem 1.35rem !important;
    box-shadow:
        0 12px 35px rgba(18, 49, 33, 0.055) !important;
    overflow: hidden;
}

.guidance-question-label,
.guidance-answer-label {
    color: #36774f;
    font-size: 0.76rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    font-weight: 800;
}

.guidance-question {
    color: #17291f;
    font-size: 1.10rem;
    font-weight: 750;
    line-height: 1.55;
    margin-top: 0.35rem;
}


/* =====================================================
   MEMORY STATUS
===================================================== */

.memory-pill {
    display: inline-block;
    margin-top: 0.5rem;
    padding: 0.35rem 0.7rem;
    border-radius: 999px;
    background: #edf7f0;
    border: 1px solid #d1e8d8;
    color: #28633f;
    font-size: 0.76rem;
    font-weight: 700;
}


/* =====================================================
   SOURCE CARDS
===================================================== */

.st-key-source_card_0,
.st-key-source_card_1,
.st-key-source_card_2,
.st-key-source_card_3,
.st-key-source_card_4 {
    background: #f7faf8 !important;
    border: 1px solid #e0e9e3 !important;
    border-radius: 16px !important;
    padding: 0.45rem 0.65rem !important;
    margin-bottom: 0.7rem;
}


/* =====================================================
   LINK BUTTONS
===================================================== */

div[data-testid="stLinkButton"] a {
    border-radius: 10px !important;
    background: #173d2b !important;
    color: white !important;
    border: none !important;
    font-weight: 650 !important;
}

div[data-testid="stLinkButton"] a:hover {
    background: #286647 !important;
    color: white !important;
}


/* =====================================================
   DISCLAIMER
===================================================== */

div[data-testid="stAlert"] {
    border-radius: 14px;
}


/* =====================================================
   FOOTER
===================================================== */

.footer {
    border-top: 1px solid #e2e9e4;
    margin-top: 5rem;
    padding: 2rem 0;
    color: #79837d;
    font-size: 0.82rem;
    display: flex;
    justify-content: space-between;
}

</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def ask_foodsafe(question):

    question = question.strip()

    if not question:
        return


    # Store the current question
    st.session_state.question = question


    # -----------------------------------------------------
    # Generate answer using recent conversation memory
    # -----------------------------------------------------

    with st.spinner(
        "Searching official FSSAI information "
        "and preparing your answer..."
    ):

        answer, documents = generate_advanced_rag_answer(
            question,
            conversation_history=(
                st.session_state.conversation_history
            )
        )


    # -----------------------------------------------------
    # Save current answer
    # -----------------------------------------------------

    st.session_state.answer = answer
    st.session_state.documents = documents
    st.session_state.has_answer = True


    # -----------------------------------------------------
    # Add new exchange to conversation memory
    # -----------------------------------------------------

    st.session_state.conversation_history.append(
        {
            "role": "user",
            "content": question
        }
    )

    st.session_state.conversation_history.append(
        {
            "role": "assistant",
            "content": answer
        }
    )


def clear_conversation():

    st.session_state.question = ""
    st.session_state.answer = ""
    st.session_state.documents = []
    st.session_state.has_answer = False
    st.session_state.conversation_history = []


# =========================================================
# TOP BAR
# =========================================================

st.markdown(
    """
<div class="top-bar">

<div class="brand">
🥗 FOODSAFE AI
</div>

<div class="verified-badge">
Official FSSAI / FoSCoS Sources
</div>

</div>
""",
    unsafe_allow_html=True
)


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
<div class="hero">

<div class="hero-kicker">
AI-powered food safety guidance
</div>

<div class="hero-title">
Know what's <span class="hero-highlight">safe.</span>
</div>

<div class="hero-description">
Ask practical questions about unsafe food, adulteration,
food myths, recalls and consumer complaints — grounded
in official FSSAI and FoSCoS information.
</div>

<div class="hero-trust">
RAG-powered • Official sources • Grounded answers
</div>

</div>
""",
    unsafe_allow_html=True
)


# =========================================================
# EXPLORE
# =========================================================

st.markdown(
    """
<div class="section-label">
Explore
</div>

<div class="section-title">
Food safety, made easier.
</div>

<div class="section-text">
Explore the most common areas where FoodSafe AI can
help you find relevant official guidance.
</div>
""",
    unsafe_allow_html=True
)


c1, c2, c3, c4, c5 = st.columns(5)


pillar_data = [
    (
        c1,
        "⚠️",
        "Unsafe Food",
        "Understand what official guidance says "
        "when food looks unsafe."
    ),
    (
        c2,
        "🥛",
        "Adulteration",
        "Find FSSAI resources for identifying "
        "common food adulteration."
    ),
    (
        c3,
        "💬",
        "Food Myths",
        "Check common food claims against "
        "official FSSAI clarifications."
    ),
    (
        c4,
        "📢",
        "Food Recall",
        "Find official information about recalled "
        "or withdrawn food."
    ),
    (
        c5,
        "📝",
        "Complaints",
        "Understand official consumer grievance "
        "guidance and resources."
    )
]


for column, icon, title, description in pillar_data:

    with column:

        st.markdown(
            f"""
<div class="pillar-card">

<div class="pillar-icon">
{icon}
</div>

<div class="pillar-title">
{title}
</div>

<div class="pillar-text">
{description}
</div>

</div>
""",
            unsafe_allow_html=True
        )


# =========================================================
# START HERE
# =========================================================

st.markdown(
    "<div style='height:0.35rem'></div>",
    unsafe_allow_html=True
)


st.markdown(
    """
<div class="section-label">
Start here
</div>

<div class="section-title">
Try a common question.
</div>

<div class="section-text">
Select a question below or ask FoodSafe AI
something in your own words.
</div>
""",
    unsafe_allow_html=True
)


q1, q2 = st.columns(2)


with q1:

    if st.button(
        "🍱 I found a foreign object in restaurant food. "
        "What should I do?",
        use_container_width=True
    ):

        ask_foodsafe(
            "I found a foreign object in restaurant food. "
            "What should I do?"
        )


    if st.button(
        "🥛 How can I check whether milk may be adulterated?",
        use_container_width=True
    ):

        ask_foodsafe(
            "How can I check whether milk may be adulterated?"
        )


    if st.button(
        "📢 How do I check whether a food product "
        "has been recalled?",
        use_container_width=True
    ):

        ask_foodsafe(
            "How do I check whether a food product "
            "has been recalled?"
        )


with q2:

    if st.button(
        "🍞 I found fungus in packaged food "
        "before the expiry date.",
        use_container_width=True
    ):

        ask_foodsafe(
            "I found fungus in packaged food before "
            "the expiry date. What should I do?"
        )


    if st.button(
        "📱 I saw a WhatsApp claim about fake food. "
        "How can I verify it?",
        use_container_width=True
    ):

        ask_foodsafe(
            "I saw a WhatsApp claim about fake food. "
            "How can I verify it?"
        )


    if st.button(
        "📝 What evidence should I keep before "
        "making an FSSAI complaint?",
        use_container_width=True
    ):

        ask_foodsafe(
            "What evidence should I keep before "
            "making an FSSAI complaint?"
        )


# =========================================================
# ASK FOODSAFE AI
# =========================================================

st.markdown(
    "<div style='height:0.35rem'></div>",
    unsafe_allow_html=True
)


st.markdown(
    """
<div class="ask-shell">

<div class="ask-title">
Ask FoodSafe AI
</div>

<div class="ask-description">
Describe your food-safety concern in plain language.
FoodSafe AI will search the indexed official FSSAI information
and provide a grounded response.
</div>

<div class="memory-pill">
Session conversation memory enabled
</div>

</div>
""",
    unsafe_allow_html=True
)


with st.container():
    question = st.chat_input(
        "Ask a food-safety question or type a follow-up...",
        key="foodsafe_chat_input"
    )


if question:

    ask_foodsafe(
        question
    )


# =========================================================
# CONVERSATION CONTROLS
# =========================================================

if st.session_state.conversation_history:

    control_col1, control_col2 = st.columns(
        [4, 1]
    )

    with control_col2:

        if st.button(
            "Clear conversation",
            use_container_width=True
        ):

            clear_conversation()
            st.rerun()


# =========================================================
# GUIDANCE / ANSWER
# =========================================================

if st.session_state.has_answer:

    st.markdown(
        "<br><br>",
        unsafe_allow_html=True
    )


    st.markdown(
        """
<div class="section-label">
FoodSafe AI
</div>

<div class="section-title">
Guidance
</div>
""",
        unsafe_allow_html=True
    )


    with st.container(
        border=True,
        key="guidance_card"
    ):

        st.markdown(
            """
<div class="guidance-question-label">
Question
</div>
""",
            unsafe_allow_html=True
        )


        safe_question = html.escape(
            st.session_state.question
        )


        st.markdown(
            f"""
<div class="guidance-question">
{safe_question}
</div>
""",
            unsafe_allow_html=True
        )


        st.divider()


        st.markdown(
            """
<div class="guidance-answer-label">
Answer
</div>
""",
            unsafe_allow_html=True
        )


        st.markdown(
            st.session_state.answer
        )


    # =====================================================
    # OFFICIAL SOURCES
    # =====================================================

    st.markdown(
        "<br><br>",
        unsafe_allow_html=True
    )


    st.markdown(
        """
<div class="section-label">
Verification
</div>

<div class="section-title">
Official sources
</div>

<div class="section-text">
FoodSafe AI generated the response using the following
indexed official FSSAI/FoSCoS sources.
</div>
""",
        unsafe_allow_html=True
    )


    seen_urls = set()
    source_number = 0


    for document in st.session_state.documents:

        category = document.metadata.get(
            "category",
            "Official FSSAI Source"
        )

        url = document.metadata.get(
            "source_url",
            ""
        )


        if url and url not in seen_urls:

            safe_category = html.escape(
                category
            )


            with st.container(
                border=True,
                key=f"source_card_{source_number}"
            ):

                st.markdown(
                    f"**{safe_category}**"
                )

                st.link_button(
                    "View official source ↗",
                    url
                )


            seen_urls.add(
                url
            )

            source_number += 1


# =========================================================
# HOW IT WORKS
# =========================================================

st.markdown(
    "<div style='height:0.35rem'></div>",
    unsafe_allow_html=True
)


st.markdown(
    """
<div class="section-label">
Behind the answer
</div>

<div class="section-title">
Built for grounded guidance.
</div>

<div class="section-text">
FoodSafe AI does not simply send your question to an AI model.
It first searches the indexed official food-safety knowledge base
and gives the most relevant evidence to GPT-4.1.
</div>
""",
    unsafe_allow_html=True
)


h1, h2, h3, h4 = st.columns(4)


steps = [
    (
        h1,
        "01",
        "Search",
        "FAISS searches semantically similar "
        "official information."
    ),
    (
        h2,
        "02",
        "Combine",
        "BM25 adds keyword-sensitive retrieval."
    ),
    (
        h3,
        "03",
        "ReRank",
        "FlashRank selects the strongest evidence."
    ),
    (
        h4,
        "04",
        "Answer",
        "GPT-4.1 answers using the retrieved context."
    )
]


for column, number, title, description in steps:

    with column:

        st.markdown(
            f"""
<div class="pillar-card">

<div class="section-label">
{number}
</div>

<div class="pillar-title">
{title}
</div>

<div class="pillar-text">
{description}
</div>

</div>
""",
            unsafe_allow_html=True
        )


# =========================================================
# DISCLAIMER
# =========================================================

st.markdown(
    "<div style='height:0.35rem'></div>",
    unsafe_allow_html=True
)


st.info(
    "FoodSafe AI is an informational assistant built from "
    "indexed official FSSAI/FoSCoS content. Conversation memory "
    "is session-only and is used only to understand follow-up "
    "questions. Always verify important food-safety or complaint "
    "information through the linked official source."
)


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
<div class="footer">

<span>
🥗 FoodSafe AI
</span>

<span>
Built with RAG • FSSAI / FoSCoS Sources
</span>

</div>
""",
    unsafe_allow_html=True
)