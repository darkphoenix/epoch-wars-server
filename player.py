import json
from turn import Turn
from map import *
from message import *
from time import sleep

class Player:
    def __init__(self, connection, number, map_size, q):
        self.points = 0
        self.q = q
        self.number = number
        self.sock = connection
        self.conn = self.sock.makefile(mode='rw')
        Turn.players += 1

        self.map = PlayerMap(map_size)
        self.waiting_for_excavate = (-1, -1)

    def tower(self, pos):
        self.map.tower(pos)

    def handleForever(self):
        while True:
            try:
                self.points += self.map.points()
                print(self.number, self.points)
                command = json.loads(self.conn.readline())
                if command['type'] == 'excavate':
                    print("Excavate!")
                    self.waiting_for_excavate = (command['x'], command['y'])

                elif command['type'] == 'build':
                    if command['building'] == "tower":
                        self.map.build((command['x'], command['y']), Building.new(command['building']))
                        self.q.put(TowerMessage(self.number, (command['x'], command['y'])))
                    else:
                        self.map.build((command['x'], command['y']), Building.new(command['building']))
                    Turn.wait_for_end()
                    sleep(0.05) # TODO better solution for waiting for possible towers
                    self.conn.write(str(self.map))
                    self.conn.write("\n")
                    self.conn.flush()
                    if self.waiting_for_excavate[0] != -1:
                        self.conn.writeline(json.dumps({'type':'excavate', 'res': 'Feld ' \
                        + str(self.waiting_for_excavate[0]) + ', ' + str(self.waiting_for_excavate[1]) + ' hat nichts.'}))
                        self.conn.write("\n")
                        self.conn.flush()

            except InvalidBuildException as error:
                self.conn.write('{"err":"' + str(error) + '"}\n')
                self.conn.flush()
            except UnknownBuildingException as error:
                self.conn.write('{"err":"Invalid building type '+ error.name + '"}\n')
                self.conn.flush()
            except Exception as error:
                print(error)
                self.conn.write('{"err":"Invalid JSON"}\n')
                self.conn.flush()
