# import SMU drivers
from Drivers.pxie_4141_main.PXIe4141 import PXIe4141
# import Oscilloscope drivers
from Drivers.pxi_5142_main.PXI_5142 import PXI_5142
# Control GPIOs
from Drivers.pxi_6363_main.GPIO import GPIOController
# import Power supply drivers
from Drivers.e3631a_main.E3631A import E3631A

import concurrent.futures
import time


class DCDCConverterResetTest:
    def __init__(self, oscilloscope, smu):
        print("init")


    @staticmethod
    def reset_test(gpio: GPIOController, smu0: PXIe4141, output_voltage=5, resistor="R1"):
        # enable the reset
        gpio.set_output(reset=True, **{resistor: True})
        smu0.set_all_smu_outputs_to_voltage(output_voltage)
        # enable the chip
        time.sleep(0.1)
        gpio.set_output(reset=False, **{resistor: True})
        
        time.sleep(0.2)
        gpio.set_output(**{resistor: False})
        smu0.set_all_smu_outputs_to_zero_and_disable()
    @staticmethod
    def run(gpio: GPIOController, smu0: PXIe4141, sc0: PXI_5142, sc1: PXI_5142, power_sup: E3631A, voltage : int, resistor : str):
        print("Connect SMU0, SMU1, SMU3 to the input of the CHIP")
        print("Connect Oscilloscope at slot8 with the Voltages osc0 with input voltage osc1 with output voltage")
        print("Connect Oscilloscope at slot7 with the Currents osc0 with input current osc1 with output current")
        print("Connect Power supply to the PCB (6V output)")
        power_sup.set_6V(5,0.4)
        power_sup.en_output(True)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            scope_return = executor.submit(PXI_5142.get_data2, sc0, sc1, trigger_source_channel_nr=1, trigger_level=0.1, delta_t=20e-3) #we trigger the output voltage
            smu_return = executor.submit(DCDCConverterResetTest.reset_test, gpio, smu0, voltage, resistor)

        return_value_scope = scope_return.result()
        return_value_scope.title = f"DCDC Reset Test with {voltage}V and resistor {resistor}"
        return_value_smu = smu_return.result()

        power_sup.en_output(False)
     
        return_value_scope.plot_all_data()
        return return_value_scope


