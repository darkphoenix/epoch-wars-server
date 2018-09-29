from enum import Enum

class MapException(Exception):
    pass

class UnknownBuildingException(Exception):
    name = ''

    def __init__(self, name):
        self.name = name

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

class Building():
    radius = 0
    points = 0

    def new(name):
        if name.lower() == 'house':
            return House()
        raise UnknownBuildingException(name)

    def place(self, fields, pos):
        for x in range(-self.radius, self.radius + 1):
            for y in range(-self.radius, self.radius + 1):
                fields[x + pos[0]][y + pos[1]].blocked = True
        fields[pos[0]][pos[1]].building = self
        return fields

class House(Building):
    points = 1

    def __str__(self):
        return '🏠'

class Villa(Building):
    radius = 1
    points = 9

    def __str__(self):
        return '🏡'

class Tower(Building):
    def __str__(self):
        return '🏯'

class Field():
    def __init__(self):
        self.building = None
        self.blocked = False

    def __init__(self, building=None, blocked=False):
        self.building = building
        self.blocked = blocked

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
    size = (0, 0)
    buildings = {}

    def __init__(self, size=(10, 10)):
        self.fields = []
        self.size = size

    def display(self):
        fields = [[Field() for _ in range(self.size[0])] for _ in range(self.size[1])]
        for pos, building in self.buildings.items():
            fields = building.place(fields, pos)
        for row in fields:
            print(*map(str, row), sep='')

    def __str__(self):
        res = ''
        fields = [[Field() for _ in range(self.size[0])] for _ in range(self.size[1])]
        for pos, building in self.buildings.items():
            fields = building.place(fields, pos)
        for row in fields:
            res += ''.join(map(str, row)) + ';'
        return res

    def build(self, pos, building):
        if any([(pos[i] < building.radius) or (pos[i] >= self.size[i] - building.radius) for i in [0, 1]]):
            raise InvalidBuildException(pos, building, 'Out of bounds.')
        for p, b in self.buildings.items():
            if all([abs(p[i] - pos[i]) <= (building.radius + b.radius) for i in [0,1]]):
                raise InvalidBuildException(pos, building, 'Field blocked.')
        self.buildings[pos] = building

    def excavate(self, pos):
        if any([(pos[i] >= self.size[i]) or (pos[i] < 0) for i in [0, 1]]):
            raise InvalidExcavateException(pos, 'Out of bounds.')
        res = Field()
        for p, b in self.buildings.items():
            if all([abs(p[i] - pos[i]) <= b.radius for i in [0,1]]):
                res.blocked = True
            if all([abs(p[i] - pos[i]) == 0 for i in [0,1]]):
                res.building = b
        return res
