import unittest
from unittest import result

from src.p4.interpreter import Interpreter
from src.p4.environment import Environment

from lark import Tree, Token


class DummyNode(Tree):
    def __init__(self, rule_name, children):
        super().__init__(rule_name, children)

class test_uminus(unittest.TestCase):
    def setUp(self):
        class TestInterpreter(Interpreter):
            def visit(self, node):
                return super().visit(node)
        self.interpreter = TestInterpreter()

    def test_uminus_integer(self):
        node = (DummyNode('uminus', [
            Token('UMINUS', '-'),
            Token('INT', '5')
        ]))
        result = self.interpreter.visit_uminus(node)
        self.assertEqual(result, -5)

    def test_uminus_decimal(self):
        node = (DummyNode('uminus', [
            Token('UMINUS', '-'),
            Token('FLOAT', '5.5')
        ]))

    #def test_uminus_fail(self):
    #    node = (DummyNode('uminus', [
    #        Token('UMINUS', '-'),
    #        Token('STRING', '"Hi"')
    #    ]))
    #    result = self.interpreter.visit_uminus(node)
    #    self.assertEqual(result, -"Hi")


class test_negate(unittest.TestCase):
    def setUp(self):
        class TestInterpreter(Interpreter):
            def visit(self, node):
                return super().visit(node)
        self.interpreter = TestInterpreter()

    def test_negate_true(self):
        node = (DummyNode('negate', [
            Token('BOOLEAN', 'true')
        ]))
        result = self.interpreter.visit_negate(node)
        self.assertEqual(result, False)

    def test_negate_false(self):
        node = (DummyNode('negate', [
            Token('BOOLEAN', 'false')
        ]))
        result = self.interpreter.visit_negate(node)
        self.assertEqual(result, True)

    #def test_negate_fail(self):
    #    node = (DummyNode('negate', [
    #        Token('INT', '5')
    #    ]))
    #    result = self.interpreter.visit_negate(node)
    #    self.assertEqual(result, False)


class test_arit_expr(unittest.TestCase):
    def setUp(self):
        class TestInterpreter(Interpreter):
            def visit(self, node):
                return super().visit(node)
        self.interpreter = TestInterpreter()

    def test_multiplication_integer(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '1'),
            Token('MUL_OP', '*'),
            Token('INT', '2'),
        ]))
        result = self.interpreter.visit_arit_expr(node)
        self.assertEqual(result, 2)

    def test_multiplication_decimal(self):
        node = (DummyNode('arit_expr',[
            Token('FLOAT', '1.5'),
            Token('MUL_OP', '*'),
            Token('FLOAT', '2.5')
        ]))
        result = self.interpreter.visit_arit_expr(node)
        self.assertEqual(result, 3.75)


    #def test_multiplication_string_fail(self):
    #    node = (DummyNode('arit_expr',[
    #        Token('STRING', '"Hello"'),
    #        Token('MUL_OP', '*'),
    #        Token('STRING', '" World"')
    #    ]))
    #    result = self.interpreter.visit_arit_expr(node)
    #    self.assertEqual(result, 3.75)

    def test_division_integer(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '10'),
            Token('MUL_OP', '/'),
            Token('INT', '2')
        ]))
        result = self.interpreter.visit_arit_expr(node)
        self.assertEqual(result, 5)

    def test_division_decimal(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '10.5'),
            Token('MUL_OP', '/'),
            Token('FLOAT', '2.5')
        ]))
        result = self.interpreter.visit_arit_expr(node)
        self.assertEqual(result, 4.2)

    #def test_division_zero(self):
    #    node = (DummyNode('arit_expr', [
    #        Token('INT', '10'),
    #        Token('MUL_OP', '/'),
    #        Token('INT', '0')
    #    ]))
    #    result = self.interpreter.visit_arit_expr(node)
    #    self.assertEqual(result, 5)

    def test_modulo_integer(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '10'),
            Token('MUL_OP', '%'),
            Token('INT', '2')
        ]))
        result = self.interpreter.visit_arit_expr(node)
        self.assertEqual(result, 0)

    def test_modulo_decimal(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '10.5'),
            Token('MUL_OP', '%'),
            Token('FLOAT', '2.5')
        ]))
        result = self.interpreter.visit_arit_expr(node)
        self.assertEqual(result, 0.5)

    def test_subtraction_integer(self):
        node = (DummyNode('arit_expr', [
            Token('INT', '10'),
            Token('ADD_OP', '-'),
            Token('INT', '5')
        ]))
        result = self.interpreter.visit_arit_expr(node)
        self.assertEqual(result, 5)

    def test_subtraction_decimal(self):
        node = (DummyNode('arit_expr', [
            Token('FLOAT', '10.5'),
            Token('ADD_OP', '-'),
            Token('FLOAT', '5.5')
        ]))
        result = self.interpreter.visit_arit_expr(node)
        self.assertEqual(result, 5)

    def test_addition_integer(self):
        node = (DummyNode('arit_expr',[
            Token('INT', '1'),
            Token('ADD_OP', '+'),
            Token('INT', '2'),
        ]))
        result = self.interpreter.visit_arit_expr(node)
        self.assertEqual(result, 3)

    def test_addition_decimal(self):
        node = (DummyNode('arit_expr',[
            Token('FLOAT', '1.5'),
            Token('ADD_OP', '+'),
            Token('FLOAT', '2.5'),
        ]))
        result = self.interpreter.visit_arit_expr(node)
        self.assertEqual(result, 4)

    def test_addition_string(self):
        node = (DummyNode('arit_expr',[
            Token('STRING', '"Hello"'),
            Token('ADD_OP', '+'),
            Token('STRING', '" World"'),
        ]))
        result = self.interpreter.visit_arit_expr(node)
        self.assertEqual(result, "Hello World")


