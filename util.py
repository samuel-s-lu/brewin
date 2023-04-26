def remove_line_num(bparser_str):
    """
    remove the bparser_str wrapper
    second return value indicates if first value is a variable or not
    """
    match bparser_str:
        case 'true':
            return (True, False)
        case 'false':
            return (False, False)
        case 'null':
            return (None, False)
        # string
        case _ if bparser_str[0] == '"':
            s = str(bparser_str)
            s = s[1:len(s)-1]
            return (s, False)
        case _:
            # int
            try:
                return (int(str(bparser_str)), False)
            # variable
            except:
                return (str(bparser_str), True)