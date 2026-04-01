import re

def clean_text(text):
    if not text:
        return ""

    # Remove "Recommended Stories" sections
    text = re.sub(r"Recommended Stories.*?(?=\n[A-Z])", "", text, flags=re.DOTALL)

    # Remove "Published On"
    text = re.sub(r"Published On.*", "", text)

    # Remove duplicate first lines
    lines = text.split("\n")
    if len(lines) > 1 and lines[0] == lines[1]:
        lines = lines[1:]
    text = "\n".join(lines)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()