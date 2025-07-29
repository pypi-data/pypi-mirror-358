#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import numpy as np
from sklearn.semi_supervised import LabelSpreading
import random
import os
import time
import socket
import argparse
import json
import itertools
import MDAnalysis as mda
try:
    from mouse2.mouse2.lib.aggregation import determine_aggregates
except ModuleNotFoundError:
    from mouse2.lib.aggregation import determine_aggregates
import pdb

MAX_UPDATE_ATTEMPTS = 10
SHORT_SLEEP = 1.0
LONG_SLEEP = 3.0
RECORD_PARAMETERS = ["sample", "choice", "i_point", "step", "state",
                         "uncertainty", "dump_frame", "initial_data", "study"]
BACKEND_PARAMS = { 'kernel' : 'rbf', 'gamma' : 20, 'max_iter' : 100000 }

# Function definitions

def read_config(config_filename):

    with open(config_filename, "r") as f:
         config = json.load(f)
         
    try:
        points_file = config["points_file"]
        config["run_parameters"]["p_mode"] = "file"
        model_parameters, _ = read_points(points_file)
        config["model_parameters"] = model_parameters
    except KeyError:
        try:
            model_parameters = config["model_parameters"]
            config["run_parameters"]["p_mode"] = "grid"
            points_file = None
        except KeyError:
            raise NameError("Either points_file or model_parameters sections\
 should be present in the configuration file")

    return config


def parameter_ordered_names(parameters):
    if type(parameters) == dict:
        p_names = list(parameters.keys())
    elif type(parameters) == list:
        p_names = parameters
    else:
        raise NameError(f"Unsupported parameters type {type(parameters)}")
    p_names.sort()
    return p_names


def read_points(points_file):
    if points_file[-4:] == ".xls" or points_file[-5:] == ".xlsx":
        points_df = pd.read_excel(points_file)
    elif points_file[-4:] == ".csv":
        points_df = pd.read_csv(points_file)

    p_names = parameter_ordered_names(list(points_df.columns))
    parameters = {}
    points_list = []
    for p_name in p_names:
        parameter_values = points_df[p_name]
        parameter_min = min(parameter_values)
        parameter_max = max(parameter_values)
        parameters[p_name] = {"min" : parameter_min, "max" : parameter_max}
        points_list.append(parameter_values)
    points_array = np.array(points_list)
    return parameters, points_array.T


def normalize(parameter, value):
    if parameter["max"] != parameter["min"]:
        return (value - parameter["min"]) / (parameter["max"] - parameter["min"])
    else:
        return value


def restore(parameter, value):
    if parameter["max"] != parameter["min"]:
        return parameter["min"] + value * (parameter["max"] - parameter["min"])
    else:
        return value


def create_grid(parameters, mode = 'itertools'):
    p_names = parameter_ordered_names(parameters)
    if mode == 'mgrid':
        """slices = []
        for p_name in p_names:
            slices.append(slice(parameters[p_name]["min"],
                          parameters[p_name]["max"]+parameters[p_name]["step"],
                          parameters[p_name]["step"]))
        points = np.mgrid[*slices].reshape(len(slices),-1).T"""
        raise NameError("Not implemented in older versions of Python")
    elif mode == 'itertools':
        p_ranges = []
        for p_name in p_names:
            p_range = np.arange(parameters[p_name]["min"],
                                parameters[p_name]["max"]
                              + parameters[p_name]["step"],
                                parameters[p_name]["step"])
            if p_range[-1] > parameters[p_name]["max"]:
                p_range = p_range[:-1]
            p_ranges.append(p_range)
        points = np.array(list(itertools.product(*p_ranges)))
    return points


