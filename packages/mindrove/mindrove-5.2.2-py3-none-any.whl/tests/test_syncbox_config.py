from typing import List
import numpy as np
import time 
import mindrove
import platform

from mindrove.board_shim import BoardShim, MindRoveInputParams, BoardIds
from mindrove.data_filter import DataFilter, FilterTypes, DetrendOperations

BoardShim.enable_dev_board_logger()


if platform.system() == "Windows":
    HOSTNAME = "::1"
else:
    HOSTNAME = "::ffff:127.0.0.1"

board_id = BoardIds.MINDROVE_SYNCBOX_BOARD.value

mock_ssids = [
    "abcdef",
    "ghijkl",
    "mnopqr"
]


params : List[MindRoveInputParams] = []

for ssid in mock_ssids:
    params.append(MindRoveInputParams())
    params[-1].mac_address = ssid
    params[-1].ip_address = HOSTNAME

board_shims : List[BoardShim] = []

for param in params: 

    board_shims.append(BoardShim(board_id, param))

    board_shims[-1].prepare_session()
    board_shims[-1].start_stream()


for i, board_shim in enumerate(board_shims): 

    data = np.array([[]])
    while data.shape[1] < 1:
        data = board_shim.get_current_board_data(1)

    got_trigger = data[board_shim.get_other_channels(board_id)[0]][0]
    assert got_trigger == 0.0, f"Error on the initial trigger value, expected 0, got {got_trigger}"

all_params = MindRoveInputParams()
all_params.ip_address = HOSTNAME
all_boards = BoardShim(board_id, all_params)
all_boards.prepare_session()
all_boards.start_stream()
all_boards.config_board(mindrove.MindroveConfigMode.BEEP)

time.sleep(1)

### We clean up the buffer 
for i, board_shim in enumerate(board_shims): 

    data = board_shim.get_board_data()

## We check wether every board has the new trigger 
for i, board_shim in enumerate(board_shims): 

    data = np.array([[]])
    while data.shape[1] < 1:
        data = board_shim.get_current_board_data(1)

    got_trigger = data[board_shim.get_other_channels(board_id)[0]][0]
    assert got_trigger == 1.0, f"Error on the configured trigger value, expected 1.0, got {got_trigger}"

    print(f"Board with ssid={mock_ssids[i]} PASSED CONFIG CHECK")

    #board_shim.stop_stream()
    #board_shim.release_session()


#all_boards.stop_stream()
all_boards.release_all_sessions()