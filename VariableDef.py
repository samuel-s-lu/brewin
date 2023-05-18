class VariableDef:
    StrToType = {'int':int, 'string':str, 'bool':bool,}

    def __init__(self, var_type, name, value, isObj):
        self.name = name
        self.value = value


        if isObj:
            # if isInit and value is not None:
            #     raise TypeError("Object fields must be initialized to 'null'")
            # else:
            from ObjectDef import ObjectDef
            self.type = ObjectDef
            self.class_type = var_type
            # print(self.class_type)
        else:
            var_type = VariableDef.StrToType[var_type]
            # print(var_type)
            if var_type is not type(value):
                raise TypeError("Type of variable does not match assigned value")
            else:
                self.type = type(value)
        # print(self.type)
        # print("")

    def __str__(self):
        return f'Variable Name: {self.name}, Value: {self.value}, Type: {self.type}\n'

    def __repr__(self):
        return self.__str__()

    def update(self, value):
        self.value = value