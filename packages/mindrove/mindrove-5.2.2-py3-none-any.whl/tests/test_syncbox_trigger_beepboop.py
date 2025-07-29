"""
Install dependencies for this test: 

From the /tests folder, run the following: 

pip install -r requirements.txt 


Instructions to use: 

This test is for testing the beep boop trigger. Currently one device is connected to, from the syncbox. 
The test is based on human-evaluation, thus the test shows a graph with the values of the beep/boop trigger channel for the particular device.
This test file sends every 5 second a beep instruction to the device. 
If the PC -> sbox -> device -> sbox -> PC line is intact, the tester should see the spikes on the graph. 


Usage:

python test_syncbox_trigger_beepboop.py --mac-address <device_mac_addr> 

Example:

python test_syncbox_trigger_beepboop.py --mac-address d87ac0

"""

import argparse
import logging

import pyqtgraph as pg
from mindrove.board_shim import BoardShim, MindRoveInputParams, BoardIds, MindroveConfigMode
from mindrove.data_filter import DataFilter, FilterTypes, DetrendOperations
from pyqtgraph.Qt import QtGui, QtCore

import time 
import threading
import numpy as np 

def send_config(board_shim : BoardShim):

    while True:

        board_shim.config_board(MindroveConfigMode.BEEP)
        time.sleep(1)
        board_shim.config_board(MindroveConfigMode.BOOP)
        
        time.sleep(5)


class Graph:
    def __init__(self, board_shim):
        self.board_id = board_shim.get_board_id()
        self.board_shim = board_shim
        self.exg_channels = BoardShim.get_exg_channels(self.board_id)
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        
        self.beepboop_channel = BoardShim.get_other_channels(self.board_id)[0]

        self.update_speed_ms = 50
        self.window_size = 50
        self.num_points = self.window_size * self.sampling_rate

        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsWindow(title='MindRove Plot', size=(800, 600))

        self._init_timeseries()
        self.last_val = -1


        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(self.update_speed_ms)
        QtGui.QApplication.instance().exec_()

    def _init_timeseries(self):
        self.plots = list()
        self.curves = list()
        i = 0
        #for i in range(len(self.exg_channels)):
        p = self.win.addPlot(row=i, col=0)
        p.showAxis('left', False)
        p.setMenuEnabled('left', False)
        p.showAxis('bottom', False)
        p.setMenuEnabled('bottom', False)
        if i == 0:
            p.setTitle('TimeSeries Plot')
        self.plots.append(p)
        curve = p.plot()
        self.curves.append(curve)

    def update(self):
        data = self.board_shim.get_current_board_data(self.num_points)
        count = 0
        channel = self.beepboop_channel
        #for count, channel in enumerate(self.exg_channels):
            # plot timeseries
        
        d = data[channel].tolist()
        self.curves[count].setData(d)

        d = np.array(d)
        non_zero = d[d!=0]
        if len(non_zero) > 0 and d[d!=0][-1] != self.last_val:
            self.last_val = d[d!=0][-1]
            print(self.last_val)

        self.app.processEvents()


def main():
    BoardShim.enable_dev_board_logger()
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    # use docs to check which parameters are required for specific board, e.g. for Cyton - set serial port
    parser.add_argument('--mac-address', type=str, help='mac address', required=True, default='')
    args = parser.parse_args()

    params = MindRoveInputParams()
    params.mac_address = args.mac_address

    board_shim = BoardShim(BoardIds.MINDROVE_SYNCBOX_BOARD, params)


    try:
        board_shim.prepare_session()
        board_shim.start_stream(450000)

        threading.Thread(target=send_config, args=(board_shim, ), daemon=True).start()

        Graph(board_shim)
    except BaseException:
        logging.warning('Exception', exc_info=True)
    finally:
        logging.info('End')
        if board_shim.is_prepared():
            logging.info('Releasing session')
            board_shim.release_session()


if __name__ == '__main__':
    main()



