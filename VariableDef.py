from intbase import InterpreterBase as IB

class VariableDef:
    StrToType = {'int':int, 'string':str, 'bool':bool}

    primitives = {'int', 'string', 'bool', int, str, bool}

    ANON = 'HASH: IHEARTMEIMEI'
    NOTHING = 'HASH: SAMMEI5EVER'

    def __init__(self, var_type, name, value, isObj):
        self.name = name
        self.value = value
        self.isObj = isObj
        self.class_type = None


        if isObj:
            # if isInit and value is not None:
            #     raise TypeError("Object fields must be initialized to 'null'")
            # else:
            from ObjectDef import ObjectDef
            self.type = ObjectDef
            self.class_type = var_type
            # print(self.class_type)
        else:
            if isinstance(var_type, str):
                var_type = VariableDef.StrToType[var_type]
            # print(var_type)
            if var_type is not type(value):
                raise TypeError("Type of variable does not match assigned value")
            else:
                self.type = type(value)
        # print(self.type)
        # print("")

    def __str__(self):
        return f'Variable Name: {self.name}, Value: {self.value}, Type: {self.type}, Class Type: {self.class_type}\n' if self.class_type else \
               f'Variable Name: {self.name}, Value: {self.value}, Type: {self.type}\n'

    def __repr__(self):
        return self.__str__()

    def update(self, other):
        self.value = other.value

def create_anon_value(val, class_type=None):
    match val:
        case IB.TRUE_DEF:
            return VariableDef(bool, VariableDef.ANON, True, False)
        case IB.FALSE_DEF:
            return VariableDef(bool, VariableDef.ANON, False, False)
        case IB.NULL_DEF:
            return VariableDef(class_type, VariableDef.ANON, None, True) if class_type else \
                   VariableDef(VariableDef.NOTHING, VariableDef.ANON, None, True)
        case _ if val[0] == '"':
            s = str(val)
            return VariableDef(str, VariableDef.ANON, s.strip('"'), False)
        case _:
            # int
            try:
                return VariableDef(int, VariableDef.ANON, int(str(val)), False)
            # variable
            except:
                return (str(val), True)