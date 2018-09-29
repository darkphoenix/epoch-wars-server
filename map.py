from enum import Enum

class MapException(Exception):
    pass

class InvalidBuildException(MapException):
    pos = None
    building = None

    def __init__(self, pos, building, message):
        self.pos = pos
        self.building = building
        self.message = message

    def __str__(self):
        return self.message

class InvalidExcavateException(MapException):
    pos = None

    def __init__(self, pos, message):
        self.pos = pos
        self.message = message

    def __str__(self):
        return self.message

class Building(Enum):
    HOUSE = 0
    VILLA = 1
    TOWER = 2

    def __repr__(self):
        if self.name == 'HOUSE':
            return '🏠'
        elif self.name == 'VILLA':
            return '🏡'
        elif self.name == 'TOWER':
            return '🗼'
        else:
            return '??'

    def __str__(self):
        return self.__repr__()

class Field():
    def __init__(self):
        self.building = None
        self.blocked = False

    def __repr__(self):
        if self.building is None:
            if self.blocked:
                return '╳╳'
            else:
                return '__'
        else:
            return str(self.building)

    def __str__(self):
        return self.__repr__()


class PlayerMap():

    def __init__(self, size=(10, 10)):
        self.fields = []
        self.size = size
        for x in range(size[0]):
            tmp = []
            for y in range(size[1]):
                tmp.append(Field())
            self.fields.append(tmp)

    def display(self):
        for row in self.fields:
            print(*map(str, row), sep='')

    def __str__(self):
        res = ''
        for row in self.fields:
            res += ''.join(map(str, row)) + ';'
        return res

    def build(self, pos, building):
        if building == Building.VILLA:
            if (pos[0] >= self.size[0] - 1) or (pos[0] < 1) or (pos[1] >= self.size[1] - 1) or (pos[1] < 1):
                raise InvalidBuildException(pos, building, 'Out of bounds.')
            for x in [-1, 0, 1]:
                for y in [-1, 0, 1]:
                    if self.fields[pos[0] + x][pos[1] + y].blocked:
                        if self.fields[pos[0]][pos[1]].blocked:
                            raise InvalidBuildException(pos, building, 'Field blocked.')
            for x in [-1, 0, 1]:
                for y in [-1, 0, 1]:
                    self.fields[pos[0] + x][pos[1] + y].blocked = True
        else:
            if (pos[0] >= self.size[0]) or (pos[0] < 0) or (pos[1] >= self.size[1]) or (pos[1] < 0):
                raise InvalidBuildException(pos, building, 'Out of bounds.')
            if self.fields[pos[0]][pos[1]].blocked:
                raise InvalidBuildException(pos, building, 'Field blocked.')
            self.fields[pos[0]][pos[1]].blocked = True
        self.fields[pos[0]][pos[1]].building = building

    def excavate(self, pos):
        if (pos[0] >= self.size[0]) or (pos[0] < 0) or (pos[1] >= self.size[1]) or (pos[1] < 0):
            raise InvalidExcavateException(pos, 'Out of bounds.')
        res = self.fields[pos[0]][pos[1]]
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                f = self.fields[pos[0] + x][pos[1] + y]
                if f.building == Building.VILLA:
                    res = f
        return res