def create_points(parameters, samples_df, p_mode = "grid", points_file = None,
                  return_unprobed = True):
    p_names = parameter_ordered_names(parameters)
    if p_mode == "grid":
        points_to_check = create_grid(parameters)
    elif p_mode == "file":
        _, points_to_check = read_points(points_file)
    else:
        raise NameError(f"Unsupported point mode {p_mode}")
    points = []
    labels = []
    for point in points_to_check:
        query_array = []
        for i_p_name in range(len(p_names)):
            query_array.append(f"{p_names[i_p_name]} == {point[i_p_name]}")
        query = " & ".join(query_array)
        samples = samples_df.query(query)
        if len(samples) > 0:
            points.append(point)
            labels.append(samples["state"].iloc[0])
        elif return_unprobed:
            points.append(point)
            labels.append(-1)
    return points, labels


def create_points2(parameters, samples_df, p_mode = "grid", points_file = None,
                   return_unprobed = True, unprobed_backend = "v1"):
    #Read parameter columns from dataframe
    p_names = parameter_ordered_names(parameters)
    transposed_points = []
    for p_name in p_names:
        transposed_points.append(samples_df[p_name])
    points = np.transpose(transposed_points)
    labels = list(samples_df["state"])
    #Create grid
    #If point from grid is not in parameters, add it
    #pdb.set_trace()
    if return_unprobed:
        if unprobed_backend == "v1":
            if p_mode == "grid":
                points_to_check = create_grid(parameters)
            elif p_mode == "file":
                _, points_to_check = read_points(points_file)
            else:
                raise NameError(f"Unsupported point mode {p_mode}")
            for point in points_to_check:
            #if point not in points:
                if not any(np.equal(points,point).all(1)):
                    #pdb.set_trace()
                    if points.shape[0] == 0:
                        points = np.array([point])
                        labels.append(-1)
                    else:
                        points = np.concatenate((points, [point]))
                        labels.append(-1)
            #pdb.set_trace()
            return points, labels
        elif unprobed_backend == "v2":
            if p_mode == "grid":
                points_to_check = create_grid(parameters)
            elif p_mode == "file":
                _, points_to_check = read_points(points_file)
            else:
                raise NameError(f"Unsupported point mode {p_mode}")
            #pdb.set_trace()
            is_unchecked = ~np.all(np.isin(points_to_check, points), axis = 1)
            unchecked_points = points_to_check[is_unchecked]
            unchecked_labels = np.full(unchecked_points.shape[0], -1)
            all_points = np.concatenate((points, unchecked_points), axis = 0)
            all_labels = np.concatenate((labels, unchecked_labels), axis = 0)
    else:
        all_points = points
        all_labels = labels
    #pdb.set_trace()
    return all_points, all_labels


def normalize_points(parameters, points):
    p_names = parameter_ordered_names(parameters)
    normalized_points = []
    for point in points:
        normalized_point = []
        for i_p_name in range(len(p_names)):
            normalized_point.append(normalize(parameters[p_names[i_p_name]],
                                              point[i_p_name]))
        normalized_points.append(normalized_point)
    return normalized_points


def restore_points(parameters, points):
    p_names = parameter_ordered_names(parameters)
    restored_points = []
    for point in points:
        restored_point = []
        for i_p_name in range(len(p_names)):
            restored_point.append(restore(parameters[p_names[i_p_name]],
                                          point[i_p_name]))
        restored_points.append(restored_point)
    return restored_points


def uncertainties_eb(label_distributions):
    """ Entropy-based: sum(p*log(p)) """
    uncertainties = []
    for sample in label_distributions:
        if np.max(sample) == 1.:
            uncertainties.append(0.)
        else:
            uncertainties.append(-1. * np.dot(sample, np.log(sample)))
    return uncertainties


def uncertainties_lc(label_distributions):
    """ Least certain: 1 - max(X,p) """
    uncertainties = []
    for sample in label_distributions:
        uncertainties.append(1. - np.max(sample))
    return uncertainties


def uncertainties_ms(label_distributions):
    """ Margin sampling: 1 - [max(X,p) - second_max(X,p)] """
    uncertainties = []
    for sample in label_distributions:
        prob_ix = np.argsort(sample)
        uncertainties.append(1. - sample[prob_ix[-1]] + sample[prob_ix[-2]])
    return uncertainties


