

def sanitize_html_context(intext):
    bad_chars = ["\"", "'", "(", ")", "\\\\", "<", ">"]
    for c in bad_chars:
        intext = intext.replace(c, "")
    return intext

def sanitize_spaces(intext):
    sanitized = intext.replace('  ', ' ')
    while intext != sanitized:
        sanitized, intext = sanitized.replace('  ', ' '), sanitized
    return sanitized

