import swanplot as plt
import numpy as np


def example_histogram():
    c = 6
    d = int(c**2)
    a = np.zeros((1, d))
    a[0, 0] = 1
    a[0, 1] = 2
    a[0, 2] = 3
    a[0, 3] = 4
    a[0, 4] = 5
    b = [np.roll(a, shift=i, axis=1) for i in range(d)]
    return np.roll(np.array(b).reshape(d, c, c), shift=4, axis=0)


def example_plot():
    a = np.zeros((3, 20))
    a[:, :5] = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4]]).T
    a[:, 5:10] = np.array([[0, 0, 0], [1, 0, 1], [2, 0, 2], [3, 0, 3], [4, 0, 4]]).T
    a[:, 10:15] = np.array([[0, 0, 0], [1, 1, 0], [2, 2, 0], [3, 3, 0], [4, 4, 0]]).T
    a[:, 15:] = np.array([[0, 4, 4], [1, 3, 2], [2, 2, 3], [3, 1, 1], [4, 2, 2]]).T
    return a


def main():
    ax = plt.axes()
    ax.hist(example_histogram())
    ax.set_xlabel("x-axis")
    ax.set_ylabel("y-axis")
    ax.set_loop()
    ax.savefig("test.json")


if __name__ == "__main__":
    main()
