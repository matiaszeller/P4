from pathlib import Path
import re
from typing import Tuple
from lark import Lark, Transformer, Token, Tree

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

HEADER_RE = re.compile(
    r"^Language\s+(?P<lang>EN|DK)\s*\nCase\s+(?P<case>camelCase|snake_case)",
    re.IGNORECASE,
)

def extract_header(src: str) -> Tuple[str, str]:
    m = HEADER_RE.match(src)
    if not m:
        raise ValueError("first two lines must be 'Language …' and 'Case …'")
    return m.group("lang"), m.group("case")

def make_parser(lang: str) -> Lark:
    try:
        kw_map = KEYWORDS[lang]
    except KeyError:
        raise ValueError(f"Unsupported language {lang}")

    injected = "\n".join(f'_{name}: "{literal}"' for name, literal in kw_map.items())
    grammar = BASE_GRAMMAR + "\n\n" + injected
    return Lark(grammar, start="start", parser="earley", lexer="dynamic")

class ParseTreeProcessor(Transformer):
    def start(self, items):
        return Tree('start', [item for item in items if item is not None])

    def syntax(self, items):
        return Tree('syntax', [item for item in items if item is not None])

    def NEWLINE(self, tok):
        return None

    def LANG(self, tok):
        return tok

    def CASE(self, tok):
        return tok

    def function_definition(self, items):
        return Tree('function_definition', [item for item in items if item is not None])

    def block(self, items):
        return Tree('block', [item for item in items if item is not None])

    def declaration_stmt(self, items):
        return Tree('declaration_stmt', items)

    def assignment_stmt(self, items):
        return Tree('assignment_stmt', items)

    def if_stmt(self, items):
        return Tree('if_stmt', items)

    def output_stmt(self, items):
        return Tree('output_stmt', items)

    def lvalue(self, items):
        return Tree('lvalue', items)

    def expr_stmt(self, items):
        return Tree('expr_stmt', items)

    def add_expr(self, items):
        return Tree('arit_expr', items)

    def mul_expr(self, items):
        return Tree('arit_expr', items)

    def arit_expr(self, items):
        if len(items) == 1:
            return items[0]
        left = items[0]
        i = 1
        while i < len(items):
            op = items[i]
            right = items[i + 1]
            left = Tree('arit_expr', [left, op, right])
            i += 2
        return left

    def _build_logical(self, op_str, items):
        if len(items) == 1:
            return items[0]
        left = items[0]
        for right in items[1:]:
            op = Token('LOGIC_OP', op_str)
            left = Tree('logical_expr', [left, op, right])
        return left

    def and_expr(self, items):
        return self._build_logical('and', items)

    def or_expr(self, items):
        return self._build_logical('or', items)

    def equality_expr(self, items):
        return Tree('compare_expr', items)

    def relational_expr(self, items):
        return Tree('compare_expr', items)

    def compare_expr(self, items):
        return items[0] if len(items) == 1 else Tree('compare_expr', items)

    def uminus(self, items):
        return Tree('uminus', items)

    def negate(self, items):
        return Tree('negate', items)

    def postfix_expr(self, items):
        return Tree('postfix_expr', items)

    def call_suffix(self, items):
        return Tree('call_suffix', items)

    def array_access_suffix(self, items):
        return Tree('array_access_suffix', items)

    def expr(self, items):
        return items[0]

    def primary(self, items):
        return items[0]

    def TYPE(self, tok):
        return tok

    def ID(self, tok):
        return tok

    def INT(self, tok):
        return tok

    def BOOLEAN(self, tok):
        return tok

    def STRING(self, tok):
        return tok