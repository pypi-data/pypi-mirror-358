def check_arr(att):
    if type(att) is not list:
        raise TypeError("Input must be a list.")
    if len(att) != 4:
        raise ValueError("List must contain exactly 4 elements.")

    x0, x1, x2, x3 = att
    if (
            type(x0) is not int or x0 < 0 or
            type(x1) is not int or x1 < 0 or
            type(x2) is not int or x2 < 0 or
            type(x3) is not int or x3 < 0
    ):
        raise ValueError("All elements must be non-negative integers.")
