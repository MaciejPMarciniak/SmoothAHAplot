import os
import matplotlib.pyplot as plt
import numpy as np


class ExNodeParser:

    def __init__(self, exnode_filepath, output_path):

        self.exnode_filepath = exnode_filepath
        if not os.path.isfile(self.exnode_filepath):
            raise FileNotFoundError('Mesh path {} is not a valid filepath.'.format(exnode_filepath))

        self.output_path = output_path
        if not os.path.isdir(self.output_path):
            raise IOError('Output path {} does not exist'.format(output_path))

        self.nodes = self.parse_exnode()
        self.wall_thicknesses = None
        self.length = None
        self.base = None
        self.endo_apex = None

    def _calc_base(self):
        endo_points = self.nodes[::2]
        self.base = np.mean(endo_points[-8:, :], axis=0)
        return self.base

    def _calc_apex(self):
        endo_points = self.nodes[::2]
        self.endo_apex = endo_points[0, :]
        return self.endo_apex

    def parse_exnode(self):
        """Extract cartesian coordinates of nodes from a Mesh.EXNODE file and return np.array.

        :return:
            nodes (np.array): Cartesian coordinates read from Mesh file, in [x,y,z] format
        """

        with open(self.exnode_filepath, 'r') as f:
            exnodes = f.readlines()

        nodes = np.zeros((0, 3))

        for idx, line in enumerate(exnodes):

            if line.strip().startswith('Node'):

                x = float(exnodes[idx + 1].split()[0])
                y = float(exnodes[idx + 2].split()[0])
                z = float(exnodes[idx + 3].split()[0])
                nodes = np.concatenate((nodes, [[x, y, z]]))

        return nodes

    def calc_wall_thickness(self):
        """Calculates the wall thicknesses of a mesh. The thickness is calculated using the Euclidean distance between
        pairs of epi/endocardium points.

        :return:
            wall_thickness (np.array): Calculated wall thickness values of the Mesh.
        """

        endo_points = self.nodes[::2]
        epi_points = self.nodes[1::2]

        self.wall_thicknesses = np.linalg.norm(endo_points - epi_points, axis=1)

        return self.wall_thicknesses

    def calculate_lv_length(self):
        """Calculates the length of the lv. The length is calculated using the Euclidean distance between
        pairs of endocardial apex and the point in the middle of the base.

        :return:
            length (np.array): Calculated length values of the Mesh.
        """
        if self.base is None:
            self._calc_base()
        if self.endo_apex is None:
            self._calc_apex()

        self.length = np.linalg.norm(self.base - self.endo_apex)

        return self.length

    def show_wall_thickness_plot(self, show_delay=False):
        """Plot wall thicknesses in 3D with optional delay.

        Args:
            show_delay (Bool, optional): Choose whether to show a 3D plot for the
                thicknesses with a delay between each value, to show the order of
                data in the file.
        """

        if self.wall_thicknesses is None:
            self.calc_wall_thickness()

        if self.length is None:
            self.calculate_lv_length()

        endo_points = self.nodes[::2]
        epi_points = self.nodes[1::2]

        fig = plt.figure(figsize=(15, 6))

        # 2D septal and lateral walls
        ax = fig.add_subplot(1, 2, 1)
        ax.set_xlim(-60, 60)
        ax.set_ylim(-60, 60)
        myo_border = {'endo_x': [], 'endo_z': [], 'epi_x': [], 'epi_z': []}
        for node in range(endo_points.shape[0]):
            if node % 4 == 3 or node == 0:
                if node <= 7:
                    _color = 'k'  # Apex = black
                elif node <= 23:
                    _color = 'r'  # Apical = red
                elif node <= 39:
                    _color = 'y'  # Mid = yellow
                elif node <= 47:
                    _color = 'g'  # Mid&base = green
                else:
                    _color = 'b'  # Basal = blue

                endo_x = endo_points[node, 0]
                epi_x = epi_points[node, 0]
                endo_z = endo_points[node, 2]
                epi_z = epi_points[node, 2]
                myo_border['endo_x'].append(endo_x)
                myo_border['endo_z'].append(endo_z)
                myo_border['epi_x'].append(epi_x)
                myo_border['epi_z'].append(epi_z)
                ax.plot((-endo_x, -epi_x), [-endo_z, -epi_z], c=_color)
                ax.plot(-endo_x, -endo_z, 'o', c=_color, markersize=2)

        for key in myo_border.keys():
            even = myo_border[key][::2]
            even.reverse()
            even.extend(myo_border[key][1::2])
            myo_border[key] = -np.array(even)

        ax.plot([-self.base[0], -self.endo_apex[0]], [-self.base[2], -self.endo_apex[2]], 'o--', c='magenta')
        ax.plot(myo_border['endo_x'], myo_border['endo_z'], 'k')
        ax.plot(myo_border['epi_x'], myo_border['epi_z'], 'k')
        ax.set_title('Septal and lateral thicknesses')

        # 3D view
        ax = fig.add_subplot(1, 2, 2, projection='3d')
        ax.plot3D(*[[base, apex] for base, apex in zip(self.base, self.endo_apex)], 'o--', c='magenta')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        ax.set_title('Wall thickness plot')
        ax.set_xlim(-60, 60)
        ax.set_ylim(-60, 60)
        ax.set_zlim(-60, 60)
        for node in range(endo_points.shape[0]):
            if node in [59, 51, 43, 35, 27, 19, 11, 3]:
                _color = 'g'  # Septum = green
            elif node == 0:
                _color = 'k'  # Apex = black
            else:
                _color = 'r'  # rest = red

            ax.plot3D(*[[endo, epi] for endo, epi in zip(endo_points[node, :], epi_points[node, :])], _color)
            ax.plot3D(*[[endo] for endo in endo_points[node, :]], 'o', c=_color, markersize=2)

            if show_delay:
                print(self.wall_thicknesses[node], np.linalg.norm(endo_points[node, :] - epi_points[node, :]))
                plt.pause(0.1)

        plt.show()

    def wt_difference(self, other_exnode_filepath):
        if not os.path.isfile(other_exnode_filepath):
            raise FileNotFoundError('File {} does not exist'.format(other_exnode_filepath))

        if self.wall_thicknesses is None:
            self.calc_wall_thickness()

        wt2 = ExNodeParser(other_exnode_filepath, self.output_path)
        wt2.calc_wall_thickness()
        wt_diff = self.wall_thicknesses - wt2.wall_thicknesses

        return wt_diff


if __name__ == '__main__':
    group_a = 2
    scale = 72
    test_exnode = r'G:\GenerationR\AtlasOutputLVLrv\ModesResTime\MeanEigen{}Scale{}.exnode'.format(group_a, scale)
    wt = ExNodeParser(test_exnode, r'G:')
    wt.show_wall_thickness_plot(show_delay=True)

