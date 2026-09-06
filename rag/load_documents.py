from pathlib import Path
import json
import re

from langchain_core.documents import Document


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "fssai_documents.json"


# ---------------------------------------------------------
# Clean scraped webpage text
# ---------------------------------------------------------
def clean_page_text(text: str) -> str:

    # Normalize line endings
    text = text.replace("\r\n", "\n")

    # Normalize repeated spaces and tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Reduce excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # -----------------------------------------------------
    # Common navigation/footer noise
    # -----------------------------------------------------
    noise_phrases = {
        "Menu",
        "Consumers",
        "Food Businesses",
        "Stakeholders",
        "Know FSSAI",
        "Home",
        "Print",

        "Contact Us",
        "Sitemap",
        "Privacy Policy",
        "Copyright Policy",
        "Terms and Conditions",
        "Website Policies",
        "Feedback",
        "Help",
        "About Us",

        "Annual Report",
        "Creative Catalogue",
        "Video Library",
        "Books, Reports & Manuals",
        "Resources",
        "Research & Development",
        "Jobs @ FSSAI (Careers)",
        "Internship @ FSSAI",
        "Tenders / EOI",

        "FOOD LAWS & NOTIFICATIONS",
        "Act & Rules",
        "Regulations",
        "Notifications",
        "Advisories / Orders",
        "Notice for Comments",

        # Additional FSSAI navigation/footer noise
        "ABOUT FSSAI",
        "Overview",
        "Food Authority",
        "Organisation Directory",
        "Internal Administration",
        "Citizen Charter",
        "Events & Calendar",
        "Jobs & Internship",
        "RTI & Disclosure",
        "Knowledge Hub",
        "Myth Buster",
    }

    cleaned_lines = []

    for line in text.splitlines():

        line = line.strip()

        # -------------------------------------------------
        # Skip empty lines
        # -------------------------------------------------
        if not line:
            continue

        # -------------------------------------------------
        # Skip exact known navigation/footer text
        # -------------------------------------------------
        if line in noise_phrases:
            continue

        # -------------------------------------------------
        # Skip decorative/breadcrumb symbols
        # -------------------------------------------------
        if line in {"/", "|", "›", "←", "↗"}:
            continue

        # -------------------------------------------------
        # Skip visitor counter
        # -------------------------------------------------
        if "Total Visitors:" in line:
            continue

        # -------------------------------------------------
        # Skip copyright footer
        # -------------------------------------------------
        if line.startswith("©"):
            continue

        # -------------------------------------------------
        # Skip Last Updated footer lines
        # -------------------------------------------------
        if line.startswith("Last Updated:"):
            continue

        if line.startswith("Last Updated :"):
            continue

        # -------------------------------------------------
        # Skip standard FSSAI footer tagline
        # -------------------------------------------------
        if line.startswith(
            "FSSAI – Ensuring Safe and Wholesome Food"
        ):
            continue

        # -------------------------------------------------
        # Skip footer contact information
        # -------------------------------------------------
        if "helpdesk-foscos" in line.lower():
            continue

        if "1800112100" in line:
            continue

        # -------------------------------------------------
        # Keep useful content
        # -------------------------------------------------
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


# ---------------------------------------------------------
# Convert structured JSON pages into LangChain Documents
# ---------------------------------------------------------
def load_fssai_documents():

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Structured data file not found: {DATA_FILE}"
        )

    # -----------------------------------------------------
    # Load the structured Playwright JSON data
    # -----------------------------------------------------
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        scraped_pages = json.load(file)

    documents = []

    for page in scraped_pages:

        raw_content = page.get("content", "")

        cleaned_content = clean_page_text(
            raw_content
        )

        # -------------------------------------------------
        # Ignore documents containing no useful content
        # -------------------------------------------------
        if not cleaned_content.strip():
            continue

        # -------------------------------------------------
        # Create one LangChain Document for each webpage
        # -------------------------------------------------
        document = Document(
            page_content=cleaned_content,

            metadata={
                "source": "FSSAI",

                "category": page.get(
                    "category",
                    "Unknown"
                ),

                "title": page.get(
                    "title",
                    "Unknown"
                ),

                "source_url": page.get(
                    "url",
                    ""
                ),

                "scraped_at": page.get(
                    "scraped_at",
                    ""
                ),

                "data_type":
                    "official_food_safety_content"
            }
        )

        documents.append(document)

    return documents


# ---------------------------------------------------------
# Test the document loader
# ---------------------------------------------------------
if __name__ == "__main__":

    documents = load_fssai_documents()

    print("=" * 70)
    print(
        "STRUCTURED LANGCHAIN DOCUMENT LOADING COMPLETED"
    )
    print("=" * 70)

    print(
        f"\nNumber of documents loaded: "
        f"{len(documents)}"
    )

    for index, document in enumerate(
        documents,
        start=1
    ):

        print("\n" + "=" * 70)

        print(
            f"DOCUMENT {index}"
        )

        print("=" * 70)

        print("\nMetadata:")
        print(
            document.metadata
        )

        print(
            "\nFirst 700 characters:"
        )

        print("-" * 70)

        print(
            document.page_content[:700]
        )

        print(
            f"\nCleaned character count: "
            f"{len(document.page_content):,}"
        )