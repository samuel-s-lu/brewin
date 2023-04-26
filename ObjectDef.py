from intbase import InterpreterBase as IB
from intbase import ErrorType as ET
from util import remove_line_num
from MethodDef import MethodDef
from VariableDef import VariableDef

class ObjectDef:
    def __init__(self, category, fields:set[VariableDef], methods:set[MethodDef], interpreter:IB):
        self.category = category
        self.fields = fields
        self.methods = methods
        self.int = interpreter

        self.fields_dict = {name:value for name, value in zip([x.name for x in fields], [x.value for x in fields])}
        self.params = None
        self.params_dict = None

    def __str__(self):
        return f'Category {self.category}\nFields: {self.fields}\nMethods: {self.methods}\n'

    def __repr__(self):
        return self.__str__()

    
    def call_method(self, method_name, param_vals):
        method = self.find_method(method_name)
        if not method:
            self.int.error(ET.NAME_ERROR, "Method not found")
        
        if len(param_vals) != len(method.args):
            self.int.error(ET.TYPE_ERROR, "Incorrent number of parameters were given")

        statement = method.statement
        if param_vals:
            self.params = {VariableDef(n, v) for n, v in zip([x for x in method.args], [x for x in param_vals])}
            self.params_dict = {name:value for name, value in zip(method.args, param_vals)}

        res = self.run_statement(statement)
        return res


    def run_statement(self, statement):
        match statement[0]:
            case self.int.PRINT_DEF:
                res = ''
                for i in range(1,len(statement)):
                    next = self.resolve_exp(statement[i])
                    if next is True:
                        next = 'true'
                    if next is False:
                        next = 'false'
                    res += str(next)
                
                self.int.output(res)
                return
            case self.int.SET_DEF:
                if len(statement) != 3:
                    self.int.error(ET.SYNTAX_ERROR, "Incorrect number of arguments for 'set'")

                # if self.params:
                #     print(f'Old params: {self.params}')
                # else:
                #     print('No parameters')
                # print(f'Old fields: {self.fields}')

                target_name = statement[1]
                new_val = self.resolve_exp(statement[2])

                self.set_var(target_name, new_val)

                # if self.params:
                #     print(f'Updated params: {self.params}')
                # else:
                #     print('No parameters')
                # print(f'Updated fields: {self.fields}')

            case self.int.BEGIN_DEF:
                for i in range(1,len(statement)):
                    self.run_statement(statement[i])
                return
            
            case self.int.INPUT_INT_DEF | self.int.INPUT_STRING_DEF:
                target_name = statement[1]
                new_val = self.int.get_input()
                if statement[0] == self.int.INPUT_INT_DEF:
                    new_val = int(new_val)
                self.set_var(target_name, new_val)

                return
            
            case self.int.IF_DEF:
                pred = self.resolve_exp(statement[1])
                if pred:
                    self.run_statement(statement[2])
                else:
                    self.run_statement(statement[3])

    def set_var(self, target_name, new_val):
        var, isParam = self.find_var(target_name)

        if var:
            self.update_var(var, isParam, new_val)
        else:
            self.int.error(ET.NAME_ERROR, "Undefined variable")



    def find_var(self, target_name):
        if (self.params and target_name not in self.params_dict.keys()) and (target_name not in self.fields_dict.keys()):
            self.int.error(ET.NAME_ERROR, "Undefined variable")
        if self.params:
            for var in self.params:
                if var.name == target_name:
                    return (var, True)
        for var in self.fields:
            if var.name == target_name:
                return (var, False)
            
        self.int.error(ET.NAME_ERROR, "Undefined variable")
        return None
    

    def update_var(self, var:VariableDef, isParam, new_val):
        # update set of variables
        var.update(new_val)

        # update dictionary of name to value pairs
        if isParam:
            self.params_dict[var.name] = new_val
        else:
            self.fields_dict[var.name] = new_val


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
                    res = arg1 / arg2
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the / operator")
            case '%':
                if self.both_int(arg1, arg2):
                    res = arg1 % arg2
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the / operator")
            case '==':
                if self.both_int(arg1, arg2) or self.both_str(arg1, arg2) or self.both_bool(arg1, arg2):
                    return arg1 == arg2
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the == operator")
            case '!=':
                if self.both_int(arg1, arg2) or self.both_str(arg1, arg2) or self.both_bool(arg1, arg2):
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

        return res


    def unwrap_simp_exp(self,exp):
        exp, isVar = remove_line_num(exp)
        # valid variable
        if isVar and  exp in self.fields_dict.keys():
            exp = self.fields_dict[exp]
        #invalid variable
        elif isVar and exp not in self.fields_dict.keys():
            self.int.error(ET.NAME_ERROR, "Undefined variable")
        return exp


    def both_str(self, arg1, arg2):
        return isinstance(arg1, str) and isinstance(arg2, str)


    def both_int(self, arg1, arg2):
        return isinstance(arg1, int) and isinstance(arg2, int)
    
    def both_bool(self, arg1, arg2):
        return isinstance(arg1, bool) and isinstance(arg2, bool)


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