import unittest
from lark import Lark
from src.p4.interpreter import Interpreter  # adjust import if needed

# Define terminals your grammar needs
terminals = """
_FUNCTION: "function"
_IF: "if"
_THEN: "then"
_ELSE: "else"
_WHILE: "while"
_DO: "do"
_RETURN: "return"
_OUTPUT: "output"
_INPUT: "input"
_TYPE: "integer" | "boolean" | "string" | "decimal" | "noType"
"""

# Load your grammar file
with open("../grammar/grammar.lark") as f:
    grammar = f.read()

# Combine terminals and grammar
full_grammar = terminals + "\n" + grammar

# Replace placeholders if any, for example:
full_grammar = full_grammar.replace("__TYPE_ALTS__", '"integer" | "boolean" | "string" | "decimal" | "noType"')

# Create the Lark parser with full grammar string
parser = Lark(full_grammar, parser="earley", start="start", lexer="dynamic")

class TestIntegration(unittest.TestCase):
    def test_output_addition(self):
        code = """
Language DK
Case camelCase

function integer main() {
    output 2 + 3
}
"""
        # Parse your code
        tree = parser.parse(code)

        # Create and run interpreter visitor on parse tree
        interpreter = Interpreter()
        interpreter.visit(tree)

        # Define expected output (adjust to your interpreter's output format)
        expected_output = [5]
        self.assertEqual(interpreter.output, expected_output)

if __name__ == '__main__':
    unittest.main()
