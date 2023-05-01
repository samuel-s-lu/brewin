# from interpreterv1 import Interpreter
from intbase import ErrorType as ET
from util import remove_line_num
from MethodDef import MethodDef
from VariableDef import VariableDef

class ObjectDef:
    def __init__(self, category, fields:set[VariableDef], methods:set[MethodDef], interpreter):
        self.category = category
        self.fields = fields
        self.methods = methods
        self.int = interpreter

        self.fields_dict = {name:value for name, value in zip([x.name for x in fields], [x.value for x in fields])}
        self.params = dict()
        self.params_dict = dict()
        self.objects = set()

        self.returned = False

    def __str__(self):
        return f'Category {self.category}\nFields: {self.fields}\nMethods: {self.methods}\n'

    def __repr__(self):
        return self.__str__()

    
    def call_method(self, method_name, param_vals):
        method = self.find_method(method_name)
        # print(method)
        # print(f'method args: {method.args}')
        # print(f'param vals: {param_vals}')
        if not method:
            self.int.error(ET.NAME_ERROR, "Method not found")
        
        if len(param_vals) != len(method.args):
            self.int.error(ET.TYPE_ERROR, "Incorrent number of parameters were given")

        statement = method.statement
        old_params = self.params
        old_params_dict = self.params_dict
        if param_vals:
            self.params = {VariableDef(n, v) for n, v in zip([x for x in method.args], [x for x in param_vals])}
            self.params_dict = {name:value for name, value in zip(method.args, param_vals)}
            # print(f'self params: {self.params}')
            # print(f'self params dict: {self.params_dict}')
        # print(f'statement: {statement}')
        res = self.run_statement(statement)
        self.params = old_params
        self.params_dict = old_params_dict
        self.returned = False
        # print(f'run statement result: {res}')
        return res


    def run_statement(self, statement):
        match statement[0]:
            case self.int.PRINT_DEF:
                res = ''
                for i in range(1,len(statement)):
                    next = self.resolve_exp(statement[i])
                    # print(next)
                    if next is True:
                        next = 'true'
                    if next is False:
                        next = 'false'
                    res += str(next)
                
                self.int.output(res)
                return res
            case self.int.SET_DEF:
                # if len(statement) != 3:
                #     self.int.error(ET.SYNTAX_ERROR, "Incorrect number of arguments for 'set'")

                # if self.params:
                #     print(f'Old params: {self.params}')
                # else:
                #     print('No parameters')
                # print(f'Old fields: {self.fields}')

                target_name = statement[1]
                # print(f'target name: {target_name}')
                new_val = self.resolve_exp(statement[2])
                # print(f'new val: {new_val}\n===\n')

                self.set_var(target_name, new_val)

                # if self.params:
                #     print(f'Updated params: {self.params}')
                # else:
                #     print('No parameters')
                # print(f'Updated fields: {self.fields}')

            case self.int.BEGIN_DEF:
                for i in range(1,len(statement)):
                    # print(f'statement: {statement[i]}')
                    res = self.run_statement(statement[i])
                    if self.returned:
                        self.returned = False
                        return res
                return res
            
            case self.int.INPUT_INT_DEF | self.int.INPUT_STRING_DEF:
                target_name = statement[1]
                new_val = self.int.get_input()
                if statement[0] == self.int.INPUT_INT_DEF:
                    new_val = int(new_val)
                self.set_var(target_name, new_val)
            
            case self.int.IF_DEF:
                # if len(statement) > 4:
                #     self.int.error(ET.SYNTAX_ERROR, "Invalid number of arguments provided to 'if'")

                pred = self.resolve_exp(statement[1])
                if not isinstance(pred, bool):
                    self.int.error(ET.TYPE_ERROR, "non boolean provided as condition to 'if'")
                
                res = None
                if pred:
                    res = self.run_statement(statement[2])
                else:
                    if len(statement) == 4:
                        res = self.run_statement(statement[3])
                
                return res

            case self.int.WHILE_DEF:
                # if len(statement) > 3:
                #     self.int.error(ET.SYNTAX_ERROR, "Invalid number of arguments provided to 'while'")

                pred = self.resolve_exp(statement[1])
                if not isinstance(pred, bool):
                    self.int.error(ET.TYPE_ERROR, "non boolean provided as condition to 'while'")

                res = None
                while pred and not self.returned:
                    res = self.run_statement(statement[2])
                    pred = self.resolve_exp(statement[1])

                return res
            
            case self.int.CALL_DEF:
                obj_name = statement[1]
                # if self.resolve_exp(obj_name) == None:
                #     self.int.error(ET.FAULT_ERROR, "Deferencing null object")
                # print(type(self.resolve_exp(obj_name)))
                method_name = statement[2]
                method_params = []
                if len(statement) >= 4:
                    method_params = [self.resolve_exp(p) for p in statement[3:]]
                # print(statement[3:])
                # print(method_params)

                res = None
                if obj_name == 'me':
                    # print(method_name, method_params)
                    res = self.call_method(method_name, method_params)
                elif (obj_name in self.fields_dict.keys()) and (self.resolve_exp(obj_name) == None):
                    self.int.error(ET.FAULT_ERROR, "Deferencing null object")
                else:
                    # print(f'params dict: {self.params_dict}')
                    # obj_var, isParam = self.find_var(obj_name)
                    res = self.fields_dict[obj_name].call_method(method_name, method_params)

                return res
            
            case self.int.RETURN_DEF:
                # if len(statement) > 2:
                #     self.int.error(ET.SYNTAX_ERROR, "Invalid number of arguments provided to 'return'")
                self.returned = True
                # ret_val = None
                if len(statement) == 2:
                    ret_val = self.resolve_exp(statement[1])
                    # print(statement)
                    # print(f'ret val: {ret_val}')
                    return ret_val
                else:
                    return None


    def set_var(self, target_name, new_val):
        var, isParam = self.find_var(target_name)

        if var:
            self.update_var(var, isParam, new_val)
        else:
            self.int.error(ET.NAME_ERROR, f"Undefined variable: {target_name}")
        



    def find_var(self, target_name):
        if (target_name not in self.params_dict.keys()) and (target_name not in self.fields_dict.keys()):
            self.int.error(ET.NAME_ERROR, f"Undefined variable: {target_name}")
        if self.params:
            for var in self.params:
                if var.name == target_name:
                    return (var, True)
        for var in self.fields:
            if var.name == target_name:
                return (var, False)
            
        self.int.error(ET.NAME_ERROR, f"Undefined variable: {target_name}")
        return None
    

    def update_var(self, var:VariableDef, isParam, new_val):
        # update set of variables
        var.update(new_val)
        # print(f'var: {var}')

        # update dictionary of name to value pairs
        if isParam:
            self.params_dict[var.name] = new_val
        else:
            self.fields_dict[var.name] = new_val
        
        # print(f'fields dict: {self.fields_dict}')


    def resolve_exp(self, exp):
        if type(exp) is not list:
            return self.unwrap_simp_exp(exp)
        
        special_exps = {'new', 'call', '!'}
        if exp[0] not in special_exps:
            arg1 = self.resolve_exp(exp[1])
            arg2 = self.resolve_exp(exp[2])

        res = None
        match exp[0]:
            case '+':
                if self.both_str(arg1, arg2) or self.both_int(arg1, arg2):
                    res = arg1 + arg2
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the + operator")
            case '-':
                if self.both_int(arg1, arg2):
                    res = arg1 - arg2
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the - operator")
            case '*':
                if self.both_int(arg1, arg2):
                    res = arg1 * arg2
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the * operator")
            case '/':
                if self.both_int(arg1, arg2):
                    res = arg1 // arg2
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the / operator")
            case '%':
                if self.both_int(arg1, arg2):
                    res = arg1 % arg2
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the / operator")
            case '==':
                # print(f'arg1 arg2: {arg1} {arg2}')
                # print(f'both obj: {self.both_obj(arg1,arg2)}')
                if self.both_int(arg1, arg2) or self.both_str(arg1, arg2) or self.both_bool(arg1, arg2) or self.both_obj(arg1, arg2):
                    return arg1 == arg2
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the == operator")
            case '!=':
                if self.both_int(arg1, arg2) or self.both_str(arg1, arg2) or self.both_bool(arg1, arg2) or self.both_obj(arg1, arg2):
                    return arg1 != arg2
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the != operator")
            case '<':
                if self.both_str(arg1, arg2) or self.both_int(arg1, arg2):
                    return arg1 < arg2
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the < operator")
            case '>':
                if self.both_str(arg1, arg2) or self.both_int(arg1, arg2):
                    return arg1 > arg2
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the > operator")
            case '<=':
                if self.both_str(arg1, arg2) or self.both_int(arg1, arg2):
                    return arg1 <= arg2
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the <= operator")
            case '>=':
                if self.both_str(arg1, arg2) or self.both_int(arg1, arg2):
                    return arg1 >= arg2
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the >= operator")
            case '&':
                if self.both_bool(arg1, arg2):
                    return arg1 and arg2
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the & operator")
            case '|':
                if self.both_bool(arg1, arg2):
                    return arg1 or arg2
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the | operator")
            case '!':
                arg = self.resolve_exp(exp[1])
                if isinstance(arg, bool):
                    return not arg
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible type using the ! operator")

            case self.int.NEW_DEF:
                class_name = exp[1]
                class_def = self.int.find_class_def(class_name)
                new_obj = class_def.instantiate_object()
                
                return new_obj
            
            case self.int.CALL_DEF:
                obj_name = exp[1]
                # if the target object name is a variable and it resolves to None, throw error
                
                # print(type(self.resolve_exp(obj_name)))
                method_name = exp[2]
                method_params = []
                if len(exp) >= 4:
                    method_params = [self.resolve_exp(p) for p in exp[3:]]
                # print(statement[3:])
                # print(method_params)

                res = None
                if obj_name == 'me':
                    # print(f'method name: {method_name}, method params: {method_params}')
                    res = self.call_method(method_name, method_params)
                    # print(f'expression res: {res}')
                elif (obj_name in self.fields_dict.keys()) and (self.resolve_exp(obj_name) == None):
                    self.int.error(ET.FAULT_ERROR, "Deferencing null object")
                else:
                    # print(f'params dict: {self.params_dict}')
                    # obj_var, isParam = self.find_var(obj_name)
                    res = self.fields_dict[obj_name].call_method(method_name, method_params)

                return res
        return res


    def unwrap_simp_exp(self,exp):
        exp, isVar = remove_line_num(exp)
        # print(f'expressions: {exp}, isVar: {isVar}')
        # valid variable within parameters
        if isVar and self.params and exp in self.params_dict.keys():
            exp = self.params_dict[exp]
        # valid variable within fields
        elif isVar and  exp in self.fields_dict.keys():
            exp = self.fields_dict[exp]
        # invalid variable
        elif isVar and (exp not in self.fields_dict.keys() and exp not in self.params_dict.keys()):
            self.int.error(ET.NAME_ERROR, f"Undefined variable: {exp}")
        return exp


    def both_str(self, arg1, arg2):
        return isinstance(arg1, str) and isinstance(arg2, str)


    def both_int(self, arg1, arg2):
        # return isinstance(arg1, int) and isinstance(arg2, int)
        return type(arg1) in {int} and type(arg2) in {int}
    
    def both_bool(self, arg1, arg2):
        # return isinstance(arg1, bool) and isinstance(arg2, bool)
        return type(arg1) in {bool} and type(arg2) in {bool}
    
    def both_obj(self, arg1, arg2):
        # true if both none, or one none one obj, or both obj
        return (not arg1 and not arg2) or ((not arg1 or not arg2) and (isinstance(arg1, ObjectDef)) or isinstance(arg2, ObjectDef)) or (isinstance(arg1, ObjectDef) and isinstance(arg2, ObjectDef))


    def find_method(self, method_name):
        for m in self.methods:
            if m.name == method_name:
                return m
            
        self.int.error(ET.NAME_ERROR, "Method not found")
        return None


    # def update_vars(self, var_set:set[VariableDef], name, new_val):
    #     """
    #     updates value of variable with specified name in var_set to new_value
    #     returns True if successful, otherwise return False
    #     """
    #     for var in var_set:
    #         if var.name == name:
    #             var.update(new_val)
    #             return True

    #     return False