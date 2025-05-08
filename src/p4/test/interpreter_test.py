import unittest
from unittest import result

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

class test_mul_expr(unittest.TestCase):
    def setUp(self):
        class TestInterpreter(Interpreter):
            def visit(self, node):
                return node
        self.interpreter = TestInterpreter()

    def test_multiplication(self):
        node = DummyNode([1, "*", 2, "*", 3])
        result = self.interpreter.visit_mul_expr(node)
        self.assertEqual(result, 6)

    def test_multiplication_2(self):
        node = DummyNode([-3, "*", 2, "*", 1])
        result = self.interpreter.visit_mul_expr(node)
        self.assertEqual(result, -6)

    def test_division(self):
        node = DummyNode([10, "/", 2, "/", 2])
        result = self.interpreter.visit_mul_expr(node)
        self.assertEqual(result, 2.5)

    #def test_division_zero(self):
    #    node = DummyNode([10, "/", 2, "/", 0])
    #    result = self.interpreter.visit_mul_expr(node)
    #    self.assertEqual(result, 0)

    def test_modulo(self):
        node = DummyNode([10, "%", 2])
        result = self.interpreter.visit_mul_expr(node)
        self.assertEqual(result, 0)

    def test_modulo_decimal(self):
        node = DummyNode([10.5, "%", 2])
        result = self.interpreter.visit_mul_expr(node)
        self.assertEqual(result, 0.5)

class test_equality_expr(unittest.TestCase):
    def setUp(self):
        class TestInterpreter(Interpreter):
            def visit(self, node):
                return node
        self.interpreter = TestInterpreter()

    def test_equal(self):
        node = DummyNode([1, "==", 2])
        result = self.interpreter.visit_equality_expr(node)
        self.assertEqual(result, 0)

    def test_equal_2(self):
        node = DummyNode([1, "==", 1])
        result = self.interpreter.visit_equality_expr(node)
        self.assertEqual(result, 1)

    def test_not_equal(self):
        node = DummyNode([1, "!=", 2])
        result = self.interpreter.visit_equality_expr(node)
        self.assertEqual(result, 1)

    def test_not_equal_2(self):
        node = DummyNode([1, "!=", 1])
        result = self.interpreter.visit_equality_expr(node)
        self.assertEqual(result, 0)

class test_relational_expr(unittest.TestCase):
    def setUp(self):
        class TestInterpreter(Interpreter):
            def visit(self, node):
                return node
        self.interpreter = TestInterpreter()

    def test_smaller(self):
        node = DummyNode([1, "<", 2])
        result = self.interpreter.visit_relational_expr(node)
        self.assertEqual(result, 1)

    def test_greater(self):
        node = DummyNode([1, ">", 2])
        result = self.interpreter.visit_relational_expr(node)
        self.assertEqual(result, 0)

    def test_smaller_equal(self):
        node = DummyNode([1, "<=", 1])
        result = self.interpreter.visit_relational_expr(node)
        self.assertEqual(result, 1)

    def test_greater_equal(self):
        node = DummyNode([2, ">=", 1])
        result = self.interpreter.visit_relational_expr(node)
        self.assertEqual(result, 1)

class test_and_or_expr(unittest.TestCase):
    def setUp(self):
        class TestInterpreter(Interpreter):
            def visit(self, node):
                return node
        self.interpreter = TestInterpreter()

    def test_and_expr(self):
        node = DummyNode(["true", "true"])
        result = self.interpreter.visit_and_expr(node)
        self.assertEqual(result, "true")

    def test_or_expr(self):
        node = DummyNode(["true","false"])
        result = self.interpreter.visit_or_expr(node)
        self.assertEqual(result, "true")