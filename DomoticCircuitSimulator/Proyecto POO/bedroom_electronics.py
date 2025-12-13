from electronic_component import ElectronicComponent



class Lights(ElectronicComponent):
    def __init__(self, name, voltage, polarized, connected, luminous: str):
        super().__init__(name, voltage, polarized, connected)
        self.luminous = luminous



# Multiple inheritance combining mixins respects ISP and OCP.
class Bulb(Lights):
    def turn_on(self):
        if self.connected == True:
            print(f"{self.name} Is on and emites light.")
        else:
            print (f"{self.name} isn't connected, please connect it.")
    
    def turn_off(self):
        print(f"{self.name} Is off")

    def broken(self):
        if self.voltage > 5: 
            print(f"{self.name} broke!. To much voltage")



# OCP: Lamp customizes illumination behavior via method overriding, without altering the parent class.
class Lamp(Lights):
    def __init__(self, name, voltage, polarized, connected, luminous, RGB: int):
        super().__init__(name, voltage, polarized, connected, luminous)
        self.RGB = RGB

    def turn_on(self):
        if self.connected == True:
            if self.RGB == 1:
                print(f"{self.name} Is on and emites a red light.")
            elif self.RGB == 2:
                print(f"{self.name} Is on and emites a blue light.")
            elif self.RGB == 3:
                print(f"{self.name} Is on and emites a green light.")
            else: 
                print(f"{self.name} Can't emite more than the 3 Base colors.")
        else:
            print (f"{self.name} isn't connected, please connect it.")
    
    def turn_off(self):
        print(f"{self.name} Is off")

    def broken(self):
        if self.voltage > 5: 
            print(f"{self.name} broke!. To much voltage")



class DeskLamp(Lights):
    # LSP and OCP: DeskLamp extends Lamp and modifies behavior without breaking substitution.
    def turn_on(self):
        if self.connected == True:
            print(f"{self.name} Is on and has a {self.luminous} intensity of light.")
        else:
            print (f"{self.name} isn't connected, please connect it.")
    
    def turn_off(self):
        print(f"{self.name} Is off")

    def broken(self):
        if self.voltage > 5: 
            print(f"{self.name} broke!. To much voltage")


