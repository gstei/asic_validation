
"""
This module contains the code for performing a step test on a DC-DC converter.
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

class DcDcConverterStepTest:
    """
    Class for performing a step test on a DC-DC converter.
    """

    def __init__(self):
        print("init")

    @staticmethod
    def step_test(gpio: GPIOController, smu0: PXIe4141, power_sup: E3631A, step=[4.3, 5.5],
                  resistor="R1"):
        """
        Perform a step test on the DC-DC converter.

        Args:
            gpio (GPIOController): The GPIO controller object.
            smu0 (PXIe4141): The SMU0 object.
            power_sup (E3631A): The power supply object.
            step (list, optional): The step voltages. Defaults to [4.3, 5.5].
            resistor (str, optional): The resistor value. Defaults to "R1".
        """
        # enable the reset
        gpio.set_output(reset=False, **{resistor: True})
        if NORMAL_MODE:
            smu0.set_all_smu_outputs_to_voltage(step[0])
            time.sleep(0.3)
            smu0.set_all_voltages(step[1], True)
            time.sleep(0.01)
            smu0.set_all_voltages(step[0], True)
            time.sleep(0.1)
            gpio.set_output(**{resistor: False})
            smu0.set_all_smu_outputs_to_zero_and_disable()
        else:
            time.sleep(0.2)
            power_sup.set_P25V(step[0], 0.4)
            time.sleep(0.1)
            power_sup.en_output(True)
            # enable the chip
            time.sleep(0.3)
            power_sup.set_P25V(step[1], 0.4)
            time.sleep(0.01)
            power_sup.set_P25V(step[0], 0.4)
            time.sleep(0.2)
            gpio.set_output(**{resistor: False})
            power_sup.en_output(False)

    @staticmethod
    def run(gpio: GPIOController, smu0: PXIe4141, sc0: PXI_5142, sc1: PXI_5142,
            power_sup: E3631A, step, resistor : str):
        """
        Run the step test on the DC-DC converter.

        Args:
            gpio (GPIOController): The GPIO controller object.
            smu0 (PXIe4141): The SMU0 object.
            sc0 (PXI_5142): The oscilloscope object for voltage measurements.
            sc1 (PXI_5142): The oscilloscope object for current measurements.
            power_sup (E3631A): The power supply object.
            step (list): The step voltages.
            resistor (str): The resistor value.

        Returns:
            object: The result of the step test.
        """
        print("Connect SMU0, SMU1, SMU3 to the input of the CHIP")
        print("""Connect Oscilloscope at slot8 with the Voltages osc0 with input voltage osc1
              with output voltage""")
        print("""Connect Oscilloscope at slot7 with the Currents osc0 with input current osc1
              with output current""")
        print("Connect Power supply to the PCB (6V output)")
        if NORMAL_MODE:
            power_sup.set_6V(5,0.4)
            power_sup.en_output(True)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            smu_return = executor.submit(DcDcConverterStepTest.step_test, gpio, smu0, power_sup,
                                         step, resistor)
            scope_return = executor.submit(PXI_5142.get_data2, sc0, sc1,
                                           trigger_source_channel_nr=0, trigger_level=step[0]+0.4,
                                           delta_t=100e-3, triger_position=5.0, voffset=0,
                                           vrange=6.0)

        return_value_scope = scope_return.result()
        return_value_scope.title = f"DCDC step test with step from {step[0]}V to {step[1]}V with "+\
            f"resistor {resistor}"
        return_value_smu = smu_return.result()
        if NORMAL_MODE:
            power_sup.en_output(False)

        return_value_scope.plot_all_data()
        return return_value_scope
