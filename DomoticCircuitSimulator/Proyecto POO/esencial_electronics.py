
# Gives energy for electric components
class Plug:
    # SRP: only manages plug behavior.
    def __init__(self):
        self.positive_connection = False
        self.negative_connection = False


    def givesEnergy(self):
        print("Energy supplied")


    def connectionCables(self):
        print("Cables connected to plug")


class Cables:
    #  SRP: only handles cable behavior.
    def _init_(self, positive_color:str, negative_color:str):
        self.positive = False
        self.negative = False
        self.positive_color = positive_color
        self.negative_color = negative_color


    def connectPositiveCable(self):
        print("Positive cable connected")


    def connectNegativeCable(self):
        print("Negative cable connected")