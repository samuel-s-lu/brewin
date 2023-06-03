class MethodDef:
    def __init__(self, rtype, name, args, statement):
        self.rtype = rtype
        self.name = name
        self.args = args
        self.statement = statement

    def __str__(self) -> str:
        return f'Method Name: {self.name}, Return Type: {self.rtype}, Args: {self.args}, Statement: {self.statement}\n'

    def __repr__(self):
        return self.__str__()