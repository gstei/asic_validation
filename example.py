import time
import matplotlib.pyplot as plt

import nidaqmx
import numpy as np
# import SMU drivers
from Drivers.pxie_4141_main.PXIe4141 import PXIe4141
# import Power supply drivers
from Drivers.e3631a_main.E3631A import E3631A
# import Oscilloscope drivers
from Drivers.pxi_5142_main.PXI_5142 import PXI_5142




import logging

logger = logging.getLogger('') # Logger is labled as root
logger.setLevel(logging.INFO)

# Add File to Logger 
fh = logging.FileHandler('TestLog.log','w')
fh.setLevel(logging.INFO)

# Add Console output to Logger
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Set the format for the logfile and console output
formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)

logger.info("Log File created")

# setupt smu
if 0:
    smu0 = PXIe4141('PXI2Slot3', name = 'smu', selftest=True,reset=True,log=True)

    smu0.set_aperture(1, 0.001, 2)
    smu0.configure_channel_vdc(1, 2.0, 1.0, -0.001, 0.0025)
    smu0.enable(1, True)

    smu0.measure(1)
    smu0.set_voltage(1, 2.0, True)
    smu0.measure(1)
    smu0.set_voltage(1, 3.0, True)
    smu0.measure(1)
    smu0.enable(1, False)

    smu0.set_aperture(0, 0.001, 2)
    smu0.set_aperture(1, 0.001, 2)
    smu0.configure_channel_vdc(0, 2.0, 1.0, -0.001, 0.0025)
    smu0.configure_channel_idc(1, 0.002, 0.001, -2, 2)
    smu0.enable(0, True)
    smu0.enable(1, True)

    smu0.measure(0)
    smu0.measure(1)
    smu0.set_voltage(0, 2.0, True)
    smu0.set_current(1, 0.002, True)
    smu0.measure(0)
    smu0.measure(1)
    smu0.enable(0, False)
    smu0.enable(1, False)


#power supply
if 0:
    PS = E3631A(address=5)

    PS.set_6V(2,0.4)
    PS.set_P25V(5)
    PS.set_N25V(-3)

if 1: 
    import matplotlib.pyplot as plt
    
    sc0 = PXI_5142('PXI2Slot7', name = 'scope', selftest=True, reset=True, log=True)
    
    vrange = 2.0
    freq_to_meas = 1000
    nr_of_periods = 10
    num_records = 100
    #amplitude_to_meas is the peak voltage (not peak to peak)
    sc0.configure_simple_ac(amplitude_to_meas=1.1, freq_to_meas=10e3, nr_of_periods=3, num_records=1, sample_rate=10e6,hysteresis=None)
    
    
    sc0.wait_until_acquisition_done(1)
    
    record_number = 0
    [t, waveform] = sc0.measure(channel_nr=0, record_number=record_number)
    plt.plot(t, waveform)
    plt.grid()
    plt.show()




PS.en_output()
time.sleep(1)


[V,I] = PS.meas_6V()
print("Voltage = "+ str(V) + "V, Current = " + str(I*1000)+"mA")
[V,I] = PS.meas_P25V()
print("Voltage = "+ str(V) + "V, Current = " + str(I*1000)+"mA")
[V,I] = PS.meas_N25V()
print("Voltage = "+ str(V) + "V, Current = " + str(I*1000)+"mA")