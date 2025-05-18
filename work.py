class Person:
    population = 0  

    def __init__(self, name, age):
        self.name = name
        self.age = age
        Person.population += 1

    def greet(self):
        return f"Hello, my name is {self.name}."

    def __str__(self):
        return f"{self.name} ({self.age} years old)"

    @classmethod
    def total_population(cls):
        return f"Total people created: {cls.population}"


class Student(Person):
    def __init__(self, name, age, student_id, grades=None):
        super().__init__(name, age)
        self.student_id = student_id
        self._grades = grades if grades is not None else []

    def add_grade(self, grade):
        if 0 <= grade <= 100:
            self._grades.append(grade)
        else:
            raise ValueError("Grade must be between 0 and 100")

    @property
    def average(self):
        if self._grades:
            return sum(self._grades) / len(self._grades)
        return 0

    def __str__(self):
        return f"Student {self.name}, ID: {self.student_id}, Avg: {self.average:.2f}"



students = [
    Student("Alice", 20, "S101"),
    Student("Bob", 22, "S102"),
    Student("Charlie", 21, "S103")
]


try:
    students[0].add_grade(85)
    students[0].add_grade(90)
    students[1].add_grade(70)
    students[1].add_grade(95)
    students[2].add_grade(105)  
except ValueError as e:
    print("Error:", e)


for student in students:
    print(student)


print(Person.total_population())
