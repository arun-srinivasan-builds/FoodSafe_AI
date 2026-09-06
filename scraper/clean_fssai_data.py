from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

INPUT_FILE = DATA_DIR / "fssai_scraped_raw.txt"
OUTPUT_FILE = DATA_DIR / "fssai_cleaned_data.txt"


def clean_text(text: str) -> str:
    # Normalize line endings
    text = text.replace("\r\n", "\n")

    # Remove excessive spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove empty lines containing only spaces
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]

    return "\n".join(lines)


def remove_common_noise(text: str) -> str:
    noise_phrases = [
        "Skip to main content",
        "Screen Reader Access",
        "A+",
        "A-",
        "A A",
        "Home",
        "Contact Us",
        "Sitemap",
        "Privacy Policy",
        "Terms and Conditions",
        "Copyright Policy",
    ]

    cleaned_lines = []

    for line in text.splitlines():
        if line.strip() not in noise_phrases:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def main():
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return

    raw_text = INPUT_FILE.read_text(encoding="utf-8")

    cleaned_text = clean_text(raw_text)
    cleaned_text = remove_common_noise(cleaned_text)
    cleaned_text = clean_text(cleaned_text)

    OUTPUT_FILE.write_text(cleaned_text, encoding="utf-8")

    print("=" * 70)
    print("DATA CLEANING COMPLETED")
    print("=" * 70)

    print(f"Raw file     : {INPUT_FILE}")
    print(f"Cleaned file : {OUTPUT_FILE}")

    print(f"\nRaw characters     : {len(raw_text):,}")
    print(f"Cleaned characters : {len(cleaned_text):,}")


if __name__ == "__main__":
    main()