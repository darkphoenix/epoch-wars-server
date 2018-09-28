#!/usr/bin/env python3

import socket
import threading
from player import Player

players = []
map_size = (10,10)

def addPlayer(conn):
    print("Player joined!")
    player = Player(conn, map_size)
    players.append(player)
    player.handleForever()

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 4200))
    s.listen(1)

    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=addPlayer, args=(conn,))
        t.daemon = True
        t.start()