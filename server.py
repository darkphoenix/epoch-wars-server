#!/usr/bin/env python3

import socket
import threading
from player import Player
from queue import Queue, Empty
from message import *
import copy
import logging
import random, string
import json

logging.basicConfig(level=logging.DEBUG)

players = []
map_size = (10,10)
tokens = {}

def addPlayer(conn, num, q):
    logging.info("Player %d joined!" % num)
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    logging.debug("Player %d's rejoin token is %s" % (num, token))
    player = Player(conn, num, map_size, q, token)
    tokens[token] = player
    players.append(player)
    player.handleForever()

def mainThread(q):
    finished_players = []
    turn_counter = 0
    while True:
        msg = q.get()
        logging.debug("Got message: " + str(msg))
        if isinstance(msg, TowerMessage):
            for p in players:
                if p.number != msg.player:
                    p.tower(msg.pos)
        elif isinstance(msg, ExcavateMessage):
            players[msg.player].excavate_result = {'depth': -1, 'building': None, 'pos': msg.pos}
            for p in range(msg.player, len(players) + msg.player):
                looking_at = players[p % len(players)]
                if looking_at.map.excavate(msg.pos) is not None:
                    match = type(looking_at.map.excavate(msg.pos)).__name__.lower()
                    players[msg.player].excavate_result = {'depth': p - msg.player, 'building': match, 'pos': msg.pos}
                    break
        elif isinstance(msg, FinishTurnMessage):
            finished_players.append((msg.player, msg.score))
            if len(finished_players) == len(players):
                turn_counter += 1
                scores = [0] * len(players)
                for p in finished_players:
                    scores[p[0]] = p[1]
                finished_players = []
                for p in players:
                    p.endTurn(scores)

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 4200))
    s.listen(1)
    q = Queue()
    t = threading.Thread(target=mainThread, args=(q,))
    t.daemon = True
    t.start()

    num = 0
    while True:
        conn, addr = s.accept()
        try:
            sock = conn.makefile(mode='rw')
            client_welcome = json.loads(sock.readline())
            sock.close()
            if client_welcome['type'] == 'welcome':
                t = threading.Thread(target=addPlayer, args=(conn, num, q))
                t.daemon = True
                t.start()
                num += 1
            elif client_welcome['type'] == 'rejoin':
                tokens[client_welcome['token']].sock = conn
                tokens[client_welcome['token']].conn = conn.makefile(mode='rw')
        except:
             logging.error("Unexpected error: ", exc_info=True)