from typing import Dict, List, Optional, Tuple, Union

import re

SYNTAX_ERROR  = "SyntaxError"
RUNTIME_ERROR = "RuntimeError"


class Number:
    def __init__(self, value: int) -> None:
        self.value = value

    def run(self, variables: Dict[str, int]) -> int:
        return self.value



class Operator:
    def __init__(self, left, right) -> None:
        self.left  = left
        self.right = right

    def add_num(self, variables: Dict[str, int]) -> None:
        if self.left not in variables:
            variables[self.left] = 0

        if self.right not in variables:
            variables[self.right] = 0


class And(Operator):
    def __init__(self, left, right) -> None:
        super().__init__(left, right)

    def run(self, variables: Dict[str, int]) -> int:
        self.add_num(variables)
        return 1 if int(variables[self.left]) != 0 and int(variables[self.right]) != 0 else 0


class Or(Operator):
    def __init__(self, left, right) -> None:
        super().__init__(left, right)

    def run(self, variables: Dict[str, int]) -> int:
        self.add_num(variables)
        return 1 if int(variables[self.left]) != 0 or int(variables[self.right]) != 0 else 0


class Nand(Operator):
    def __init__(self, left, right) -> None:
        super().__init__(left, right)

    def run(self, variables: Dict[str, int]) -> int:
        self.add_num(variables)
        return 1 if not (int(variables[self.left]) != 0 and int(variables[self.right]) != 0) else 0


class Add(Operator):
    def __init__(self, left, right) -> None:
        super().__init__(left, right)
    
    def run(self, variables: Dict[str, int]) -> int:
        self.add_num(variables)
        return int(variables[self.left]) + int(variables[self.right])


class Sub(Operator):
    def __init__(self, left, right) -> None:
        super().__init__(left, right)

    def run(self, variables: Dict[str, int]) -> int:
        self.add_num(variables)
        return int(variables[self.left]) - int(variables[self.right])


class Mul(Operator):
    def __init__(self, left, right) -> None:
        super().__init__(left, right)

    def run(self, variables: Dict[str, int]) -> int:
        self.add_num(variables)
        return int(variables[self.left]) * int(variables[self.right])


class Div(Operator):
    def __init__(self, left, right) -> None:
        super().__init__(left, right)

    def run(self, variables: Dict[str, int]) -> int:
        self.add_num(variables)
        return int(int(variables[self.left]) / int(variables[self.right]))


class Lt(Operator):
    def __init__(self, left, right) -> None:
        super().__init__(left, right)

    def run(self, variables: Dict[str, int]) -> int:
        self.add_num(variables)
        return 1 if int(variables[self.left]) < int(variables[self.right]) else 0
        

class Gt(Operator):
    def __init__(self, left, right) -> None:
        super().__init__(left, right)

    def run(self, variables: Dict[str, int]) -> int:
        self.add_num(variables)
        return 1 if variables[self.left] > variables[self.right] else 0


class Eq(Operator):
    def __init__(self, left, right) -> None:
        super().__init__(left, right)

    def run(self, variables: Dict[str, int]) -> int:
        self.add_num(variables)
        return 1 if int(variables[self.left]) == int(variables[self.right]) else 0


class Leq(Operator):
    def __init__(self, left, right) -> None:
        super().__init__(left, right)
    
    def run(self, variables: Dict[str, int]) -> int:
        self.add_num(variables)
        return 1 if int(variables[self.left]) <= int(variables[self.right]) else 0


class Geq(Operator):
    def __init__(self, left, right) -> None:
        super().__init__(left, right)

    def run(self, variables: Dict[str, int]) -> int:
        self.add_num(variables)
        return 1 if int(variables[self.left]) >= int(variables[self.right]) else 0

class Call(Operator):
    def __init__(self, left, right) -> None:
        super().__init__(left, right)

    def run(self, variables: Dict[str, int], functions: List['Function']) -> Union[int, str]:
        
        func_to_run = [fun for fun in functions if fun.function_name == self.left]
        if len(func_to_run) == 0:
            return "NameError"
        
        if len(func_to_run[0].arguments_names) != len(self.right):
            return "TypeError"

        arguments = []
        for var in self.right:
            if var not in variables:
                variables[var] = 0
            arguments.append(variables[var])

        rt_val = func_to_run[0].run(arguments, functions)

        return rt_val


