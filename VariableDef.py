from intbase import InterpreterBase as IB
import copy

class VariableDef:
    StrToType = {'int':int, 'string':str, 'bool':bool}

    primitives = {'int', 'string', 'bool', int, str, bool}

    ANON = 'ANON HASH: IHEARTMEIMEI'
    NOTHING = 'NOTHING HASH: SAMMEI5EVER'
    LOCAL = 'LOCAL HASH: HAMMYWIZZY'
    PARAM = 'PARAM HASH: XIAOBAOBEI'
    FIELD = 'FIELD HASH: ERIKISDEAD'

    def __init__(self, var_type, name, value, isObj):
        self.name = name
        self.value = value
        self.isObj = isObj
        self.class_type = None
        self.cur_class_type = None


        if isObj:
            from ObjectDef import ObjectDef
            self.type = ObjectDef
            self.class_type = var_type
            self.cur_class_type = var_type
            # print(self.class_type)
        else:
            if isinstance(var_type, str):
                var_type = VariableDef.StrToType[var_type]
            # print(var_type)
            if var_type is not type(value):
                raise TypeError("Type of variable does not match assigned value")
            else:
                self.type = type(value)
                self.class_type = self.type
        # print(self.type)
        # print("")

    def __str__(self):
        return f'Variable Name: {self.name}\nType: {self.type}\nClass Type: {self.class_type}\nCurrent Class Type: {self.cur_class_type}\nValue: {self.value}\n'

    def __repr__(self):
        return self.__str__()

    def update(self, other):
        self.value = other.value
        if self.cur_class_type:
            self.cur_class_type = other.cur_class_type

def create_anon_value(val, class_type=None):
    if class_type:
        if val == IB.NULL_DEF:
            return VariableDef(class_type, VariableDef.ANON, None, True)
        else:
            # if not val.parametrized_mapping:
                return VariableDef(class_type, VariableDef.ANON, val, True)
            # templated value
            # else:
            #     class_name = class_type.split('@')[0]
            #     types = class_type.split('@')[1:]
            #     class_type = [class_name]
            #     for t in types:
            #         class_type.append(val.parametrized_mapping[t])
            #     return VariableDef('@'.join(class_type), VariableDef.ANON, val, True)
    if val == IB.TRUE_DEF:
        return VariableDef(bool, VariableDef.ANON, True, False)
    elif val == IB.FALSE_DEF:
        return VariableDef(bool, VariableDef.ANON, False, False)
    elif val == "":
        return VariableDef(str, VariableDef.ANON, "", False)
    elif val.lstrip("-").isnumeric():
        return VariableDef(int, VariableDef.ANON, int(str(val)), False)
    elif type(val) is str and not class_type:
        return VariableDef(str, VariableDef.ANON, val, False)
    elif val[0] == '"' and not class_type:
        s = str(val)
        return VariableDef(str, VariableDef.ANON, s.strip('"'), False)
    elif val == IB.NULL_DEF:
        return VariableDef(VariableDef.NOTHING, VariableDef.ANON, None, True)
    return None

def create_def_value(name, type):
    if type in VariableDef.primitives:
        if type in {int, 'int'}:
            new_var = create_anon_value('0')
        elif type in {str, 'string'}:
            new_var = create_anon_value("")
        elif type in {bool, 'bool'}:
            new_var = create_anon_value('false')
    else:
        new_var = create_anon_value('null', type)

    new_var.name = name
    return new_var