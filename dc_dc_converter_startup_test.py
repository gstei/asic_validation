"""
This module contains the code for testing the startup functionality of a DC-DC converter.
"""

import concurrent.futures
import time
# import SMU drivers
from Drivers.pxie_4141_main.PXIe4141 import PXIe4141
# import Oscilloscope drivers
from Drivers.pxi_5142_main.PXI_5142 import PXI_5142
# import Power supply drivers
from Drivers.e3631a_main.E3631A import E3631A
# Control GPIOs
from Drivers.pxi_6363_main.GPIO import GPIOController

NORMAL_MODE=False
class DcDcConverterStartupTest:
    """
    Class for performing the DC-DC converter startup test.
    """
    def __init__(self):
        print("init")

    @staticmethod
    def smu_startup_test(smu0: PXIe4141, power_sup: E3631A, gpio: GPIOController,
                         output_voltage=5, resistor="R1"):
        """
        Performs the startup test for the SMU (Source Measurement Unit) and power supply.

        Args:
            smu0 (PXIe4141): The SMU object.
            power_sup (E3631A): The power supply object.
            gpio (GPIOController): The GPIO controller object.
            output_voltage (float, optional): The desired output voltage. Defaults to 5.
            resistor (str, optional): The resistor to be used. Defaults to "R1".
        """
        gpio.set_output(reset=False, **{resistor: True})
        time.sleep(0.3)
        if NORMAL_MODE:
            smu0.set_all_smu_outputs_to_voltage(output_voltage)
        else:
            time.sleep(0.2)
            power_sup.set_P25V(output_voltage, 1)
            time.sleep(0.1)
            power_sup.en_output(True)
        time.sleep(0.1)
        gpio.set_output(reset=False, **{resistor: False})
        if NORMAL_MODE:
            smu0.set_all_smu_outputs_to_zero_and_disable()
        else:
            power_sup.en_output(False)
    @staticmethod
    def run(smu0: PXIe4141, sc0: PXI_5142, sc1: PXI_5142, power_sup: E3631A, gpio: GPIOController,
            voltage : int, resistor : str):
        """
        Runs the DC-DC converter startup test.

        Args:
            smu0 (PXIe4141): The SMU0 object.
            sc0 (PXI_5142): The first PXI_5142 oscilloscope object.
            sc1 (PXI_5142): The second PXI_5142 oscilloscope object.
            power_sup (E3631A): The power supply object.
            gpio (GPIOController): The GPIO controller object.
            voltage (int): The input voltage.
            resistor (str): The resistor value.

        Returns:
            ScopeData: The scope data object containing the results of the test.
        """
        print("Connect SMU0, SMU1, SMU2 to the input of the CHIP")
        print("""Connect Oscilloscope at slot8 with the Voltages osc0 with input voltage osc1
              with output voltage""")
        print("""Connect Oscilloscope at slot7 with the Currents osc0 with input current osc1 with
              output current""")
        print("Connect Power supply to the PCB (6V output)")
        if NORMAL_MODE:
            power_sup.set_6V(5,0.4)
            power_sup.en_output(True)
        # wait so that power supply is for sure on
        time.sleep(0.1)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            scope_return = executor.submit(PXI_5142.get_data2, sc0, sc1,
                                           trigger_source_channel_nr=0)
            smu_return = executor.submit(DcDcConverterStartupTest.smu_startup_test, smu0,
                                         power_sup, gpio, 5.0, resistor)

        return_value_scope = scope_return.result()
        return_value_scope.title = f"DCDC startup test with {voltage}V and resistor {resistor}"
        return_value_smu = smu_return.result()
        if NORMAL_MODE:
            power_sup.en_output(False)


        return_value_scope.plot_all_data()
        return return_value_scope
