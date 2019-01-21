""" Simple Math Functions """


def clamp(value, min, max):
    if value < min:
        return min
    elif value > max:
        return max
    return value


def max(a, b):
    return (a if a > b else b)


def min(a, b):
    return (a if a < b else b)
