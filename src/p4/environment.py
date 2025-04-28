class Environment:
    def __init__(self):
        self.variables = {}

    def declare(self, name, array_depth=0):
        if name in self.variables:
            raise NameError(f'Variable {name} already exists')
        self.variables[name] = {
            'value': None,
            'arrayDepth': array_depth
        }
        for _ in range(array_depth):
            self.variables[name]['value'] = [self.variables[name]['value']]

    def define(self, name, value):
        if name in self.variables:
            raise NameError(f'Variable {name} already exists')
        self.variables[name] = {
            'value': value,
            'arrayDepth': 0
        }

    def get(self, name, array_index=None):
        if name not in self.variables:
            raise NameError(f'Variable {name} is not defined')
        target = self.variables[name]['value']

        if array_index is not None:
            for i in array_index:
                if not isinstance(target, list):
                    raise TypeError(f'Cannot index into non-list value: {target}')
                if i >= len(target):
                    raise IndexError(f'Array index {i} out of range')
                target = target[i]

        return target

    def set(self, name, value, array_index=None):
        if name not in self.variables:
            raise NameError(f'Variable {name} is not defined')

        variable_data = self.variables[name]
        target = variable_data['value']
        dimensions = variable_data['arrayDepth']

        if array_index is None:
            if dimensions != 0:
                raise ValueError(f'Variable {name} requires {dimensions} indices, got 0')
            else:
                variable_data['value'] = value
        else:
            if len(array_index) != dimensions:
                raise ValueError(f'Variable {name} requires {dimensions} indices, got {len(array_index)}')

        for i in array_index[:-1]:
            while i >= len(target):
                target.append([])
            target = target[i]

        while array_index[-1] >= len(target):
            target.append(None)
        target[array_index[-1]] = value

    def print_variables(self):
        for name, value in self.variables.items():
            print(f'{name} = {value}')