def rounding(f, r):
    import math
    if not r:
        return f
    return math.ceil(f / r) * r
