import unittest
from io import StringIO
from unittest.mock import patch
from pathlib import Path

from src.p4.interpreter import Interpreter
from src.p4.environment import Environment
from lark import Lark
from src.p4.parse_tree_processor import make_parser
from src.p4.parse_tree_processor import ParseTreeProcessor
from src.p4.semantics_checker import TypeError_
from src.p4.semantics_checker import SemanticsChecker


GRAMMAR_PATH = Path(__file__).resolve().parents[1] / "grammar" / "grammar.lark"

with open(GRAMMAR_PATH, "r", encoding="utf-8") as grammar_file:
    grammar = grammar_file.read()

parser = make_parser("EN")

class TestSemantics(unittest.TestCase):

    def test_add_mul_1(self):
        try:
            # open test source
            with open("test_sample_old/test_add_mul_1", "r") as src_file:
                sample_input = src_file.read()
                print(sample_input)
        except FileNotFoundError:
            print("Error reading file")
            return
        self.semantics_checker = TestSemantics()
        tree = parser.parse(sample_input)
        processor = ParseTreeProcessor()
        processed_tree = processor.transform(tree)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.semantics_checker.visit(processed_tree)
            result = self.semantics_checker.visit_arit_expr(node)
            self.assertEqual(result, "integer")