def uncertainties(label_distributions, mode = None):
    match mode:
        case "EB":
            return uncertainties_eb(label_distributions)
        case "LC":
            return uncertainties_lc(label_distributions)
        case "MS":
            return uncertainties_ms(label_distributions)


def fit_model(parameters, points, labels, mode = None, backend_params = None):

    normalized_points = normalize_points(parameters, points)

    label_prop = LabelSpreading(**backend_params)

    label_prop.fit(normalized_points, labels)

    distributions = label_prop.label_distributions_
    
    converged_features, converged_distributions, nsamples = converge_points(
                                                    points,
                                                    distributions)

    uc = uncertainties(converged_distributions, mode = mode)
    
    uc_normalized = [uc_ns[0] / uc_ns[1] for uc_ns in list(zip(uc, nsamples))]

    uc_features = list(zip(uc_normalized, converged_features))

    uc_features.sort(key = lambda k: k[0])
    
    return uc_features, points, distributions


def converge_points(features, label_distributions):
    """Converge the the different samples with identical features into one
        with the correspoinding label distribution"""
    nsamples = len(features)
    factors = np.full(nsamples, 1)
    if len(label_distributions) != nsamples:
        raise NameError(
            "features and label distributions dimensions do not match")
    for i in range(nsamples):
        for j in range(i):
            if np.array_equal(features[j],features[i]) and factors[j] != 0:
                label_distributions[j] = np.add(label_distributions[j],
                                                label_distributions[i])
                factors[i] -= 1
                factors[j] += 1
    converged_features, converged_label_distributions, converged_factors\
                                                                = [], [], []
    #pdb.set_trace()
    for i in range(nsamples):
        if factors[i] > 0:
            converged_features.append(features[i])
            converged_label_distributions.append(label_distributions[i]
                                                 /factors[i])
            converged_factors.append(factors[i])
    return converged_features, converged_label_distributions, converged_factors


def choose_random_prefer_unprobed(points, labels):
    points_labels = zip(points, labels)
    unprobed_points = [p_l[0] for p_l in points_labels if p_l[1] == -1]
    if len(unprobed_points) > 0:
        return random.choice(unprobed_points)
    else:
        return random.choice(list(points))


def choose_parameters(config, samples_df):

    mode = config["run_parameters"]["sampling_mode"]
    uc_threshold = config["run_parameters"]["uc_threshold"]
    p_mode = config["run_parameters"]["p_mode"]
    parameters = config["model_parameters"]
    
    if p_mode == "points":
        points_file = config["points_file"]
    else:
        points_file = None
    
    points, labels = create_points2(parameters, samples_df, p_mode = p_mode,
                                   points_file = points_file)

    if samples_df.shape[0] > config["run_parameters"]["n_random"]:

        uc_features, _, _ = fit_model(parameters, points, labels, mode = mode,
                                      backend_params = BACKEND_PARAMS)

        uc_delta = uc_features[-1][0] - uc_features[0][0]
        
        max_uc = uc_features[-1][0]

        if uc_delta > uc_threshold:
            top_list_length = config["run_parameters"].get(
                                    "randomize_top_points", 1)
            top_list_length = min(top_list_length, len(uc_features))
            i_point = -1 * random.randint(1, top_list_length)
            return uc_features[i_point][1], mode, max_uc, i_point
        else:
            mode = "random"
            return choose_random_prefer_unprobed(points,labels), mode, max_uc, 0
    else:
        mode = "random"
        max_uc = "N/A"
        return choose_random_prefer_unprobed(points, labels), mode, max_uc, 0


