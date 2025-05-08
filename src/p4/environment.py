class Environment:
    def __init__(self):
        self.variables = {}
        self.functions = {}

    def declare_variable(self, name, type, array_depth=0):
        if name in self.variables:
            raise NameError(f'Variable {name} already exists')
        self.variables[name] = {
            'value': None,
            'type': type,
            'arrayDepth': array_depth
        }
        for _ in range(array_depth):
            self.variables[name]['value'] = [self.variables[name]['value']]

    def get_variable(self, name, array_index=None):
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

    def set_variable(self, name, value, array_index=None):
        if name not in self.variables:
            raise NameError(f'Variable {name} is not defined')

        variable_data = self.variables[name]
        target = variable_data['value']
        variable_dimension = variable_data['arrayDepth']
        value_dimension = self._get_dimensions(value)
        index_dimension = len(array_index) if array_index is not None else 0

        if value_dimension + index_dimension != variable_dimension:
            raise ValueError(f'Value {value} has wrong dimension, expected {variable_dimension + index_dimension}')
        elif index_dimension == 0:
            variable_data['value'] = value
        else:
            for i in array_index[:-1]:
                target = target[i]
            target[array_index[-1]] = value

    def declare_function(self, name, return_type, block, parameters=None):
        if name in self.functions:
            raise NameError(f'Function {name} already exists')
        self.functions[name] = {
            'type': return_type,
            'block': block
        }
        if parameters is not None:
            self.functions[name]['parameters'] = parameters

    def get_function(self, name):
        if name not in self.functions:
            raise NameError(f'Function {name} is not defined')
        return self.functions[name]

    def _get_dimensions(self, value):
        depth = 0
        while isinstance(value, list):
            if not value:
                return depth
            depth += 1
            value = value[0]
        return depth