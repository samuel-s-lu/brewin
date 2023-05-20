def remove_line_num(bparser_str):
    """
    remove the bparser_str wrapper
    second return value indicates if first value is a variable or not
    """
    from VariableDef import VariableDef
    if isinstance(bparser_str, VariableDef):
        return bparser_str

    match bparser_str:
        case 'true':
            return VariableDef(bool, VariableDef.ANON, True, False)
        case 'false':
            return VariableDef(bool, VariableDef.ANON, False, False)
        case 'null':
            return VariableDef(VariableDef.NOTHING, VariableDef.ANON, None, True)
        # string
        case _ if bparser_str[0] == '"':
            s = str(bparser_str)
            s = s[1:len(s)-1]
            return VariableDef(str, VariableDef.ANON, s, False)
        case _:
            # int
            try:
                return VariableDef(int, VariableDef.ANON, int(str(bparser_str)), False)
            # variable
            except:
                return (str(bparser_str), True)