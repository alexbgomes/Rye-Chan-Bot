# General helper functions for Rye-Chan-Bot

def escape_markdown(text: str) -> str:
    """Escapes discord markdown characters in a string."""
    markdown_chars = ["*", "_", "~", "`", ">", "|"]
    for char in markdown_chars:
        text = text.replace(char, f"\\{char}")
    return text
