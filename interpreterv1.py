from intbase import InterpreterBase as IB, ErrorType as ET
from bparser import BParser
from ClassDef import ClassDef
from MethodDef import MethodDef
from ObjectDef import ObjectDef
from VariableDef import VariableDef
from util import remove_line_num


class Interpreter(IB):

    def __init__(self, console_output=True, inp=None, trace_output=True):
        super().__init__(console_output, inp)
        self.classes = set()
        self.class_names = set()
    
    def run(self, program):
        res, parsed_program = BParser.parse(program)
        
        if not res:
            super().error(error_type=ET.SYNTAX_ERROR, description="Parsing Error")
                
        print("\n")
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
                super().error(ET.NAME_ERROR, "Duplicate class names not allowed", class_def[1].line_num)
            new_class = ClassDef(new_class_name, self)

            for token in class_def:
                if type(token) is list:
                    match token[0]:
                        case IB.FIELD_DEF:
                            field_name = token[1]
                            field_value = remove_line_num(token[2])[0]

                            new_class.add_field(VariableDef(field_name, field_value))
                        case IB.METHOD_DEF:
                            method_name = token[1]
                            method_args = token[2]
                            method_statement = token[3]
                            if method_name in new_class.method_names:
                                super().error(ET.NAME_ERROR, "Duplicate method names not allowed")

                            new_class.add_method(MethodDef(method_name, method_args, method_statement))
                        case _:
                            super().error(ET.SYNTAX_ERROR, 'Class can only contain field or method')
            self.classes.add(new_class)
            self.class_names.add(new_class_name)

    def find_class_def(self, class_def):
        for c in self.classes:
            if c.class_name == class_def:
                return c
            
        super().error(ET.NAME_ERROR, "Undefined class name")
        return None
    
# if __name__ == '__main__':
#     f = open('./call2.brewin')
#     program_lines = list(map(lambda x: x.rstrip("\n"), f.readlines()))
#     my_int = Interpreter()
#     my_int.run(program_lines)
#     f.close()