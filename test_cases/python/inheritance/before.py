class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        return "Some generic animal sound"
    
    def eat(self):
        return f"{self.name} is eating"

class Mammal(Animal):
    def give_birth(self):
        return f"{self.name} gave birth to live young"

class Bird(Animal):
    def lay_eggs(self):
        return f"{self.name} laid eggs"

class Dog(Mammal):
    def speak(self):
        return "Woof!"
    
    def fetch(self):
        return f"{self.name} fetched the ball"

class Cat(Mammal):
    def speak(self):
        return "Meow!"
    
    def scratch(self):
        return f"{self.name} scratched the furniture"

# Multiple inheritance example
class Pet:
    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
    
    def get_owner(self):
        return self.owner

class WorkingDog(Dog):
    def __init__(self, name, job):
        super().__init__(name)
        self.job = job
    
    def work(self):
        return f"{self.name} is working as a {self.job}"

class FamilyPet(Pet, Dog):
    def __init__(self, name, owner):
        Pet.__init__(self, name, owner)
        Dog.__init__(self, name)
