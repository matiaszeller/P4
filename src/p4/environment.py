class Environment:
    def __init__(self):
        self.variables = {}

    def declare(self, name, isArray=False):
        if name in self.variables:
            raise NameError(f'Variable {name} already exists')

        if isArray:
            self.variables[name] = []
        elif not isArray:
            self.variables[name] = [None]
        else:
            raise NameError(f'Variable {name} is both an array and a variable')

    def define(self, name, value):
        if name in self.variables:
            raise NameError(f'Variable {name} already exists')
        self.variables[name] = value

    def get(self, name, arrayIndex=None):
        if name not in self.variables:
            raise NameError(f'Variable {name} is not defined')
        if arrayIndex is None:
            return self.variables[name]
        else:
            index = arrayIndex[-1]
            target = self.variables[name]
            if index >= len(target):
                raise NameError(f'Index {index} is out of range for variable {name}')
            return self.variables[name][index]

    def set(self, name, value, arrayIndex=None):
        if name not in self.variables:
            raise NameError(f'Variable {name} is not defined')
        if arrayIndex is None:
            self.variables[name] = value
        else:
            index = arrayIndex[-1]
            target = self.variables[name]
            target.extend([None] * (index - len(target) + 1))
            target[index] = value


    def print_variables(self):
        for name, value in self.variables.items():
            print(f'{name} = {value}')