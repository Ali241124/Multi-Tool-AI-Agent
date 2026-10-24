
def calculator(operation: str, a: float, b: float) -> float:
    """
    Perform a basic mathematical operation.

    Args:
        operation: The operation to perform.
        a: First number.
        b: Second number.

    Returns:
        The calculated result.
    """

    if operation == "add":
        return a + b

    elif operation == "subtract":
        return a - b

    elif operation == "multiply":
        return a * b

    elif operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero.")

        return a / b

    else:
        raise ValueError(
            f"Unsupported operation: {operation}"
        )
