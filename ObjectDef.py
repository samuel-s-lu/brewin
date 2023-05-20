# from interpreterv1 import Interpreter
from intbase import ErrorType as ET
from MethodDef import MethodDef
from VariableDef import VariableDef, create_anon_value

class ObjectDef:
    def __init__(self, category, fields:set[VariableDef], methods:set[MethodDef], interpreter):
        self.category = category
        self.fields = fields
        self.methods = methods
        self.int = interpreter

        self.fields_dict = {name:value for name, value in zip([x.name for x in fields], [x.value for x in fields])}
        self.params = set()
        self.params_dict = dict()

        self.returned = False
        self.rtype = None

        self.stack = []

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

        self.rtype = method.rtype
        try:
            self.rtype = VariableDef.StrToType[self.rtype]
        except:
            pass

        statement = method.statement

        old_params = self.params
        old_params_dict = self.params_dict
        if param_vals:
            self.params.clear()
            self.params_dict.clear()
            for param, arg_val in zip([x for x in method.args], [x.value for x in param_vals]):
                arg_type = param[0]
                arg_name = param[1]
                try:
                    new_var = VariableDef(arg_type, arg_name, arg_val, True) if arg_type in self.int.class_names else \
                              VariableDef(arg_type, arg_name, arg_val, False)
                    self.params.add(new_var)
                    self.params_dict[arg_name] = arg_val
                except TypeError:
                    self.int.error(ET.NAME_ERROR, "Type mismatch in passed arguments and formal parameters")
                except KeyError:
                    self.int.error(ET.NAME_ERROR, f"Attempting to pass in an argument annotated with an undefined class: {arg_type}")
            # print(f'self params: {self.params}')
            # print(f'self params dict: {self.params_dict}')
        # print(f'statement: {statement}')
        res = self.run_statement(statement, method.rtype)
        self.params = old_params
        self.params_dict = old_params_dict
        self.returned = False
        # print(f'run statement result: {res}')
        return res


    def run_statement(self, statement, return_type=None):
        res = None
        match statement[0]:
            case self.int.PRINT_DEF:
                res = ''
                for i in range(1,len(statement)):
                    next = self.resolve_exp(statement[i]).value
                    # print(next)
                    if next is True:
                        next = 'true'
                    if next is False:
                        next = 'false'
                    res += str(next)
                
                self.int.output(res)

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
                new_anon_val = self.resolve_exp(statement[2], return_type)
                # print(f'new val: {new_val}\n===\n')

                self.set_var(target_name, new_anon_val)
                # print(f"returned?: {self.returned}")

                # if self.params:
                #     print(f'Updated params: {self.params}')
                # else:
                #     print('No parameters')
                # print(f'Updated fields: {self.fields}')

            case self.int.BEGIN_DEF:
                for i in range(1,len(statement)):
                    # print(f'statement: {statement[i]}')
                    res = self.run_statement(statement[i], return_type)
                    if self.returned:
                        return res
                if return_type != 'void':
                    res = self.def_return(return_type)
            
            case self.int.INPUT_INT_DEF | self.int.INPUT_STRING_DEF:
                target_name = statement[1]
                new_val = self.int.get_input()
                new_val = create_anon_value(new_val)
                self.set_var(target_name, new_val)
            
            case self.int.IF_DEF:
                # if len(statement) > 4:
                #     self.int.error(ET.SYNTAX_ERROR, "Invalid number of arguments provided to 'if'")

                pred = self.resolve_exp(statement[1]).value
                if not isinstance(pred, bool):
                    self.int.error(ET.TYPE_ERROR, "non boolean provided as condition to 'if'")
                
                res = None
                if pred:
                    res = self.run_statement(statement[2], return_type)
                else:
                    if len(statement) == 4:
                        res = self.run_statement(statement[3], return_type)

            case self.int.WHILE_DEF:
                # if len(statement) > 3:
                #     self.int.error(ET.SYNTAX_ERROR, "Invalid number of arguments provided to 'while'")

                pred = self.resolve_exp(statement[1]).value
                if not isinstance(pred, bool):
                    self.int.error(ET.TYPE_ERROR, "non boolean provided as condition to 'while'")

                res = None
                while pred and not self.returned:
                    res = self.run_statement(statement[2], return_type)
                    pred = self.resolve_exp(statement[1]).value
            
            case self.int.CALL_DEF:
                obj_name = statement[1]
                method_name = statement[2]
                method_params = []
                if len(statement) >= 4:
                    method_params = [self.resolve_exp(p) for p in statement[3:]]
                # print(statement[3:])
                # print(method_params)

                res = self.call_method_aux(obj_name, method_name, method_params)
            
            case self.int.RETURN_DEF:
                # if len(statement) > 2:
                #     self.int.error(ET.SYNTAX_ERROR, "Invalid number of arguments provided to 'return'")
                res = None
                self.returned = True
                if len(statement) == 2:
                    ret_val = self.resolve_exp(statement[1], return_type)
                    # print(statement)
                    # print(f'ret val: {ret_val}')
                    
                    self.check_rtype(ret_val)
                    # print("returned")

                    res = ret_val
                else:
                    if return_type != 'void':
                        res = self.def_return(return_type)

            case self.int.LET_DEF:
                local_vars = statement[1]
                self.add_to_let_stack(local_vars)

                for i in range(2, len(statement)):
                    # print(self.stack)
                    res = self.run_statement(statement[i], return_type)
                    if self.returned:
                        self.stack.pop()
                        return res
                    
                if return_type != 'void':
                    res = self.def_return(return_type)
                
                self.stack.pop()

                
        return res


    def search_let_stack(self, target_name):
        for scope in reversed(self.stack):
            for local in scope:
                if local.name == target_name:
                    return local
                
        return None


    def add_to_let_stack(self, local_vars):
        temp = []
        for var in local_vars:
            var_type = var[0]
            var_name = var[1]
            var_value = create_anon_value(var[2]).value

            try:
                if var_type in self.int.class_names and var_value is not None:
                    self.int.error(ET.TYPE_ERROR, "Object fields must be initialized to 'null'")

                new_var = VariableDef(var_type, var_name, var_value, True) if var_type in self.int.class_names else \
                            VariableDef(var_type, var_name, var_value, False)
                temp.append(new_var)
            except TypeError:
                self.int.error(ET.TYPE_ERROR, "Field and initial value assignment type mismatch")
            except KeyError:
                self.int.error(ET.TYPE_ERROR, "Attempting to annotate field with an undefined class")
            except:
                self.int.error(ET.TYPE_ERROR, "Error in local variable initialization")
        
        self.stack.append(temp)


    def call_method_aux(self, obj_name, method_name, method_params):
        res = None
        if obj_name == 'me':
            res = self.call_method(method_name, method_params)
        elif (type(obj_name) is not list) and (obj_name in self.fields_dict.keys()) and (self.resolve_exp(obj_name) == None):
            self.int.error(ET.FAULT_ERROR, "Deferencing null object")
        else:
            try:
                res = self.resolve_exp(obj_name).value.call_method(method_name, method_params)
            except AttributeError:
                self.int.error(ET.FAULT_ERROR, "Deferencing null object")
        return res



    def check_rtype(self, ret_val:VariableDef):
        if (self.rtype in VariableDef.primitives) and (self.rtype == ret_val.type):
            return
        elif (self.rtype not in VariableDef.primitives) and (ret_val.type is ObjectDef and self.rtype == ret_val.class_type):
            return
        
        self.int.error(ET.TYPE_ERROR,
                       f'Inconsistency between method return type and the type of the returned value')


    def type_check(self, var1:VariableDef, var2:VariableDef):
        """
        Throws TYPE_ERROR if type of var1 and var2 are inconsistent
        Otherwise do nothing
        """
        # print(f'var1: {var1}')
        # print(f'var2: {var2}')

        if self.both_obj(var1, var2) and \
           (var1.class_type == var2.class_type or var2.class_type == VariableDef.NOTHING or var1.class_type == VariableDef.NOTHING):
            return
        elif (not self.both_obj(var1, var2)) and (var1.type == var2.type):
            return
        
        self.int.error(ET.TYPE_ERROR,
                        f'Type mismatch | Type: {var1.type} and {var2.type} | Class Type: {var1.class_type} and {var2.class_type}')

    def set_var(self, target_name, new_val: VariableDef):
        var, var_scope = self.find_var(target_name)

        # print(f'self.rtype: {self.rtype}')
        # print(f'target_name: {target_name}')

        self.type_check(var, new_val)
        self.update_var(var, new_val, var_scope)
        



    def find_var(self, target_name):
        local = self.search_let_stack(target_name)
        if local:
            return local, VariableDef.LOCAL
        elif self.params:
            for var in self.params:
                if var.name == target_name:
                    return var, VariableDef.PARAM
        for var in self.fields:
            if var.name == target_name:
                return var, VariableDef.FIELD
            
        self.int.error(ET.NAME_ERROR, f"Undefined variable: {target_name}")
    

    def update_var(self, var:VariableDef, new_val, var_scope):
        # update set of variables
        var.update(new_val)
        # print(f'var: {var}')

        # update dictionary of name to value pairs
        if var_scope == VariableDef.PARAM:
            self.params_dict[var.name] = new_val
        elif var_scope == VariableDef.FIELD:
            self.fields_dict[var.name] = new_val
        
        # print(f'fields dict: {self.fields_dict}')


    def resolve_exp(self, exp, return_type=None) -> VariableDef:
        if type(exp) is not list:
            if isinstance(exp, VariableDef):
                return exp
            else:
                # print(f'exp: {exp}')
                try:
                    var, _ = self.find_var(exp)
                    return var
                except:
                    if exp == 'null' and return_type != 'void':
                        return create_anon_value(exp, return_type)
                    else:
                        res = create_anon_value(exp)
                        if res:
                            return res
                        
                        self.int.error(ET.NAME_ERROR,
                                       f'Undefined variable: {exp}')
        
        special_exps = {'new', 'call', '!'}
        if exp[0] not in special_exps:
            arg1 = self.resolve_exp(exp[1])
            arg2 = self.resolve_exp(exp[2])

        res = None
        match exp[0]:
            case '+':
                if self.both_str(arg1, arg2) or self.both_int(arg1, arg2):
                    val = arg1.value + arg2.value
                    res = VariableDef(type(val), VariableDef.ANON, val, False)
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the + operator")
            case '-':
                if self.both_int(arg1, arg2):
                    val = arg1.value - arg2.value
                    res = VariableDef(type(val), VariableDef.ANON, val, False)
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the - operator")
            case '*':
                if self.both_int(arg1, arg2):
                    val = arg1.value * arg2.value
                    res = VariableDef(type(val), VariableDef.ANON, val, False)
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the * operator")
            case '/':
                if self.both_int(arg1, arg2):
                    val = arg1.value // arg2.value
                    res = VariableDef(type(val), VariableDef.ANON, val, False)
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the / operator")
            case '%':
                if self.both_int(arg1, arg2):
                    val = arg1.value % arg2.value
                    res = VariableDef(type(val), VariableDef.ANON, val, False)
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the / operator")
            case '==':
                if self.both_int(arg1, arg2) or self.both_str(arg1, arg2) or self.both_bool(arg1, arg2):
                    val = arg1.value == arg2.value
                    res = VariableDef(type(val), VariableDef.ANON, val, False)
                elif self.both_obj(arg1, arg2):
                    self.type_check(arg1, arg2)
                    val =  arg1.value is arg2.value
                    res = VariableDef(type(val), VariableDef.ANON, val, False)
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the == operator")
            case '!=':
                if self.both_int(arg1, arg2) or self.both_str(arg1, arg2) or self.both_bool(arg1, arg2):
                    val = arg1.value != arg2.value
                    res = VariableDef(type(val), VariableDef.ANON, val, False)
                elif self.both_obj(arg1, arg2):
                    self.type_check(arg1, arg2)
                    val =  arg1.value is not arg2.value
                    res = VariableDef(type(val), VariableDef.ANON, val, False)
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the != operator")
            case '<':
                if self.both_str(arg1, arg2) or self.both_int(arg1, arg2):
                    val = arg1.value < arg2.value
                    res = VariableDef(type(val), VariableDef.ANON, val, False)
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the < operator")
            case '>':
                if self.both_str(arg1, arg2) or self.both_int(arg1, arg2):
                    val = arg1.value > arg2.value
                    res = VariableDef(type(val), VariableDef.ANON, val, False)
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the > operator")
            case '<=':
                if self.both_str(arg1, arg2) or self.both_int(arg1, arg2):
                    val = arg1.value <= arg2.value
                    res = VariableDef(type(val), VariableDef.ANON, val, False)
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the <= operator")
            case '>=':
                if self.both_str(arg1, arg2) or self.both_int(arg1, arg2):
                    val = arg1.value >= arg2.value
                    res = VariableDef(type(val), VariableDef.ANON, val, False)
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the >= operator")
            case '&':
                if self.both_bool(arg1, arg2):
                    val = arg1.value and arg2.value
                    res = VariableDef(type(val), VariableDef.ANON, val, False)
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the & operator")
            case '|':
                if self.both_bool(arg1, arg2):
                    val = arg1.value or arg2.value
                    res = VariableDef(type(val), VariableDef.ANON, val, False)
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible types using the | operator")
            case '!':
                arg = self.resolve_exp(exp[1]).value
                if isinstance(arg, bool):
                    val = not arg
                    res = VariableDef(type(val), VariableDef.ANON, val, False)
                else:
                    self.int.error(ET.TYPE_ERROR, "Incompatible type using the ! operator")

            case self.int.NEW_DEF:
                class_name = exp[1]
                class_def = self.int.find_class_def(class_name)
                val = class_def.instantiate_object()
                
                res = VariableDef(class_name, VariableDef.ANON, val, True)
            
            case self.int.CALL_DEF:
                obj_name = exp[1]
                method_name = exp[2]
                method_params = []
                if len(exp) >= 4:
                    method_params = [self.resolve_exp(p) for p in exp[3:]]
                # print(statement[3:])
                # print(method_params)

                res = self.call_method_aux(obj_name, method_name, method_params)

                return res
        return res


    def both_str(self, arg1, arg2):
        return isinstance(arg1.value, str) and isinstance(arg2.value, str)


    def both_int(self, arg1, arg2):
        return type(arg1.value) in {int} and type(arg2.value) in {int}
    
    def both_bool(self, arg1, arg2):
        return type(arg1.value) in {bool} and type(arg2.value) in {bool}
    
    def both_obj(self, arg1, arg2):
        return arg1.type is ObjectDef and arg2.type is ObjectDef


    def find_method(self, method_name):
        for m in self.methods:
            if m.name == method_name:
                return m
            
        self.int.error(ET.NAME_ERROR, "Method not found")
        return None
    

    def def_return(self, rtype):
        if rtype in VariableDef.primitives:
            if rtype in {int, 'int'}:
                return create_anon_value('0')
            elif rtype in {str, 'str'}:
                return create_anon_value("")
            elif rtype in {bool}:
                return create_anon_value('false')       
        else:
            return create_anon_value('null', rtype)