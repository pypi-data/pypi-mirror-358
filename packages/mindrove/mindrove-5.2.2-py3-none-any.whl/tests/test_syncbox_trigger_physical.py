"""
Install dependencies for this test: 

From the /tests folder, run the following: 

pip install -r requirements.txt 


Instructions to use: 

This test is for testing the input physical trigger. Currently one device is connected to, from the syncbox. 
The test is based on human-evaluation, thus the test shows a graph with the values of the physical trigger channel for the particular device.
If the phy_trigger -> sbox -> device -> sbox -> PC line is intact, the tester should see the spikes on the graph. 


Usage:

python test_syncbox_trigger_physical.py --mac-address <device_mac_addr> 

"""

import argparse
import logging

import pyqtgraph as pg
from mindrove.board_shim import BoardShim, MindRoveInputParams, BoardIds
from mindrove.data_filter import DataFilter, FilterTypes, DetrendOperations
from pyqtgraph.Qt import QtGui, QtCore


class Graph:
    def __init__(self, board_shim):
        self.board_id = board_shim.get_board_id()
        self.board_shim = board_shim
        self.exg_channels = BoardShim.get_exg_channels(self.board_id)
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        
        self.physical_trigger_channel = BoardShim.get_other_channels(self.board_id)[2]

        self.update_speed_ms = 50
        self.window_size = 4
        self.num_points = self.window_size * self.sampling_rate

        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsWindow(title='MindRove Plot', size=(800, 600))

        self._init_timeseries()

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
        channel = self.physical_trigger_channel
        #for count, channel in enumerate(self.exg_channels):
            # plot timeseries
        
        self.curves[count].setData(data[channel].tolist())

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



