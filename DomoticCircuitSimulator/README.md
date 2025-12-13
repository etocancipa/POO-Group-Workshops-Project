# SHOWCASE OF THE PROJECT VIA YOUTUBE:

https://www.youtube.com/watch?v=zyHnQsU8XeU

## UPDATED VIDEO (New changes):
https://www.youtube.com/watch?v=7pjaQMILNS0

# Smart Home Electronics Simulator – OOP Project

This project is a Smart Home Electronics Simulator developed for an Object-Oriented Programming (OOP) course. It models different rooms of a house, each containing multiple electronic devices, organized by category and functionality. The objective of the project is to demonstrate the application of OOP principles such as inheritance, polymorphism, encapsulation, class hierarchy design, and modular architecture.

## Project Structure

Proyecto POO/
│
├── main.py  
├── rooms.py  
├── others.py  
│
├── electronic_component.py  
├── esencial_electronics.py  
├── kitchen_electronics.py  
├── bedroom_electronics.py  
├── livingroom_electronics.py  
│
└── __pycache__/ (auto-generated)

## File Descriptions

main.py  
Entry point of the program. It initializes the rooms, loads electronic components, and manages program execution.

rooms.py  
Defines the Room class and its corresponding subclasses that represent different room types in the simulated house.

electronic_component.py  
Defines the base ElectronicComponent class, which includes general attributes and behaviors shared by all electronic devices.

esencial_electronics.py  
Contains essential electronic devices that can be used across different rooms.

kitchen_electronics.py  
Defines electronic devices specific to the kitchen, such as appliances.

bedroom_electronics.py  
Defines devices located in the bedroom, such as lights and fans.

livingroom_electronics.py  
Defines devices located in the living room, such as televisions and audio systems.

others.py  
Contains additional or optional electronic devices used across different room types.

__pycache__/  
Automatically generated Python cache files.

## How to Run the Simulator

Requirements  
- Python 3.10 or higher  
- No external libraries required  

Execution Steps  
1. Download or extract the project folder.  
2. Open a terminal inside the folder "Proyecto POO".  
3. Run the program using the following command:

cd path/to/Proyecto\ POO


The simulator will load the rooms and their corresponding electronic devices.

## Features

- Simulation of multiple room types, including kitchen, bedroom, and living room.  
- Each room contains a structured list of electronic components.  
- Devices inherit from the base ElectronicComponent class.  
- Support for basic device actions such as turning on, turning off, and displaying device information.  
- Encapsulation of device attributes such as name, power consumption, and operational status.  
- Modular organization into multiple files following OOP and clean architecture practices.

## User Manual (Summary)

When the program starts, the user is presented with room information and a list of available devices in each room. The system allows the user to perform actions such as:

- Displaying room information  
- Listing all electronics within a room  
- Turning on or off specific devices  
- Viewing device attributes and power consumption  

The exact interaction flow may vary depending on the implementation within main.py.

## Object-Oriented Design Principles Applied

Inheritance  
Specialized devices inherit shared attributes and behaviors from the ElectronicComponent class.

Polymorphism  
Devices may override base class methods to define room-specific or device-specific behaviors.

Encapsulation  
Attributes such as device name, status, and power consumption are protected to comply with OOP principles.

Modularity  
The program is split into multiple files based on functionality and responsibility, improving maintainability.

Composition  
Rooms are composed of lists of electronic components, demonstrating object composition within the overall system.

## External Resources

This project does not use external libraries. All functionality is implemented using Python’s standard library.

## Author

Developed by Valeria Aranda, Eddy Tocancipa, Luis Vargas for an Object-Oriented Programming (OOP) Class.
