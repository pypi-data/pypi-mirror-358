import numpy as np

def mock_WUA2_data(k=0) -> dict:

    CHANNEL_LSB = 0.045
    GYRO_LSB    = 0.01526
    ACC_LSB     = 0.061035 * 1e-3
    res_dict = {}

    i = 200*k
    
    res_dict["exg_channels"] = (np.array(range(i, i+8), dtype=np.float64))*CHANNEL_LSB
    i = i+8

    res_dict["resistance_channels"] =  (np.array(range(i, i+10), dtype=np.float64))
    i = i+10

    res_dict["battery_channel"] = ((((float(i)))/1000.0)-2.8)*100 / 1.45; 
    i = i+1

    res_dict["trigger"] =  0.0
    i = i+1

    res_dict["accel_channels"] =  (np.array(range(i, i+3), dtype=np.float64)) * ACC_LSB
    i = i+3

    res_dict["gyro_channels"] =  (np.array(range(i, i+3), dtype=np.float64)) * GYRO_LSB
    i = i+3

    res_dict["package_num_channel"] = float(i)

    return res_dict


def mock_2_MES_data(k=0) -> dict: 

    CHANNEL_LSB = 0.045
    GYRO_LSB    = 0.01526
    ACC_LSB     = 0.061035 * 1e-3
    res_dict = {}

    i = 200*k 

    res_dict["exg_channels"] = (np.array(range(i, i+8), dtype=np.float64))*CHANNEL_LSB
    i = i+8

    res_dict["resistance_channels"] =  (np.zeros(shape=(10,), dtype=np.float64))
    
    res_dict["battery_channel"] = 99#float(i)
    i = i+1

    res_dict["trigger"] =  0.0
    i = i+1

    # here we do not increase i ... 
    res_dict["trigger_auto"] =  13.0
    res_dict["trigger_physical"] =  1.0

    res_dict["accel_channels"] =  (np.array(range(i, i+3), dtype=np.float64)) * ACC_LSB
    i = i+3

    res_dict["gyro_channels"] =  (np.array(range(i, i+3), dtype=np.float64)) * GYRO_LSB
    i = i+3

    res_dict["package_num_channel"] = float(i)

    return res_dict

def mock_3_IMP_data(k=0) -> dict: 

    CHANNEL_LSB = 0.045
    GYRO_LSB    = 0.01526
    ACC_LSB     = 0.061035 * 1e-3

    res_dict = {}

    i = 200*k 

    res_dict["exg_channels"] = (np.zeros(shape=(8,), dtype=np.float64))
    
    res_dict["resistance_channels"] =  (np.array(range(i, i+10), dtype=np.float64))
    
    i += 10
    
    res_dict["battery_channel"] = 99#float(i)

    i += 1
    
    res_dict["accel_channels"] =  (np.zeros(shape=(3,), dtype=np.float64)) * ACC_LSB

    res_dict["gyro_channels"] =  (np.zeros(shape=(3,), dtype=np.float64)) * GYRO_LSB

    res_dict["package_num_channel"] = float(i)
    i = i+1

    res_dict["trigger"] =  0.0
    

    return res_dict

def mock_4_MES_data(k=0) -> dict: 

    CHANNEL_LSB = 0.045
    GYRO_LSB    = 0.01526
    ACC_LSB     = 0.061035 * 1e-3
    res_dict = {}

    i = 200*k 

    res_dict["exg_channels"] = (np.array(range(i, i+8), dtype=np.float64))*CHANNEL_LSB
    i = i+8

    res_dict["resistance_channels"] =  (np.zeros(shape=(10,), dtype=np.float64))
    
    res_dict["battery_channel"] = 99#float(i)
    i = i+1

    res_dict["trigger"] =  0.0
    i = i+1

    # here we do not increase i ... 
    res_dict["trigger_auto"] =  13.0
    res_dict["trigger_physical"] =  1.0

    res_dict["accel_channels"] =  (np.array(range(i, i+3), dtype=np.float64)) * ACC_LSB
    i = i+3

    res_dict["gyro_channels"] =  (np.array(range(i, i+3), dtype=np.float64)) * GYRO_LSB
    i = i+3

    res_dict["ppg_channels"] = np.array([90,100], dtype=np.float64)


    res_dict["package_num_channel"] = float(i)

    return res_dict

def mock_5_MES_data(k=0) -> dict: 

    CHANNEL_LSB = 0.045
    GYRO_LSB    = 0.01526
    ACC_LSB     = 0.061035 * 1e-3
    res_dict = {}

    i = 200*k 

    res_dict["exg_channels"] = (np.array(range(i, i+8), dtype=np.float64))*CHANNEL_LSB
    i = i+8

    res_dict["resistance_channels"] =  (np.zeros(shape=(10,), dtype=np.float64))
    
    res_dict["battery_channel"] = 99#float(i)
    i = i+1

    res_dict["trigger"] =  0.0
    i = i+1

    # here we do not increase i ... 
    res_dict["trigger_auto"] =  13.0
    res_dict["trigger_physical"] =  1.0

    res_dict["accel_channels"] =  (np.array(range(i, i+3), dtype=np.float64)) * ACC_LSB
    i = i+3

    res_dict["gyro_channels"] =  (np.array(range(i, i+3), dtype=np.float64)) * GYRO_LSB
    i = i+3

    res_dict["ppg_raw_channels"] = np.array([90,100, 110], dtype=np.float64)


    res_dict["package_num_channel"] = float(i)

    return res_dict
###########################
###########################
###########################
BUFFER_MOCKS = {
    "wua2": mock_WUA2_data,
    "2_mes" : mock_2_MES_data,
    "3_imp" : mock_3_IMP_data,
    "4_mes" : mock_4_MES_data,
    "5_mes" : mock_5_MES_data
}