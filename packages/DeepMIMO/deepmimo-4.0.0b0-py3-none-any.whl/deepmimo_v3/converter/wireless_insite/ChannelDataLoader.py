import glob
import pandas as pd
import re
import numpy as np
import os
from tqdm import tqdm
from math import cos, sin, radians
import re
import scipy.io

EXTS = ['cir', 'doa', 'dod', 'paths', 'pl']
PARSE_FUNCS = ['parse_first', 'parse_first', 'parse_first', 'parse_third', 'parse_second']


class WIChannelConverter:

    def __init__(self, directory, save_folder, moving_objects=None, interacts=False):
        self.channels = []
        self.interacts = interacts
        
        self.moving_objects = moving_objects
        
        self.save_folder = save_folder
        if not os.path.exists(self.save_folder):
            os.mkdir(self.save_folder)
            
        self.import_dir(directory)

    def import_dir(self, directory):
        file_table = self.directory_table(directory)
        self.import_files(file_table)

    def import_files(self, file_table):
        triplet_cols = ['TX_ID', 'TX_CNT', 'RX_ID']
        unique_table = file_table[triplet_cols].drop_duplicates()
        
        # To collect the TX locs
        unique_tx = unique_table[['TX_ID', 'TX_CNT']].drop_duplicates()
        unique_tx = unique_tx['TX_ID'].astype(str) + '-' + unique_tx['TX_CNT'].astype(str)
        tx_locs = {unique_tx.iloc[i]:None for i in range(len(unique_tx))}
        
        for i in tqdm(range(len(unique_table))):
            rx_tx_pair = unique_table.iloc[i]
            
            # Find the files matching to the TX-RX pair
            match = (file_table[triplet_cols] == rx_tx_pair).sum(axis=1) == len(triplet_cols)
            read_table = file_table[match].reset_index(drop=True)
            
            # Read all the files of the TX-RX pair and collect information
            files = {'ID': rx_tx_pair}
            for j in range(len(read_table)):
                file_data = self.import_file(filename=read_table['Dir'][j], 
                                             extension=read_table['Extension'][j])
                files = {**files, read_table['Extension'][j]: file_data}

            self.channels = self.create_ch_from_files(files, tx_locs)
            if self.moving_objects is not None:
                self.add_Doppler(self.moving_objects)
            self.save_channels('TX%i-%i_RX%i.mat'%tuple(rx_tx_pair))
            
        for key in tx_locs.keys():
            if tx_locs[key] is None:
                print('Warning: The transmitter %s has no paths with any receiver! (or debug the code)')
        scipy.io.savemat(os.path.join(self.save_folder, 'TX_locs.mat'), tx_locs)

    def create_ch_from_files(self, file_data, tx_locs):

        # Create Channels from Information
        num_rx = len(file_data[EXTS[0]])
        channels = []
        for i in range(num_rx):
            # Location finding
            TX_ID = re.findall(r' Tx: (\d+) ', file_data[EXTS[4]]['TX_str'])[0]
            RX_ID = re.findall(r' Rx: (\d+) ', file_data[EXTS[4]]['RX_str'])[0]
                                    
            channels.append(Channel(file_data['ID'],
                                    file_data[EXTS[4]]['TX_str'],
                                    file_data[EXTS[4]]['RX_str'],
                                    int(TX_ID),
                                    int(RX_ID),
                                    file_data[EXTS[0]][i],
                                    file_data[EXTS[1]][i],
                                    file_data[EXTS[2]][i],
                                    file_data[EXTS[3]][i],
                                    file_data[EXTS[4]]['PL_data'][i],
                                    tx_locs))

        return channels

    def import_file(self, filename, extension):

        matches = [i for i in range(len(EXTS)) if extension == EXTS[i]]
        if len(matches) == 0:  # Other potential files
            return None

        parse_func = getattr(self, PARSE_FUNCS[matches[0]])

        with open(filename) as f:
            lines = f.readlines()

        info = parse_func(lines)

        return info

    def parse_first(self, lines, header_len=5, num_cols=4):  # CIR DoD DoA
        cnt = header_len
        num_rx = int(lines[cnt])
        cnt += 1

        info = []

        for i in np.arange(num_rx) + 1:

            # User - path line
            read_vals = lines[cnt].split(' ')
            if int(read_vals[0]) != i:
                raise ValueError
            num_paths = int(read_vals[1])

            cnt += 1
            # Paths lines
            path_info = np.fromstring(''.join(lines[cnt:cnt + num_paths]), sep=' ', 
                                      dtype=np.single).reshape((num_paths, num_cols))
            info.append(path_info)
            cnt += num_paths

        return info

    def parse_second(self, lines, header_len=3, num_cols=6):  # PL File
        # Obtain header
        TX_str = lines[0][3:-3]
        RX_str = lines[1][3:-3]

        cnt = header_len
        info = np.fromstring(''.join(lines[cnt:]), sep=' ', 
                             dtype=np.single).reshape((-1, num_cols))

        info = {
                'PL_data': info,
                'TX_str': TX_str,
                'RX_str': RX_str
                }

        return info

    def parse_third(self, lines, header_len=21):  # Paths
        cnt = header_len
        num_rx = int(lines[cnt])
        cnt += 1

        info = []

        for i in np.arange(num_rx) + 1:

            # User - path line
            read_vals = lines[cnt].split(' ')
            if int(read_vals[0]) != i:
                raise ValueError
            num_paths = int(read_vals[1])

            # Summary
            cnt += 1
            # ch_sum = np.fromstring(lines[cnt], sep=' ', dtype=np.single) 
            # We don't need channel info

            # Paths
            path_info = []
            if num_paths > 0:
                cnt += 1
                for j in np.arange(num_paths):
                    num_interactions = int(lines[cnt].strip().split()[1]) 

                    cnt += 1
                    interactions = lines[cnt].strip(' \n').split('-')[:]

                    cnt += 1
                    interaction_pos = np.fromstring(''.join(lines[cnt:cnt + num_interactions + 2]), sep=' ',
                                                    dtype=np.single).reshape((num_interactions + 2, -1))

                    cnt += num_interactions + 2

                    path_info.append([interactions, interaction_pos])
            info.append(path_info)

        return info

    def directory_table(self, directory):
        list_files = glob.glob(os.path.join(os.path.abspath(directory), '*'))

        table_data = []

        for filename in list_files:
            file_dir = filename
            filename = os.path.split(filename)[-1]
            file_ids = filename.split('.')

            # Extension check
            if len(file_ids) != 5 or file_ids[4] != 'p2m':
                print('Skipping reading non-p2m file: %s' % (filename))
                continue

            file_scen = file_ids[0]
            file_type = file_ids[1]

            # TX ID
            tx_str = re.findall(r't(\d+)_(\d+)', file_ids[2])
            if len(tx_str[0]) != 2 or len(tx_str) != 1:
                # Problem with ID reading - The format is assumed to be 'txxx_xx'
                raise NotImplementedError
            tx_str = tx_str[0]
            file_tx_id = int(tx_str[0])
            file_tx_count = int(tx_str[1])

            # RX File ID
            rx_str = re.findall(r'r(\d+)', file_ids[3])
            if len(rx_str) != 1:
                # Problem with ID reading - The format is assumed to be 'rxxx'
                raise NotImplementedError
            file_rx_count = int(rx_str[0])

            table_data.append([file_type, file_tx_id, file_tx_count, 
                               file_rx_count, file_scen, file_dir])

        df = pd.DataFrame(table_data, columns=['Extension', 'TX_CNT', 'TX_ID', 
                                               'RX_ID', 'Scenario', 'Dir'])

        return df

    def add_Doppler_single_obj(self, bound_min, bound_max, vel_acc=[1, 0], 
                               vel_dir=np.array([1, 1, 1])):
        for channel in self.channels:
            channel.calc_Doppler(bound_min, bound_max, vel_acc, vel_dir)

    def add_Doppler(self, objects):
        self.Doppler = True
        
        for obj in objects:
            self.add_Doppler_single_obj(bound_min=obj['bounds'][0],
                                        bound_max=obj['bounds'][1],
                                        vel_acc=[obj['speed'], obj['acceleration']],
                                        vel_dir=np.array([cos(radians(obj['angle'])), 
                                                          sin(radians(obj['angle'])), 0]))

    def save_channels(self, filename):

        TX_ids = []
        ch_dicts = []
        loc_dicts = []
        for ch in self.channels:
            ch_dict, second_mat = ch.ch_dict(interacts=self.interacts)
            ch_dicts.append(ch_dict)
            loc_dicts.append(second_mat)
            
        scipy.io.savemat(os.path.join(self.save_folder, filename), 
                         {'channels': np.array(ch_dicts).T, 
                          'rx_locs': np.array(loc_dicts)})

    # def save_channels(self, save_folder, scene_idx=None, interacts=False, max_len=10000):
        
    #     if not os.path.exists(save_folder):
    #         os.mkdir(save_folder)
        
    #     TX_ids = []
    #     ch_dicts = []
    #     for ch in self.channels:
    #         ch_dict = ch.ch_dict(interacts=interacts)
    #         ch_dicts.append(ch_dict)
    #         TX_ids.append(ch_dict['TX_id_w'])
            
    #     for tx_id in set(TX_ids):
    #         save_ch = []
    #         for i in range(len(TX_ids)):
    #             if TX_ids[i] == tx_id:
    #                 save_ch.append(ch_dicts[i])
                        

    #         save_cnt = 0  
    #         num_ch = len(save_ch)                  
    #         # Dynamic and static scenarios
    #         while save_cnt<num_ch:
    #             next_cnt = min(num_ch, save_cnt+max_len)
    #             if scene_idx:
    #                 file = os.path.join(save_folder, 'scene_%i_TX%i_%i-%i.mat' % 
    #                                     (scene_idx, tx_id, save_cnt, next_cnt))
    #                 scipy.io.savemat(file, {'channels': save_ch[save_cnt:next_cnt]})
    #             else:
    #                 file = os.path.join(save_folder, 'TX%i_%i-%i.mat' %
    #                                     (tx_id, save_cnt, next_cnt))
    #                 scipy.io.savemat(file, {'channels': save_ch[save_cnt:next_cnt]})
    #             save_cnt = next_cnt


