class MethodDef:
    def __init__(self, name, args, statement):
        self.name = name
        self.args = args
        self.statement = statement

    def __str__(self) -> str:
        return f'Method Name: {self.name}, Args: {self.args}, Statement: {self.statement}\n'

    def __repr__(self):
        return self.__str__()