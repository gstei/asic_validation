"""
This module contains the DCDCConverterLoadTest class which is used to perform load tests 
on a DC-DC converter.
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

class DcDcConverterLoadTest:
    """
    Class for performing load tests on a DC-DC converter.
    """
    def __init__(self):
        print("init")

    @staticmethod
    def step_test(gpio: GPIOController, smu0: PXIe4141, power_sup: E3631A, voltage: float,
                  resistor="R1"):
        """
        Perform a step test on the DC-DC converter.

        Args:
            gpio (GPIOController): The GPIO controller object.
            smu0 (PXIe4141): The SMU0 object.
            power_sup (E3631A): The power supply object.
            voltage (float): The voltage to be applied.
            resistor (str, optional): The resistor to be used. Defaults to "R1".
        """
        # enable the reset
        # gpio.set_output(reset=False, **{resistor: False})
        if NORMAL_MODE:
            smu0.set_all_smu_outputs_to_voltage(voltage)
        else:
            time.sleep(0.2)
            power_sup.set_P25V(voltage, 0.4)
            time.sleep(0.1)
            power_sup.en_output(True)
        # enable the chip
        time.sleep(0.3)
        gpio.set_output(reset=False, **{resistor: True})
        time.sleep(0.005)
        gpio.set_output(reset=False, **{resistor: False})
        time.sleep(0.1)
        if NORMAL_MODE:
            smu0.set_all_smu_outputs_to_zero_and_disable()
        else:
            power_sup.en_output(False)
        time.sleep(0.2)
    @staticmethod
    def run(gpio: GPIOController, smu0: PXIe4141, sc0: PXI_5142, sc1: PXI_5142, power_sup: E3631A,
            voltage: float, resistor : str):
        """
        Runs the DCDCConverterLoadTest with the given parameters.

        Args:
            gpio (GPIOController): The GPIO controller object.
            smu0 (PXIe4141): The SMU object.
            sc0 (PXI_5142): The first Oscilloscope object.
            sc1 (PXI_5142): The second Oscilloscope object.
            power_sup (E3631A): The power supply object.
            voltage (float): The input voltage.
            resistor (str): The resistor value.

        Returns:
            return_value_scope (ScopeData): The scope data object containing the test results.
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
            smu_return = executor.submit(DcDcConverterLoadTest.step_test, gpio, smu0, power_sup,
                                         voltage, resistor)
            scope_return = executor.submit(PXI_5142.get_data2, sc0, sc1,
                                           trigger_source_channel_nr=1, trigger_level=0.01,
                                           delta_t=25e-3, triger_position=10.0, voffset=0,
                                           vrange=6.0, trigger_scope=0, delay=0.2)

        return_value_scope = scope_return.result()
        return_value_scope.title = f"""DCDC step test with load step with resistor {resistor}
                                    at voltage {voltage}V"""
        return_value_smu = smu_return.result()
        if NORMAL_MODE:
            power_sup.en_output(False)
        return_value_scope.plot_all_data()
        return return_value_scope