class Channel:
    def __init__(self, info_ID, TX_str, RX_str, TX_id, RX_id, 
                 info_ext_0, info_ext_1, info_ext_2, info_ext_3, info_ext_4, tx_locs):
        self.Doppler = False
        
        self.TX_ID = info_ID['TX_ID']
        self.RX_ID = info_ID['RX_ID']
        self.TX_ID_s = info_ID['TX_CNT']
        self.RX_ID_s = info_ext_4[0]
        self.RX_loc = info_ext_4[1:4]
        self.TX_id_w = TX_id
        self.RX_id_w = RX_id
        
        self.tx_loc_key = str(self.TX_ID) + '-' + str(self.TX_ID_s)

        self.dist = info_ext_4[4]
        self.PL = info_ext_4[5]
        self.TX_str = TX_str
        self.RX_str = RX_str

        self.num_paths = len(info_ext_0)
        
        self.paths = []
        seek_tx_loc = tx_locs[self.tx_loc_key] is None
        for i in range(self.num_paths):
            self.paths.append(Path(phase=info_ext_0[i][1],
                                ToA=info_ext_0[i][2],
                                power=info_ext_0[i][3],
                                doa_phi=info_ext_1[i][1],
                                doa_theta=info_ext_1[i][2],
                                dod_phi=info_ext_2[i][1],
                                dod_theta=info_ext_2[i][2],
                                interact=info_ext_3[i][0],
                                interact_locs=info_ext_3[i][1]))
            if seek_tx_loc:
                if info_ext_3[i][0][0] == 'Tx':
                    tx_locs[self.tx_loc_key] = info_ext_3[i][1][0]
                    seek_tx_loc = False
                    
        self.LOS = self.identify_LOS()

    def calc_Doppler(self, bound_min, bound_max, vel_acc, vel_dir):
        self.Doppler = True
        for path in self.paths:
            path.calc_Doppler(bound_min, bound_max, vel_acc, vel_dir)

    def identify_LOS(self):
        if self.num_paths == 0:
            return -1
        else:
            LOS = 0
            for path in self.paths:
                if path.LOS:
                    LOS = 1
                    break
            return LOS

    def __str__(self):
        print('TX ID: %i' % self.TX_ID)
        print('RX ID: %i' % self.TX_ID)

    def ch_dict(self, interacts=False):
        path_dict = {'phase': [],
                     'ToA': [],
                     'power': [],
                     'DoA_phi': [],
                     'DoA_theta': [],
                     'DoD_phi': [],
                     'DoD_theta': [],
                     'LOS': []
                     }
        # if interacts:
        #     interacts_dict = {'type': [],
        #                       'loc': []
        #                       }
        
        if self.Doppler:
            path_dict['Doppler_vel'] = []
            path_dict['Doppler_acc'] = []
        
        for path in self.paths:
            path_dict['phase'].append(path.phase)
            path_dict['ToA'].append(path.ToA)
            path_dict['power'].append(path.power)
            path_dict['DoA_phi'].append(path.doa_phi)
            path_dict['DoA_theta'].append(path.doa_theta)
            path_dict['DoD_phi'].append(path.dod_phi)
            path_dict['DoD_theta'].append(path.dod_theta)
            path_dict['LOS'].append(path.LOS)
            if self.Doppler:
                path_dict['Doppler_vel'].append(path.Doppler_vel)
                path_dict['Doppler_acc'].append(path.Doppler_acc)
            
            # if interacts:
            #     interacts_dict['type'].append(path.interact)
            #     interacts_dict['loc'].append(path.interact_locs)

        
        store_array = np.zeros((len(path_dict), self.num_paths), dtype=np.single)
        for i, key in enumerate(path_dict):
            store_array[i, :] = path_dict[key]

        for key in path_dict:
            path_dict[key] = np.array(path_dict[key])

        # if interacts:
        #     path_dict['interactions'] = {**interacts_dict}
        #     np.array(path_dict['interactions']['type'], dtype=object)
        #     np.array(path_dict['interactions']['loc'])
        
        second_mat = list(self.RX_loc) + [self.dist] + [self.PL]
        return {'p': store_array}, second_mat