built_in_func = {
    "add": Add,
    "sub": Sub,
    "mul": Mul,
    "div": Div,
    "lt" : Lt,
    "gt" : Gt,
    "eq" : Eq,
    "leq": Leq,
    "geq": Geq,
    "and": And,
    "or" : Or,
    "nand": Nand,
}


class Expression:
    def __init__(self) -> None:
        self.variable: Optional[str] = None
        self.right: Optional[Operator] = None
        self.code_line_num: Optional[int] = None
    
    def check(self, functions: List['Function']) -> Optional[int]:

        if isinstance(self.right, Call):

            fun = [fun for fun in functions if fun.function_name == self.right.left and len(fun.arguments_names) == len(self.right.right)]

            if len(fun) != 1:
                return self.code_line_num

        return None

    def build(self, index: int, line: str, functions: List['Function']) -> Union[int, Tuple[int, str]]:
        self.code_line_num = index + 1

        left, right = line.split("=")
        self.left = left.split()[0]

        if not check_variable(self.left):
            return (self.code_line_num, SYNTAX_ERROR)

        right_parts = right.split()

        if len(right_parts) == 0:
            return (self.code_line_num, SYNTAX_ERROR)

        elif len(right_parts) == 1 and right_parts[0].lstrip("-").isdigit():
            
            self.right = Number(int(right_parts[0]))

        elif len(right_parts) == 3 and right_parts[0] in built_in_func:
            if not (check_variable(right_parts[1]) and check_variable(right_parts[2])):
                return (self.code_line_num, SYNTAX_ERROR)
            self.right = built_in_func[right_parts[0]](right_parts[1], right_parts[2])

        else:
            if right_parts[0] in built_in_func:
                return (self.code_line_num, SYNTAX_ERROR)
            
            for var in right_parts[1:]:
                if not check_variable(var):
                    return (self.code_line_num, SYNTAX_ERROR)
            
            self.right = Call(right_parts[0], right_parts[1:])
        
        return index + 1

    def run(self, variables: Dict[str, int], functions: List['Function']) -> Optional[Tuple[int, str]]:
        
        try:
            if isinstance(self.right, Call):
                rt_val = self.right.run(variables, functions)
            else:
                rt_val = self.right.run(variables)
        except:
            return (self.code_line_num, RUNTIME_ERROR)
        
        if not isinstance(rt_val, int):
            return (self.code_line_num, rt_val)

        variables[self.left] = rt_val

class Scope:
    def __init__(self) -> None:
        self.objects_to_run: List[Union["Scope", "Operator", "Number"]]    = []

    def check_valid_line(self, line: str, pattern: str) -> bool:
        return re.search(pattern, line) is not None or line.isspace() or line == ""

    def check(self, functions: List['Function']) -> Optional[int]:
        for object_to_run in self.objects_to_run:
            rt_val = object_to_run.check(functions)
            if rt_val is not None:
                return rt_val
        
        return None

    def build_scope(self, index: int, code_lines: List[str], 
    functions: List['Function'], indent: str) \
    -> Union[int, Tuple[int, str]]:
        
        pattern = "^" + indent + "[a-zA-Z].*$"

        while index < len(code_lines) and self.check_valid_line(code_lines[index], pattern):

            line = code_lines[index]

            if line.isspace() or line == "":
                index += 1
                continue

            line_parts = line.split()

            if len(line_parts) < 2:
                return (index + 1, SYNTAX_ERROR)

            elif len(line_parts) == 2:

                if line_parts[0] != "if" and line_parts[1] != "while":
                    return (index + 1, SYNTAX_ERROR)
                
                new_object = PredicateScope()
                rt_val = new_object.build(index, code_lines, functions, indent + " ")
                if isinstance(rt_val, int):
                    index = rt_val
                else:
                    return rt_val

                self.objects_to_run.append(new_object)

            elif line_parts[1] == "=":
                new_object = Expression()
                rt_val = new_object.build(index, line, functions)
                if isinstance(rt_val, int):
                    index = rt_val
                else:
                    return rt_val

                self.objects_to_run.append(new_object)
            else:
                return (index + 1, SYNTAX_ERROR)

        return index


