from enum import Enum
import json

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
    def __init__(self, pos, message):
        self.pos = pos
        self.message = message

    def __str__(self):
        return self.message

class Building():
    base_price = 0
    radius = 0
    points = 0

    def new(name):
        if name.lower() == 'house':
            return House()
        elif name.lower() == 'villa':
            return Villa()
        elif name.lower() == 'tower':
            return Tower()
        raise UnknownBuildingException(name)

    def place(self, fields, pos):
        for x in range(-self.radius, self.radius + 1):
            for y in range(-self.radius, self.radius + 1):
                fields[x + pos[0]][y + pos[1]].blocked = True
        fields[pos[0]][pos[1]].building = self
        return fields

    def get_price(self, count):
        def fib(n):
            if n < 2:
                return 1
            return fib(n-2) + fib(n-1)
        return fib(count)*self.base_price - 1

class House(Building):
    points = 1
    base_price = 1

    def __str__(self):
        return '🏠'

class Villa(Building):
    radius = 1
    base_price = 9
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
                return '🌲'
            else:
                return '░░'
        else:
            return str(self.building)

    def __str__(self):
        return self.__repr__()


class PlayerMap():
    def __init__(self, size=(10, 10)):
        self.buildings = {}
        self.turn_buildings = []
        self.turn_towers = []
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
            res += ''.join(map(str, row)) + '\n'
        return res
    
    def json(self):
        res = []
        for p, b in self.buildings.items():
            res.append({'pos': p, 'building': type(b).__name__.lower()})
        return res

    def build(self, pos, building):
        if any([(pos[i] < building.radius) or (pos[i] >= self.size[i] - building.radius) for i in [0, 1]]):
            raise InvalidBuildException(pos, building, 'Out of bounds.')
        for p, b in self.buildings.items():
            if all([abs(p[i] - pos[i]) <= (building.radius + b.radius) for i in [0,1]]):
                raise InvalidBuildException(pos, building, 'Field blocked.')
        self.turn_buildings.append((pos, building))

    def excavate(self, pos):
        if any([(pos[i] >= self.size[i]) or (pos[i] < 0) for i in [0, 1]]):
            raise InvalidExcavateException(pos, 'Out of bounds.')
        for p, b in self.buildings.items():
            if all([abs(p[i] - pos[i]) <= b.radius for i in [0,1]]):
                return b
        return None

    def tower(self, pos):
        if any([(pos[i] >= self.size[i]) or (pos[i] < 0) for i in [0, 1]]):
            raise InvalidBuildException(pos, Tower(), 'Out of bounds.')
        self.turn_towers.append(pos)

    def apply(self):
        for b in self.turn_buildings:
            self.buildings[b[0]] = b[1]
        self.turn_buildings = []
        for pos in self.turn_towers:
            remove = []
            for p, b in self.buildings.items():
                if all([abs(p[i] - pos[i]) <= b.radius for i in [0,1]]):
                    remove.append(p)
            for p in remove:
                del self.buildings[p]
            self.buildings[pos] = Tower()
        self.turn_towers = []

    def points(self):
        return sum(map(lambda x: x.points, self.buildings.values()))
