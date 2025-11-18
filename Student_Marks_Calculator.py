# Take inputs
name = input("Enter student name: ")

# Store marks in a list
marks = []
for i in range(5):
    m = float(input(f"Enter mark {i+1}:"))
    marks.append(m)

# Create functions
def calc_total(marks):
    return sum(marks)
def calc_percentage(total):
    return total / 5

# Find grade
def calc_grade(percentage):
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "c"
    else:
        return "Fail"
    
# Combine everything
total = calc_total(marks)
percentage = calc_percentage(total)
grade = calc_grade(percentage)

# Print clean output
print("--- Student Report ---")
print("Name:", name)
print("Marks:", marks)
print("Total:", total)
print("Percentage:", percentage)
print("Grade:", grade)
