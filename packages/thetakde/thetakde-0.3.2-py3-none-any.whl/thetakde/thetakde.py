import numpy as np
from scipy import optimize
from DCT import dct, idct


def mise(h, a2, a2k, N):
    """
    Compute the Mean Integrated Squared Error (MISE) for a given bandwidth.

    Parameters:
    - h (float): Bandwidth parameter.
    - a2 (ndarray): DCT-related coefficients.
    - a2k (ndarray): Even-indexed DCT coefficients.
    - N (int): Number of data points.

    Returns:
    - float: The estimated MISE value for the given bandwidth.

    This function is used internally to optimize the bandwidth by minimizing the MISE.
    """

    B = (np.arange(1, len(a2) + 1) ** 2) * np.pi ** 2 * h ** 2
    val = 0.5 * np.sum(a2 * (np.exp(-B / 2) - 1) ** 2)
    val += 1 / (2 * N) * np.sum(np.exp(-B) * (2 + a2k - a2))
    return val


def kde(data, m=2**16, MIN=None, MAX=None, sig=None, resamp=False):
    """
    Perform theta kernel density estimation.

    Parameters:
    - data (array-like): Input 1D data array for which the density is to be estimated.
    - m (int, optional): Number of grid points (default is 2^16).
    - MIN (float, optional): Minimum value of the data range. If None, uses data.min().
    - MAX (float, optional): Maximum value of the data range. If None, uses data.max().
    - sig (float, optional): Bandwidth. If None, it is optimized using MISE.
    - resamp (bool, optional): If True, applies a two-stage KDE for resampled (non-iid) data.

    Returns:
    - density (ndarray): Estimated density values over the mesh grid.
    - mesh (ndarray): Grid points corresponding to the density estimates.
    - sig (float): Bandwidth used for the KDE.

    This function implements a fast and accurate KDE using DCT-based computation and
    automatic bandwidth selection via MISE minimization. It supports both iid and
    resampled data scenarios.


    References:
    [1] Z.I. Botev, D.P. Kroese, and T. Taimre (2025). *Data Science and Machine Learning: Mathematical and Statistical Methods*, Second Edition. Chapman & Hall/CRC, Boca Raton.
    [2] Z.I. Botev, J.F. Grotowski, and D.P. Kroese (2010). Kernel density estimation via diffusion. *Annals of Statistics*, 38(5), 2916–2957.

    """

    data = np.asarray(data)
    m = int(2**np.ceil(np.log2(m)))
    n = data.size
    MIN = data.min() if MIN is None else MIN
    MAX = data.max() if MAX is None else MAX

    # Compute the full range and the grid spacing.
    R = MAX - MIN
    dx = R / m
    mesh = np.linspace(MIN, MAX, m) + dx / 2

    # Create the histogram.
    bins = np.linspace(MIN - 1e-7, MAX + 1e-7, m + 1)
    hist, _ = np.histogram(data, bins=bins)
    binned_prop = hist / n

    # Perform the DCT.
    a = dct(binned_prop)
    a2k = a[2:m:2]
    a2 = n / (n - 1) * a[1:m // 2] ** 2 - (2 + a2k) / (n - 1)

    # Optimize the bandwidth if not provided.
    if sig is None:
        def mise1(h):
            return mise(np.exp(h) * R, a2, a2k, n)
        res = optimize.minimize_scalar(
            mise1, bounds=(-40, 10), method='bounded')
        sig = np.exp(res.x / 2)

    # Apply the smoothing in the frequency domain.
    indices = np.arange(m, dtype=np.float64)
    a_t = a * np.exp(-(indices ** 2) * np.pi ** 2 * (sig ** 2 * R) ** 2 / 2)
    density = idct(a_t) / dx

    # Optionally, when data is not iid, e.g., due to resampling
    if resamp:
        udata = np.unique(data)
        density, _, usig = kde(udata, m, np.min(udata), np.max(udata))
        density, _, sig = kde(data, m, MIN, MAX, usig)

    return density, mesh, sig
