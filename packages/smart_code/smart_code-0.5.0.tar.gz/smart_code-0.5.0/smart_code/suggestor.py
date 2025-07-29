def format_suggestions(suggestions):
    lines = []
    for fname, lineno, pname, msg in suggestions:
        lines.append(f"{fname}:{lineno} [{pname}] {msg}")
    return '\n'.join(lines)
