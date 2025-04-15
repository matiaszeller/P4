class Environment:
    def __init__(self):
        self.variables = {}

    def declare(self, name):
        if name in self.variables:
            raise NameError(f'Variable {name} already exists')
        self.variables[name] = 0

    def define(self, name, value):
        if name in self.variables:
            raise NameError(f'Variable {name} already exists')
        self.variables[name] = value

    def get(self, name):
        if name not in self.variables:
            raise NameError(f'Variable {name} is not defined')
        return self.variables[name]

    def set(self, name, value):
        if name not in self.variables:
            raise NameError(f'Variable {name} is not defined')
        self.variables[name] = value