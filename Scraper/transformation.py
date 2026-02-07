def clean_text(text):
    """Removes extra whitespace and newlines."""
    if not text:
        return ""
    # Collapses "Hello   \n  World" -> "Hello World"
    return " ".join(text.split()).strip()

def clean_email(email_text):
    """Fixes anti-spam obfuscation."""
    if not email_text:
        return "Unknown"
    clean = email_text.replace("[at]", "@").replace("(at)", "@")
    clean = clean.replace("[dot]", ".").replace("(dot)", ".")
    return clean.strip()

def clean_list(items):
    """Converts a list into a bulleted string."""
    if not items:
        return ""
    if isinstance(items, str):
        return items
    cleaned_items = [clean_text(i) for i in items if i]
    return "\n".join([f"• {item}" for item in cleaned_items])

def clean_profile(raw_data: dict) -> dict:
    """The Main Transformation Function."""
    return {
        "name": clean_text(raw_data.get("name")),
        "designation": clean_text(raw_data.get("designation")),
        "email": clean_email(raw_data.get("email")),
        "bio": clean_text(raw_data.get("bio")),
        "research": clean_text(raw_data.get("research")),
        "publications": clean_list(raw_data.get("publications")),
        "teaching": clean_text(raw_data.get("teaching")),  # <--- NEW FIELD
        "specialization": clean_text(raw_data.get("specialization")),
        "url": raw_data.get("url")
    }