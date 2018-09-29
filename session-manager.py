#!/usr/bin/env python3

import socket
import time
from random import randint
import subprocess

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 4200))
    s.listen(1)

    waitlist = []
    while True:
        conn, addr = s.accept()
        waitlist.append(conn)
        if len(waitlist) == 2:
            port = randint(49152, 65535)
            print("Starting server on port %d" % port)
            subprocess.Popen(["./server.py", str(port)])
            for conn in waitlist:
                conn.sendall(("10.42.0.146:" + str(port) + "\n").encode('utf-8'))
            for conn in waitlist:
                try:
                    conn.shutdown(socket.SHUT_RDWR)
                    conn.close()
                except:
                    pass
                waitlist.remove(conn)