import unittest
from unittest import result

from src.p4.interpreter import Interpreter

from src.p4.env import Environment


class DummyNode:
    def __init__(self, children):
        self.children = children

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

class test_uminus(unittest.TestCase):
    def setUp(self):
        class TestInterpreter(Interpreter):
            def visit(self, node):
                return node
        self.interpreter = TestInterpreter()

    def test_uminus(self):
        node = DummyNode(["-", 3])
        result = self.interpreter.visit_uminus(node)
        self.assertEqual(result, -3)

class test_negate(unittest.TestCase):
    def setUp(self):
        class TestInterpreter(Interpreter):
            def visit(self, node):
                return node
        self.interpreter = TestInterpreter()

    def test_negate_true(self):
        node = DummyNode([True])
        result = self.interpreter.visit_negate(node)
        self.assertEqual(result, False)

    def test_negate_false(self):
        node = DummyNode([False])
        result = self.interpreter.visit_negate(node)
        self.assertEqual(result, True)

    #def test_negate_fail(self):
    #    node = DummyNode([9])
    #    result = self.interpreter.visit_negate(node)
    #    self.assertEqual(result, True)

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

    def test_addition_and_subtraction_1(self):
        node = DummyNode([10, "-", 3, "+", 2])
        result = self.interpreter.visit_add_expr(node)
        self.assertEqual(result, 9)

    def test_addition_and_subtraction_2(self):
        node = DummyNode([-10, "-", 10, "+", 5])
        result = self.interpreter.visit_add_expr(node)
        self.assertEqual(result, -15)

    #def test_addition_and_subtraction_fail(self):
    #    node = DummyNode([-10, "*", 10, "+", 5])
    #    result = self.interpreter.visit_add_expr(node)
    #    self.assertEqual(result, -15)

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

    def test_division_2(self):
        node = DummyNode([-10, "/", 2])
        result = self.interpreter.visit_mul_expr(node)
        self.assertEqual(result, -5)

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

    #def test_equal_fail(self):
    #    node = DummyNode([1, "+", 1])
    #    result = self.interpreter.visit_equality_expr(node)
    #    self.assertEqual(result, 1)

    def test_not_equal(self):
        node = DummyNode([1, "!=", 2])
        result = self.interpreter.visit_equality_expr(node)
        self.assertEqual(result, 1)

    def test_not_equal_2(self):
        node = DummyNode([1, "!=", 1])
        result = self.interpreter.visit_equality_expr(node)
        self.assertEqual(result, 0)

    #def test_not_equal_fail(self):
    #    node = DummyNode([1, "+", 1])
    #    result = self.interpreter.visit_equality_expr(node)
    #    self.assertEqual(result, 0)

    def test_equal_not_equal_1(self):
        node = DummyNode([1, "==", 1, "!=", False])
        result = self.interpreter.visit_equality_expr(node)
        self.assertEqual(result, True)

    def test_equal_not_equal_2(self):
        node = DummyNode([1, "==", 2, "!=", False])
        result = self.interpreter.visit_equality_expr(node)
        self.assertEqual(result, False)

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

    #def test_greater_fail(self):
    #    node = DummyNode([1, "+", 2])
    #    result = self.interpreter.visit_relational_expr(node)
    #    self.assertEqual(result, 0)

    def test_smaller_equal(self):
        node = DummyNode([1, "<=", 1])
        result = self.interpreter.visit_relational_expr(node)
        self.assertEqual(result, 1)

    def test_greater_equal(self):
        node = DummyNode([2, ">=", 1])
        result = self.interpreter.visit_relational_expr(node)
        self.assertEqual(result, 1)

    #def test_greater_equal_fail(self):
    #    node = DummyNode([2, "+", 1])
    #    result = self.interpreter.visit_relational_expr(node)
    #    self.assertEqual(result, 1)

    def test_greater_equal_comb_1(self):
        node = DummyNode([2, ">=", 1, "==", True])
        result = self.interpreter.visit_relational_expr(node)
        self.assertEqual(result, True)

    def test_greater_equal_comb_2(self):
        node = DummyNode([2, ">=", 3, "==", True])
        result = self.interpreter.visit_relational_expr(node)
        self.assertEqual(result, False)


class test_and_or_expr(unittest.TestCase):
    def setUp(self):
        class TestInterpreter(Interpreter):
            def visit(self, node):
                return node
        self.interpreter = TestInterpreter()

    def test_and_expr_1(self):
        node = DummyNode([True, True])
        result = self.interpreter.visit_and_expr(node)
        self.assertEqual(result, True)

    def test_and_expr_2(self):
        node = DummyNode([True, False])
        result = self.interpreter.visit_and_expr(node)
        self.assertEqual(result, False)

    def test_and_expr_1(self):
        node = DummyNode([False, True])
        result = self.interpreter.visit_and_expr(node)
        self.assertEqual(result, False)

    def test_and_expr_1(self):
        node = DummyNode([False, False])
        result = self.interpreter.visit_and_expr(node)
        self.assertEqual(result, False)

    def test_or_expr(self):
        node = DummyNode([True, True])
        result = self.interpreter.visit_or_expr(node)
        self.assertEqual(result, True)

    def test_or_expr(self):
        node = DummyNode([True, False])
        result = self.interpreter.visit_or_expr(node)
        self.assertEqual(result, True)

    def test_or_expr(self):
        node = DummyNode([False, True])
        result = self.interpreter.visit_or_expr(node)
        self.assertEqual(result, True)

    def test_or_expr(self):
        node = DummyNode([False, False])
        result = self.interpreter.visit_or_expr(node)
        self.assertEqual(result, False)
