from intbase import ErrorType as ET
from VariableDef import VariableDef
from MethodDef import MethodDef
from ObjectDef import ObjectDef

class ClassDef:
    def __init__(self, class_name, interpreter):
        self.class_name = class_name
        self.int = interpreter

        self.fields = set()
        self.field_names = set()
        self.methods = set()
        self.method_names = set()

    def __str__(self):
        return f'Class {self.class_name}\nFields: {self.fields}\nMethods: {self.methods}\n'

    def __repr__(self):
        return self.__str__()

    def instantiate_object(self):
        obj = ObjectDef(self.class_name, self.fields, self.methods, self.int)
        # for method in self.methods:
        #     obj.add_method(method)
        # for field in self.fields:
        #     obj.add_field(field.name(), field.initial_value())
        return obj

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