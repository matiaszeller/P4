import unittest

from interpreter import Interpreter

from environment import Environment

class TestInterpreter (unittest.testcase):
    def setUp(self):
        self.env = Environment()
        self.interpreter = Interpreter(self.env)

    def test_add_expr(self):
        code = """ 
        
        """