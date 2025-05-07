from pathlib import Path
import re
from typing import Tuple

from lark import Lark

# Keyword Table
KEYWORDS = {
    "EN": dict(
        FUNCTION="function",
        NEW="new",
        IF="if",
        THEN="then",
        ELSE="else",
        WHILE="while",
        DO="do",
        RETURN="return",
        OUTPUT="output",
        INPUT="input",
    ),
    "DK": dict(
        FUNCTION="funktion",
        NEW="ny",
        IF="hvis",
        THEN="så",
        ELSE="ellers",
        WHILE="mens",
        DO="gør",
        RETURN="returner",
        OUTPUT="skriv",
        INPUT="indlæs",
    ),
}

BASE_GRAMMAR = Path("grammar/grammar.lark").read_text(encoding="utf-8")

# Header extraction
HEADER_RE = re.compile(
    r"^Language\s+(?P<lang>EN|DK)\s*\nCase\s+(?P<case>camelCase|snake_case)",
    re.IGNORECASE,
)

def extract_header(src: str) -> Tuple[str, str]:
    m = HEADER_RE.match(src)
    if not m:
        raise ValueError("first two lines must be 'Language …' and 'Case …'")
    return m.group("lang"), m.group("case")


# Parser Builder
def make_parser(lang: str) -> Lark:
    try:
        kw_map = KEYWORDS[lang]
    except KeyError:
        raise ValueError(f"Unsupported language {lang}")

    # Each token pattern is injected as TOKEN: "literal"
    injected = "\n".join(f'{name}: "{literal}"' for name, literal in kw_map.items())

    grammar = BASE_GRAMMAR + "\n\n// ── injected literals ──\n" + injected
    return Lark(grammar, start="start", parser="earley", lexer="dynamic")