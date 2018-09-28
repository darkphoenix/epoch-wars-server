from enum import Enum

class Field(Enum):
    EMPTY = 0
    HOUSE = 1
    VILLA = 2
    TOWER = 3

    def __repr__(self):
        if self.name == 'EMPTY':
            return '__'
        elif self.name == 'HOUSE':
            return '🏠'
        elif self.name == 'VILLA':
            return '🏡'
        elif self.name == 'TOWER':
            return '🗼'
        else:
            return '??'

    def __str__(self):
        return self.__repr__()


class PlayerMap():
    fields = []

    def __init__(self, size=(20, 20)):
        for x in range(size[0]):
            tmp = []
            for y in range(size[1]):
                tmp.append(Field.EMPTY)
            self.fields.append(tmp)

    def display(self):
        for row in self.fields:
            print(*map(str, row), sep='')

