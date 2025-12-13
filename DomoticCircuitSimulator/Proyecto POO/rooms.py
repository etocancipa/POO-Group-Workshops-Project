# =======
# ROOMS
# =======


# SRP: Room only manages room information, nothing else.
class Room:
    def _init_(self, name:str):
        self.name = name


    def selectRoom(self):
        print(f"You are in the {self.name}")

class Kitchen(Room):
    #  SRP: handles room structure only.
    def _init_(self, shelf:int, oven:int, counter:int):
        super()._init_("Kitchen")
        self.shelf = shelf
        self.oven = oven
        self.counter = counter

class Bedroom(Room):
    def _init_(self, bed:int, wardrobe:int, shelf:int, nightstand:int):
        super()._init_("Bedroom")
        self.bed = bed
        self.wardrobe = wardrobe
        self.shelf = shelf
        self.nightstand = nightstand

class LivingRoom(Room):
    def _init_(self, couch:int, shelving:int):
        super()._init_("Living Room")
        self.couch = couch
        self.shelving = shelving