from intbase import InterpreterBase as IB, ErrorType as ET
from bparser import BParser
from ClassDef import ClassDef
from MethodDef import MethodDef
from ObjectDef import ObjectDef
from VariableDef import VariableDef, create_anon_value, create_def_value


class Interpreter(IB):

    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.classes = set()
        self.class_names = set()
    
    def run(self, program):
        res, parsed_program = BParser.parse(program)
        
        # if not res:
        #     super().error(error_type=ET.SYNTAX_ERROR, description="Parsing Error")

        self.discover_classes(parsed_program)
        # print(f'# classes: {len(self.classes)}')
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
                super().error(ET.TYPE_ERROR, "Duplicate class names not allowed")
            self.class_names.add(new_class_name)

            # templated class
            if class_def[0] == 'tclass':
                new_class = ClassDef(new_class_name, self)
                for spec_type in class_def[2]:
                    new_class.spec_types[spec_type] = None
                    
            # derived class
            elif type(class_def[2]) is not list:
                super_class_name = class_def[3]
                if super_class_name not in self.class_names:
                    super().error(ET.TYPE_ERROR,
                                  f'Undefined class name: {super_class_name}')
                new_class = ClassDef(new_class_name, self, super_class_name)


                parent = self.find_class_def(super_class_name)
                parent.add_child(new_class_name)

            # normal class
            else:
                new_class = ClassDef(new_class_name, self)

            for token in class_def:
                match token[0]:
                    case IB.FIELD_DEF:
                        field_type = token[1]
                        field_name = token[2]

                        # checks for parametric field type
                        if '@' in field_type:
                            if field_type.split('@')[0] == new_class_name:
                                c_def = new_class
                            else:
                                c_def = self.find_class_def(field_type.split('@')[0])
                            num_class_spec_types = len(c_def.spec_types.keys())
                            num_field_spec_types = len(field_type.split('@')) - 1

                            # check number of field parametric types match with the number that the template requires
                            if num_class_spec_types != num_field_spec_types:
                                super().error(ET.TYPE_ERROR,
                                              f'Field {field_name} has {num_field_spec_types} types while class {c_def.class_name} require {num_class_spec_types} parametric types')
                            
                            # check that each parametric type is valid
                            types = field_type.split('@')[1:]
                            for t in types:
                                if t not in VariableDef.primitives and \
                                   t not in self.class_names and \
                                   t not in new_class.spec_types.keys():
                                    super().error(ET.TYPE_ERROR,
                                                  f"Field {field_name} has illegal type {t} within its type")

                        # checks for regular field type
                        elif field_type not in VariableDef.primitives and \
                             field_type not in self.class_names and \
                             field_type not in new_class.spec_types.keys():
                            super().error(ET.TYPE_ERROR,
                                          f"Attempting to annotate field with an undefined class {field_type}")

                        # default initialization
                        if len(token) == 3:
                            new_var = create_def_value(field_name, field_type)
                            
                        # initialization with a value
                        else:
                            # if field_type.split('@')[0] in self.class_names:
                            #     super().error(ET.TYPE_ERROR, 'Parametrized types may not be initialized with a value')
                            if (field_type in self.class_names or \
                                '@' in field_type) and \
                                token[3] != 'null':
                                super().error(ET.TYPE_ERROR, "Object fields must be initialized to 'null'")

                            field_value = create_anon_value(token[3]).value
                            try:
                                # print(f'field type: {field_type}')
                                # print(f'spec type keys: {new_class.spec_types.keys()}')
                                if field_type.split('@')[0] in self.class_names or \
                                   field_type in new_class.spec_types.keys():
                                    new_var = VariableDef(field_type, field_name, field_value, True)
                                else:
                                    new_var = VariableDef(field_type, field_name, field_value, False)
                                
                            except TypeError:
                                super().error(ET.TYPE_ERROR, "Field and initial value assignment type mismatch")
                            except KeyError:
                                super().error(ET.TYPE_ERROR,
                                                f"Attempting to annotate field with an undefined class {field_type}")
                        
                        new_class.add_field(new_var)

                    case IB.METHOD_DEF:
                        method_rtype = token[1]
                        method_name = token[2]
                        method_args = token[3]
                        method_statement = token[4]

                        # check for duplicate formal params
                        if method_args:
                            arg_names = [arg[1] for arg in method_args]
                            max_freq = max(map(lambda x: arg_names.count(x), arg_names))
                            if max_freq > 1:
                                super().error(ET.NAME_ERROR,
                                            f'Duplicate formal parameters for method {method_name}')

                        try:
                            method_rtype = VariableDef.StrToType[method_rtype]
                        except KeyError:
                            if method_rtype not in self.class_names and \
                               method_rtype != 'void' and \
                               method_rtype.split('@')[0] not in self.class_names and \
                               method_rtype not in new_class.spec_types.keys():
                                super().error(ET.TYPE_ERROR,
                                              f'Invalid method return type {method_rtype} for method {method_name}')
                            
                            if '@' in method_rtype:
                                if method_rtype.split('@')[0] == new_class_name:
                                    c_def = new_class
                                else:
                                    c_def = self.find_class_def(method_rtype.split('@')[0])
                                num_class_spec_types = len(c_def.spec_types.keys())
                                num_return_spec_types = len(method_rtype.split('@')) - 1

                                # check number of return type parametric types match with the number the template requires
                                if num_class_spec_types != num_return_spec_types:
                                    super().error(ET.TYPE_ERROR,
                                                  f'Method {method_name} has {num_return_spec_types} types while class {c_def.class_name} require {num_class_spec_types} parametric types')
                                
                                # check that each parametric type is valid
                                types = method_rtype.split('@')[1:]
                                for t in types:
                                    if t not in VariableDef.primitives and \
                                       t not in self.class_names and \
                                       t not in new_class.spec_types.keys():
                                        super().error(ET.TYPE_ERROR,
                                                    f"Method {method_name} has illegal type {t} within its return type")

                        if method_name in new_class.method_names:
                            super().error(ET.NAME_ERROR, "Duplicate method names not allowed")

                        new_class.add_method(MethodDef(method_rtype, method_name, method_args, method_statement))

            self.classes.add(new_class)
            # print(f'added class: {new_class_name}')
            # print(f'{new_class}\n')

    def find_class_def(self, class_def) -> ClassDef:
        for c in self.classes:
            if c.class_name == class_def:
                return c
            
        super().error(ET.TYPE_ERROR, f"Undefined class name: {class_def}")