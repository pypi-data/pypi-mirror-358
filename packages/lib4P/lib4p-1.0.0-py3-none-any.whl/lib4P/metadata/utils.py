
def is_equivalent_to_a_list(value):
    if isinstance(value, str):
        return False
    if not hasattr(value, "__iter__"):
        return False
    if not hasattr(value, "__getitem__"):
        return False
    if not hasattr(value, "__len__"):
        return False
    return True

