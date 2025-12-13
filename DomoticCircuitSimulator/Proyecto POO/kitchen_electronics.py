from electronic_component import ElectronicComponent
from bedroom_electronics import Bulb



class Sensors(ElectronicComponent):
    #  SRP: represents only electronics in kitchens.
    #  LSP: can be used wherever an ElectronicComponent is expected.
    def __init__(self, name, voltage, polarized, connected):
        super().__init__(name, voltage, polarized, connected)



class HeatSensor(Sensors):
    # LSP: A sensor behaves like an electronic component.
    # ISP: Break functionality only added where needed.
    def __init__(self, name, voltage, polarized, connected, temperature: int):
        super().__init__("Heat Sensor", polarized, connected)
        self.temperature = temperature

    def turn_on(self):
        if self.connected == True:
            print(f"{self.name} Is on.")
        else:
            print (f"{self.name} isn't connected, please connect it.")
    
    def turn_off(self):
        print(f"{self.name} Is off")

    def broken(self):
        if self.voltage > 10: 
            print(f"{self.name} broke!. To much power.")

    def temperature_alarm(self):
        if self.temperature > 30:
            print("High temperature detected!")
            print(f"{self.name} ACTIVE")



class MovementSensor(Sensors):
    # Similar SOLID principles as HeatSensor
    def __init__(self, name, voltage, polarized, connected, laser: bool):
        super().__init__(name, voltage, polarized, connected)
        self.laser = laser


    def turn_on(self):
        if self.connected == True:
            print(f"{self.name} Is on.")
        else:
            print (f"{self.name} isn't connected, please connect it.")
    
    def turn_off(self):
        print(f"{self.name} Is off")

    def broken(self):
        if self.voltage > 10: 
            print(f"{self.name} broke!. To much power.")

    def movement_alarm(self):
        if self.laser == True:
            print("Movement Dectected.")
            print(f"{self.name} ACTIVE")






