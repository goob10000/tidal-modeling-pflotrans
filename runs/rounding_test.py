import numpy as np

def round_to_n(x, n):
    return round(x, -int(np.floor(np.log10(abs(x)))) + n - 1)

round_to_n(123.456, 3)