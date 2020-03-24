import os
import re
import matplotlib.pyplot as plt
import numpy as np
from ahasmoothplot import SmoothAHAPlot


def parse_exnode(exnode_file):
    """Extract node cartesian coordinates from a Mesh.EXNODE file and return Dict.
    Loads a mesh from an Mesh.EXNODE file, calculates the thicknesses and
    optionally plots this along with an optional gradual plot.

    Args:
        exnode_file (str):  Full file path to Mesh.EXNODE file

    Returns:
        nodes_dict (Dict): Cartesian coordinates read from Mesh file, in (x,y,z) format
    """

    if not os.path.isfile(exnode_file):
        raise FileNotFoundError('Mesh path is not a valid filepath.')

    with open(exnode_file, 'r') as f:
        exnodes = f.readlines()

    nodes_dict = dict()

    for idx, line in enumerate(exnodes):
        # Remove empty spaces at beginning and end of line
        line = line.strip()

        if line.startswith('Node'):
            node_no_regex = re.compile(r'\d+')
            node_no = re.findall(node_no_regex, line)
            node_no = int(node_no[0])

            x = exnodes[idx + 1].split()[0]
            y = exnodes[idx + 2].split()[0]
            z = exnodes[idx + 3].split()[0]
            node_name = 'n' + str(node_no)
            nodes_dict[node_name] = [float(x), float(y), float(z)]

    return list(nodes_dict.values())


def calc_wall_thickness(mesh_dir, show_thickness=False, show_delay=False):
    """Calculates the wall thicknesses of a mesh.

    Loads a mesh from an Mesh.EXNODE file, calculates the thicknesses and
    optionally plots this along with an optional gradual plot.

    The thickness is calculated using the Euclidean distance between pairs of
    epi/endocardium points.

    Args:
        mesh_dir (str): Full path to Mesh.EXNODE file
        show_thickness (Bool, optional): Choose whether to show a 3D plot of the
            thicknesses.
        show_delay (Bool, optional): Choose whether to show a 3D plot for the
            thicknesses with a delay between each value, to show the order of
            data in the file.

    Returns:
        wall_thickness (list): Calculated wall thickness values for the Mesh.
    """

    points = parse_exnode(mesh_dir)
    x, y, z = [], [], []

    for line in points:
        x += [line[0]]
        y += [line[1]]
        z += [line[2]]

    dist_x, dist_y, dist_z = [], [], []
    wall_thickness, show_x, show_y, show_z = [], [], [], []

    for num in range(1, len(points), 2):
        dist_x += [abs(points[num][0] - points[num - 1][0])]
        dist_y += [abs(points[num][1] - points[num - 1][1])]
        dist_z += [abs(points[num][2] - points[num - 1][2])]

        # show_(x,y,z) are pairs of epi/endocardium cartesian coordinates to
        # the thicknesses (To form a vector).
        show_x += [(points[num][0], points[num - 1][0])]
        show_y += [(points[num][1], points[num - 1][1])]
        show_z += [(points[num][2], points[num - 1][2])]

        thick_ind = int((num - 1) / 2)

        wall_thickness += [np.sqrt(
            pow(dist_x[thick_ind], 2) +
            pow(dist_y[thick_ind], 2) +
            pow(dist_z[thick_ind], 2))]

    if show_thickness:
        show_wall_thickness_plot(show_x, show_y, show_z, show_delay)

    return wall_thickness


def show_wall_thickness_plot(show_x, show_y, show_z, show_delay=False):
    """Plot wall thicknesses in 3D with optional delay.

    Args:
        show_x, show_y, show_z (list of tuples): Cartesian coordinate pairs to
            plot the wall thicknesses.
        show_delay (Bool, optional): Choose whether to show a 3D plot for the
            thicknesses with a delay between each value, to show the order of
            data in the file.
    """

    if not len(show_x) == len(show_y) == len(show_z):
        raise ValueError('Lengths of inputted coordinates should be the same.')

    ax = plt.axes(projection='3d')
    count = 0

    for i in range(0, len(show_y)):
        if count in [59, 51, 43, 35, 27, 19, 11, 3]:
            _color = 'g'
        elif count == 0:
            _color = 'k'
        elif count in range(1, 9):
            _color = 'b'
        elif count in range(9, 17):
            _color = 'magenta'
        else:
            _color = 'r'

        ax.plot3D(show_x[i], show_y[i], show_z[i], _color)

        if show_delay:
            plt.pause(0.4)

        count += 1

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.set_title('Wall thickness plot')
    plt.show()


def wt_difference(exnode_1, exnode_2):
    wt1 = np.array(calc_wall_thickness(exnode_1))
    wt2 = np.array(calc_wall_thickness(exnode_2))
    wt_diff = list(wt1 - wt2)

    return wt_diff


if __name__ == '__main__':
    test_exnode = r'G:\Tephra\Processed\AtlasOutputLVLrv\Averages\All\ExFiles\MeanEigen1Scale97.exnode'
    wt = calc_wall_thickness(test_exnode)
    plot_wt = SmoothAHAPlot(wt, r'G:\Tephra\Processed\AtlasOutputLVLrv\Averages\All\ExFiles', n_segments=17)
    plot_wt.plot_wall_thickness('WT_test2.png')