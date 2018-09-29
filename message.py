class Message():
    def __init__(self, player):
        self.player = player

    def __str__(self):
        return type(self).__name__ + "(" + str(self.player) + ")"

class PosMessage(Message):    
    def __init__(self, player, pos):
        self.player = player
        self.pos = pos
    
    def __str__(self):
        return type(self).__name__ + "(" + str(self.player) + ", " + str(self.pos) + ")"

class FinishTurnMessage(Message):
    def __init__(self, player, score):
        self.player = player
        self.score = score
    
    def __str__(self):
        return type(self).__name__ + "(" + str(self.player) + ", " + str(self.score) + ")"

class TowerMessage(PosMessage):
    pass

class ExcavateMessage(PosMessage):
    pass