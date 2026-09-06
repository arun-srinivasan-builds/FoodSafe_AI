from pathlib import Path
from datetime import datetime
import json

from playwright.sync_api import sync_playwright


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

RAW_OUTPUT_FILE = DATA_DIR / "fssai_scraped_raw.txt"
JSON_OUTPUT_FILE = DATA_DIR / "fssai_documents.json"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# OFFICIAL FSSAI / FOSCOS SOURCES
# =========================================================

URLS = [
    {
        "category": "Food Recall",
        "url": "https://fssai.gov.in/food-law/food-recall",
    },
    {
        "category": "Food Recall Consumer Information",
        "url": "https://fssai.gov.in/citizen/about-food-recall",
    },
    {
        "category": "Consumer Complaint Guidance",
        "url": "https://foscos.fssai.gov.in/consumergrievance/faqs",
    },
    {
        "category": "Food Safety Myth Busters",
        "url": "https://fssai.gov.in/myth-buster",
    },
    {
        "category": "FSSAI Knowledge Hub",
        "url": "https://fssai.gov.in/knowledge-hub?tab=books",
    },
    {
        "category": "Check Adulteration at Home",
        "url": "https://fssai.gov.in/citizen/about-check-adulteration",
    },
]


# =========================================================
# FOSCOS FAQ EXPANSION
# =========================================================

def expand_foscos_faqs(page):
    """
    Expand FoSCoS FAQ accordion items before scraping.

    The complaint FAQ page contains answers inside
    collapsible sections. Reading body.inner_text()
    without opening them may capture only the questions.

    This function attempts several safe selectors because
    the exact HTML structure may vary.
    """

    print("FoSCoS FAQ page detected.")
    print("Attempting to expand FAQ answers...")

    # -----------------------------------------------------
    # Wait for FAQ content
    # -----------------------------------------------------

    try:
        page.wait_for_selector(
            "text=FREQUENTLY ASKED QUESTIONS",
            timeout=15000
        )
    except Exception:
        print(
            "Warning: FAQ heading was not detected, "
            "but expansion will still be attempted."
        )


    # -----------------------------------------------------
    # Known FAQ question texts
    # -----------------------------------------------------

    faq_questions = [
        "What is the purpose and objectives of Food Grievance Portal?",
        "What kind of complaints can I submit?",
        "What details do I need to register/ login the system?",
        "What is the process of registering a complaint?",
        "Is it important to attach a supporting docuement along with the compliant or suggestion?",
        "Within what time frame my complaint will be resolved?",
        "Where can I track the complaint already submitted by me?",
        "What is the process of complaint resolution?",
        "Can I edit/modify my complaint or suggestion after it has been submitted?",
        "What should I do if the portal stops responding or displays an error?",
        "Can complaint be submitted via social media handles of FSSAI or Email provided?",
        "Is there provision to lodge complaints against your FSOs in the field?",
        "Can I see my history of the lodged complaints?",
        "Is there any provision for feedback about the quality of resolution of my complaint?",
        "Where can I provide general suggestions to FSSAI?",
    ]


    expanded_count = 0


    # -----------------------------------------------------
    # Method 1:
    # Click each FAQ using its visible question text
    # -----------------------------------------------------

    for question in faq_questions:

        try:
            locator = page.get_by_text(
                question,
                exact=True
            )

            if locator.count() > 0:

                element = locator.first

                element.scroll_into_view_if_needed()

                page.wait_for_timeout(
                    150
                )

                element.click(
                    timeout=3000
                )

                expanded_count += 1

                page.wait_for_timeout(
                    200
                )

        except Exception:
            # Do not fail the complete scrape because
            # one accordion item could not be clicked.
            pass


    print(
        f"FAQ items clicked using question text: "
        f"{expanded_count}"
    )


    # -----------------------------------------------------
    # Method 2 fallback:
    # If very few items were clicked, attempt common
    # Bootstrap/accordion selectors.
    # -----------------------------------------------------

    if expanded_count < 5:

        print(
            "Trying fallback accordion selectors..."
        )

        fallback_selectors = [
            ".panel-heading",
            ".panel-title",
            ".accordion-header",
            ".accordion-button",
            ".card-header",
            "[data-toggle='collapse']",
            "[data-bs-toggle='collapse']",
        ]


        for selector in fallback_selectors:

            try:

                elements = page.locator(
                    selector
                )

                count = elements.count()

                if count == 0:
                    continue

                print(
                    f"Found {count} elements "
                    f"using selector: {selector}"
                )

                for index in range(count):

                    try:

                        element = elements.nth(
                            index
                        )

                        if not element.is_visible():
                            continue

                        text = element.inner_text().strip()

                        # Limit clicks to elements that
                        # appear to be FAQ questions.
                        if "?" not in text:
                            continue

                        element.scroll_into_view_if_needed()

                        element.click(
                            timeout=2500
                        )

                        page.wait_for_timeout(
                            150
                        )

                    except Exception:
                        continue

            except Exception:
                continue


    # -----------------------------------------------------
    # Allow accordion animation/content to finish loading
    # -----------------------------------------------------

    page.wait_for_timeout(
        1500
    )


    # -----------------------------------------------------
    # Diagnostic information
    # -----------------------------------------------------

    try:

        body_text = page.locator(
            "body"
        ).first.inner_text()

        print(
            "FoSCoS text length after FAQ expansion:",
            len(body_text)
        )

    except Exception:
        pass


