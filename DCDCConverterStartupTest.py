# import SMU drivers
from Drivers.pxie_4141_main.PXIe4141 import PXIe4141
# import Oscilloscope drivers
from Drivers.pxi_5142_main.PXI_5142 import PXI_5142
# import Power supply drivers
from Drivers.e3631a_main.E3631A import E3631A
# Control GPIOs
from Drivers.pxi_6363_main.GPIO import GPIOController

import concurrent.futures
import time


class DCDCConverterStartupTest:
    def __init__(self, oscilloscope, smu):
        print("init")

    @staticmethod
    def smu_startup_test(smu0: PXIe4141, gpio: GPIOController, output_voltage=5, resistor="R1"):
        gpio.set_output(reset=False, **{resistor: True})
        time.sleep(0.3)
        smu0.set_all_smu_outputs_to_voltage(output_voltage)
        time.sleep(0.1)
        gpio.set_output(reset=False, **{resistor: False})
        smu0.set_all_smu_outputs_to_zero_and_disable()
    @staticmethod
    def run(smu0: PXIe4141, sc0: PXI_5142, sc1: PXI_5142, power_sup: E3631A, gpio: GPIOController, voltage : int, resistor : str):
        print("Connect SMU0, SMU1, SMU2 to the input of the CHIP")
        print("Connect Oscilloscope at slot8 with the Voltages osc0 with input voltage osc1 with output voltage")
        print("Connect Oscilloscope at slot7 with the Currents osc0 with input current osc1 with output current")
        print("Connect Power supply to the PCB (6V output)")
        power_sup.set_6V(5,0.4)
        power_sup.en_output(True)
        # wait so that power supply is for sure on
        time.sleep(0.1)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            scope_return = executor.submit(PXI_5142.get_data2, sc0, sc1, trigger_source_channel_nr=0) #must be changed for the real test.
            smu_return = executor.submit(DCDCConverterStartupTest.smu_startup_test, smu0, gpio, 5.0, resistor)
        
        return_value_scope = scope_return.result()
        return_value_scope.title = f"DCDC startup test with {voltage}V and resistor {resistor}"
        return_value_smu = smu_return.result()
        power_sup.en_output(False)

     
        return_value_scope.plot_all_data()
        return return_value_scope


