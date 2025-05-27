import unittest

from lark.exceptions import UnexpectedCharacters
from io import StringIO
from unittest.mock import patch
from pathlib import Path
from src.p4.interpreter import Interpreter
from src.p4.parse_tree_processor import make_parser
from src.p4.parse_tree_processor import ParseTreeProcessor
from src.p4.error import IndexRangeError, UndeclaredNameError, DuplicateNameError

GRAMMAR_PATH = Path(__file__).resolve().parents[1] / "grammar" / "grammar.lark"
with open(GRAMMAR_PATH, "r", encoding="utf-8") as grammar_file:
    grammar = grammar_file.read()
parser = make_parser("EN")

class integration_testing_interpreter(unittest.TestCase):

    def test_arit_expr_comb(self):
        try:
            # open test source
            with open("test_sample/test_arit_expr_comb", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpreter = Interpreter()
        tree = parser.parse(sample_input)
        processor = ParseTreeProcessor()
        processed_tree = processor.transform(tree)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.visit(processed_tree)
            output = fake_out.getvalue().strip()
            self.assertIn("38.5", output)

    def test_compare_expr_comb(self):
        try:
            # open test source
            with open("test_sample/test_compare_expr_comb", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpreter = Interpreter()
        tree = parser.parse(sample_input)
        processor = ParseTreeProcessor()
        processed_tree = processor.transform(tree)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.visit(processed_tree)
            output = fake_out.getvalue().strip()
            self.assertIn("True", output)

    def test_logical_expr_comb(self):
        try:
            # open test source
            with open("test_sample/test_logical_expr_comb", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpreter = Interpreter()
        tree = parser.parse(sample_input)
        processor = ParseTreeProcessor()
        processed_tree = processor.transform(tree)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.visit(processed_tree)
            output = fake_out.getvalue().strip()
            self.assertIn("False", output)

    def test_decl_assign(self):
        try:
            # open test source
            with open("test_sample/test_decl_assign", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpreter = Interpreter()
        tree = parser.parse(sample_input)
        processor = ParseTreeProcessor()
        processed_tree = processor.transform(tree)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.visit(processed_tree)
            output = fake_out.getvalue().strip()
            self.assertIn("10", output)

    def test_shadowing(self):
        with open("test_sample/test_shadowing") as src:
            sample_input = src.read()

        interpreter = Interpreter()
        tree       = parser.parse(sample_input)
        processed  = ParseTreeProcessor().transform(tree)

        with self.assertRaisesRegex(DuplicateNameError, r'Duplicate name'):
            interpreter.visit(processed)

    def test_undeclared(self):
        with open("test_sample/test_undeclared") as src:
            sample_input = src.read()

        interpreter = Interpreter()
        tree       = parser.parse(sample_input)
        processed  = ParseTreeProcessor().transform(tree)

        with self.assertRaisesRegex(UndeclaredNameError, r'Undeclared name'):
            interpreter.visit(processed)

    def test_if(self):
        try:
            # open test source
            with open("test_sample/test_if", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpreter = Interpreter()
        tree = parser.parse(sample_input)
        processor = ParseTreeProcessor()
        processed_tree = processor.transform(tree)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.visit(processed_tree)
            output = fake_out.getvalue().strip()
            self.assertIn("discount applied", output)

    def test_else(self):
        try:
            # open test source
            with open("test_sample/test_else", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpreter = Interpreter()
        tree = parser.parse(sample_input)
        processor = ParseTreeProcessor()
        processed_tree = processor.transform(tree)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.visit(processed_tree)
            output = fake_out.getvalue().strip()
            self.assertIn("discount not applied", output)

    def test_bool_variable_true(self):
        try:
            # open test source
            with open("test_sample/test_bool_variable_true", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpreter = Interpreter()
        tree = parser.parse(sample_input)
        processor = ParseTreeProcessor()
        processed_tree = processor.transform(tree)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.visit(processed_tree)
            output = fake_out.getvalue().strip()
            self.assertIn("True working", output)

    def test_bool_variable_false(self):
        try:
            # open test source
            with open("test_sample/test_bool_variable_false", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpreter = Interpreter()
        tree = parser.parse(sample_input)
        processor = ParseTreeProcessor()
        processed_tree = processor.transform(tree)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.visit(processed_tree)
            output = fake_out.getvalue().strip()
            self.assertIn("False working", output)

    def test_while_true(self):
        try:
            # open test source
            with open("test_sample/test_while_true", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpreter = Interpreter()
        tree = parser.parse(sample_input)
        processor = ParseTreeProcessor()
        processed_tree = processor.transform(tree)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.visit(processed_tree)
            output = fake_out.getvalue().strip()
            self.assertIn("5", output)

    def test_while_false(self):
        try:
            # open test source
            with open("test_sample/test_while_false", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpreter = Interpreter()
        tree = parser.parse(sample_input)
        processor = ParseTreeProcessor()
        processed_tree = processor.transform(tree)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.visit(processed_tree)
            output = fake_out.getvalue().strip()
            self.assertIn("1", output)

    def test_array_access(self):
        try:
            # open test source
            with open("test_sample/test_array_access", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpreter = Interpreter()
        tree = parser.parse(sample_input)
        processor = ParseTreeProcessor()
        processed_tree = processor.transform(tree)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.visit(processed_tree)
            output = fake_out.getvalue().strip()
            self.assertIn("2", output)

    def test_array_2d(self):
        try:
            # open test source
            with open("test_sample/test_array_2d", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpreter = Interpreter()
        tree = parser.parse(sample_input)
        processor = ParseTreeProcessor()
        processed_tree = processor.transform(tree)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.visit(processed_tree)
            output = fake_out.getvalue().strip()
            self.assertIn("3", output)

    def test_array_assign_fail(self):
        with open("test_sample/test_array_assign_fail") as src:
            sample_input = src.read()
        with self.assertRaises(UnexpectedCharacters):
            tree = parser.parse(sample_input)

    def test_array_access_fail(self):
        try:
            with open("test_sample/test_array_access_fail", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpreter = Interpreter()
        tree = parser.parse(sample_input)
        processed = ParseTreeProcessor().transform(tree)

        with self.assertRaisesRegex(IndexRangeError, r'exceeds the upper limit'):
            interpreter.visit(processed)

    def test_function_call(self):
        try:
            # open test source
            with open("test_sample/test_function_call", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpreter = Interpreter()
        tree = parser.parse(sample_input)
        processor = ParseTreeProcessor()
        processed_tree = processor.transform(tree)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpreter.visit(processed_tree)
            output = fake_out.getvalue().strip()
            self.assertIn("", output)