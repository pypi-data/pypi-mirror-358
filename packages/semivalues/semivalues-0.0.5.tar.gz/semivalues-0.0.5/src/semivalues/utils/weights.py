def compute_weights(factorials, n):
    return factorials[:-1] * factorials[n - 1::-1] / factorials[n]
