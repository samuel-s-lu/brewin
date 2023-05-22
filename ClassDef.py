from intbase import ErrorType as ET
from VariableDef import VariableDef
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

    def __str__(self):
        return f'Class {self.class_name}\nFields: {self.fields}\nMethods: {self.methods}\nSuper Class: {self.super_class_name}\nChildren: {self.children}\n'

    def __repr__(self):
        return self.__str__()
    
    def add_child(self, class_name):
        self.children.add(class_name)
        if self.super_class_def:
            self.super_class_def.add_child(class_name)


    def instantiate_object(self) -> ObjectDef:
        # print(self.fields)
        return ObjectDef(self.class_name, copy.deepcopy(self.fields), self.methods, self.int, self.super_class_name, self.super_obj, self.children)
    

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