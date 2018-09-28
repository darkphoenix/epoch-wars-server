class Turn(object):
    players = 0
    waiting = 0

    def wait_for_end():
        Turn.waiting += 1
        while True:
            if Turn.players == Turn.waiting or Turn.waiting == 0:
                Turn.waiting = 0
                return