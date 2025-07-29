from typing import List
import numpy as np
import time 
import argparse

import mindrove
from mindrove.board_shim import BoardShim, MindRoveInputParams, BoardIds
from mindrove.data_filter import DataFilter, FilterTypes, DetrendOperations


BoardShim.enable_dev_board_logger()


parser = argparse.ArgumentParser()

parser.add_argument("--board-id", type=int, choices=[x.value for x in list(BoardIds) if  x>= 0], help="Id of the target Board to test ")
parser.add_argument('--data', type=str, help='-- Not used, only for cross-compatibility', required=False,
                    default="wua2")
parser.add_argument('--config', type=str, help='-- Not used, only for cross-compatibility', required=False, 
                    default="wua2")
args = parser.parse_args()

board_id = args.board_id#BoardIds.MINDROVE_WIFI_BOARD.value



param = MindRoveInputParams()
param.ip_address = "127.0.0.1"
param.ip_port = 5000
board_shim = BoardShim(board_id, param)
board_shim.prepare_session()
board_shim.start_stream()


data = np.array([[]])
while data.shape[1] < 1:
    data = board_shim.get_current_board_data(1)

got_trigger = data[board_shim.get_other_channels(board_id)[0]][0]

assert got_trigger == 0.0, f"Error on the initial trigger value, expected 0, got {got_trigger}"


board_shim.config_board(mindrove.MindroveConfigMode.BEEP)

time.sleep(1)

data = board_shim.get_board_data()

## We check wether every board has the new trigger 

data = np.array([[]])
while data.shape[1] < 1:
    data = board_shim.get_current_board_data(1)

got_trigger = data[board_shim.get_other_channels(board_id)[0]][0]
assert got_trigger == 1.0, f"Error on the configured trigger value, expected 1.0, got {got_trigger}"

print(f"Board PASSED CONFIG CHECK")

board_shim.release_all_sessions()

