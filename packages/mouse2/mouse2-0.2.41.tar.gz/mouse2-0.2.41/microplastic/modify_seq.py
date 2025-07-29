#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 20:22:55 2024

@author: misha
"""

import MDAnalysis as mda
import argparse
import random
import math
from mouse2.lib.neighbor import calculate_neighborlists_from_distances


types = ['1', '2']

MAX_BONDING_ATTEMPTS = 30

def modify_seq(u, prob = 0., nsplit = None, ncross = 0,
               distribution = "random", r_cross_link = 1.2):
    if nsplit is not None and nsplit > 1:
        split_sequence_uniform(u, nsplit)
    if prob > 0.:
        if distribution == "random":
            modify_atoms_random(u, prob)
        elif distribution == "uniform":
            modify_atoms_uniform(u, prob)
        else:
            raise NameError(f"{distribution} atomtype modification\
 is not implemented")
    if ncross > 0:
        cross_link(u, ncross, r_max = r_cross_link)


def modify_atoms_random(u, prob):
    atomtypes = u.atoms.types

    npoly = len(u.atoms)

    target_n_modified = int(round(npoly * prob))

    n_modified = 0

    while n_modified < target_n_modified:
        i = random.randrange(npoly)
        if atomtypes[i] == types[0]:
            atomtypes[i] = types[1]
            n_modified += 1

    u.atoms.types = atomtypes


def modify_atoms_uniform(u, prob):
    atomtypes = []
    npoly = len(u.atoms)
    for iatom in range(npoly):
        if math.floor((iatom + 1) * prob) > math.floor(iatom * prob):
            atomtypes.append(types[1])
        else:
            atomtypes.append(types[0])

    u.atoms.types = atomtypes


def split_sequence_uniform(u, nsplit):
    npoly = len(u.atoms)
    #Remove bonds
    atom_molecule_tags = [int(i*nsplit/npoly)+1 for i in range(npoly)]
    u.trajectory.ts.data['molecule_tag'] = atom_molecule_tags
    remove_connectivity(u)


def find_terminal_atoms(u):
    """Determine the indices of the terminal atoms"""


def remove_connectivity(u):
    atom_molecule_tags = u.trajectory.ts.data['molecule_tag']
    prev_tag = atom_molecule_tags[:-1]
    prev_ix = u.atoms.ix[:-1]
    next_tag = atom_molecule_tags[1:]
    next_ix = u.atoms.ix[1:]
    diff_tags = [next_tag != prev_tag for prev_tag, next_tag
                 in zip(prev_tag, next_tag)]
    indices = [i for i, to_cut in enumerate(diff_tags) if to_cut]
    prev_atom_ix = [prev_ix[ix] for ix in indices]
    next_atom_ix = [next_ix[ix] for ix in indices]
    #Remove angles
    bonds_to_delete = list(zip(prev_atom_ix, next_atom_ix))
    u.delete_bonds(bonds_to_delete)
    for bond_atoms in bonds_to_delete:
        for angle in u.angles:
            atom_in_angle_count = 0
            for i in range(3):
                atom_ix = angle.atoms[i].ix
                if atom_ix in bond_atoms:
                    atom_in_angle_count += 1
            if atom_in_angle_count >= 2:
                u.delete_angles([angle])


def cross_link(u, n_links, r_max = 1.2):
    n_created_links = 0
    indices = u.atoms.ix
    coords_x = u.atoms.positions[:, 0]
    coords_y = u.atoms.positions[:, 1]
    coords_z = u.atoms.positions[:, 2]
    neighborlists = calculate_neighborlists_from_distances(indices,
                                            [coords_x, coords_y, coords_z],
                                            box = u.dimensions,
                                            r_max = r_max)
    existing_bonds = list(u.bonds.to_indices())
    existing_bonds_types = [bond.type for bond in u.bonds]
    u.remove_bonds(existing_bonds)
    while True:
#Randomly choose atom
        atom1_ix = random.choice(indices)
        atom1_bonded_atoms_ix = [atom.ix for atom 
                                 in u.atoms[atom1_ix].bonded_atoms]
#Determine its neighbors within the cross-linking cutoff
        atom1_neighbors_ix = neighborlists[atom1_ix]
        attempts = 0
        while attempts < MAX_BONDING_ATTEMPTS:
#Randomly choose a neighbor
            atom2_ix = random.choice(atom1_neighbors_ix)
            attempts += 1
            if atom2_ix not in atom1_bonded_atoms_ix and atom2_ix != atom1_ix:
                existing_bonds.append([atom1_ix, atom2_ix])
                existing_bonds_types.append('2')
                n_created_links += 1
                break
        if n_created_links >= n_links:
            break
    u.add_bonds(existing_bonds, types = existing_bonds_types)


def choose_initial_sequence_file(initial_data):
    id_type = type(initial_data)
    if id_type == str:
        initial_sequence_file = initial_data
    elif id_type == list:
        initial_sequence_file = random.choice(initial_data)
    else:
        raise NameError("Initial data is of type {id_type} in the config")
    return initial_sequence_file


def prepare_sample(simulation):
    """Move this to the label_prop module"""
    """Fetch the required inital sequence and modify it"""

    config = simulation['config']
    run_parameters = config['run_parameters']
    model_parameters = config['model_parameters']
    trial_parameters = simulation['trial_parameters']
    
    initial_sequence_file = choose_initial_sequence_file(
                                run_parameters['initial_data'])
    simulation["initial_data"] = initial_sequence_file

    for model_parameter in model_parameters:
        initial_sequence_file = initial_sequence_file.replace(
                             model_parameter, str(
                        trial_parameters[model_parameter]))

    u = mda.Universe(initial_sequence_file)

    prob = trial_parameters.get('fmod', 0.)
    nsplit = trial_parameters.get('nsplit', 1)
    ncross = trial_parameters.get('ncross', 0)
    r_cross_link = run_parameters.get('r_cross_link', 1.2)
    try:
        distribution = model_parameters['fmod']['details']['distribution']
    except KeyError:
        distribution = "random"
    modify_seq(u, prob = prob, nsplit = nsplit, 
               ncross = ncross, distribution = distribution,
               r_cross_link = r_cross_link)

    return u


if __name__ == "__main__":

    parser = argparse.ArgumentParser("Modify some atoms' types from 1 to 2")

    parser.add_argument("input", type = str, help = "input filename")

    parser.add_argument("output", type = str, help = "output filename")

    parser.add_argument("--prob", type = float, help = "probability of atom type change")

    parser.add_argument("--split-equal", metavar = "M", nargs = 1, type = int, 
                        default = None, help = "split into M equal chains")

    args = parser.parse_args()

    prob = args.prob

    nsplit = args.split_equal[0]

    # Read configuration

    u = mda.Universe(args.input)

    modify_seq(u, prob = prob, nsplit = nsplit)

    u.atoms.write(args.output)