def run_simulation(simulation):
    from microplastic.modify_seq import prepare_sample
    i_iter = simulation["sample"]
    rp = simulation["config"]["run_parameters"]
    try:
        simulation_type = rp["simulation_type"]
    except KeyError:
        simulation_type = "standard"
    for i_step in range(1, rp["n_steps"] + 1):
        if i_step == 1:
            try:
                run_template = rp["initial_run_template"]
            except KeyError:
                run_template = rp["run_template"]
        else:
            run_template = rp["run_template"]
        run_filename = f"run_{i_iter}.{i_step}.lammps"
        infile_name = f"in_{i_iter}.{i_step}.data"
        prev_outfile_name = f"out_{i_iter}.{i_step-1}.data"
        outfile_name = f"out_{i_iter}.{i_step}.data"
        logfile_name = f"{i_iter}.{i_step}.log"
        xdata_name = f"xdata.{i_iter}.{i_step}.lammps"
        dump_name = f"atoms.{i_iter}.{i_step}.lammpsdump"
        if simulation_type != "rerun":
            substitute_values(run_template, run_filename,
                          [["INPUT", infile_name],
                           ["OUTPUT", outfile_name],
                           ["LOG", logfile_name],
                           ["XDATA", xdata_name],
                           ["DUMP", dump_name],
                           ["RANDOM", f"{random.randint(1,100000)}"],
                           ])
        if i_step == 1 and simulation_type != "rerun":
            u = prepare_sample(simulation)
            if simulation_type == "dpd":
                u.atoms.write("system_pre.data")
                substitute_values("system_pre.data", "system.data",
                                  [["""1 1.000000
2 1.000000""", """1 1.000000 # C
2 1.000000 # O"""]])
                os.system("./mesoconstructor.exe")
                os.system(f"mv system_lmp.dpd {infile_name}")
            else:
                u.atoms.write(infile_name)
            simulation["step"] = 1
        else:
            if simulation_type != "rerun":
                os.system(f"cp -a {prev_outfile_name} {infile_name}")
            if simulation_type == "rerun":
                get_simulation_parameters(infile_name)
            simulation["step"] += 1
        if simulation_type != "rerun":
            if rp["run_mode"] == "module":
                from lammps import lammps
                lmp = lammps()
                lmp.file(run_filename)
            elif rp["run_mode"] == "standalone":
                run_command = rp["run_command"]
                command = f"{run_command} --input {run_filename}"
            exit_code = os.system(command)
    # Process the simulation data: determine the aggregation number
        output_exists = os.path.isfile(outfile_name)
        dump_exists = os.path.isfile(dump_name)
        actions = eval(rp["actions"])
        if output_exists:
            if dump_exists:
                if simulation_type == "dpd":
                    u = mda.Universe("system.data", dump_name)
                else:
                    u = mda.Universe(outfile_name, dump_name)
            else:
                u = mda.Universe(outfile_name)
            simulation["state"], simulation["dump_frame"] = label(simulation, u)
        else:
            simulation["state"] = 0
        if actions[simulation["state"]] == "break":
            break


def label(simulation, u):
    r_neigh_aggregation = simulation["config"]["run_parameters"]\
                                    ["r_neigh_aggregation"]
    aggregates_dict = determine_aggregates(u, r_neigh = r_neigh_aggregation)
    aggregates_data = aggregates_dict["data"]
    timesteps = list(aggregates_data.keys())
    for i_ts in range(len(timesteps)):
        n_aggregates = len(aggregates_data[timesteps[i_ts]])
        if n_aggregates > 1:
            return 2, i_ts
    return 1, len(timesteps)


