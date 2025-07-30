"""
Constants and configuration parameters for the legacy v3 DeepMIMO dataset generation.

This module contains all constant definitions used in the v3 version of DeepMIMO toolkit,
including parameter names, file paths, and configuration options.
"""

import numpy as np

# Core Configuration
VERSION = 3
FP_TYPE = np.float32  # floating point precision for saving values

# Dict names
DICT_UE_IDX = 'user'
DICT_BS_IDX = 'basestation'

# NAME OF PARAMETER VARIABLES
PARAMSET_DATASET_FOLDER = 'dataset_folder'
PARAMSET_SCENARIO = 'scenario'
PARAMSET_DYNAMIC_SCENES = 'dynamic_scenario_scenes'

PARAMSET_NUM_PATHS = 'num_paths'
PARAMSET_ACTIVE_BS = 'active_BS'
PARAMSET_USER_ROWS = 'user_rows'
PARAMSET_USER_SUBSAMP = 'user_subsampling'

PARAMSET_BS2BS = 'enable_BS2BS'

# INNER VARIABLES
PARAMSET_ACTIVE_UE = 'active_UE'
PARAMSET_SCENARIO_FIL = 'scenario_files'
PARAMSET_ANT_BS_DIFF = 'BS2BS_isnumpy'

# SCENARIO PARAMS
PARAMSET_SCENARIO_PARAMS = 'scenario_params'
PARAMSET_SCENARIO_PARAMS_CF = 'carrier_freq'
PARAMSET_SCENARIO_PARAMS_TX_POW = 'tx_power'
PARAMSET_SCENARIO_PARAMS_NUM_BS = 'num_BS'
PARAMSET_SCENARIO_PARAMS_USER_GRIDS = 'user_grids'
PARAMSET_SCENARIO_PARAMS_POLAR_EN = 'dual_polar_available'
PARAMSET_SCENARIO_PARAMS_DOPPLER_EN = 'doppler_available'

PARAMSET_SCENARIO_PARAMS_PATH = 'scenario_params_path'

# OUTPUT VARIABLES
OUT_CHANNEL = 'channel'
OUT_PATH = 'paths'
OUT_LOS = 'LoS'
OUT_LOC = 'location'
OUT_DIST = 'distance'
OUT_PL = 'pathloss'

OUT_PATH_NUM = 'num_paths'
OUT_PATH_DOD_PHI = 'DoD_phi'
OUT_PATH_DOD_THETA = 'DoD_theta'
OUT_PATH_DOA_PHI = 'DoA_phi'
OUT_PATH_DOA_THETA = 'DoA_theta'
OUT_PATH_PHASE = 'phase'
OUT_PATH_TOA = 'ToA'
OUT_PATH_RX_POW = 'power'
OUT_PATH_LOS = 'LoS'
OUT_PATH_DOP_VEL = 'Doppler_vel'
OUT_PATH_DOP_ACC = 'Doppler_acc'
OUT_PATH_ACTIVE = 'active_paths'

# FILE LISTS - raytracing.load_ray_data()
LOAD_FILE_EXT = ['DoD', 'DoA', 'CIR', 'LoS', 'PL', 'Loc']
LOAD_FILE_EXT_FLATTEN = [1, 1, 1, 1, 0, 0]
LOAD_FILE_EXT_UE = ['DoD.mat', 'DoA.mat', 'CIR.mat', 'LoS.mat', 'PL.mat', 'Loc.mat']
LOAD_FILE_EXT_BS = ['DoD.BSBS.mat', 'DoA.BSBS.mat', 'CIR.BSBS.mat', 'LoS.BSBS.mat', 'PL.BSBS.mat', 'BSBS.RX_Loc.mat']

# TX LOCATION FILE VARIABLE NAME - load_scenario_params()
LOAD_FILE_TX_LOC = 'TX_Loc_array_full'

# SCENARIO PARAMS FILE VARIABLE NAMES - load_scenario_params()
LOAD_FILE_SP_VERSION = 'version'
LOAD_FILE_SP_RAYTRACER = 'raytracer'
LOAD_FILE_SP_RAYTRACER_VERSION = 'raytracer_version'
LOAD_FILE_SP_EXT = '.params.mat'
LOAD_FILE_SP_CF = 'carrier_freq'
LOAD_FILE_SP_TX_POW = 'transmit_power'
LOAD_FILE_SP_NUM_BS = 'num_BS'
LOAD_FILE_SP_USER_GRIDS = 'user_grids'
LOAD_FILE_SP_DOPPLER = 'doppler_available'
LOAD_FILE_SP_POLAR = 'dual_polar_available'
LOAD_FILE_SP_NUM_TX_ANT = 'num_tx_ant'
LOAD_FILE_SP_NUM_RX_ANT = 'num_rx_ant'

# Channel parameters
PARAMSET_POLAR_EN = 'enable_dual_polar'
PARAMSET_DOPPLER_EN = 'enable_doppler'  # Doppler from Ray Tracer
PARAMSET_FD_CH = 'freq_domain'  # Time Domain / Frequency Domain (OFDM)

PARAMSET_OFDM = 'ofdm'
PARAMSET_OFDM_SC_NUM = 'subcarriers'
PARAMSET_OFDM_SC_SAMP = 'selected_subcarriers'
PARAMSET_OFDM_BW = 'bandwidth'
PARAMSET_OFDM_BW_MULT = 1e9  # Bandwidth input is GHz, multiply by this
PARAMSET_OFDM_LPF = 'rx_filter'

PARAMSET_ANT_BS = 'bs_antenna'
PARAMSET_ANT_UE = 'ue_antenna'
PARAMSET_ANT_SHAPE = 'shape'
PARAMSET_ANT_SPACING = 'spacing'
PARAMSET_ANT_ROTATION = 'rotation'
PARAMSET_ANT_RAD_PAT = 'radiation_pattern'
PARAMSET_ANT_RAD_PAT_VALS = ['isotropic', 'halfwave-dipole']
PARAMSET_ANT_FOV = 'fov'

# Physical Constants
LIGHTSPEED = 299792458  # Speed of light in m/s

# Scenarios folder
SCENARIOS_FOLDER = 'deepmimo_scenarios_v3' 