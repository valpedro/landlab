import numpy as np
from numpy.testing import assert_array_equal

from landlab import RasterModelGrid
import landlab.grid.mappers as maps


class TestLinkEndsToLink():
    def test_max(self):
        rmg = RasterModelGrid(4, 5)
        rmg.add_empty('node', 'values')
        node_values = rmg.at_node['values']
        node_values[:] = np.arange(rmg.number_of_nodes)

        maps.map_link_end_node_max_value_to_link(rmg, 'values')

        assert_array_equal(
            rmg.at_link['values'],
            np.array([ 5,  6,  7,  8,  9,
                      10, 11, 12, 13, 14,
                      15, 16, 17, 18, 19,
                       1,  2,  3,  4,
                       6,  7,  8,  9,
                      11, 12, 13, 14,
                      16, 17, 18, 19]))

    def test_min(self):
        rmg = RasterModelGrid(4, 5)
        rmg.add_empty('node', 'values')
        node_values = rmg.at_node['values']
        node_values[:] = np.arange(rmg.number_of_nodes)

        maps.map_link_end_node_min_value_to_link(rmg, 'values')

        assert_array_equal(
            rmg.at_link['values'],
            np.array([ 0,  1,  2,  3,  4,
                       5,  6,  7,  8,  9,
                      10, 11, 12, 13, 14,
                       0, 1,  2,  3,
                       5, 6,  7,  8,
                      10, 11, 12, 13,
                      15, 16, 17, 18]))


class TestNodeToLinkMappers():
    def test_to_node(self):
        rmg = RasterModelGrid(num_rows=4, num_cols=5, dx=1.)
        rmg.add_empty('node', 'values')

        node_values = rmg.at_node['values']
        node_values[:] = np.arange(rmg.number_of_nodes)

        maps.map_values_from_link_tail_node_to_link(rmg, 'values')

        link_values = rmg.at_link['values']
        assert_array_equal(link_values,
                           np.array([ 0,  1,  2,  3,  4,
                                      5,  6,  7,  8,  9,
                                     10, 11, 12, 13, 14,
                                      0, 1,  2,  3,
                                      5, 6,  7,  8,
                                     10, 11, 12, 13,
                                     15, 16, 17, 18]))

    def test_from_node(self):
        rmg = RasterModelGrid(4, 5, 1.)
        rmg.add_empty('node', 'values')

        node_values = rmg.at_node['values']
        node_values[:] = np.arange(rmg.number_of_nodes)

        maps.map_values_from_link_head_node_to_link(rmg, 'values')

        link_values = rmg.at_link['values']
        assert_array_equal(link_values,
                           np.array([5,  6,  7,  8,  9,
                                     10, 11, 12, 13, 14,
                                     15, 16, 17, 18, 19,
                                      1,  2,  3, 4,
                                      6,  7,  8, 9,
                                     11, 12, 13, 14,
                                     16, 17, 18, 19]))

    def test_mean_node(self):
        rmg = RasterModelGrid(4, 5, 1.)
        rmg.add_empty('node', 'values')

        node_values = rmg.at_node['values']
        node_values[:] = np.arange(rmg.number_of_nodes)

        maps.map_values_from_link_end_nodes_to_link(rmg, 'values')

        link_values = rmg.at_link['values']
        assert_array_equal(link_values,
                           np.array([ 2.5,  3.5,  4.5,  5.5,  6.5,
                                      7.5,  8.5,  9.5, 10.5, 11.5,
                                     12.5, 13.5, 14.5, 15.5, 16.5,
                                      0.5,  1.5,  2.5,  3.5,
                                      5.5,  6.5,  7.5,  8.5,
                                     10.5, 11.5, 12.5, 13.5,
                                     15.5, 16.5, 17.5, 18.5]))

    def test_cell(self):
        rmg = RasterModelGrid(4, 5, 1.)
        rmg.add_empty('node', 'values')

        node_values = rmg.at_node['values']
        node_values[:] = np.arange(rmg.number_of_nodes)

        maps.map_values_from_cell_node_to_cell(rmg, 'values')

        cell_values = rmg.at_cell['values']
        assert_array_equal(np.array([6., 7., 8., 11., 12., 13.]), cell_values)
