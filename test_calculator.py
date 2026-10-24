
from tools.calculator import calculator

print("Addition:", calculator("add", 10, 5))
print("Subtraction:", calculator("subtract", 10, 5))
print("Multiplication:", calculator("multiply", 10, 5))
print("Division:", calculator("divide", 10, 5))

try:
    calculator("divide", 10, 0)
except ValueError as error:
    print("Expected error:", error)
