import unittest
from io import StringIO
from unittest.mock import patch

from src.p4.interpreter import Interpreter
from src.p4.env import Environment
from lark import Lark


with open("../grammar/grammar.lark", "r") as grammar_file:
    grammar = grammar_file.read()
parser = Lark(grammar, parser='earley', start='start', lexer='dynamic')

class IntegrationTesting(unittest.TestCase):

    def test_add_mul_1(self):
        try:
            # open test source
            with open("test_sample/test_add_mul_1", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpretor = Interpreter()
        tree = parser.parse(sample_input)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpretor.visit(tree)
            output = fake_out.getvalue().strip()
            self.assertIn("5", output)

    def test_add_mul_2(self):
        try:
            # open test source
            with open("test_sample/test_add_mul_2", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpretor = Interpreter()
        tree = parser.parse(sample_input)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpretor.visit(tree)
            output = fake_out.getvalue().strip()
            self.assertIn("0", output)

    #def test_parentheses(self):
    #    try:
    #        # open test source
    #        with open("test_sample/test_parentheses", "r") as src_file:
    #            sample_input = src_file.read()
    #    except FileNotFoundError:
    #        print("Error reading file")
    #        return
    #    interpretor = Interpreter()
    #    tree = parser.parse(sample_input)

    #    with patch('sys.stdout', new=StringIO()) as fake_out:
    #        interpretor.visit(tree)
    #        output = fake_out.getvalue().strip()
    #        self.assertIn("Both integer", output)

    #def test_parentheses_fail(self):
    #    try:
    #        # open test source
    #        with open("test_sample/test_parentheses_fail", "r") as src_file:
    #            sample_input = src_file.read()
    #    except FileNotFoundError:
    #        print("Error reading file")
    #        return
    #    interpretor = Interpreter()
    #    tree = parser.parse(sample_input)

    #    with patch('sys.stdout', new=StringIO()) as fake_out:
    #        interpretor.visit(tree)
    #        output = fake_out.getvalue().strip()
    #        self.assertIn("Both integer", output)

    def test_declaration(self):
        try:
            # open test source
            with open("test_sample/test_decl", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpretor = Interpreter()
        tree = parser.parse(sample_input)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpretor.visit(tree)
            output = fake_out.getvalue().strip()
            self.assertIn("None", output)

    def test_decl_assign(self):
        try:
            # open test source
            with open("test_sample/test_decl_assign", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpretor = Interpreter()
        tree = parser.parse(sample_input)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpretor.visit(tree)
            output = fake_out.getvalue().strip()
            self.assertIn("10", output)

    #def test_decl_fail(self):
    #    try:
    #        # open test source
    #        with open("test_sample/test_decl_fail", "r") as src_file:
    #            sample_input = src_file.read()
    #    except FileNotFoundError:
    #        print("Error reading file")
    #        return
    #    interpretor = Interpreter()
    #    tree = parser.parse(sample_input)

    #    with patch('sys.stdout', new=StringIO()) as fake_out:
    #        interpretor.visit(tree)
    #        output = fake_out.getvalue().strip()
    #        self.assertIn("10", output)

    #def test_decl_fail_2(self):
    #    try:
    #        # open test source
    #        with open("test_sample/test_decl_fail_2", "r") as src_file:
    #            sample_input = src_file.read()
    #    except FileNotFoundError:
    #        print("Error reading file")
    #        return
    #    interpretor = Interpreter()
    #    tree = parser.parse(sample_input)

    #    with patch('sys.stdout', new=StringIO()) as fake_out:
    #        interpretor.visit(tree)
    #        output = fake_out.getvalue().strip()
    #        self.assertIn("10", output)

    def test_if(self):
        try:
            # open test source
            with open("test_sample/test_if", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpretor = Interpreter()
        tree = parser.parse(sample_input)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpretor.visit(tree)
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
        interpretor = Interpreter()
        tree = parser.parse(sample_input)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpretor.visit(tree)
            output = fake_out.getvalue().strip()
            self.assertIn("discount not applied", output)

    def test_while_true(self):
        try:
            # open test source
            with open("test_sample/test_while_true", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpretor = Interpreter()
        tree = parser.parse(sample_input)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpretor.visit(tree)
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
        interpretor = Interpreter()
        tree = parser.parse(sample_input)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpretor.visit(tree)
            output = fake_out.getvalue().strip()
            self.assertIn("1", output)

    #Cases will also be checked here
    def test_function_call_cc(self):
        try:
            # open test source
            with open("test_sample/test_function_call_cc", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpretor = Interpreter()
        tree = parser.parse(sample_input)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpretor.visit(tree)
            output = fake_out.getvalue().strip()
            self.assertIn("Hello world", output)

    def test_function_call_sc(self):
        try:
            # open test source
            with open("test_sample/test_function_call_sc", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpretor = Interpreter()
        tree = parser.parse(sample_input)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpretor.visit(tree)
            output = fake_out.getvalue().strip()
            self.assertIn("Hello world", output)

    def test_case_fail(self):
        try:
            # open test source
            with open("test_sample/test_case_fail", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpretor = Interpreter()
        tree = parser.parse(sample_input)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpretor.visit(tree)
            output = fake_out.getvalue().strip()
            self.assertIn("Hello world", output)

    def test_bool_literal_true(self):
        try:
            # open test source
            with open("test_sample/test_bool_literal_true", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpretor = Interpreter()
        tree = parser.parse(sample_input)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpretor.visit(tree)
            output = fake_out.getvalue().strip()
            self.assertIn("Bool", output)

    #def test_bool_literal_false(self):
    #    try:
    #        # open test source
    #        with open("test_sample/test_bool_literal_false", "r") as src_file:
    #            sample_input = src_file.read()
    #    except FileNotFoundError:
    #        print("Error reading file")
    #        return
    #    interpretor = Interpreter()
    #    tree = parser.parse(sample_input)

    #    with patch('sys.stdout', new=StringIO()) as fake_out:
    #        interpretor.visit(tree)
    #        output = fake_out.getvalue().strip()
    #        self.assertIn("This won't print", output)

    #def test_bool_variable_true(self):
    #    try:
    #        # open test source
    #        with open("test_sample/test_bool_variable_true", "r") as src_file:
    #            sample_input = src_file.read()
    #    except FileNotFoundError:
    #        print("Error reading file")
    #        return
    #    interpretor = Interpreter()
    #    tree = parser.parse(sample_input)

    #    with patch('sys.stdout', new=StringIO()) as fake_out:
    #        interpretor.visit(tree)
    #        output = fake_out.getvalue().strip()
    #        self.assertIn("", output)


    def test_array_creation(self):
        try:
            # open test source
            with open("test_sample/test_array_creation", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpretor = Interpreter()
        tree = parser.parse(sample_input)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpretor.visit(tree)
            output = fake_out.getvalue().strip()
            self.assertIn("None", output)

    def test_array_creation_assign(self):
        try:
            # open test source
            with open("test_sample/test_array_creation_assign", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpretor = Interpreter()
        tree = parser.parse(sample_input)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpretor.visit(tree)
            output = fake_out.getvalue().strip()
            self.assertIn("[1, 2, 3]", output)

    #def test_array_assign_fail(self):
    #    try:
    #        # open test source
    #        with open("test_sample/test_array_assign_fail", "r") as src_file:
    #            sample_input = src_file.read()
    #    except FileNotFoundError:
    #        print("Error reading file")
    #        return
    #    interpretor = Interpreter()
    #    tree = parser.parse(sample_input)

    #    with patch('sys.stdout', new=StringIO()) as fake_out:
    #        interpretor.visit(tree)
    #        output = fake_out.getvalue().strip()
    #        self.assertIn("10", output)

    def test_array_access(self):
        try:
            # open test source
            with open("test_sample/test_array_access", "r") as src_file:
                sample_input = src_file.read()
        except FileNotFoundError:
            print("Error reading file")
            return
        interpretor = Interpreter()
        tree = parser.parse(sample_input)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            interpretor.visit(tree)
            output = fake_out.getvalue().strip()
            self.assertIn("2", output)

    #def test_array_access_fail(self):
    #    try:
    #        # open test source
    #        with open("test_sample/test_array_access_fail", "r") as src_file:
    #            sample_input = src_file.read()
    #    except FileNotFoundError:
    #        print("Error reading file")
    #        return
    #    interpretor = Interpreter()
    #    tree = parser.parse(sample_input)

    #    with patch('sys.stdout', new=StringIO()) as fake_out:
    #        interpretor.visit(tree)
    #        output = fake_out.getvalue().strip()
    #        self.assertIn("0", output)

