import json
from map import *
from message import *
from time import sleep
import logging

class Player:
    def __init__(self, connection, number, map_size, q):
        self.points = 0
        self.q = q
        self.number = number
        self.sock = connection
        self.conn = self.sock.makefile(mode='rw')
        self.turn_over = False

        self.map = PlayerMap(map_size)
        self.waiting_for_excavate = (-1, -1)

    def tower(self, pos):
        self.map.tower(pos)

    def handleForever(self):
        while True:
            try:
                command = json.loads(self.conn.readline())
                if command['type'] == 'excavate':
                    logging.debug("Player " + str(self.number) + " excavated field (" + str(command['x']) + ", " + str(command['y']) + ")")
                    self.waiting_for_excavate = (command['x'], command['y'])

                elif command['type'] == 'build' and not self.turn_over:
                    if command['building'] == "tower":
                        logging.debug("Player " + str(self.number) + " built a tower on field (" + str(command['x']) + ", " + str(command['y']) + ")")
                        self.map.build((command['x'], command['y']), Building.new(command['building']))
                        self.q.put(TowerMessage(self.number, (command['x'], command['y'])))
                    else:
                        logging.debug("Player " + str(self.number) + " built a " + command['building'] + " on field (" + str(command['x']) + ", " + str(command['y']) + ")")
                        self.map.build((command['x'], command['y']), Building.new(command['building']))
                    self.q.put(FinishTurnMessage(self.number))
                    self.turn_over = True
                elif self.turn_over:
                    self.conn.write('{"type":"error", "message":"Build action already made this turn"}\n')
                    self.conn.flush()
                else:
                    self.conn.write('{"type":"error", "message":"Invalid command"}\n')
                    self.conn.flush()

            except InvalidBuildException as error:
                self.conn.write('{"type":"error", "message":"' + str(error) + '"}\n')
                self.conn.flush()
            except UnknownBuildingException as error:
                self.conn.write('{"type":"error", "message":"Invalid building type '+ error.name + '"}\n')
                self.conn.flush()
            except Exception as error:
                logging.error(error)
                self.conn.write('{"type":"error", "message":"Invalid JSON"}\n')
                self.conn.flush()

    def endTurn(self):
        self.points += self.map.points()
        logging.debug("Current score for player " + str(self.number) + ": " + str(self.points))
        self.map.apply()
        self.turn_over = False
        self.conn.write(self.map.json())
        self.conn.write("\n")
        map_mes = {"type":"debug", "message":str(self.map)}
        self.conn.write(json.dumps(map_mes))
        self.conn.write("\n")
        self.conn.flush()
        if self.waiting_for_excavate[0] != -1:
            self.conn.write(json.dumps({'type':'excavate', 'res': 'Feld ' \
            + str(self.waiting_for_excavate[0]) + ', ' + str(self.waiting_for_excavate[1]) + ' hat nichts.'}))
            self.conn.write("\n")
            self.conn.flush()