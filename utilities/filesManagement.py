# -*- coding: utf-8 -*-
# _____________________________________________________________________________
# _____________________________________________________________________________
#
#                       Coded by: Daniel Gonzalez-Duque
#
#                               Last revised 2021-01-25
# _____________________________________________________________________________
# _____________________________________________________________________________
"""
The functions given on this package allow the user to save data in different
formats

"""
# ------------------------
# Importing Modules
# ------------------------ 
# Data Managment
import copy
import pickle
import scipy.io as sio
import pandas as pd
from scipy import special
# import fiona
import json
import numpy as np
import glob as gl
import os

# Personal Libraries
from . import utilities as utl
from . import classExceptions as CE

# ------------------------
# Functions
# ------------------------


def get_save_formats():
    return ['p', 'mat', 'json', 'txt', 'csv', 'shp']

def get_load_formats():
    return ['p', 'mat', 'json', 'txt', 'csv', 'shp', 'dbf']


def save_data(data, path_output, file_name, *args, **kwargs):
    """
    DESCRIPTION:
        Saves data depending on the format. It can save files in pickle,
        matlab, cvs, and txt.
    _______________________________________________________________________
    INPUT:
        :param data: dict,
            Dictionary with the data to be saved.
        :type data: dict or gpd.read_file() or pd.DataFrame
        :param path_output: str,
            Directory to be saved, the directory will be created.
        :type path_output: str
        :param file_name: str,
            Name of the file, it must include the extension.
        :type file_name: str
    _______________________________________________________________________
    OUTPUT:
        Saves the data.
    """
    # ---------------------
    # Error Management
    # ---------------------
    # if not isinstance(data, dict) and not isinstance(
    #         data, gpd.geodataframe.GeoDataFrame):
    #     raise TypeError('data must be a dictionary or a geopandas dataframe')
    # ---------------------
    # Create Folder
    # ---------------------
    utl.cr_folder(path_output)

    # ---------------------
    # Save data
    # ---------------------
    name_out = f'{path_output}{file_name}'
    extension = file_name.split('.')[-1]

    if isinstance(data, pd.DataFrame) and extension != 'shp':
        dataframe = copy.deepcopy(data)
        data = {}
        for i in dataframe.columns:
            data[i] = dataframe[i].values

    if extension == 'mat':
        sio.savemat(name_out, data, *args, **kwargs)
    elif extension in ('txt', 'csv'):
        dataframe = pd.DataFrame.from_dict(data)
        dataframe.to_csv(name_out, *args, **kwargs)
    elif extension == 'p':
        file_open = open(name_out, "wb")
        pickle.dump(data, file_open)
        file_open.close()
    elif extension == 'json':
        with open(name_out, 'w') as json_file:
            json.dump(data, json_file)
    elif extension == 'shp':
        if isinstance(data, pd.DataFrame):
            data = gpd.GeoDataFrame(data, geometry=data.geometry)
        data.to_file(name_out)
    else:
        raise CE.FormatError(
            f'format .{extension} not implemented. '
            f'Use extensions {get_save_formats()}')


def load_data(file_data, pandas_dataframe=False, *args, **kwargs):
    """
    DESCRIPTION:
        Loads data depending on the format and returns a dictionary.

        The data can be loaded from pickle, matlab, csv, or txt.
    _______________________________________________________________________
    INPUT:
        :param file_data: str,
            Data file
        :param pandas_dataframe: boolean,
            If true returns a pandas dataframe instead of a dictionary.
                                
    _______________________________________________________________________
    OUTPUT:
        :return data: dict,
            Dictionary or pandas dataframe with the data in the file.
    """
    # ---------------------
    # Error Management
    # ---------------------
    if not isinstance(file_data, str):
        raise TypeError('data must be a string.')

    # ---------------------
    # load data
    # ---------------------
    extension = file_data.split('.')[-1].lower()
    if extension == 'mat':
        data = sio.loadmat(file_data, *args, **kwargs)
    elif extension in ('txt', 'csv'):
        dataframe = pd.read_csv(file_data, *args, **kwargs)
        data = {}
        for i in dataframe.columns:
            data[i] = dataframe[i].values
    elif extension == 'p':
        file_open = open(file_data, "rb")
        data = pickle.load(file_open)
        file_open.close()
    elif extension == 'json':
        with open(file_data) as f:
            data = json.load(f)
    else:
        raise CE.FormatError(
            f'format .{extension} not implemented. '
            f'Use files with extensions {get_load_formats()}')
    if pandas_dataframe:
        data = pd.DataFrame.from_dict(data)
    return data
