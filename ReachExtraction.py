# -*- coding: utf-8 -*-
# _____________________________________________________________________________
# _____________________________________________________________________________
#
#                       Coded by: Daniel Gonzalez-Duque
#                               Last revised 2022-09-03
# _____________________________________________________________________________
# _____________________________________________________________________________
"""
______________________________________________________________________________

 DESCRIPTION:
   This class extracts the complete reaches obtained with the model
______________________________________________________________________________
"""
# -----------
# Libraries
# -----------
# System Management
import os
import copy
import logging
# Data Management
import numpy as np
from scipy import interpolate
from scipy.interpolate import UnivariateSpline
import pandas as pd
# MeanderCONUS Packages
from utilities import classExceptions as CE
from utilities import filesManagement as FM
from utilities import statistics as ST


# ------------------
# Logging
# ------------------
# Set logger
logging.basicConfig(handlers=[logging.NullHandler()])


# ------------------
# Class
# ------------------
class CompleteReachExtraction:
    """
    This class obtained meander information from the NHD dataset.
    It works by loading the NHD geometry and using different methods
    to obtain meander information.

    The following are the available attributes

    ===================== =====================================================
    Attribute             Description
    ===================== =====================================================
    path_out              path to save the files.
    save_format           save format of the information, the formats are:\n
                          'p': pickle.\n
                          'json': json type file.\n
                          'mat': MATLAB type file.\n
                          'csv': csv type file.\n
                          'txt': txt type file.\n
    nhd_tables            NHD tables to be loaded, by default it will load the
                          'NHDPlusFlowlineVAA', 'NHDPlusEROMMA',
                          'NHDPlusIncrPrecipMA', 'NHDPlusIncrTempMA'
    ===================== =====================================================

    The following are the methods of the class.

    ===================== =====================================================
    Methods               Description
    ===================== =====================================================
    read_mt_file          read in a MT file [ EDI | XML | j ]
    ===================== =====================================================


    Examples
    -------------------
    :Read from NHD GBD: ::

        >>> import
    """
    def __init__(self, data, path_coordinates, logger=None, **kwargs):
        """
        Class constructor
        """
        # ------------------------
        # Logging
        # ------------------------
        if logger is None:
            self._logging = logging.getLogger(self.__class__.__name__)
            self._logging.setLevel(logging.DEBUG)
        else:
            self._logging = logger
            self._logging.info(f'Starting logger {self.__class__.__name__}')
        # ------------------------
        # Attribute management
        # ------------------------
        # Default data
        # Path management
        self.data_info = data
        self.data_info.set_index('NHDPlusID', inplace=True)
        self.huc_04 = np.unique(self.data_info['HUC04'].values)
        self._path_coordinates = path_coordinates
        self._save_format = 'csv'
        self.__save_formats = FM.get_save_formats()

        # Change parameters
        valid_kwargs = ['save_format']
        for k, v in zip(kwargs.keys(), kwargs.values()):
            if k not in valid_kwargs:
                raise TypeError("Invalid keyword argument %s" % k)
            k = f'_{k}'
            setattr(self, k, v)

        # --------------------
        # Data Management
        # --------------------
        self.data_reaches = {}
        self.id_reaches = []
        self.data_reaches_spl = {}

        # ------------
        # NHD Data
        # ------------
        self.coords_all = None

    # --------------------------
    # get functions
    # --------------------------
    @property
    def path_coordinates(self):
        """ path for data saving"""
        return self._path_coordinates

    @property
    def save_format(self):
        """save format of the files"""
        return self._save_format

    @property
    def logger(self):
        """logger for debbuging"""
        return self._logging
    # --------------------------
    # set functions
    # --------------------------
    @save_format.setter
    def save_format(self, save_format):
        """set save format of the files"""
        if save_format not in self.__save_formats:
            self.logger.error(f"format '{save_format}' not implemented. "
                              f"Use any of these formats "
                              f"{self.__save_formats}")
            raise CE.FormatError(f"format '{save_format}' not implemented. "
                                 f"Use formats 'p', 'mat', 'json', 'txt', or"
                                 f"'csv'")
        else:
            self.logger.info(f"Setting save_format to '{save_format}'")
            self._save_format = save_format

    def map_complete_reach(self, start_comid, huc_number=4):
        """
        DESCRIPTION:
            Separate complete reach comid from the ToNode and FromNode
            values
        _______________________________________________________________________
        INPUT:
            :param start_comid: str,
                Start comid value.
            :param path: int,
                Path of the current reach.
        _______________________________________________________________________
        OUTPUT:
            :return reach: list,
                List of comids for the values
        """
        # comid = self.data_info['NHDPlusID'].values.astype(str)
        comid = np.array(self.data_info.index)
        from_node = self.data_info['FromNode'].values
        huc_n = self.data_info.loc[start_comid, f'HUC{huc_number:02d}']
        data_info = self.data_info[
            self.data_info[f'HUC{huc_number:02d}'] == huc_n]
        # div = self.data_info['Divergence'].values

        c_comid = start_comid
        comid_network = np.zeros(len(comid))
        i = 0
        while True:

            # Get to and from nodes
            to_i = data_info.loc[c_comid, 'ToNode']

            # Save Data
            comid_network[i] = c_comid
            # Extract new comid
            c_comid = data_info.index[
                data_info['FromNode'] == to_i]
            if len(c_comid) == 0:
                break
            else:
                c_comid = c_comid[0]
            i += 1
        comid_network = comid_network[comid_network != 0]
        return comid_network

    def map_coordinates(self, comid_list):
        """
        Map Coordinates and additional data to the comid_list
        """
        comid_list = np.array(comid_list).astype(float)
        huc_04s = self.data_info.loc[comid_list, 'HUC04'].values
        slope = self.data_info.loc[comid_list, 'Slope'].values
        so_values = self.data_info.loc[comid_list, 'StreamOrde']
        # cm to m
        max_elev = self.data_info.loc[comid_list, 'MaxElevSmo'].values / 100
        # Generate Loop
        data = {}
        for huc in self.huc_04:
            c_all = comid_list[huc_04s == huc]
            file_coords = (f'{self.path_coordinates}HUC04_'
                           f'{huc}_coordinates_p_102003.hdf5')
            # Load File
            if file_coords.split('.')[-1] == 'hdf5':
                keys = [str(i) for i in c_all]
                coordinates = FM.load_data(f'{file_coords}', keys=keys)
                coordinates = {float(i): coordinates[i] for i in keys}
            else:
                coordinates = FM.load_data(f'{file_coords}')
            # -----------------
            # Get coordinates
            # -----------------
            lengths = [len(coordinates[i][0]) for i in c_all]
            xx = [item for i in c_all for item in coordinates[i][0]]
            yy = [item for i in c_all for item in coordinates[i][1]]
            indices = np.unique(xx, return_index=True)[1]
            x = np.array([xx[i] for i in sorted(indices)])
            y = np.array([yy[i] for i in sorted(indices)])
            # ------------------------------------
            # Calculate distance along the river
            # ------------------------------------
            # Check if the complete reach is lower than 3
            x_coord = np.vstack((x, y)).T
            s = ST.get_reach_distances(x_coord)
            # -----------------------------
            # Additional values
            # -----------------------------
            comid_values = [
                float(i) for i in c_all for item in coordinates[i][0]]
            comid_values = np.array([comid_values[i] for i in sorted(indices)])
            so = [so_values[float(i)] for i in c_all for item in
                  coordinates[i][0]]
            so = np.array([so[i] for i in sorted(indices)])
            # -----------------------------
            # Include Elevation
            # -----------------------------
            z = np.zeros(x.shape)
            i_cc = 0
            for i_c, c in enumerate(c_all):
                if i_c == 0:
                    z_max = max_elev[i_c]
                else:
                    z_max = z[i_cc]

                z[i_cc:i_cc + lengths[i_c]] = (
                        z_max - (s[i_cc:i_cc + lengths[i_c]] - s[i_cc])
                        * slope[i_c])
                i_cc += lengths[i_c] - 1

            data = {'comid': comid_values, 'x': x, 'y': y, 'z': z, 's': s,
                    'so': so}
            data = pd.DataFrame.from_dict(data)
            data.set_index('comid', inplace=True)

        return data

    @staticmethod
    def fit_splines(data):
        """
        Fit splines to the coordinates
        """
        # Extract data
        comid = np.array(data.index)
        so = data['so'].values
        s = data['s'].values
        x = data['x'].values
        y = data['y'].values
        z = data['z'].values
        # ---------------
        # Get poly S
        # ---------------
        diff_s = np.min(np.diff(s))
        s_poly = np.arange(s[0], s[-1], diff_s)
        # ------------------
        # Generate Splines
        # -----------------
        x_spl = UnivariateSpline(s, x, k=3, s=0, ext=0)
        y_spl = UnivariateSpline(s, y, k=3, s=0, ext=0)
        z_spl = UnivariateSpline(s, z, k=1, s=0, ext=0)
        f_comid = interpolate.interp1d(s, comid,
                                       fill_value=(comid[0], comid[-1]),
                                       kind='previous', bounds_error=False)
        # ------------------
        # Create points
        # -----------------
        x_poly = x_spl(s_poly)
        y_poly = y_spl(s_poly)
        z_poly = z_spl(s_poly)
        comid_poly = f_comid(s_poly)
        # ------------------
        # Create data
        # -----------------
        data_fitted = {'s_poly': s_poly ,'x_poly': x_poly, 'y_poly': y_poly,
                       'z_poly': z_poly, 'comid_poly': comid_poly}
        data_fitted = pd.DataFrame.from_dict(data_fitted)
        data_fitted.set_index('comid_poly', inplace=True)

        return data_fitted

