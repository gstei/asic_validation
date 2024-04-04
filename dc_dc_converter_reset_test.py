"""
This module contains the code for testing the reset functionality of a DC-DC converter.
"""

import concurrent.futures
import time

# import SMU drivers
from Drivers.pxie_4141_main.PXIe4141 import PXIe4141
# import Oscilloscope drivers
from Drivers.pxi_5142_main.PXI_5142 import PXI_5142
# Control GPIOs
from Drivers.pxi_6363_main.GPIO import GPIOController
# import Power supply drivers
from Drivers.e3631a_main.E3631A import E3631A

NORMAL_MODE=False

class DcDcConverterResetTest:
    """
    Class for performing a reset test on the DC-DC converter.
    """

    def __init__(self):
        print("init")

    @staticmethod
    def reset_test(gpio: GPIOController, smu0: PXIe4141, power_sup: E3631A, output_voltage=5,
                   resistor="R1"):
        """
        Performs a reset test on the DC-DC converter.

        Args:
            gpio (GPIOController): The GPIO controller object.
            smu0 (PXIe4141): The PXIe4141 object for SMU0.
            power_sup (E3631A): The E3631A object for the power supply.
            output_voltage (float, optional): The output voltage for the reset test. Defaults to 5.
            resistor (str, optional): The resistor to be used for the reset test. Defaults to "R1".
        """
        # enable the reset
        gpio.set_output(reset=True, **{resistor: True})
        if NORMAL_MODE:
            smu0.set_all_smu_outputs_to_voltage(output_voltage)
        else:
            time.sleep(0.4)
            power_sup.set_P25V(output_voltage, 0.4)
            time.sleep(0.1)
            power_sup.en_output(True)
        # enable the chip
        time.sleep(0.1)
        gpio.set_output(reset=False, **{resistor: True})

        time.sleep(0.2)
        gpio.set_output(**{resistor: False})
        if NORMAL_MODE:
            smu0.set_all_smu_outputs_to_zero_and_disable()
        else:
            power_sup.en_output(False)
    @staticmethod
    def run(gpio: GPIOController, smu0: PXIe4141, sc0: PXI_5142, sc1: PXI_5142, power_sup: E3631A,
            voltage : int, resistor : str):
        """
        Runs the DC-DC converter reset test.

        Args:
            gpio (GPIOController): The GPIO controller object.
            smu0 (PXIe4141): The SMU0 object.
            sc0 (PXI_5142): The oscilloscope object at slot 0.
            sc1 (PXI_5142): The oscilloscope object at slot 1.
            power_sup (E3631A): The power supply object.
            voltage (int): The input voltage for the test.
            resistor (str): The resistor value for the test.

        Returns:
            ScopeData: The scope data object containing the test results.
        """
        print("Connect SMU0, SMU1, SMU3 to the input of the CHIP")
        print("""Connect Oscilloscope at slot8 with the Voltages osc0 with input voltage
              osc1 with output voltage""")
        print("""Connect Oscilloscope at slot7 with the Currents osc0 with input current
              osc1 with output current""")
        print("Connect Power supply to the PCB (6V output)")
        if NORMAL_MODE:
            power_sup.set_6V(5,0.4)
            power_sup.en_output(True)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            scope_return = executor.submit(PXI_5142.get_data2, sc0, sc1,
                                           trigger_source_channel_nr=1, trigger_level=2,
                                           delta_t=20e-3) #we trigger the output voltage
            smu_return = executor.submit(DcDcConverterResetTest.reset_test, gpio, smu0,
                                         power_sup, voltage, resistor)

        return_value_scope = scope_return.result()
        return_value_scope.title = f"DCDC Reset Test with {voltage}V and resistor {resistor}"
        return_value_smu = smu_return.result()
        if NORMAL_MODE:
            power_sup.en_output(False)

        return_value_scope.plot_all_data()
        return return_value_scope
