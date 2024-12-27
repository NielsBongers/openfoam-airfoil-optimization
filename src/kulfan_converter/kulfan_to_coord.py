# This code is taken from https://github.com/Ry10/Kulfan_CST.
# No license is specified there.
# This takes six parameters and converts it into an airfoil shape.
# Slightly modified to work with Python 3.

from math import cos, factorial, pi

import numpy as np


class CST_shape:
    def __init__(self, wl=[-1, -1, -1], wu=[1, 1, 1], dz=0, N=200):
        self.wl = wl
        self.wu = wu
        self.dz = dz
        self.N = N
        self.coordinate = np.zeros(N)

    def airfoil_coor(self):
        wl = self.wl
        wu = self.wu
        dz = self.dz
        N = self.N

        # Create x coordinate
        x = np.ones((N, 1))
        zeta = np.zeros((N, 1))

        for i in range(N):
            zeta[i] = 2 * pi / N * i
            x[i] = 0.5 * (cos(zeta[i].item()) + 1)

        # N1 and N2 parameters (N1 = 0.5 and N2 = 1 for airfoil shape)
        N1 = 0.5
        N2 = 1

        center_loc = np.where(x == 0)[0][0]  # Used to separate upper and lower surfaces

        xl = x[:center_loc].flatten()
        xu = x[center_loc:].flatten()

        yl = self.__ClassShape(
            wl, xl, N1, N2, -dz
        )  # Determine lower surface y-coordinates
        yu = self.__ClassShape(
            wu, xu, N1, N2, dz
        )  # Determine upper surface y-coordinates

        y = np.concatenate([yl, yu])  # Combine upper and lower y coordinates

        self.coord = np.column_stack((x.flatten(), y))

        return self.coord

    # Function to calculate class and shape function
    def __ClassShape(self, w, x, N1, N2, dz):
        # Class function; taking input of N1 and N2
        C = x**N1 * (1 - x) ** N2

        # Shape function; using Bernstein Polynomials
        n = len(w) - 1  # Order of Bernstein polynomials
        K = [factorial(n) / (factorial(i) * factorial(n - i)) for i in range(n + 1)]

        S = np.zeros(len(x))
        for i in range(len(x)):
            S[i] = sum(
                w[j] * K[j] * x[i] ** j * (1 - x[i]) ** (n - j) for j in range(n + 1)
            )

        # Calculate y output
        y = C * S + x * dz
        return y


if __name__ == "__main__":
    wu = [0.2, 0.25, 0.01]  # Upper surface
    wl = [-0.1, -0.1, -0.01]  # Lower surface
    dz = 0
    N = 100

    airfoil_CST = CST_shape(wl, wu, dz, N)
    array = airfoil_CST.airfoil_coor()

    import matplotlib.pyplot as plt

    plt.plot(array[:, 0], array[:, 1])
    plt.axis("equal")
    plt.show()