# =========================================================
# SCRAPE ONE PAGE
# =========================================================

def scrape_page(page, source):
    """
    Scrape one official FSSAI/FoSCoS page.
    """

    category = source["category"]
    url = source["url"]

    print("\n" + "=" * 80)
    print(f"Category: {category}")
    print(f"URL: {url}")
    print("=" * 80)


    # -----------------------------------------------------
    # Open webpage
    # -----------------------------------------------------

    page.goto(
        url,
        wait_until="domcontentloaded",
        timeout=60000
    )


    # -----------------------------------------------------
    # Allow dynamic content to load
    # -----------------------------------------------------

    page.wait_for_timeout(
        2500
    )


    # -----------------------------------------------------
    # Special handling for FoSCoS FAQ page
    # -----------------------------------------------------

    if "foscos.fssai.gov.in/consumergrievance/faqs" in url:

        expand_foscos_faqs(
            page
        )


    # -----------------------------------------------------
    # Read title
    # -----------------------------------------------------

    try:
        title = page.title().strip()

    except Exception:
        title = category


    # -----------------------------------------------------
    # Read page text
    # -----------------------------------------------------

    try:

        content = page.locator(
            "body"
        ).first.inner_text()

        content = content.strip()

    except Exception as exc:

        print(
            f"Could not extract body text: {exc}"
        )

        content = ""


    print(
        f"Characters scraped: {len(content)}"
    )


    # -----------------------------------------------------
    # Return structured document
    # -----------------------------------------------------

    return {
        "category": category,
        "title": title,
        "url": url,
        "scraped_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "content": content,
    }


# =========================================================
# MAIN SCRAPER
# =========================================================

def main():

    print("=" * 80)
    print("FOODSAFE AI - OFFICIAL FSSAI / FOSCOS SCRAPER")
    print("=" * 80)

    print(
        f"\nPages configured: {len(URLS)}"
    )


    documents = []


    with sync_playwright() as playwright:

        # -------------------------------------------------
        # Launch Chromium
        # -------------------------------------------------

        browser = playwright.chromium.launch(
            headless=True
        )


        # -------------------------------------------------
        # Create browser context
        # -------------------------------------------------

        context = browser.new_context(
            viewport={
                "width": 1440,
                "height": 1000,
            }
        )


        # -------------------------------------------------
        # Create page
        # -------------------------------------------------

        page = context.new_page()


        # -------------------------------------------------
        # Scrape every source
        # -------------------------------------------------

        for source in URLS:

            try:

                document = scrape_page(
                    page,
                    source
                )

                documents.append(
                    document
                )

                print(
                    "Status: SUCCESS"
                )

            except Exception as exc:

                print(
                    f"Status: FAILED"
                )

                print(
                    f"Error: {exc}"
                )


        # -------------------------------------------------
        # Close browser
        # -------------------------------------------------

        context.close()
        browser.close()


    # =====================================================
    # SAVE STRUCTURED JSON
    # =====================================================

    with open(
        JSON_OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            documents,
            file,
            ensure_ascii=False,
            indent=4
        )


    # =====================================================
    # SAVE HUMAN-READABLE RAW TEXT
    # =====================================================

    with open(
        RAW_OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        for document in documents:

            file.write(
                "=" * 100
            )

            file.write(
                "\n"
            )

            file.write(
                f"CATEGORY: "
                f"{document['category']}\n"
            )

            file.write(
                f"TITLE: "
                f"{document['title']}\n"
            )

            file.write(
                f"URL: "
                f"{document['url']}\n"
            )

            file.write(
                f"SCRAPED AT: "
                f"{document['scraped_at']}\n"
            )

            file.write(
                "=" * 100
            )

            file.write(
                "\n\n"
            )

            file.write(
                document["content"]
            )

            file.write(
                "\n\n"
            )


    # =====================================================
    # FINAL SUMMARY
    # =====================================================

    print("\n" + "=" * 80)
    print("SCRAPING COMPLETED")
    print("=" * 80)

    print(
        f"Pages scraped: {len(documents)}"
    )

    print(
        f"JSON saved to: "
        f"{JSON_OUTPUT_FILE}"
    )

    print(
        f"Raw text saved to: "
        f"{RAW_OUTPUT_FILE}"
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()