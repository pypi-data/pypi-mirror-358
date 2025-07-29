#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 15:23:31 2025

@author: misha
"""

import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import argparse
import scipy
from scipy.spatial import Voronoi, voronoi_plot_2d
from sklearn.preprocessing import MinMaxScaler
from matplotlib.colors import Normalize
from shapely.geometry import Polygon
import seaborn as sns

from label_prop import parameter_ordered_names, read_config
from label_prop import create_points, create_points2, fit_model, uncertainties, converge_points

import pdb

#FILTER = [0.2,0.2]
FILTER = [0., 0.]
#BP = { 'kernel' : 'rbf', 'gamma' : 20.,
#                  'max_iter' : 30, 'alpha' : 0.01}
BP = { 'kernel' : 'knn', 'n_neighbors' : 4,
                  'max_iter' : 30, 'alpha' : 0.01}
DEFAULT_PLOT_PARAMETERS = {
    'backend_params' : BP,
    'marker' : 'o',
    'label' : 'State probabilities',
    'filter' : [0., 0],
    'contour_linecolor' : 'black'}


def nvalues(parameter):
    return int((parameter["max"] - parameter["min"]) / parameter["step"]) + 1


def histogram_nbins(parameters):
    p_names = parameter_ordered_names(parameters)
    histogram_nbins = []
    for p_name in p_names:
        parameter = parameters[p_name]
        histogram_nbins.append(nvalues(parameter))
    return histogram_nbins


def histogram_edges(parameters):
    p_names = parameter_ordered_names(parameters)
    histogram_edges = []
    for p_name in p_names:
        parameter = parameters[p_name]
        histogram_min = parameter["min"] - parameter["step"] / 2
        histogram_max = parameter["max"] + parameter["step"] / 2
        histogram_edges.append([histogram_min, histogram_max])
    return np.array(histogram_edges)


def merge_adjacent_polygons(polygons, tolerance=0.01):
    """Merge polygons that share edges within tolerance"""
    merged = []
    visited = set()
    
    for i, poly1 in enumerate(polygons):
        if i in visited:
            continue
        current_union = poly1
        neighbors_found = True
        
        while neighbors_found:
            neighbors_found = False
            for j, poly2 in enumerate(polygons):
                if j not in visited and j != i and current_union.distance(poly2) < tolerance:
                    current_union = current_union.union(poly2)
                    visited.add(j)
                    neighbors_found = True
        
        merged.append(current_union)
        visited.add(i)
    
    return merged


def labels_to_distributions(labels):
    unique_labels = sorted(set(labels))
    n_unique_labels = len(unique_labels)
    label_distributions = []
    for label in labels:
        label_distribution = [0.] * n_unique_labels
        label_distribution[unique_labels.index(label)] = 1.
        label_distributions.append(label_distribution)
    return label_distributions


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description = 'Build a diagram of states plot')

    parser.add_argument('--config', metavar = 'JSON', type = str, nargs = '+',
        help = 'configuration file')

    args = parser.parse_args()
    
    
    axes = []
    lines = []
    labels = []
    
    for i_plot, config_filename in enumerate(args.config):

        config = read_config(config_filename)

        mp, rp = config["model_parameters"], config["run_parameters"]
        pp = config.get("plot_parameters", DEFAULT_PLOT_PARAMETERS)

        p_names = parameter_ordered_names(mp)

        samples_df = pd.read_excel(rp["samples_file"])

        probed_points, probed_labels = create_points2(mp, samples_df,
                                                 return_unprobed = False)

        points_labels = list(zip(probed_points, probed_labels))
        points1 = [pl[0] for pl in points_labels if int(pl[1]) == 1]
        points2 = [pl[0] for pl in points_labels if int(pl[1]) == 2]

        points1x = [p[0] for p in points1]
        points1y = [p[1] for p in points1]

        points2x = [p[0] for p in points2]
        points2y = [p[1] for p in points2]

        if i_plot == 0:
            #fig, current_ax = plt.subplots(figsize=(8, 8))
            #current_ax.set_ylabel('Degree of modification')
            plt.ylabel('Degree of modification')

        
        if i_plot > 0:
            pass
            #current_ax = axes[0]
            #current_ax.spines['top'].set_position(('outward', (i_plot-1)*40))


        sns.stripplot(x=points1y, y=points1x, s = 4, marker = 'o', jitter=0.2,
                 facecolor = pp['colors']['1'], edgecolor = pp['colors']['1'], 
                 label = pp['label'] + ' stable')
        sns.stripplot(x=points2y, y=points2x, s = 6, jitter = 0.2, linewidth = 0.2,
                    marker = 'X', facecolor = pp['colors']['2'], edgecolor = pp['colors']['2'],
                    alpha = 1,
                    label = pp['label'] + ' unstable')
        
        #current_ax.tick_params(axis='x', labelcolor=pp['color'])
        #current_ax.set_xlabel(r'$N_{cut}$, ' + f"{pp['label']}", color=pp['color'])
        #current_ax.set_xlabel(r"$N_{cut}$")
        plt.xlabel(r"$N_{cut}$")
        
        #current_lines, current_labels = current_ax.get_legend_handles_labels()
        
        """
        axes.append(current_ax)
        lines.append(current_lines)
        labels.append(current_labels)
        
        if i_plot == 0:
            all_lines = current_lines
            all_labels = current_labels
        else:
            all_lines += current_lines
            all_labels += current_labels
            """


    #plt.xlabel('$N_{cut}$')
    #plt.xlim((0.,1.))
    #plt.ylim((0,1))
    #plt.rcParams["figure.figsize"] = (8,6)
    
    # Combine legends from all axes
    #plt.legend()
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend([handles[0], handles[16], handles[32], handles[48]], ["DPD stable", "DPD unstable", "LD stable", "LD unstable"])
    #axes[0].legend(all_lines, all_labels, loc='upper right')
    
    plt.rcParams.update({
    'font.size': 12,           # Default font size
    'axes.titlesize': 24,      # Axes title size
    'axes.labelsize': 16,      # X and Y labels size
    'xtick.labelsize': 16,     # X tick label size
    'ytick.labelsize': 16,     # Y tick label size
    'legend.fontsize': 16,     # Legend font size
    'figure.titlesize': 16     # Figure title size
})

    plt.show()