class test_compare_expr(unittest.TestCase):
    def setUp(self):
        class TestInterpreter(Interpreter):
            def visit(self, node):
                return super().visit(node)
        self.interpreter = TestInterpreter()

    def test_equal_integer_true(self):
        node = (DummyNode('compare_expr', [
            Token('INT', '1'),
            Token('EQ_OP', '=='),
            Token('INT', '1')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, True)

    def test_equal_integer_false(self):
        node = (DummyNode('compare_expr', [
            Token('INT', '1'),
            Token('EQ_OP', '=='),
            Token('INT', '2')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, False)

    def test_equal_decimal_true(self):
        node = (DummyNode('compare_expr', [
            Token('FLOAT', '1.5'),
            Token('EQ_OP', '=='),
            Token('FLOAT', '1.5')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, True)

    def test_equal_decimal_false(self):
        node = (DummyNode('compare_expr', [
            Token('FLOAT', '1.5'),
            Token('EQ_OP', '=='),
            Token('FLOAT', '2.5')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, False)

    def test_equal_string_true(self):
        node = (DummyNode('compare_expr', [
            Token('STRING', '"Hi"'),
            Token('EQ_OP', '=='),
            Token('STRING', '"Hi"')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, True)

    def test_equal_string_false(self):
        node = (DummyNode('compare_expr', [
            Token('STRING', '"Hi"'),
            Token('EQ_OP', '=='),
            Token('STRING', '"Hiii"')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, False)

    def test_not_equal_integer_true(self):
        node = (DummyNode('compare_expr', [
            Token('INT', '1'),
            Token('EQ_OP', '!='),
            Token('INT', '2')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, True)

    def test_not_equal_integer_false(self):
        node = (DummyNode('compare_expr', [
            Token('INT', '1'),
            Token('EQ_OP', '!='),
            Token('INT', '1')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, False)

    def test_not_equal_decimal_true(self):
        node = (DummyNode('compare_expr', [
            Token('FLOAT', '1.5'),
            Token('EQ_OP', '!='),
            Token('FLOAT', '2.5')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, True)

    def test_not_equal_decimal_false(self):
        node = (DummyNode('compare_expr', [
            Token('FLOAT', '1.5'),
            Token('EQ_OP', '!='),
            Token('FLOAT', '1.5')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, False)

    def test_not_equal_string_true(self):
        node = (DummyNode('compare_expr', [
            Token('STRING', '"Hi"'),
            Token('EQ_OP', '!='),
            Token('STRING', '"Hiii"')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, True)


    def test_not_equal_string_false(self):
        node = (DummyNode('compare_expr', [
            Token('STRING', '"Hi"'),
            Token('EQ_OP', '!='),
            Token('STRING', '"Hi"')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, False)

    def test_smaller_integer_true(self):
        node = (DummyNode('compare_expr', [
            Token('INT', '1'),
            Token('REL_OP', '<'),
            Token('INT', '2')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, True)

    def test_greater_integer_false(self):
        node = (DummyNode('compare_expr', [
            Token('INT', '1'),
            Token('REL_OP', '>'),
            Token('INT', '2')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, False)

    def test_smaller_decimal_true(self):
        node = (DummyNode('compare_expr', [
            Token('FLOAT', '1.5'),
            Token('REL_OP', '<'),
            Token('FLOAT', '2.5')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, True)

    def test_greater_decimal_false(self):
        node = (DummyNode('compare_expr', [
            Token('FLOAT', '1.5'),
            Token('REL_OP', '>'),
            Token('FLOAT', '2.5')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, False)

    def test_smaller_equal_integer_true(self):
        node = (DummyNode('compare_expr', [
            Token('INT', '1'),
            Token('REL_OP', '<='),
            Token('INT', '1')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, True)

    def test_smaller_equal_integer_2_true(self):
        node = (DummyNode('compare_expr', [
            Token('INT', '1'),
            Token('REL_OP', '<='),
            Token('INT', '2')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, True)

    def test_smaller_equal_integer_false(self):
        node = (DummyNode('compare_expr', [
            Token('INT', '2'),
            Token('REL_OP', '<='),
            Token('INT', '1')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, False)

    def test_smaller_equal_decimal_true(self):
        node = (DummyNode('compare_expr', [
            Token('FLOAT', '1.5'),
            Token('REL_OP', '<='),
            Token('FLOAT', '1.5')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, True)

    def test_smaller_equal_integer_2_true(self):
        node = (DummyNode('compare_expr', [
            Token('FLOAT', '1.5'),
            Token('REL_OP', '<='),
            Token('FLOAT', '2.5')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, True)

    def test_smaller_equal_decimal_false(self):
        node = (DummyNode('compare_expr', [
            Token('FLOAT', '2.5'),
            Token('REL_OP', '<='),
            Token('FLOAT', '1.5')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, False)

    def test_greater_equal_integer_true(self):
        node = (DummyNode('compare_expr', [
            Token('INT', '1'),
            Token('REL_OP', '>='),
            Token('INT', '1')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, True)

    def test_greater_equal_integer_2_true(self):
        node = (DummyNode('compare_expr', [
            Token('INT', '2'),
            Token('REL_OP', '>='),
            Token('INT', '1')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, True)

    def test_greater_equal_integer_false(self):
        node = (DummyNode('compare_expr', [
            Token('INT', '1'),
            Token('REL_OP', '>='),
            Token('INT', '2')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, False)

    def test_greater_equal_decimal_true(self):
        node = (DummyNode('compare_expr', [
            Token('FLOAT', '1.5'),
            Token('REL_OP', '>='),
            Token('FLOAT', '1.5')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, True)

    def test_greater_equal_integer_2_true(self):
        node = (DummyNode('compare_expr', [
            Token('FLOAT', '2.5'),
            Token('REL_OP', '>='),
            Token('FLOAT', '1.5')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, True)

    def test_greater_equal_decimal_false(self):
        node = (DummyNode('compare_expr', [
            Token('FLOAT', '1.5'),
            Token('REL_OP', '>='),
            Token('FLOAT', '2.5')
        ]))
        result = self.interpreter.visit_compare_expr(node)
        self.assertEqual(result, False)


class test_logical_expr(unittest.TestCase):
    def setUp(self):
        class TestInterpreter(Interpreter):
            def visit(self, node):
                return super().visit(node)
        self.interpreter = TestInterpreter()

    def test_and_expr_1(self):
        node = (DummyNode('logical_expr', [
            Token('BOOLEAN', 'true'),
            Token('LOGIC_OP', 'and'),
            Token('BOOLEAN', 'true')
        ]))
        result = self.interpreter.visit_logical_expr(node)
        self.assertEqual(result, True)

    def test_and_expr_2(self):
        node = (DummyNode('logical_expr', [
            Token('BOOLEAN', 'true'),
            Token('LOGIC_OP', 'and'),
            Token('BOOLEAN', 'false')
        ]))
        result = self.interpreter.visit_logical_expr(node)
        self.assertEqual(result, False)

    def test_and_expr_3(self):
        node = (DummyNode('logical_expr', [
            Token('BOOLEAN', 'false'),
            Token('LOGIC_OP', 'and'),
            Token('BOOLEAN', 'true')
        ]))
        result = self.interpreter.visit_logical_expr(node)
        self.assertEqual(result, False)

    def test_and_expr_4(self):
        node = (DummyNode('logical_expr', [
            Token('BOOLEAN', 'false'),
            Token('LOGIC_OP', 'and'),
            Token('BOOLEAN', 'false')
        ]))
        result = self.interpreter.visit_logical_expr(node)
        self.assertEqual(result, False)

    def test_or_expr_1(self):
        node = (DummyNode('logical_expr', [
            Token('BOOLEAN', 'true'),
            Token('LOGIC_OP', 'or'),
            Token('BOOLEAN', 'true')
        ]))
        result = self.interpreter.visit_logical_expr(node)
        self.assertEqual(result, True)

    def test_or_expr_2(self):
        node = (DummyNode('logical_expr', [
            Token('BOOLEAN', 'true'),
            Token('LOGIC_OP', 'or'),
            Token('BOOLEAN', 'false')
        ]))
        result = self.interpreter.visit_logical_expr(node)
        self.assertEqual(result, True)

    def test_or_expr_3(self):
        node = (DummyNode('logical_expr', [
            Token('BOOLEAN', 'false'),
            Token('LOGIC_OP', 'or'),
            Token('BOOLEAN', 'true')
        ]))
        result = self.interpreter.visit_logical_expr(node)
        self.assertEqual(result, True)

    def test_or_expr_4(self):
        node = (DummyNode('logical_expr', [
            Token('BOOLEAN', 'false'),
            Token('LOGIC_OP', 'or'),
            Token('BOOLEAN', 'false')
        ]))
        result = self.interpreter.visit_logical_expr(node)
        self.assertEqual(result, False)

if __name__ == '__main__':
    unittest.main()