def concurrent_update(filename, simulation):

    process_id = f"{socket.gethostname()}_{os.getpid()}"
    filename_noext, extension = os.path.splitext(filename)
    lock_filename = filename_noext + ".lock"
    version_filename =  filename_noext + ".version"
    temp_filename = filename_noext + process_id + "." + extension

    if not os.path.exists(version_filename):
        with open(version_filename, 'w') as f:
            f.write('0')

    while True:
        attempt_count = 0
        max_attempts = MAX_UPDATE_ATTEMPTS

        try:
            # Attempt to acquire lock
            if not os.path.exists(lock_filename):
                # Create lock file
                with open(lock_filename, 'w') as f:
                    f.write(process_id)

                # Small delay to ensure lock is established
                time.sleep(SHORT_SLEEP)

                # Verify we still have the lock
                with open(lock_filename, 'r') as f:
                    if f.read().strip() == process_id:
                        # Lock acquired successfully
                        break

            attempt_count += 1
            if attempt_count >= max_attempts:
                raise Exception("Could not acquire lock after multiple attempts")
            time.sleep(random.uniform(SHORT_SLEEP, LONG_SLEEP))

        except (IOError, PermissionError):
            time.sleep(random.uniform(SHORT_SLEEP, LONG_SLEEP))
            continue

    try:
        # Read current version
        with open(version_filename, 'r') as f:
            current_version = int(f.read().strip())

        # Read existing data
        updated_data = updated_dataframe(filename, simulation)

        # Write to temporary file first
        updated_data.to_excel(temp_filename, index=False)

        # Verify version hasn't changed
        with open(version_filename, 'r') as f:
            if int(f.read().strip()) != current_version:
                raise Exception("Version conflict detected")

        # Atomic operations
        os.replace(temp_filename, filename)

        # Increment version
        with open(version_filename, 'w') as f:
            f.write(str(current_version + 1))

    except Exception as e:
        # Handle errors
        print(f"Error during update: {str(e)}")
        # Clean up temp file if it exists
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        raise

    finally:
        # Release lock
        if os.path.exists(lock_filename):
            with open(lock_filename, 'r') as f:
                if f.read().strip() == process_id:
                    os.remove(lock_filename)


def updated_dataframe(filename, simulation):
    #Prepare the simulation output
    simulation_record = {k: simulation.get(k, "n/a") for k in RECORD_PARAMETERS}
    for tp in simulation["trial_parameters"]:
        simulation_record[tp] = simulation["trial_parameters"][tp]
    new_dataframe = pd.DataFrame(simulation_record, index = [0])
    #Read and update the dataframe
    # Read existing data
    try:
        existing_dataframe = pd.read_excel(filename)
        updated_dataframe = pd.concat([existing_dataframe, new_dataframe],
                                      ignore_index = True)
    except FileNotFoundError:
        updated_dataframe = new_dataframe

    updated_dataframe.reset_index()
    return updated_dataframe


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = 'Build a phase diagram')

    parser.add_argument('--config', metavar = 'JSON', type = str, nargs = 1,
        help = 'configuration file')


    args = parser.parse_args()

    config_filename = args.config[0]

    config = read_config(config_filename)

    mp, rp = config["model_parameters"], config["run_parameters"]

    p_names = parameter_ordered_names(mp)

    if True:
        #from microplastic.modify_seq import modify_seq
        from parzen_search import substitute_values
        # Main loop
        while True:
            samples_df = pd.read_excel(rp["samples_file"])
            i_iter = samples_df.shape[0] + 1
            if i_iter > rp["iterations"]:
                break
            # Fit the model and choose simulation parameters
            trial_parameters, choice_mode, uc, i_point = choose_parameters(
                                                             config,samples_df)
            #pdb.set_trace()
            # Create the simulation dict object with all the attributes stored
            simulation = {}
            simulation["study"] = rp.get("study", "n/a")
            simulation["sample"] = i_iter
            simulation["choice"] = choice_mode
            simulation["uncertainty"] = uc
            simulation["i_point"] = i_point
            simulation["config"] = config
            simulation["trial_parameters"] = {}
            for i_param in range(len(p_names)):
                simulation["trial_parameters"][p_names[i_param]] \
                = trial_parameters[i_param]
            # Run the simulation
            run_simulation(simulation)
            # Update the dataframe
            samples_df = concurrent_update(rp["samples_file"], simulation)