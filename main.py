class Person:
    def __init__(self, name):
        self.name = name

    def show_name(self):
        print("My name is", self.name)

p2 = Person("Alice")
p2.show_name()
