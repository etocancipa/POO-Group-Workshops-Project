from electronic_component import ElectronicComponent


class Electrodomestics(ElectronicComponent):
    def __init__(self, name, voltage, polarized, connected, power: int):
        super().__init__(name, voltage, polarized, connected)
        self.power = power




class TV(Electrodomestics):
    #  ISP: TV is breakable but LivingRoomElectronics is not forced to implement it.
    def turn_on(self):
        if self.connected == True:
            print(f"{self.name} Is on.")
        else:
            print (f"{self.name} isn't connected, please connect it.")
    
    def turn_off(self):
        print(f"{self.name} Is off")

    def broken(self):
        if self.power > 120: 
            print(f"{self.name} broke!. To much power.")




class Radio(Electrodomestics):
    def turn_on(self):
        if self.connected == True:
            print(f"{self.name} Is on.")
        else:
            print (f"{self.name} isn't connected, please connect it.")
    
    def turn_off(self):
        print(f"{self.name} Is off")

    def broken(self):
        if self.power > 120: 
            print(f"{self.name} broke!. To much power.")

class Computer(Electrodomestics):
    def turn_on(self):
        if self.connected == True:
            print(f"{self.name} Is on.")
        else:
            print (f"{self.name} isn't connected, please connect it.")
    
    def turn_off(self):
        print(f"{self.name} Is off")

    def broken(self):
        if self.power > 120: 
            print(f"{self.name} broke!. To much power.")