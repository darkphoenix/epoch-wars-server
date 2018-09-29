#!/usr/bin/env python3

import socket
import threading
from player import Player
from queue import Queue, Empty
from message import *
import copy
import logging

logging.basicConfig(level=logging.DEBUG)

players = []
map_size = (10,10)
finished_players = 0

def addPlayer(conn, num, q):
    logging.info("Player %d joined!" % num)
    player = Player(conn, num, map_size, q)
    players.append(player)
    player.handleForever()

def mainThread(q):
    while True:
        msg = q.get()
        logging.debug("Got message: " + str(msg))
        if isinstance(msg, TowerMessage):
            for p in players:
                if p.number != msg.player:
                    p.tower(msg.pos)
        elif isinstance(msg, FinishTurnMessage):
            finished_player += 1
            if finished_players == len(players):
                finished_players = 0
                for p in players:
                    p.endTurn()

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
        t = threading.Thread(target=addPlayer, args=(conn, num, q))
        t.daemon = True
        t.start()
        num += 1
