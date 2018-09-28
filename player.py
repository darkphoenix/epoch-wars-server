import json
from turn import Turn

class Player:
    def __init__(self, connection):
        self.sock = connection
        self.conn = self.sock.makefile(mode='rw')
        Turn.players += 1

        self.map = [[0] * 5 for i in range(5)]
        self.waiting_for_excavate = (-1, -1)

    def handleForever(self):
        while True:
            try:
                command = json.loads(self.conn.readline())
                if command['type'] == 'excavate':
                    print("Excavate!")
                    self.waiting_for_excavate = (command['x'], command['y'])

                elif command['type'] == 'build':
                    #Build
                    Turn.wait_for_end()
                    if self.waiting_for_excavate[0] != -1:
                        self.conn.writeline(json.dumps({'type':'excavate', 'res': 'Feld ' \
                        + str(self.waiting_for_excavate[0]) + ', ' + str(self.waiting_for_excavate[1]) + ' hat nichts.'}))
                        self.conn.write("\n")
                        self.conn.flush()

            except Exception as error:
                print(error)
                self.conn.write('{"err":"Invalid JSON"}\n')
                self.conn.flush()
