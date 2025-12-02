class Student:
    def __init__(self, name, age, marks):
        self.name = name
        self.age = age
        self.marks = marks  # list of numbers

    def total_marks(self):
        return sum(self.marks)

    def average(self):
        return sum(self.marks) / len(self.marks)

    def info(self):
        print("Name:", self.name)
        print("Age:", self.age)
        print("Total Marks:", self.total_marks())
        print("Average:", self.average())

s1 = Student("Bhuvan", 20, [80, 90, 95])
s2 = Student("John", 22, [70, 60, 85])

s1.info()
s2.info()