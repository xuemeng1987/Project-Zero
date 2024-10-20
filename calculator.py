import math

def perform_operation(operation, num1=None, num2=None):
    try:
        if operation == 'add':
            return num1 + num2
        elif operation == 'subtract':
            return num1 - num2
        elif operation == 'multiply':
            return num1 * num2
        elif operation == 'divide':
            if num2 == 0:
                return "Cannot divide by zero!"
            return num1 / num2
        elif operation == 'power':
            return math.pow(num1, num2)
        elif operation == 'sqrt':
            return math.sqrt(num1)
        elif operation == 'log':
            return math.log(num1) if num2 is None else math.log(num1, num2)
        elif operation == 'sin':
            return math.sin(math.radians(num1))
        elif operation == 'cos':
            return math.cos(math.radians(num1))
        elif operation == 'tan':
            return math.tan(math.radians(num1))
        else:
            return "Invalid operation!"
    except ValueError:
        return "Invalid input for the operation!"
