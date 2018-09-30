#!/usr/bin/env python3

import socket
import threading
import _thread
from player import Player
from queue import Queue, Empty
from message import *
import copy
import logging
import random, string
import json
import sys
from connection_counter import ConnectionCounter

logging.basicConfig(level=logging.DEBUG)

players = []
map_size = (10,10)
tokens = {}
turn_counter = 0
num = 0

def getPlayers():
    res = []
    for p in players:
        res.append({'name': p.name, 'score': p.points})
    return res

def handleConnection(conn):
    global num
    try:
        sock = conn.makefile(mode='rw')
        client_welcome = json.loads(sock.readline())
        if client_welcome['type'] == 'welcome' and turn_counter == 0:
            sock.close()

            logging.info("Player %d joined!" % num)
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            logging.debug("Player %d's rejoin token is %s" % (num, token))

            player = Player(conn, num, map_size, q, token, client_welcome['name'])
            tokens[token] = player
            players.append(player)

            playersList = getPlayers()
            for p in players:
                p.endTurn(playersList, turn_counter)
            num += 1
            ConnectionCounter.connections += 1
            player.handleForever()
        elif client_welcome['type'] == 'rejoin':
            sock.close()
            if client_welcome['token'] in tokens:
                ConnectionCounter.connections += 1
                logging.debug("Player %d rejoined with a new connection!" %tokens[client_welcome['token']].number)
                tokens[client_welcome['token']].sock = conn
                tokens[client_welcome['token']].conn = conn.makefile(mode='rw')
                tokens[client_welcome['token']].sendWelcome()
                tokens[client_welcome['token']].endTurn(getPlayers(), turn_counter)
            else:
                conn.close()
        elif turn_counter > 0:
            sock.write(json.dumps({'type': 'error', 'message': 'The game is already running', 'subtype': 'GameAlreadyRunning'}))
            sock.write("\n")
            sock.flush()
            sock.close()
            conn.close()
    except:
        logging.error("Unexpected error: ", exc_info=True)

def mainThread(q):
    global turn_counter
    finished_players = {}
    scores = []
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
            if len(players) > len(scores):
                scores.extend([None]*(len(players)-len(scores)))
            finished_players[players[msg.player].name] = msg.score
            scores[msg.player] = {'name': players[msg.player].name, 'score': msg.score}
            if len(finished_players) == len(players):
                turn_counter += 1
                for p in players:
                    p.endTurn(scores, turn)
                finished_players = {}
                if turn_counter == 20:
                    for p in players:
                        p.conn.write(json.dumps({"type": "game_over", "message": "GAME OVER", "score": msg.score}))
                        p.conn.write("\n")
                        p.conn.flush()
                    _thread.interrupt_main()
                scores = [0] * len(players)

def adminConsole():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', int(sys.argv[1]) + 42))
    s.listen(1)
    while True:
        conn, addr = s.accept()
        sock = conn.makefile(mode='rw')   
        while True:
            try:
                sock.write(str(eval(sock.readline(), globals(), locals())) + "\n")
                sock.flush()
            except (ConnectionResetError, BrokenPipeError):
                break
            except Exception as err:
                if not sock.closed:
                    try:
                        sock.write(str(err) + "\n")
                        sock.flush()
                    except:
                        pass

if __name__ == "__main__":
    t = threading.Thread(target=adminConsole)
    t.daemon = True
    t.start()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', int(sys.argv[1])))
    s.listen(1)
    s.settimeout(10)
    q = Queue()
    t = threading.Thread(target=mainThread, args=(q,))
    t.daemon = True
    t.start()

    while True:
        try:
            conn, addr = s.accept()
            t = threading.Thread(target=handleConnection, args=(conn,))
            t.daemon = True
            t.start()
        except socket.timeout:
            pass
        except KeyboardInterrupt:
            logging.info("Exiting.")
            s.close()
            break