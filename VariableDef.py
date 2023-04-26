class VariableDef:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.type = type(value)

    def __str__(self):
        return f'Variable Name: {self.name}, Value: {self.value}, Type: {self.type}\n'

    def __repr__(self):
        return self.__str__()

    def update(self, value):
        self.value = value
        self.type = type(value)