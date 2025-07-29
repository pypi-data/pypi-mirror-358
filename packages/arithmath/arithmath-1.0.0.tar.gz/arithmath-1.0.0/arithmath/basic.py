from typing import Union

def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Args:
        a (int or float)
        b (int or float)

    Returns:
        Sum of a & b (int or float)
    """
    return a + b


def subtraction(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Args:
        a (int or float)
        b (int or float)

    Returns:
        Subtraction of b from a (int or float)
    """
    return a - b


def multiply(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Args:
        a (int or float)
        b (int or float)

    Returns:
        Multiplies a & b (int or float)
    """
    return a * b


def division(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Args:
        a (int or float)
        b (int or float)

    Returns:
        Divides a by b (int or float)
    """
    if b == 0:
        raise ValueError("Can't divide by 0")
    
    return a / b