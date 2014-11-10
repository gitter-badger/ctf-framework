

def sanitize_spaces(intext):
    sanitized = intext.replace('  ', ' ')
    while intext != sanitized:
        sanitized, intext = sanitized.replace('  ', ' '), sanitized
    return sanitized

