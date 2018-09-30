import json
from map import *
from message import *
from time import sleep
import logging
from connection_counter import ConnectionCounter

class Player:
    def __init__(self, connection, number, map_size, q, token, name):
        self.points = 0
        self.q = q
        self.number = number
        self.sock = connection
        self.conn = self.sock.makefile(mode='rw')
        self.turn_over = False
        self.excavate_result = None
        self.size = map_size
        self.name = name
        self.token = token
        self.tower_count = 5
        self.dead = False

        self.map = PlayerMap(map_size)
        self.sendWelcome()

    def sendWelcome(self):
        self.conn.write(json.dumps({'type': 'welcome','player': self.number, 'map_size': self.size, 'rejoin': self.token}))
        self.conn.write("\n")
        self.conn.flush()

    def tower(self, pos):
        self.map.tower(pos)

    def handleForever(self):
        while True:
            try:
                command = json.loads(self.conn.readline())
                if command['type'] == 'excavate':
                    logging.debug("Player " + str(self.number) + " excavated field (" + str(command['x']) + ", " + str(command['y']) + ")")
                    if (command['x'] >= self.size[0]) or (command['y'] >= self.size[1]) or any([(command[i] < 0) for i in ['x','y']]):
                        self.conn.write('{"type":"error", "message":"Out of bounds", "subtype":"InvalidExcavateError"}\n')
                        self.conn.flush()
                        continue
                    self.q.put(ExcavateMessage(self.number, (command['x'], command['y'])))
                elif command['type'] == 'build' and not self.turn_over:
                    if command['building'] == "tower":
                        if self.tower_count > 0 and self.points - Tower.base_price >= 0:
                            self.points -= Tower.base_price
                            self.tower_count -= 1
                            logging.debug("Player " + str(self.number) + " built a tower on field (" + str(command['x']) + ", " + str(command['y']) + ")")
                            self.map.build((command['x'], command['y']), Building.new(command['building']))
                            self.q.put(TowerMessage(self.number, (command['x'], command['y'])))
                        elif self.tower_count > 0:
                            self.conn.write('{"type":"error", "message":"You can\'t afford that!", "subtype":"InvalidBuildError"}\n')
                            self.conn.flush()
                            continue
                        else:
                            self.conn.write('{"type":"error", "message":"You can\'t build another tower!", "subtype":"InvalidBuildError"}\n')
                            self.conn.flush()
                            continue
                    else:
                        building_count = len(list(filter(lambda x: type(x).__name__.lower() == command['building'].lower(), self.map.buildings.values())))
                        if self.points - Building.new(command['building']).get_price(building_count) >= 0:
                            self.map.build((command['x'], command['y']), Building.new(command['building']))
                            self.points -= Building.new(command['building']).get_price(building_count)
                            logging.debug("Player " + str(self.number) + " built a " + command['building'] + " on field (" + str(command['x']) + ", " + str(command['y']) + ")")
                        else:
                            self.conn.write('{"type":"error", "message":"You can\'t afford that!", "subtype":"InvalidBuildError"}\n')
                            self.conn.flush()
                            continue
                    self.points += self.map.points()
                    self.q.put(FinishTurnMessage(self.number, self.points))
                    self.turn_over = True
                elif command['type'] == 'end_turn':
                    self.points += self.map.points()
                    self.q.put(FinishTurnMessage(self.number, self.points))
                    self.turn_over = True
                elif self.turn_over:
                    self.conn.write(json.dumps({"type":"error", "message":"Build action already made this turn", "subtype":"BuildActionAlreadyUsedError",\
                    "pos": self.map.turn_buildings[0][0], "building": type(self.map.turn_buildings[0][1]).__name__.lower()}))
                    self.conn.write("\n")
                    self.conn.flush()
                else:
                    self.conn.write('{"type":"error", "message":"Invalid command", "subtype":"InvalidCommandError"}\n')
                    self.conn.flush()

            except InvalidBuildException as error:
                self.conn.write('{"type":"error", "message":"' + str(error) + '", "subtype":"InvalidBuildError"}\n')
                self.conn.flush()
            except UnknownBuildingException as error:
                self.conn.write('{"type":"error", "message":"Invalid building type '+ error.name + '", "subtype":"UnknownBuildingError"}\n')
                self.conn.flush()
            except ValueError:
                try:
                    self.conn.write('{"type":"error", "message":"Invalid JSON", "subtype":"InvalidJSONError"}\n')
                    self.conn.flush()
                except:
                    if not self.dead:
                        ConnectionCounter.connectionDied()
                        self.dead = True
            except Exception as error:
                logging.error(error)
                try:
                    self.conn.write('{"type":"error", "message":"Internal server error", "subtype":"InternalServerError"}\n')
                    self.conn.flush()
                except:
                    ConnectionCounter.connectionDied()

    def endTurn(self, scores, turn):
        logging.debug("Current score for player " + str(self.number) + ": " + str(self.points))
        self.map.apply()
        self.turn_over = False

        current_prices = {}
        for b in ['house','villa','tower']:
            building_count = len(list(filter(lambda x: type(x).__name__.lower() == b, self.map.buildings.values())))
            current_prices[b] = Building.new(b).get_price(building_count)
        result_message = {"type":"end_of_turn", "scores": scores, "map": self.map.json(), "excavate_result": self.excavate_result, "turn": turn,\
        "current_prices": current_prices, "tower_count": self.tower_count}
        self.conn.write(json.dumps(result_message))
        self.conn.write("\n")

        self.excavate_result = None

        #map_mes = {"type":"debug", "message":str(self.map)}
        #self.conn.write(json.dumps(map_mes))
        #self.conn.write("\n")
        self.conn.flush()