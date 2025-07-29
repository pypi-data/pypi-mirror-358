from typing import List
import numpy as np

import argparse
import time 

import mindrove
from mindrove.board_shim import BoardShim, MindRoveInputParams, BoardIds
from mindrove.data_filter import DataFilter, FilterTypes, DetrendOperations
from buffer_mocks import BUFFER_MOCKS

def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue

BoardShim.enable_dev_board_logger()

parser = argparse.ArgumentParser()

parser.add_argument("--board-id", type=int, choices=[x.value for x in list(BoardIds) if  x>= 0], help="Id of the target Board to test", required=False, default=0)
parser.add_argument('--data', type=str, help='What kind of communication protocol to test with data transfer', required=True,
                        default="wua2", choices=BUFFER_MOCKS.keys())
parser.add_argument('--timeout', type=check_positive, help='Number of seconds to wait for data, before throwing error', required=False,
                        default=2)
args = parser.parse_args()

board_id = args.board_id#BoardIds.MINDROVE_WIFI_BOARD.value


param = MindRoveInputParams()
param.ip_address = "127.0.0.1"
param.ip_port = 5000
board_shim = BoardShim(board_id, param)
board_shim.prepare_session()
board_shim.start_stream()


data = np.array([[]])
t1 = time.time()
got_data = False

while data.shape[1] < 1 and time.time()-t1 < args.timeout:
    data = board_shim.get_current_board_data(1)

assert data.shape[1] > 0, f"No incoming data after {args.timeout} seconds"

expected_data = BUFFER_MOCKS[args.data]()

exg_channels = data[board_shim.get_exg_channels(board_id)][:,0]
resistance_channels = data[board_shim.get_resistance_channels(board_id)][:,0]
battery_channel = data[board_shim.get_battery_channel(board_id)][0]
trigger = data[board_shim.get_other_channels(board_id)[0]][0]
accel_channels = data[board_shim.get_accel_channels(board_id)][:,0]
gyro_channels = data[board_shim.get_gyro_channels(board_id)][:,0]
package_num_channel = data[board_shim.get_package_num_channel(board_id)][0]

print(f"Package number: {package_num_channel}")

## check the actual values 
#assert np.array_equal(exg_channels, expected_data["exg_channels"]),               f"GET-DATA - Exg_channels do not match for board {i} with ssid {mock_ssids[i]}, got {exg_channels}, and expected {expected_data['exg_channels']}"
assert np.array_equal(resistance_channels, expected_data["resistance_channels"]), f"GET-DATA - resistance_channels do not match for board {i} with ssid {mock_ssids[i]}, got {resistance_channels}, and expected {expected_data['resistance_channels']}"
assert battery_channel == expected_data["battery_channel"],                       f"GET-DATA - battery_channel do not match for board {i} with ssid {mock_ssids[i]}, got {battery_channel}, and expected {expected_data['battery_channel']}"
assert trigger == expected_data["trigger"],                                       f"GET-DATA - trigger do not match for board {i} with ssid {mock_ssids[i]}, got {trigger}, and expected {expected_data['trigger']}"
assert np.array_equal(accel_channels, expected_data["accel_channels"]),           f"GET-DATA - accel_channels do not match for board {i} with ssid {mock_ssids[i]}, got {accel_channels}, and expected {expected_data['accel_channels']}"
assert np.array_equal(gyro_channels, expected_data["gyro_channels"]),             f"GET-DATA - gyro_channels do not match for board {i} with ssid {mock_ssids[i]}, got {gyro_channels}, and expected {expected_data['gyro_channels']}"
assert package_num_channel == expected_data["package_num_channel"],               f"GET-DATA - package_num_channel do not match for board {i} with ssid {mock_ssids[i]}, got {package_num_channel}, and expected {expected_data['package_num_channel']}"
    

print(f"{args.data} board PASSED GET_DATA CHECK")


board_shim.release_all_sessions()
    