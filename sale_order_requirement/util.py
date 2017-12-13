
def rounding(f, r):
    import math
    if not r:
        return f
    return math.ceil(f / r) * r

# def fix_fields(vals):
#     if vals:
#         for key in vals:
#             if isinstance(vals[key], tuple):
#                 vals[key] = vals[key][0]
