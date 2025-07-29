# etsi/fliplist/core.py

def reverse_list(data):
    """Reverse a list using slicing."""
    if not isinstance(data, list):
        raise TypeError("Input must be a list")
    return data[::-1]

def reverse_inplace(data):
    """Reverse a list in-place (modifies original list)."""
    if not isinstance(data, list):
        raise TypeError("Input must be a list")
    data.reverse()
    return data

def reverse_custom(data):
    """Reverse a list using manual swap logic."""
    if not isinstance(data, list):
        raise TypeError("Input must be a list")
    reversed_list = data[:]
    left, right = 0, len(reversed_list) - 1
    while left < right:
        reversed_list[left], reversed_list[right] = reversed_list[right], reversed_list[left]
        left += 1
        right -= 1
    return reversed_list
