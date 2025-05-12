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

#    def test_declaration(self):
#        try:
#            # open test source
#            with open("test_sample/test_decl", "r") as src_file:
#                sample_input = src_file.read()
#        except FileNotFoundError:
#            print("Error reading file")
#            return
#        interpretor = Interpreter()
#        tree = parser.parse(sample_input)
#
#        with patch('sys.stdout', new=StringIO()) as fake_out:
#            interpretor.visit(tree)
#            output = fake_out.getvalue().strip()
#            self.assertIn(None, output)

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