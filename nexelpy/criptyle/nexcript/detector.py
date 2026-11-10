import re


def is_typescript(code: str) -> bool:
    """
    Heuristic detection of TypeScript vs JavaScript.
    Returns True if the code looks like TypeScript.
    """
    patterns = [
        # Type annotations on variables/parameters
        r":\s*(?:string|number|boolean|any|void|null|undefined|object|unknown|never|bigint|symbol)\b",
        # Array types
        r":\s*Array<",
        r":\s*Record<",
        r":\s*\w+\[\]",
        # Interfaces
        r"interface\s+\w+\s*\{",
        # Type aliases
        r"type\s+\w+\s*=",
        # Generic functions
        r"<\w+(?:,\s*\w+)*>\s*\(",
        # Type assertions
        r"\bas\s+\w+",
        # Non-null assertion operator
        r"!\s*[\.;]",
        # Optional properties in interfaces
        r"\?\s*:",
        # Enums
        r"enum\s+\w+\s*\{",
        # Type imports
        r"import\s+type\s+",
        r"export\s+type\s+",
        # Function return types
        r"\)\s*:\s*\w+",
        # Visibility modifiers (TypeScript class features)
        r"\b(?:public|private|protected|readonly)\s+\w+",
    ]
    for pattern in patterns:
        if re.search(pattern, code):
            return True
    return False
