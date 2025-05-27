from src.p4.error import BooleanError, UndeclaredNameError, UnknownTypeError, DuplicateNameError, IndexRangeError
from src.p4.error import OverIndexedError


class Environment:
    def __init__(self):
        self.variables = {}
        self.functions = {}

    # type helpers
    def base(self, type_str):
        return type_str.split("[")[0]

    def coerce_scalar(self, value, type_str, line=None):
        if not isinstance(value, str):
            return value
        base = self.base(type_str)
        if base == "integer":
            return int(value)
        if base == "decimal":
            return float(value)
        if base == "boolean":
            if value == "true" or value == "sand":
                return True
            if value == "false" or value == "falsk":
                return False
            raise BooleanError(value, line)
        if base == "string":
            return value
        raise UnknownTypeError(base, line=line)

    def coerce_any(self, val, type_str, line=None):
        if isinstance(val, list):
            return [self.coerce_any(v, type_str, line=line) for v in val]
        return self.coerce_scalar(val, type_str, line=line)

    # variable handling
    def declare_variable(self, name, type, sizes=None, line=None):
        if name in self.variables:
            raise DuplicateNameError(name,line)
        if sizes is None:
            sizes = []
        self.variables[name] = {
            'value': self.make_array(sizes),
            'type': type,
            'sizes': sizes
        }

    def make_array(self, sizes, depth=0):
        if depth == len(sizes):
            return None
        return [self.make_array(sizes, depth + 1) for _ in range(sizes[depth])]

    def get_variable(self, name, array_index=None, line=None):
        if name not in self.variables:
            raise UndeclaredNameError(name, line)
        var = self.variables[name]
        value = var['value']

        if array_index is None:
            return value

        if len(array_index) > len(var['sizes']):
            raise OverIndexedError(array_index, len(var['sizes']), line)

        for depth, idx in enumerate(array_index):
            if idx >= var['sizes'][depth]:
                raise IndexRangeError(idx, var['sizes'][depth], line)
            value = value[idx]
        return value

    # assignment with shape checking + coercion
    def set_variable(self, name, value, array_index=None, line=None):
        if name not in self.variables:
            raise UndeclaredNameError(name, line=line)

        var   = self.variables[name]
        sizes = var['sizes']
        value = self.coerce_any(value, var['type'], line=line)

        # whole-variable assignment
        if array_index is None:
            if self.get_dimensions(value) != len(sizes):
                raise ValueError(
                    f'Expected {len(sizes)}-D value for {name}, got {self.get_dimensions(value)}-D'
                )
            if sizes and not self.shape_matches(value, sizes):
                raise ValueError(
                    f'Array shape {self.shape(value)} does not match declared sizes {tuple(sizes)} for {name}'
                )
            var['value'] = value
            return

        # element assignment
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
        tgt[last_idx] = self.coerce_scalar(value, var['type'])

    # function handling
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

    # helpers
    def get_dimensions(self, value):
        depth = 0
        while isinstance(value, list):
            if not value:
                return depth + 1
            depth += 1
            value = value[0]
        return depth

    def shape(self, value):
        if not isinstance(value, list):
            return ()
        if len(value) == 0:
            return (0,)
        inner = self.shape(value[0])
        return (len(value),) + inner

    def shape_matches(self, value, sizes):
        if not sizes:
            return not isinstance(value, list)
        if not isinstance(value, list):
            return False
        if len(value) != sizes[0]:
            return False
        return all(self.shape_matches(v, sizes[1:]) for v in value)