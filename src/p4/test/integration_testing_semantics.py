import unittest

from io import StringIO
from unittest.mock import patch
from pathlib import Path
from src.p4.interpreter import Interpreter
from src.p4.parse_tree_processor import make_parser
from src.p4.parse_tree_processor import ParseTreeProcessor
from src.p4.semantics_checker import ScopeError

GRAMMAR_PATH = Path(__file__).resolve().parents[1] / "grammar" / "grammar.lark"
with open(GRAMMAR_PATH, "r", encoding="utf-8") as grammar_file:
    grammar = grammar_file.read()
parser = make_parser("EN")

class integration_testing_interpreter(unittest.TestCase):

    def test_shadowing(self):
        try:
            # open test source
            with open("test_sample/test_undeclared", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpretor = Interpreter()
        tree = parser.parse(sample_input)
        processor = ParseTreeProcessor()
        processed_tree = processor.transform(tree)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpretor.visit(processed_tree)
            output = fake_out.getvalue().strip()
            self.assertRaises(NameError, output)