class Vehicle:
    def __init__(self, brand, model, year) -> None:
        self.brand = brand
        self.model = model
        self.year = year
        self.running = False

    def start_engine(self):
        self.running = True
        return f"{self.brand} {self.model}'s engine started"
    
    def stop_engine(self):
        self.running = False
        return f"{self.brand} {self.model}'s engine Stopped"
    
    def description(self):
        return f"{self.brand} of {self.year} with {self.model} model"
    

class Car(Vehicle):

    def __init__(self, brand, model, year, num_doors) -> None:
        super().__init__(brand, model, year)
        self.num_doors = num_doors
        self.wheels = 4
    
    def description(self):
        return f"{super().description()}, {self.num_doors} doors, {self.wheels} wheels"


    def drive(self):
        if self.running:
            return f"The {self.brand} {self.model} is driving smoothly"
        return f"Start the engine first!"

class Motorcycle(Vehicle):
    """Motorcycle class that inherits from Vehicle"""
    def __init__(self, brand, model, year, has_sidecar):
        super().__init__(brand, model, year)
        self.has_sidecar = has_sidecar
        self.wheels = 2 if not has_sidecar else 3
    
    def wheelie(self):
        if self.running and not self.has_sidecar:
            return f"The {self.brand} {self.model} pops a wheelie!"
        elif self.has_sidecar:
            return f"Can't do a wheelie with a sidecar!"
        else:
            return f"Start the engine first!"
    

    
# Create a Car object
my_car = Car("Toyota", "Camry", 2022, 4)
print(my_car.description())

# Call method from the parent class
print(my_car.start_engine())  # Output: Toyota Camry's engine started

# Call method specific to the Car class
print(my_car.drive())  # Output: The Toyota Camry is driving smoothly

# Create a Motorcycle object
my_motorcycle = Motorcycle("Harley-Davidson", "Sportster", 2021, False)

print(my_motorcycle.description())  # Output: 2021 Harley-Davidson Sportster
print(my_motorcycle.start_engine())  # Output: Harley-Davidson Sportster's engine started

print(my_motorcycle.wheelie())  # Output: The Harley-Davidson Sportster pops a wheelie!

class Test:
    def __init__(self, name) :
        self.name = name

    def __str__(self) -> str:
        return f"My name is {self.name}"

p = Test('akshay')
print(p)









