from llama_index.core.tools import FunctionTool


# function tools
def multiply(a: float, b: float) -> float:
    """Multiply two numbers and returns the product"""
    return a * b


multiply_tool = FunctionTool.from_defaults(fn=multiply)


def add(a: float, b: float) -> float:
    """Add two numbers and returns the sum"""
    return a + b


add_tool = FunctionTool.from_defaults(fn=add)
