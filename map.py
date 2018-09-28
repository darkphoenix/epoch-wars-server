from enum import Enum

class MapError(Exception):
    pass

class InvalidBuild(MapError):
    def __init__(self, pos, building):
        pass


class Buliding(Enum):
    HOUSE = 0
    VILLA = 1
    TOWER = 2

    def __repr__(self):
        if self.building == 'HOUSE':
            return '🏠'
        elif self.building == 'VILLA':
            return '🏡'
        elif self.building == 'TOWER':
            return '🗼'
        else:
            return '??'

    def __str__(self):
        return self.__repr__()

class Field():
    building = None
    blocked = False

    def __repr__(self):
        if self.building is None:
            if self.blocked:
                return '╳╳'
            else:
                return '  '
        else:
            return str(self.building)

    def __str__(self):
        return self.__repr__()


class PlayerMap():
    fields = []

    def __init__(self, size=(20, 20)):
        for x in range(size[0]):
            tmp = []
            for y in range(size[1]):
                tmp.append(Field())
            self.fields.append(tmp)

    def display(self):
        for row in self.fields:
            print(*map(str, row), sep='')

    def build(self, pos, building):
        pass
