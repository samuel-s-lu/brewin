from intbase import ErrorType as ET
from VariableDef import VariableDef, create_def_value
from MethodDef import MethodDef
from ObjectDef import ObjectDef
import copy

class ClassDef:
    def __init__(self, class_name, interpreter, super_class_name=None):
        self.class_name = class_name
        self.int = interpreter

        self.fields = set()
        self.field_names = set()
        self.methods = set()
        self.method_names = set()

        self.super_class_name = super_class_name
        self.super_class_def = None
        self.super_obj = None
        if self.super_class_name:
            self.super_class_def = self.int.find_class_def(self.super_class_name)
            self.super_obj = self.super_class_def.instantiate_object()
        self.children = set()

        self.spec_types = dict()

    def __str__(self):
        return f'Class {self.class_name}\nFields: {self.fields}\nMethods: {self.methods}\nSuper Class: {self.super_class_name}\nChildren: {self.children}\nParametrized types: {self.spec_types}\n'

    def __repr__(self):
        return self.__str__()
    
    def add_child(self, class_name):
        self.children.add(class_name)
        if self.super_class_def:
            self.super_class_def.add_child(class_name)


    def instantiate_object(self, parametrized_types=None) -> ObjectDef:
        if not parametrized_types:
            return ObjectDef(self.class_name, copy.deepcopy(self.fields), copy.deepcopy(self.methods), self.int,
                             self.super_class_name, self.super_obj, self.children, parametrized_types)
        else:
            spec_types = {k:v for k,v in zip(self.spec_types.keys(), parametrized_types)}
            fields = self.replace_fields(spec_types)
            # print(f'old methods: {self.methods}')
            methods = self.replace_methods(spec_types)
            # print(f'new methods: {methods}')

            return ObjectDef(self.class_name, fields, methods, self.int,
                             self.super_class_name, self.super_obj, self.children, parametrized_types)

            # print(f'spec types: {self.spec_types}\n')
            # print(f'fields: {self.fields}\n')
            # print(f'methods: {self.methods}\n')


    def replace_methods(self, spec_types):
        methods = copy.deepcopy(self.methods)
        if methods:
            for m in methods:
                if m.rtype in spec_types.keys():
                    m.rtype = spec_types[m.rtype]
                if not isinstance(m.rtype, type) and '@' in m.rtype:
                    class_name = m.rtype.split('@')[0]
                    types = m.rtype.split('@')[1:]
                    res = [class_name]
                    for t in types:
                        try:
                            res.append(spec_types[t])
                        except:
                            res.append(t)
                    m.rtype = '@'.join(res)
                for arg in m.args:
                    if '@' in arg[0]:
                        class_name = arg[0].split('@')[0]
                        types = arg[0].split('@')[1:]
                        res = [class_name]
                        for t in types:
                            res.append(spec_types[t])
                        arg[0] = '@'.join(res)
        return methods


    def replace_fields(self, spec_types):
        fields = copy.deepcopy(self.fields)
        # print(f'old fields: {fields}\n')
        if fields:
            for field in fields:
                if not isinstance(field.class_type, type) and '@' in field.class_type:
                    class_name = field.class_type.split('@')[0]
                    types = field.class_type.split('@')[1:]
                    res = [class_name]
                    for t in types:
                        try:
                            res.append(spec_types[t])
                        except:
                            pass
                    field.class_type = '@'.join(res)
                    field.cur_class_type = field.class_type
                else:
                    try:
                        field.class_type = spec_types[field.class_type]
                    except:
                        pass
                    field.cur_class_type = field.class_type
                    if field.class_type in VariableDef.primitives:
                        try:
                            field.type = VariableDef.StrToType[field.class_type]
                            # print(f'field type: {field.type}')
                            # print(f'field value: {field.value}')
                            # print(f'field value type: {type(field.value)}')
                            # print(isinstance(field.value, field.type))
                            if field.value and not isinstance(field.value, field.type):
                                self.int.error(ET.TYPE_ERROR,
                                               f'Type mismatch for field {field.name}: {field.type} and {type(field.value)}')
                            if field.value is None:
                                temp = create_def_value(field.name, field.type)
                                field.value = temp.value
                            # print(f'field: {field}')
                        except KeyError:
                            pass
        
        # print(f'new fields: {fields}\n')
        return fields

    

    def add_field(self, var: VariableDef):
        if var.name in self.field_names:
            self.int.error(ET.NAME_ERROR, "Duplicate field names not allowed")
        
        self.fields.add(var)
        self.field_names.add(var.name)

    def add_method(self, method: MethodDef):
        if method.name in self.method_names:
            self.int.error(ET.NAME_ERROR, "Duplicate method names not allowed")

        self.methods.add(method)
        self.method_names.add(method.name)