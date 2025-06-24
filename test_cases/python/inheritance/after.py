from abc import ABC, abstractmethod

# Changed to abstract base class
class Animal(ABC):
    def __init__(self, name):
        self.name = name
    
    @abstractmethod
    def speak(self):
        pass
    
    def eat(self):
        return f"{self.name} is eating"

# Unchanged inheritance
class Mammal(Animal):
    def give_birth(self):
        return f"{self.name} gave birth to live young"
    
    # Implementing abstract method
    def speak(self):
        return "Mammal sound"

# Unchanged inheritance
class Bird(Animal):
    def lay_eggs(self):
        return f"{self.name} laid eggs"
    
    # Implementing abstract method
    def speak(self):
        return "Bird sound"

# Changed inheritance - no longer inherits from Mammal
class Dog(Animal):
    def speak(self):
        return "Woof!"
    
    def fetch(self):
        return f"{self.name} fetched the ball"
    
    # Added method that was in Mammal
    def give_birth(self):
        return f"{self.name} gave birth to puppies"

# Added new parent class for cats
class Feline(Mammal):
    def purr(self):
        return f"{self.name} is purring"

# Changed inheritance to use new parent
class Cat(Feline):
    def speak(self):
        return "Meow!"
    
    def scratch(self):
        return f"{self.name} scratched the furniture"

# Changed to interface-style class using ABC
class PetInterface(ABC):
    @abstractmethod
    def get_owner(self):
        pass

# Implementing interface instead of inheriting from concrete class
class Pet(PetInterface):
    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
    
    def get_owner(self):
        return self.owner

# Multiple inheritance order changed
class WorkingDog(Animal, Pet):
    def __init__(self, name, owner, job):
        Animal.__init__(self, name)
        Pet.__init__(self, name, owner)
        self.job = job
    
    def speak(self):
        return "Woof!"
    
    def work(self):
        return f"{self.name} is working as a {self.job}"

# Inheritance completely changed
class FamilyPet(Pet):
    def __init__(self, name, owner, species):
        super().__init__(name, owner)
        self.species = species
    
    def describe(self):
        return f"{self.name} is a {self.species} owned by {self.owner}"
