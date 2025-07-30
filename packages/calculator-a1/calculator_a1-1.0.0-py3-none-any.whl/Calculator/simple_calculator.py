def add(a,b):
    """This is Function to Addition"""
    return a+b


def subs(a,b):
    """This is fuction to Substraction"""
    return a-b


def multiply(a,b):
    """This is function to Multiply"""
    return a*b


def divide(a,b):
    """This is function to Divition"""
    if b == 0:
        raise ValueError("Can't divide by zero")
    return a/b


def power(a,b):
    """This is function to Power"""
    return a**b
