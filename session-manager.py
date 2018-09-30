#!/usr/bin/env python3

import socket
from socket import errno
import time
from random import randint
import subprocess

def getPort():
    port = randint(42000, 42100)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', port))
    except socket.error as e:
        if e.errno == errno.EADDRINUSE:
            s.close()
            return getPort()
    else:
        s.close()
        return port

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 4200))
    s.listen(1)

    waitlist = []
    while True:
        conn, addr = s.accept()
        waitlist.append(conn)
        if len(waitlist) == 2:
            port = getPort()
            print("Starting server on port %d" % port)
            subprocess.Popen(["./server.py", str(port)])
            for conn in waitlist:
                conn.sendall(("10.42.0.146:" + str(port) + "\n").encode('utf-8'))
            while len(waitlist) > 0:
                conn = waitlist.pop()
                try:
                    conn.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                try:
                    conn.close()
                except:
                    pass