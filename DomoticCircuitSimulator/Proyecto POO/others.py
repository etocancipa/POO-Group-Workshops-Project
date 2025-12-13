class Temperature:
    #  SRP: manages only temperature-related logic.
    def _init_(self, celsius:float):
        self.celsius = celsius
        


    def increaseTemperature(self, celsius):
        if celsius > 20:
            print("It's warm")
            print("Turning on the air conditioning")


    def decreaseTemperature(self, celsius):
        if celsius < 5:
            print("It's cold")
            print("Turning on the heating")



