class Environment:
    def __init__(self):
        self.variables = {}
        self.functions = {}

    def declare_variable(self, name, type, sizes=None):
        if name in self.variables:
            raise NameError(f'Variable {name} already exists')
        if sizes is None:
            sizes = []
        self.variables[name] = {
            'value': self._make_array(sizes),
            'type': type,
            'sizes': sizes
        }

    def _make_array(self, sizes, depth=0):
        if depth == len(sizes):
            return None
        return [self._make_array(sizes, depth + 1) for _ in range(sizes[depth])]

    def get_variable(self, name, array_index=None):
        if name not in self.variables:
            raise NameError(f'Variable {name} is not defined')
        var = self.variables[name]
        value = var['value']

        if array_index is None:
            return value

        if len(array_index) > len(var['sizes']):
            raise IndexError('Too many indices for array')

        for depth, idx in enumerate(array_index):
            if idx >= var['sizes'][depth]:
                raise IndexError(f'Array index {idx} out of range')
            value = value[idx]
        return value

    def set_variable(self, name, value, array_index=None):
        if name not in self.variables:
            raise NameError(f'Variable {name} is not defined')

        var = self.variables[name]
        sizes = var['sizes']

        if array_index is None:
            if self._get_dimensions(value) != len(sizes):
                raise ValueError(f'Value {value} has wrong dimension, expected {len(sizes)}')
            var['value'] = value
            return

        if len(array_index) > len(sizes):
            raise IndexError('Too many indices for array')

        tgt = var['value']
        for depth, idx in enumerate(array_index[:-1]):
            if idx >= sizes[depth]:
                raise IndexError(f'Array index {idx} out of range')
            tgt = tgt[idx]

        last_idx = array_index[-1]
        if last_idx >= sizes[len(array_index) - 1]:
            raise IndexError(f'Array index {last_idx} out of range')
        tgt[last_idx] = value

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
                return depth + 1
            depth += 1
            value = value[0]
        return depth