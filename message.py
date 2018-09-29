class Message():
    player = None

class TowerMessage():
    def __init__(self, player, pos):
        self.player = player
        self.pos = pos