class PredicateScope(Scope):
    def __init__(self) -> None:
        super().__init__()
        self.predicate_var: Optional[str] = None
        self.code_line_num: Optional[int] = None
        self.type_scp: Optional[str] = None 

    def build(self, index: int, code_lines: List[str], functions: List['Function'], indent: str) -> Union[int, Tuple[int, str]]:
        self.code_line_num = index + 1

        line = code_lines[index]

        line_parts = line.split()

        self.type_scp = "if" if line_parts[0] == "if" else "while"

        if not check_variable(line_parts[1]):
            return (index + 1, SYNTAX_ERROR)

        self.predicate_var = line_parts[1]

        return self.build_scope(index + 1, code_lines, functions, indent)

    def run(self, variables: Dict[str, int], functions: List['Function']) -> Optional[Tuple[int, str]]:
        if self.predicate_var not in variables:
            variables[self.predicate_var] = 0
            return None

        if self.type_scp == "if" and variables[self.predicate_var] != 0:
            for line in self.objects_to_run:
                rt_val = line.run(variables, functions)
                if rt_val is not None:
                    return rt_val
        
        while self.type_scp == "while" and variables[self.predicate_var] != 0:
            for line in self.objects_to_run:
                rt_val = line.run(variables, functions)
                if rt_val is not None:
                    return rt_val


class Function(Scope):
    def __init__(self) -> None:
        super().__init__()
        self.function_name: Optional[str] = None
        self.arguments_names: List[str]   = []
        self.line_num: Optional[int]      = None

    def check_function_name(self, functions: List['Function']) -> bool:
        if re.search("^[a-zA-Z][a-zA-Z0-9_]*$", self.function_name) is None:
            return False
        
        if self.function_name in built_in_func:
            return False

        if any(map(lambda func: func.function_name == self.function_name, functions)):
            return False

        return True

    def build(self, index: int, code_lines: List[str], functions: List['Function']) -> Union[int, Tuple[int, str]]:
        self.line_num = index + 1
        line = code_lines[index]

        header = line.split()

        if len(header) < 2:
            return (self.line_num, SYNTAX_ERROR)
        
        _, self.function_name, *arguments = header
        self.arguments_names = arguments

        for var in self.arguments_names:
            if not check_variable(var):
                return (self.line_num, SYNTAX_ERROR)

        if not self.check_function_name(functions):
            return (self.line_num, SYNTAX_ERROR)

        functions.append(self)

        return self.build_scope(index + 1, code_lines, functions, " ")

    def run(self, variables: List[str], functions: List['Function']) -> Union[int, Tuple[int, str]]:
        
        if len(self.arguments_names) != len(variables):
            return (self.line_num, RUNTIME_ERROR)

        variables_dict = {}
        variables_dict[self.function_name] = 0

        for var, val in zip(self.arguments_names, variables):
            variables_dict[var] = val 

        for line in self.objects_to_run:
            rt_val = line.run(variables_dict, functions)
            if rt_val is not None:
                return rt_val
        
        return variables_dict[self.function_name]
        

class Interpreter:
    def __init__(self, code_str: str) -> None:
        self.code_lines: List[str] = code_str.split("\n")
        self.functions: List["Function"] = []

    def func_check(self) -> Optional[int]:
        
        for fun in self.functions:
            rt_val = fun.check(self.functions)
            if rt_val is not None:
                return rt_val
        
        return None

    def build(self) -> Optional[Tuple[int, str]]:
        index = 0

        while index < len(self.code_lines):
            line = self.code_lines[index]
            if line.isspace() or line == "":
                index += 1
            
            elif line.startswith("def"):
                new_function = Function()
                rt_val = new_function.build(index, self.code_lines, self.functions)

                if isinstance(rt_val, int):
                    index = rt_val
                else:
                    return rt_val

            else:
                return (index + 1, SYNTAX_ERROR)

        rt_val = self.func_check()
        if rt_val is not None:
            return (rt_val, SYNTAX_ERROR)

    def run(self, func_name: str, variables: List[str]) -> Union[int, Tuple[int, str]]:
        function_to_run = [fun for fun in self.functions if fun.function_name == func_name]
        if len(function_to_run) != 1:
            return (0, RUNTIME_ERROR)

        return function_to_run[0].run(variables, self.functions)

def check_variable(name: str) -> bool:
    return re.search("^[a-zA-Z][a-zA-Z0-9_]*$", name) is not None


def do_rec(code: str, func_name: str, *args) -> Union[int, Tuple[int, str]]:
    interpreter = Interpreter(code)
    rt_val = interpreter.build()
    if rt_val is not None:
        return rt_val
    
    return interpreter.run(func_name, args)
