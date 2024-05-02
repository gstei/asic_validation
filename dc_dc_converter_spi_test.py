"""
This module contains the SPITest class which is used to perform SPI tests
on a DC-DC converter.
"""
import time
# import SMU drivers
from Drivers.pxie_4141_main.PXIe4141 import PXIe4141
# Control GPIOs
from Drivers.pxi_6363_main.GPIO import GPIOController
# import Power supply drivers
from Drivers.e3631a_main.E3631A import E3631A
# import the SPI class
from Drivers.FTDI.ftdi_spi import FtdiSpi



NORMAL_MODE=False

class DcDcConverterSpiTest:
    """
    Class for performing load tests on a DC-DC converter.
    """
    def __init__(self):
        print("init")

    @staticmethod
    def setup_test(gpio: GPIOController, smu0: PXIe4141, power_sup: E3631A, voltage: float,
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
            time.sleep(0.1)
            power_sup.set_P25V(voltage, 0.4)
            time.sleep(0.1)
            power_sup.en_output(True)
        # enable the chip
        time.sleep(0.3)
        gpio.set_output(reset=False, **{resistor: True})
    @staticmethod
    def finish_test(smu0: PXIe4141, power_sup: E3631A):
        """
        Finish the test by resetting the GPIO, SMU, and power supply.

        Args:
            gpio (GPIOController): The GPIO controller object.
            smu0 (PXIe4141): The SMU object.
            power_sup (E3631A): The power supply object.
        """
        if NORMAL_MODE:
            smu0.set_all_smu_outputs_to_zero_and_disable()
        else:
            power_sup.en_output(False)
        time.sleep(0.2)
    @staticmethod
    def simple_spi_test(spi: FtdiSpi):
        """
        Performs a simple SPI test by reading data from a register and checking if it
        matches a specific value.

        Args:
            spi (FtdiSpi): An instance of the FtdiSpi class.

        Returns:
            bool: True if the test passes, False otherwise.
        """
        if spi.read_data_from_register(1) != 0x5:
            print("Simple SPI test failed")
            return False
        return True


    @staticmethod
    def run(gpio: GPIOController, smu0: PXIe4141, power_sup: E3631A,
            spi: FtdiSpi, voltage: float, resistor : str):
        """
        Runs the DC-DC converter SPI test.

        Args:
            gpio (GPIOController): The GPIO controller object.
            smu0 (PXIe4141): The PXIe4141 object for SMU0.
            sc0 (PXI_5142): The PXI_5142 object for SC0.
            sc1 (PXI_5142): The PXI_5142 object for SC1.
            power_sup (E3631A): The E3631A object for the power supply.
            spi (FtdiSpi): The FtdiSpi object for SPI communication.
            voltage (float): The voltage value for the test.
            resistor (str): The resistor value for the test.

        Returns:
            bool: False if the test fails, True otherwise.
        """
        DcDcConverterSpiTest.setup_test(gpio, smu0, power_sup, voltage, resistor)
        DcDcConverterSpiTest.simple_spi_test(spi)
        DcDcConverterSpiTest.finish_test(gpio, smu0, power_sup)
        return False

# when this is the main script then run the following
if __name__ == "__main__":
    # create spi instance
    spi=FtdiSpi()
    spi.configure()
    DcDcConverterSpiTest.simple_spi_test(spi)
