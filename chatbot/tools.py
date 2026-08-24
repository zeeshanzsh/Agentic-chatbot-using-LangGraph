from langchain_core.tools import tool


@tool
def add(a: float, b: float) -> float:
    """Add two numbers and return the sum."""
    return a + b


@tool
def subtract(a: float, b: float) -> float:
    """Subtract b from a and return the difference."""
    return a - b


@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers and return the product."""
    return a * b


@tool
def divide(a: float, b: float) -> float:
    """Divide a by b and return the quotient. Raises an error if b is 0."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


@tool
def power(a: float, b: float) -> float:
    """Raise a to the power of b and return the result."""
    return a**b


# collected here so graph.py can bind them to the LLM and build a ToolNode in one line
math_tools = [add, subtract, multiply, divide, power]
