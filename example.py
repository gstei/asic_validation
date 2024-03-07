import time
import matplotlib
import matplotlib.pyplot as plt

import numpy as np
# import SMU drivers
from Drivers.pxie_4141_main.PXIe4141 import PXIe4141
# import Power supply drivers
from Drivers.e3631a_main.E3631A import E3631A
# import Oscilloscope drivers
from Drivers.pxi_5142_main.PXI_5142 import PXI_5142
import niscope
# import Signal generator
from Drivers.pxi_5402_main.PXI_5402 import PXI_5402

import nitclk

import logging

import PlotData

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
print("This is a simple example script which tests if all the instrumments are working correctly:\n" +
      "To make sure everything is working make sure that all the cardas are in the right place:\n"
      " 1. PXI Controller PXIe-8881 is in slot1\n"+
      " 2. PXI-Modul für die multifunkions I/O PXIe-6363 is in slot2\n"+
      " 3. SMU PXIe-4141 is in slot3\n"+
      " 4. Oscilloscope PXIe-5142 is in slot8\n"+
      " 5. Signal generator PXIe-5402 is in slot9\n"
      )
print("When you are not sure open the Utility manager in the Hardware")
print("Make the following connections for the self test:\n"+
      " 1: Connect BNC cable from signal generator 0 to Oscilloscope probe 1\n"+
      " 2: Connect Agilent E3631A With PXIe-8881\n"+
      " 3: Connect IO baord with PXIe-6363\n"+
      " 4. Connect SMU0 with OSC channel 2\n"+
      " 5. Connect Oscillscope probe 3 with GPIO boards\n")

# input("Press enter to continue")

if 1:
    print("Initialize SMU")
    smu0 = PXIe4141('PXI2Slot3', name = 'smu', selftest=True,reset=True,log=True)
    print("Set speed of SMU channel")
    smu0.set_aperture(1, 0.001, 2)
    print("Set one volt on output of SMU channel 1")
    smu0.configure_channel_vdc(0, 2.0, 1.0, -0.001, 0.0025)
    print("enable the channel")
    smu0.enable(0, True)

    if abs(1-smu0.measure(0)[0])>0.01:
        print("SMU does not work")
    smu0.set_voltage(0, 2.0, True)
    smu0.measure(0)
    smu0.set_voltage(0, 3.0, True)
    smu0.measure(0)
    smu0.enable(0, False)

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
    PS.en_output()

#signal generator
if 1:
    fg0 = PXI_5402('PXI2Slot9', name = 'fgen', selftest=False, reset=True, log=False)
    fg0.set_load_impedance(9999999999.0)#1e99)
    fg0.set_output_impedance(50.0)
    fg0.configure_sin(1.0,1000,0.5,0.0) # 1V Peak_to_Peak output, offset 0.5V (min out = 0V, max out = 1V)
    fg0.configure_rect(1.0,2, 0.5,0)
    fg0.enable(True)
    print("On the signal generator one should know see the signal press enter to continue")
    # sc0 = PXI_5142('PXI2Slot7', name = 'scope', selftest=True, reset=True, log=True)
    if 0:
        resource_name="PXI2Slot8"
        channels=0
        options=''
        length=100
        voltage=1
        with niscope.Session(resource_name=resource_name, options=options) as session:
            session.configure_vertical(range=voltage, coupling=niscope.VerticalCoupling.AC)
            session.configure_chan_characteristics(input_impedance=1000000.0, max_input_frequency=100e3) #self.NISCOPE_VAL_20MHZ_MAX_INPUT_FREQUENCY
            session.configure_horizontal_timing(min_sample_rate=1e4, min_num_pts=length, ref_position=0.0, num_records=1, enforce_realtime=True)
            waveforms = session.channels[channels].read(num_samples=length)
            for i in range(len(waveforms)):
                print('Waveform {0} information:'.format(i))
                print(str(waveforms[i]) + '\n\n')
        array_n=np.array(waveforms[0].samples.obj)*100000

        plt.plot(array_n.astype(int))
        plt.xlabel('Index')
        plt.ylabel('Value')
        plt.title('Plot of Numbers')
        plt.show()
        input("On the signal generator one should know see the signal press enter to continue")
        plt.close()
        print("ok")

if 1:
    sc0 = PXI_5142('PXI2Slot8', name = 'scope', selftest=True, reset=True, log=True)
    sc1 = PXI_5142('PXI2Slot7', name = 'scope', selftest=True, reset=True, log=True)


    print("Initialize SMU")
    smu0 = PXIe4141('PXI2Slot3', name = 'smu', selftest=True,reset=True,log=True)
    print("Set speed of SMU channel")
    smu0.set_aperture(1, 0.001, 2)
    print("Set one volt on output of SMU channel 1")
    smu0.configure_channel_vdc(0, 2.0, 1.0, -0.001, 0.0025)
    print("enable the channel")
    smu0.enable(0, True)
    time.sleep(1)
    if abs(1-smu0.measure(0)[0])>0.01:
        print("SMU does not work")

    # Get some data from the Oscilloscope
    PlotData = PXI_5142.get_data(sc0,sc1)
    PlotData.plot_all_data()
    plt.close()


# [V,I] = PS.meas_6V()
# print("Voltage = "+ str(V) + "V, Current = " + str(I*1000)+"mA")
# [V,I] = PS.meas_P25V()
# print("Voltage = "+ str(V) + "V, Current = " + str(I*1000)+"mA")
# [V,I] = PS.meas_N25V()
# print("Voltage = "+ str(V) + "V, Current = " + str(I*1000)+"mA")