class Path:
    def __init__(self, phase, ToA, power, doa_phi, doa_theta, dod_phi, dod_theta, interact, interact_locs):
        self.phase = phase
        self.ToA = ToA
        self.power = power
        self.doa_phi = doa_phi
        self.doa_theta = doa_theta
        self.dod_phi = dod_phi
        self.dod_theta = dod_theta
        self.interact = interact
        self.interact_locs = interact_locs
        self.LOS = self.identify_LOS()
        self.Doppler_vel = 0.
        self.Doppler_acc = 0.

    def identify_LOS(self):
        LOS_status = 1
        for i in range(len(self.interact)):
            if self.interact[i] in ['R', 'D',  'DS', 'T', 'F', 'X']:
                LOS_status = 0
                break
            elif self.interact[i] in ['Fx', 'Rx', 'Tx']:
                pass
            else:
                raise NotImplementedError
        return LOS_status == 1

    def calc_Doppler(self, bound_min, bound_max, vel_acc, vel_dir):
        for i in range(len(self.interact)):
            if np.all(np.logical_and(bound_max >= self.interact_locs[i], self.interact_locs[i] >= bound_min)):

                if i > 0:
                    self.arrival_vec = self.interact_locs[i - 1] - self.interact_locs[i]
                    self.arrival_vec /= np.sqrt(np.sum(self.arrival_vec ** 2))
                else:
                    self.arrival_vec = np.zeros(3)
                if i < len(self.interact) - 1:
                    self.departure_vec = self.interact_locs[i + 1] - self.interact_locs[i]
                    self.departure_vec /= np.sqrt(np.sum(self.departure_vec ** 2))
                else:
                    self.departure_vec = np.zeros(3)

                self.Doppler_vel += np.asscalar(np.dot((self.arrival_vec + self.departure_vec), vel_acc[0] * vel_dir))
                self.Doppler_acc += np.asscalar(np.dot((self.arrival_vec + self.departure_vec), vel_acc[1] * vel_dir))
