import numpy as np

def bounded_normal(mean, sd, low, high):
    return np.clip(np.random.normal(mean, sd), low, high)

def categorical(choices, probs):
    return np.random.choice(choices, p=probs)
