
def sanitize_html_context(intext):
    bad_chars = ["\"", "'", "(", ")", "\\\\", "<", ">"]
    for c in bad_chars:
        intext = intext.replace(c, "")
    return intext
