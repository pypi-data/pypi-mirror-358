from typing import List
import numpy as np

from buffer_mocks import BUFFER_MOCKS

import mindrove
from mindrove.board_shim import BoardShim, MindRoveInputParams, BoardIds
from mindrove.data_filter import DataFilter, FilterTypes, DetrendOperations

import platform 
import argparse

def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue

BoardShim.enable_dev_board_logger()

if platform.system() == "Windows":
    HOSTNAME = "::1"
else:
    HOSTNAME = "::ffff:127.0.0.1"

parser = argparse.ArgumentParser()

parser.add_argument("--board-id", type=int, choices=[x.value for x in list(BoardIds) if  x>= 0], help="Id of the target Board to test", required=False, default=0)
parser.add_argument('--data', type=str, help='What kind of communication protocol to test with data transfer', required=True,
                        default="wua2", choices=BUFFER_MOCKS.keys())
parser.add_argument('--timeout', type=check_positive, help='Number of seconds to wait for data, before throwing error', required=False,
                        default=2)
args = parser.parse_args()

board_id = args.board_id#BoardIds.MINDROVE_WIFI_BOARD.value

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

    expected_data = BUFFER_MOCKS[args.data](k=i)

    exg_channels = data[board_shim.get_exg_channels(board_id)][:,0]
    resistance_channels = data[board_shim.get_resistance_channels(board_id)][:,0]
    battery_channel = data[board_shim.get_battery_channel(board_id)][0]
    trigger = data[board_shim.get_other_channels(board_id)[0]][0]
    trigger_physical = data[board_shim.get_other_channels(board_id)[2]][0]
    trigger_auto = data[board_shim.get_other_channels(board_id)[3]][0]
    accel_channels = data[board_shim.get_accel_channels(board_id)][:,0]
    gyro_channels = data[board_shim.get_gyro_channels(board_id)][:,0]
    package_num_channel = data[board_shim.get_package_num_channel(board_id)][0]

    ## check the actual values 
    assert np.array_equal(exg_channels, expected_data["exg_channels"]),               f"GET-DATA - Exg_channels do not match for board {i} with ssid {mock_ssids[i]}, got {exg_channels}, and expected {expected_data['exg_channels']}"
    assert np.array_equal(resistance_channels, expected_data["resistance_channels"]), f"GET-DATA - resistance_channels do not match for board {i} with ssid {mock_ssids[i]}, got {resistance_channels}, and expected {expected_data['resistance_channels']}"
    assert battery_channel == expected_data["battery_channel"],                       f"GET-DATA - battery_channel do not match for board {i} with ssid {mock_ssids[i]}, got {battery_channel}, and expected {expected_data['battery_channel']} "
    assert trigger == expected_data["trigger"],                                       f"GET-DATA - trigger do not match for board {i} with ssid {mock_ssids[i]}, got {trigger}, and expected {expected_data['trigger']}"
    
    if "trigger_physical" in expected_data.keys():
        assert trigger_physical == expected_data["trigger_physical"],                     f"GET-DATA - trigger_physical do not match for board, got {trigger_physical}, and expected {expected_data['trigger_physical']}"
    
    if "trigger_auto" in expected_data.keys():
        assert trigger_auto == expected_data["trigger_auto"],                             f"GET-DATA - trigger_auto do not match for board, got {trigger_auto}, and expected {expected_data['trigger_auto']}"
    

    assert np.array_equal(accel_channels, expected_data["accel_channels"]),           f"GET-DATA - accel_channels do not match for board {i} with ssid {mock_ssids[i]}, got {accel_channels}, and expected {expected_data['accel_channels']}"
    assert np.array_equal(gyro_channels, expected_data["gyro_channels"]),             f"GET-DATA - gyro_channels do not match for board {i} with ssid {mock_ssids[i]}, got {gyro_channels}, and expected {expected_data['gyro_channels']}"
    assert package_num_channel == expected_data["package_num_channel"],               f"GET-DATA - package_num_channel do not match for board {i} with ssid {mock_ssids[i]}, got {package_num_channel}, and expected {expected_data['package_num_channel']}"
    
    print(f"GET-DATA - Board with ssid={mock_ssids[i]} PASSED GET_DATA CHECK")




board_shims[0].release_all_sessions()
    