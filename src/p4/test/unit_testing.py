import unittest
from unittest import result

from src.p4.interpreter import Interpreter

from src.p4.environment import Environment


class DummyNode:
    #def __init__(self, children):
    #    self.children = children
    def make_dummy_tree(self, rule_name.children):


class test_isBoolean(unittest.TestCase):
    def setUp(self):
        class TestInterpreter(Interpreter):
            def visit(self, node):
                return node
        self.interpreter = TestInterpreter()

    def test_true(self):
        node = True
        result = self.interpreter.isBoolean(node)
        self.assertTrue(result, True)

    def test_false(self):
        node = False
        result = self.interpreter.isBoolean(node)
        self.assertTrue(result, False)

    #def test_fail(self):
    #    node = 9
    #    result = self.interpreter.isBoolean(node)
    #    self.assertTrue(result, True)

class test_decimal(unittest.TestCase):
    def setUp(self):
        class TestInterpreter(Interpreter):
            def visit(self, node):
                return node
        self.interpreter = TestInterpreter()

    def test_decimal(self):
        node = DummyNode([2,5])
        result = self.interpreter.visit_decimal(node)
        self.assertEqual(result, 2.5)
        self.assertIsInstance(result, float)

class test_string(unittest.TestCase):
    def setUp(self):
        class TestInterpreter(Interpreter):
            def visit(self, node):
                return node
        self.interpreter = TestInterpreter()

    def test_string(self):
        node = DummyNode(["Hi"])
        result = self.interpreter.visit_string(node)
        self.assertEqual(result, "Hi")
        self.assertIsInstance(result, str)