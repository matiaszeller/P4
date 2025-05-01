import unittest

from src.p4.interpreter import Interpreter

from src.p4.environment import Environment


class DummyNode:
    def __init__(self, children):
        self.children = children


class test_add_expr(unittest.TestCase):
    def setUp(self):
        class TestInterpreter(Interpreter):
            def visit(self, node):
                return node

        self.interpreter = TestInterpreter()

    def test_addition(self):
        node = DummyNode([1, "+", 2, "+", 3])
        result = self.interpreter.visit_add_expr(node)
        self.assertEqual(result, 6)

    def test_addition_2(self):
        node = DummyNode([-3, "+", 2, "+", 1])
        result = self.interpreter.visit_add_expr(node)
        self.assertEqual(result, 0)

    def test_subtraction(self):
        node = DummyNode([3, "-", 2, "-", 1])
        result = self.interpreter.visit_add_expr(node)
        self.assertEqual(result, 0)

    def test_subtraction_2(self):
        node = DummyNode([-1, "-", 2, "-", 3])
        result = self.interpreter.visit_add_expr(node)
        self.assertEqual(result, -6)

    def test_addition_and_subtraction(self):
        node = DummyNode([10, "-", 3, "+", 2])
        result = self.interpreter.visit_add_expr(node)
        self.assertEqual(result, 9)