from thetakde import kde
import numpy as np
import matplotlib.pyplot as plt


def test_data():
    """Test theta KDE on known dataset and compare bandwidth to expected value."""
    data = np.loadtxt("testingdata.csv", delimiter=',')
    density, mesh, sig = kde(data)
    print("Bandwidth:", sig, '=', 0.23299825030379537 )


def test_exponential_pdf():
    """
    Generate synthetic data from an exponential distribution and estimate its density using the theta KDE.

    This function:
    - Generates 5000 samples from an exponential distribution using inverse transform sampling.
    - Computes the KDE of the data using the `kde` function.
    - Plots the estimated density alongside the true exponential PDF for visual comparison.
    """

    # Generate exponential data
    data = -np.log(np.random.uniform(size=5000))

    # Estimate density
    density, mesh, sig = kde(data)

    # Plot
    plt.plot(mesh, density,'r', label='KDE')
    plt.plot(mesh, np.exp(-mesh), 'b--', label='True PDF')
    plt.legend()
    plt.show()



def test_bootstrap_resampling(n=100, K=1000):
    """
    Perform bootstrap resampling on a synthetic dataset and estimate the KDE of medians and means.

    Parameters:
    - n (int): Size of the original dataset to be resampled.
    - K (int): Number of bootstrap resampling iterations.

    This function:
    - Generates a synthetic dataset of size `n` using a ratio of uniform random variables.
    - Performs `K` bootstrap resampling iterations to compute distributions of medians and means.
    - Estimates the theta KDE for both the median and mean distributions.
    - Plots the theta KDEs for visual comparison.
    """

    # Original data
    x = np.random.rand(n) / np.random.rand(n)

    med = np.zeros(K)
    mean = np.zeros(K)
    for k in range(K):
        # resample data
        s = np.random.choice(x, n, replace=True)
        # compute median and mean of resampled data
        med[k] = np.median(s)
        mean[k] = np.mean(s)

    for stat, label in zip([med, mean], ["Median", "Mean"]):
        density, mesh, sig = kde(stat, resamp=True)
        plt.plot(mesh, density, label=label)

    plt.legend()
    plt.show()


def main():
    test_data()
    test_exponential_pdf()
    test_bootstrap_resampling()


if __name__ == "__main__":
    main()
