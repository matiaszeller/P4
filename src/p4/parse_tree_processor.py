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
        OR="or",
        AND="and"
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
        OUTPUT="udskriv",
        INPUT="indskriv",
        OR="eller",
        AND="og"
    ),
}

# language-specific literal list for the TYPE token
TYPE_ALTS = {
    "EN": '"boolean" | "integer" | "decimal" | "string" | "noType"',
    "DK": '"boolean" | "heltal" | "kommatal" | "tekst" | "ingenType"',
}

TYPE_MAP = {
    "heltal": "integer",
    "kommatal": "decimal",
    "tekst": "string",
    "ingenType": "noType",
}

BASE_GRAMMAR = (Path(__file__).resolve().parent / "grammar" / "grammar.lark").read_text(encoding="utf-8")

HEADER_RE = re.compile(r"^Language\s+(EN|DK)\s*$", re.IGNORECASE)

def extract_language(src: str) -> str:
    first_line = src.lstrip().splitlines()[0]
    m = HEADER_RE.match(first_line)
    return m.group(1)

def make_parser(lang: str) -> Lark:
    try:
        kw_map   = KEYWORDS[lang]
        type_alt = TYPE_ALTS[lang]
    except KeyError:
        raise ValueError(f"Unsupported language {lang}")

    injected_keywords = "\n".join(f'_{n}: "{lit}"' for n, lit in kw_map.items())

    grammar = (
        BASE_GRAMMAR
        .replace("__TYPE_ALTS__", type_alt)
        + "\n\n"
        + injected_keywords
    )
    return Lark(grammar, start="start", parser="earley", lexer="dynamic")

class ParseTreeProcessor(Transformer):
    def start(self, items):
        return Tree('start', [i for i in items if i is not None])

    def syntax(self, items):
        return Tree('syntax', [i for i in items if i is not None])

    def NEWLINE(self, tok): return None
    def LANG(self, tok): return tok
    def CASE(self, tok): return tok

    def function_definition(self, items):
        return Tree('function_definition', [i for i in items if i is not None])

    def block(self, items):
        return Tree('block', [i for i in items if i is not None])

    def declaration_stmt(self, items): return Tree('declaration_stmt', items)
    def assignment_stmt(self, items): return Tree('assignment_stmt', items)
    def if_stmt(self, items): return Tree('if_stmt', items)
    def output_stmt(self, items): return Tree('output_stmt', items)
    def lvalue(self, items): return Tree('lvalue', items)
    def expr_stmt(self, items): return Tree('expr_stmt', items)

    def add_expr(self, items): return self.arit_expr(items)
    def mul_expr(self, items): return self.arit_expr(items)

    def arit_expr(self, items):
        if len(items) == 1:
            return items[0]
        left = items[0]
        i = 1
        while i < len(items):
            op, right = items[i], items[i + 1]
            left = Tree('arit_expr', [left, op, right])
            i += 2
        return left

    def build_logical(self, op_str, items):
        if len(items) == 1:
            return items[0]
        left = items[0]
        for right in items[1:]:
            op = Token('LOGIC_OP', op_str)
            left = Tree('logical_expr', [left, op, right])
        return left

    def and_expr(self, items): return self.build_logical('and', items)
    def or_expr(self, items): return self.build_logical('or', items)

    def equality_expr(self, items): return Tree('compare_expr', items)
    def relational_expr(self, items): return Tree('compare_expr', items)
    def compare_expr(self, items): return items[0] if len(items) == 1 else Tree('compare_expr', items)

    def uminus(self, items): return Tree('uminus', items)
    def negate(self, items): return Tree('negate', items)

    def postfix_expr(self, items): return Tree('postfix_expr', items)
    def call_suffix(self, items): return Tree('call_suffix', items)
    def array_access_suffix(self, items): return Tree('array_access_suffix', items)
    def array_suffix(self, items): return Tree('array_suffix', items)

    def expr(self, items): return items[0]
    def primary(self, items): return items[0]

    def TYPE(self, tok):
        tok.value = TYPE_MAP.get(tok.value, tok.value)
        return tok

    def ID(self, tok): return tok
    def INT(self, tok): return tok
    def BOOLEAN(self, tok): return tok
    def STRING(self, tok): return tok