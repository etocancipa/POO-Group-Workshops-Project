from electronic_component import ElectronicComponent


class Resistance(ElectronicComponent):
    # LSP (Liskov Substitution Principle): this class can replace its parent ElectronicComponent without breaking behavior.
    def __init__(self, name, voltage, polarized, connected, resistance):
        super().__init__(name, voltage, polarized, connected)
        self.resistance = resistance  # Keeps the original logic


    def dividesVoltage(self):
        voltage = self.voltage / self.resistance


    def protectsComponents(self):
        print("Components have been protected")



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