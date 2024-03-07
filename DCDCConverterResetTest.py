# import SMU drivers
from Drivers.pxie_4141_main.PXIe4141 import PXIe4141
# import Oscilloscope drivers
from Drivers.pxi_5142_main.PXI_5142 import PXI_5142
# Control GPIOs
from Drivers.pxi_6363_main.GPIO import GPIOController

import concurrent.futures
import time


class DCDCConverterResetTest:
    def __init__(self, oscilloscope, smu):
        print("init")


    @staticmethod
    def reset_test(gpio: GPIOController, smu0: PXIe4141, output_voltage=5):
        # enable the reset
        gpio.set_output(reset=True)
        # region prepare the SMU
        print("Set speed of SMU channel")
        smu0.set_aperture(0, 0.001, 2)
        print(f"Set {output_voltage}V on output of SMU channel zero")
        # Todo change current limit to 100mA
        smu0.configure_channel_vdc(0, 6, 0.0, -0.001, 0.1)
        if abs(smu0.measure(0)[0])>0.01:
            print("Voltage:" + str(smu0.measure(0)[0]))
            print("SMU Voltage was not zero before enabling the channel")
        print("enable the channel")
        smu0.enable(0, True)
        if abs(smu0.measure(0)[0])>0.01:
            print("Voltage:" + str(smu0.measure(0)[0]))
            print("SMU Voltage was not zero after enabling the channel")
        smu0.set_voltage(0 ,5,True)
        if abs(1-(abs(smu0.measure(0)[0]/output_voltage)))>0.01:
            print("Voltage:" + str(smu0.measure(0)[0]))
            print("SMU output does not have correct value")
        # endregion
        time.sleep(0.1)
        # enable the chip
        gpio.set_output(reset=False)
        time.sleep(5)
        smu0.set_voltage(0 ,0,True)
        smu0.set_voltage(0 ,0,False)
    @staticmethod
    def run(gpio: GPIOController, smu0: PXIe4141, sc0: PXI_5142, sc1: PXI_5142):
        print("Connect SMU0, SMU1, SMU3 to the input of the CHIP")
        print("Connect Oscilloscope at slot8 with the Voltages osc0 with input voltage osc1 with output voltage")
        print("Connect Oscilloscope at slot7 with the Currents osc0 with input current osc1 with output current")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            scope_return = executor.submit(PXI_5142.get_data2, sc0, sc1, trigger_source_channel_nr=0) #we trigger the output voltage
            smu_return = executor.submit(DCDCConverterResetTest.reset_test, gpio, smu0, 5.0)

        return_value_scope = scope_return.result()
        return_value_smu = smu_return.result()

     
        return_value_scope.plot_all_data()
        return return_value_scope


