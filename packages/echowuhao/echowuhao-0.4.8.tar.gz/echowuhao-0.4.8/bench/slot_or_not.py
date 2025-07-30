class PersonWithoutSlots:
    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email

class PersonWithSlots:
    __slots__ = ['name', 'age', 'email']
    
    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email

# Let's compare memory usage and performance

import sys
import timeit

# Create instances
person1 = PersonWithoutSlots("Alice", 30, "alice@example.com")
person2 = PersonWithSlots("Bob", 25, "bob@example.com")

# Compare memory usage
print(f"Memory usage with slots: {sys.getsizeof(person2)} bytes")
print(f"Memory usage without slots: {sys.getsizeof(person1)} bytes")

# Compare attribute access speed
def access_attributes_without_slots():
    return person1.name, person1.age, person1.email

def access_attributes_with_slots():
    return person2.name, person2.age, person2.email

time_without_slots = timeit.timeit(access_attributes_without_slots, number=1000000)
time_with_slots = timeit.timeit(access_attributes_with_slots, number=1000000)

print(f"Time to access attributes with slots: {time_with_slots:.6f} seconds")
print(f"Time to access attributes without slots: {time_without_slots:.6f} seconds")

# Try to add a new attribute
try:
    person1.new_attr = "This works"
    print("Added new attribute to PersonWithoutSlots")
except AttributeError:
    print("Cannot add new attribute to PersonWithoutSlots")

try:
    person2.new_attr = "This will raise an error"
except AttributeError:
    print("Cannot add new attribute to PersonWithSlots")