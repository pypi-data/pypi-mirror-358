#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 19:45:18 2025

@author: misha
"""
import os
import MDAnalysis as mda
from mouse2.lib.aggregation import determine_aggregates

def find_molecule(ix, molecules):
    molecules.sort()
    for i, molecule in enumerate(molecules):
        try:
            ix.index(molecule)
            return i + 1
        except IndexError:
            continue
    raise NameError(f"Molecule not found for atom with index {ix}")

for isample in range(1,50):
    for istep in range(1,13):
        filename = f"out_{isample}.{istep}.data"
        if os.path.exists(filename):
            u = mda.Universe(filename)
            data = determine_aggregates(u, r_neigh = 1.2)
            aggregates = list(data['data'].values())[0]
            molecule_data = determine_aggregates(u, r_neigh = 0.,
                                                 bonded_as_neighbors = True)
            molecules = list(molecule_data['data'].values())[0]
            aggregate_molecules = [set([find_molecule(ix, molecules)
                                        for ix in aggregate])
                                   for aggregate in aggregates]
            aggregate_lengths = [len(a) for a in aggregate_molecules]
            aggregate_lengths.sort()
            if len(aggregate_lengths) > 1 and aggregate_lengths[-2] > 1:
                print(isample)
                print(aggregate_molecules)