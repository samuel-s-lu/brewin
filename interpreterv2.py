from intbase import InterpreterBase as IB, ErrorType as ET
from bparser import BParser
from ClassDef import ClassDef
from MethodDef import MethodDef
from ObjectDef import ObjectDef
from VariableDef import VariableDef, create_anon_value


class Interpreter(IB):

    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.classes = set()
        self.class_names = set()
    
    def run(self, program):
        res, parsed_program = BParser.parse(program)
        
        # if not res:
        #     super().error(error_type=ET.SYNTAX_ERROR, description="Parsing Error")
                
        # print("\n")
        self.discover_classes(parsed_program)
        # for c in self.classes:
        #     print(c)
        
        class_def = self.find_class_def("main")
        if not class_def:
            super().error(ET.NAME_ERROR, "Main class not found")
        obj = class_def.instantiate_object() 
        obj.call_method("main", [])

    
    def discover_classes(self,parsed_program):
        for class_def in parsed_program:
            new_class_name = str(class_def[1])
            if new_class_name in self.class_names:
                super().error(ET.TYPE_ERROR, "Duplicate class names not allowed", class_def[1].line_num)
            new_class = ClassDef(new_class_name, self)

            for token in class_def:
                if type(token) is list:
                    match token[0]:
                        case IB.FIELD_DEF:
                            field_type = token[1]
                            if field_type in self.class_names and token[3] != 'null':
                                    super().error(ET.TYPE_ERROR, "Object fields must be initialized to 'null'")
                            field_name = token[2]

                            field_value = create_anon_value(token[3]).value

                            try:
                                new_var = VariableDef(field_type, field_name, field_value, True) if field_type in self.class_names else \
                                          VariableDef(field_type, field_name, field_value, False)
                                new_class.add_field(new_var)
                            except TypeError:
                                super().error(ET.TYPE_ERROR, "Field and initial value assignment type mismatch")
                            except KeyError:
                                super().error(ET.TYPE_ERROR, "Attempting to annotate field with an undefined class")

                        case IB.METHOD_DEF:
                            method_rtype = token[1]
                            method_name = token[2]
                            method_args = token[3]
                            method_statement = token[4]

                            if method_args:
                                arg_names = [arg[1] for arg in method_args]
                                max_freq = max(map(lambda x: arg_names.count(x), arg_names))
                                if max_freq > 1:
                                    super().error(ET.NAME_ERROR,
                                                f'Duplicate formal parameters for method {method_name}')

                            try:
                                method_rtype = VariableDef.StrToType[method_rtype]
                            except KeyError:
                                if method_rtype not in self.class_names and method_rtype != 'void':
                                    super().error(ET.TYPE_ERROR, f'Invalid method return type {method_rtype} for method {method_name}')

                            if method_name in new_class.method_names:
                                super().error(ET.NAME_ERROR, "Duplicate method names not allowed")

                            new_class.add_method(MethodDef(method_rtype, method_name, method_args, method_statement))
                        # case _:
                        #     super().error(ET.SYNTAX_ERROR, 'Class can only contain field or method')
            self.classes.add(new_class)
            self.class_names.add(new_class_name)

    def find_class_def(self, class_def):
        for c in self.classes:
            if c.class_name == class_def:
                return c
            
        super().error(ET.TYPE_ERROR, f"Undefined class name: {class_def}")
        return None