from typing import List
import numpy as np

import argparse
import time 

import mindrove
from mindrove.board_shim import BoardShim, MindRoveInputParams, BoardIds
from mindrove.data_filter import DataFilter, FilterTypes, DetrendOperations

MEASUREMENT_TIME = 5 * 60 # in seconds 


BoardShim.enable_dev_board_logger()

parser = argparse.ArgumentParser()

timeout = 20

board_id = BoardIds.MINDROVE_WIFI_BOARD.value

param = MindRoveInputParams()

board_shim = BoardShim(board_id, param)
board_shim.prepare_session()
board_shim.start_stream()


data = np.array([[]])
t1 = time.time()
got_data = False

while data.shape[1] < 1 and time.time()-t1 < 20:
    data = board_shim.get_current_board_data(1)

assert data.shape[1] > 0, f"No incoming data after {20} seconds"


t1 = time.time()

last_packet_id = -1

packet_idx = board_shim.get_package_num_channel(board_id)

total_packets = 0
total_loss = 0

while time.time() - t1 < MEASUREMENT_TIME:

    print(f"Elapsed time: {time.time() - t1}       \r", end="")
    data = board_shim.get_board_data()
    
    if data.shape[1] < 1:
        continue

    if last_packet_id == -1:
        last_packet_id = data[packet_idx, 0]-1 # we simulate previous packet for code clarity 

    total_packets += data.shape[1]

    for drdy in data[packet_idx]:

        total_loss += abs(drdy - last_packet_id - 1) # abs is needed in case we get a negative number. Negative number can occur when two drdy values are the same after each other. 
        last_packet_id = drdy


    time.sleep(1)

print()
print(f"Total elapsed time is: {MEASUREMENT_TIME} seconds ")
print(f"Total packets got : {total_packets}")
print(f"Total lost packets: {total_loss} ")
print("-------------------")
print("-------------------")
print(f"Loss percentage : {(total_loss*100) / (total_packets+total_loss)}%")
print("-------------------")
print("-------------------")

board_shim.release_all_sessions()
    