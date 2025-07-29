import numpy as np
from scipy.fft import fft, ifft


def dct(x):
    n = len(x)
    ind = np.hstack((np.arange(0, n, 2), np.flip(np.arange(1, n, 2))))
    r_tilde = fft(x[ind])
    alpha = 2 * np.ones(n)
    alpha[0] = 1
    w = np.exp(-1j * np.pi / (2 * n))
    return np.real(alpha * w ** np.arange(n) * r_tilde)


def idct(xtilde):
    n = len(xtilde)
    w = np.exp(1j * np.pi / (2 * n))
    x_scrambled = np.real(ifft(w ** np.arange(n) * xtilde))
    ind = np.hstack((np.arange(0, n, 2), np.flip(np.arange(1, n, 2))))
    jind = np.argsort(ind)
    return x_scrambled[jind]


# x = np.arange(1, 11)
# y = dct(x)
# print(y)
# print(idct(y))
