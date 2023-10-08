import numpy as np
import matplotlib.pyplot as plt

from parameters import AHA17Parameters


def draw_interpolation_positions(levels: tuple(int, ...)) -> None:
    """
    Show interpolation levels on the plot
    """
    x = levels
    _, ax = plt.subplots(figsize=(12, 8), nrows=1, ncols=1, subplot_kw=dict(projection="polar"))
    ip = AHA17Parameters()

    r = np.linspace(0.2, 1, 4)
    theta = np.linspace(0, 2 * np.pi, ip.resolution[0])
    linewidth = 2

    # Create the radial bounds
    for i in range(r.shape[0]):
        ax.plot(theta, np.repeat(r[i], theta.shape), "-k", lw=linewidth)

    # Create the bounds for the segments 1-12
    for i in range(6):
        theta_i = np.deg2rad(i * 60)
        ax.plot([theta_i, theta_i], [r[1], 1], "-k", lw=linewidth)

    # Create the bounds for the segments 13-16
    for i in range(4):
        theta_i = np.deg2rad(i * 90 - 45)
        ax.plot([theta_i, theta_i], [r[0], r[1]], "-k", lw=linewidth)

    # Clear the bullseye plot
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.set_ylim([0, 1])

    for i in range(8):
        theta_i = np.deg2rad(i * 45)
        ax.plot([theta_i, theta_i], [0, 1], "--", c="gray")

    for i in range(360):
        theta_i = np.deg2rad(i)
        theta_i_roll = theta_i + np.deg2rad(1)
        mesh_nodes = [0, 0.1, 0.25, 0.4, 0.5, 0.63, 0.75, 0.87, 1]
        for m_node in mesh_nodes:
            color_ = (
                "b"
                if m_node in [0.87, 1]
                else "g"
                if m_node == 0.75
                else "y"
                if m_node in [0.5, 0.63]
                else "r"
                if m_node in [0.25, 0.4]
                else "k"
            )

            ax.plot([theta_i, theta_i_roll], [m_node, m_node], ":", c=color_, lw=5)
    plt.show()


if __name__ == "__main__":
    draw_interpolation_positions(1)
