from abc import ABC, abstractmethod

# Base class with a single responsibility: represent an electronic component
# SRP (Single Responsibility Principle): this class only handles generic electronic component behavior.
class ElectronicComponent(ABC):
    def __init__(self, name:str, voltage:float, polarized:bool,  connected:bool):
        self.name = name                   # Component name
        self.voltage = voltage             # Voltage
        self.polarized = polarized         # Mentions if the components is polarized
        self.connected = connected         # Checks if component is connected


    # Turns the component on
    @abstractmethod
    def turn_on(self):
        pass


    # Turns the component off
    @abstractmethod
    def turn_off(self):
        pass

    # Mixin for classes that can break
    # ISP again: being "breakable" is optional and injected via mixin instead of forcing all components to implement it.
    @abstractmethod
    def broken(self):
        pass
        
        

    # Indicates if it consumes power
    def consumePower(self):
        if self.connected:
            print(f"{self.name} is consuming power")
        else:
            print(f"{self.name} is not consuming power")







