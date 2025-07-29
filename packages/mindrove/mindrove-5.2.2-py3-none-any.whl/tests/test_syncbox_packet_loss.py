from typing import List
import numpy as np

import argparse
import time 

import mindrove
from mindrove.board_shim import BoardShim, MindRoveInputParams, BoardIds
from mindrove.data_filter import DataFilter, FilterTypes, DetrendOperations

import threading

MEASUREMENT_TIME = 5 * 60 # in seconds 


BoardShim.enable_dev_board_logger()

timeout = 20


total_packets = {}
total_loss = {}

start_logging = False

def board_logger(board_ssid : str):

    global total_loss
    global total_packets
    global start_logging

    total_loss[board_ssid] = 0
    total_packets[board_ssid] = 0

    board_id = BoardIds.MINDROVE_SYNCBOX_BOARD.value

    param = MindRoveInputParams()
    param.mac_address = board_ssid

    board_shim = BoardShim(board_id, param)
    board_shim.prepare_session()
    board_shim.start_stream()


    data = np.array([[]])
    t1 = time.time()
    got_data = False

    while data.shape[1] < 1 and time.time()-t1 < 20:
        data = board_shim.get_current_board_data(1)

    assert data.shape[1] > 0, f"No incoming data after {20} seconds"

    time.sleep(10)

    t1 = time.time()

    last_packet_id = -1


    packet_idx = board_shim.get_package_num_channel(board_id)

    while not start_logging:
        pass

    while time.time() - t1 < MEASUREMENT_TIME:

        data = board_shim.get_board_data()
        
        if data.shape[1] < 1:
            continue

        if last_packet_id == -1:
            last_packet_id = data[packet_idx, 0]-1 # we simulate previous packet for code clarity 

        total_packets[board_ssid] += data.shape[1]

        for drdy in data[packet_idx]:

            total_loss[board_ssid] += abs(drdy - last_packet_id - 1) # abs is needed in case we get a negative number. Negative number can occur when two drdy values are the same after each other. 
            last_packet_id = drdy


        time.sleep(1)

    
    board_shim.release_all_sessions()
    

# Devices: 
    #005 - 40f20c 
    #EMG_FELIRATOS: 0b088c 
    #FLOW - b74354    
    #FLOW_SPO2 - 351c60

    ## ARC - d9d560

    ## MIndrove matricas (hunoros) - d9e914

    #### "a39bd0"

    # BRN - #d87ac0

ssids = [
    "d9d560", # ARC 
    "d87ac0", # BRN
    "351c60", # SPO2_FLOW
    "b74354" # FLOW
]
boards = [threading.Thread(target=board_logger, args=(x,), daemon=True) for x in ssids]

[board.start() for board in boards]

time.sleep(5)

start_logging = True
tt1 = time.time()

while time.time() - tt1 < MEASUREMENT_TIME:
    print(f"Elapsed time: {time.time() - tt1}       \r", end="")
    time.sleep(1)

for bssid in ssids:
    print()
    print()
    print(f"Data loss for : {bssid}")
    print(f"Total elapsed time is: {MEASUREMENT_TIME} seconds ")
    print(f"Total packets got : {total_packets[bssid]}")
    print(f"Total lost packets: {total_loss[bssid]} ")
    print("-------------------")
    print("-------------------")
    print(f"Loss percentage : {(total_loss[bssid]*100) / (total_packets[bssid]+total_loss[bssid])}%")
    print("-------------------")
    print("-------------------")
