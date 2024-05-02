"""
This is the execution script to execute the different tests
To see the functions of the different instruments go to
https://nimi-python.readthedocs.io/en/1.2.1/niscope/class.html
"""

from dc_dc_converter_startup_test import DcDcConverterStartupTest
from dc_dc_converter_reset_test import DcDcConverterResetTest
from dc_dc_converter_step_test import DcDcConverterStepTest
from dc_dc_converter_load_test import DcDcConverterLoadTest
from dc_dc_converter_reset_power_on_test import DcDcConverterResetPowerOnTest
# import SMU drivers
from Drivers.pxie_4141_main.PXIe4141 import PXIe4141
# import Oscilloscope drivers
from Drivers.pxi_5142_main.PXI_5142 import PXI_5142
# import Power supply drivers
from Drivers.e3631a_main.E3631A import E3631A
# import Signal generator
# from Drivers.pxi_5402_main.PXI_5402 import PXI_5402
# Control GPIOs
from Drivers.pxi_6363_main.GPIO import GPIOController
# import elefant
from Drivers.tp04300a_main.python.TP04300 import TP04300
# import the SPI class
from Drivers.FTDI.ftdi_spi import FtdiSpi
# import Database
from database import Database

def main():
    """
    This is the main function that initializes the PXIe4141 and PXI_5142 instruments,
    and runs the different tests.

    Args:
        None

    Returns:
        None
    """
    #region initialize Elefant
    ploton = True
    with_selftest = True
    with_reset = True
    tp04300_obj = TP04300('Elefant', 'GPIB1::9::INSTR')
    tp04300_obj.open_com(with_selftest, with_reset, ploton)
    #TP04300_obj.headLock(False)
    tp04300_obj.headDown(False)
    tp04300_obj.flow(False)
    tp04300_obj.reset()
    tp04300_obj.setup(TP04300.dutSensorType.index("type K thermocouple"),
        TP04300.dutType.index("Smallest DUT mass"),
        TP04300.dutMode.index("dut control"),
        dutThermalConstant = 20,
        maxTemperatureError = 0.4,
        soakTime = 10, llim = -15, ulim = 100)
    tp04300_obj.to_string()
    #TP04300_obj.waitUntilHeadDownManual(True)
    #endregion



    # Create instruments
    smu0 = PXIe4141('PXI2Slot3', name='smu', selftest=False, reset=True, log=True)
    sc0 = PXI_5142('PXI2Slot8', name='scope', selftest=False, reset=True, log=True)
    sc1 = PXI_5142('PXI2Slot7', name='scope', selftest=False, reset=True, log=True)
    # Create gpio controller
    gpio = GPIOController()
    power_sup = E3631A(address=5)
    spi=FtdiSpi()
    spi.configure()

    # Create database
    database = Database("measurements")
    chip_id= "TI"
    temperature=[0, 25, 70]
    for measurement_temperature in temperature:
        tp04300_obj.headDown(True)
        tp04300_obj.flow(True)
        tp04300_obj.setPointAndWait(measurement_temperature, ploton)
        if 1: #normal startup test (no reset active)
            resistor_values = ['R1', 'R2', 'R3', 'R4']
            voltages = [4.3, 5, 5.5]
            for voltage in voltages:
                for resistor in resistor_values:
                    dcdc = DcDcConverterStartupTest.run(smu0, sc0, sc1, power_sup, gpio,
                                                        voltage, resistor)
                    dcdc.temperature = measurement_temperature
                    dcdc.title = dcdc.title + f", {measurement_temperature}°C"
                    database.insert(f"{chip_id}", "normal startup", dcdc, "Passed", f"{voltage}V",
                                    resistor, measurement_temperature=measurement_temperature)
        if 1: #reset startup test (reset active and then released)
            resistor_values = ['R1', 'R2', 'R3', 'R4']
            voltages = [4.3, 5, 5.5]
            for voltage in voltages:
                for resistor in resistor_values:
                    dcdc = DcDcConverterResetTest.run(gpio, smu0, sc0, sc1, power_sup, voltage,
                                                        resistor)
                    dcdc.temperature = measurement_temperature
                    dcdc.title = dcdc.title + f", {measurement_temperature}°C"
                    database.insert(f"{chip_id}", "reset startup", dcdc, "Passed",
                                    f"{voltage}V", resistor,
                                    measurement_temperature=measurement_temperature)
        if 1: #input step test (change input voltage up and down and measure output voltage)
            resistor_values = ['R1', 'R2', 'R3']
            steps = [[4.3,4.8], [4.3,5], [4.3,5.3]]
            for step in steps:
                for resistor in resistor_values:
                    dcdc = DcDcConverterStepTest.run(gpio, smu0, sc0, sc1, power_sup,
                                                        step, resistor)
                    dcdc.temperature = measurement_temperature
                    dcdc.title = dcdc.title + f", {measurement_temperature}°C"
                    database.insert(f"{chip_id}", "input voltage jump", dcdc, "Passed",
                                    f"{step[0]}V to {step[1]}V", resistor,
                                    measurement_temperature=measurement_temperature)
        if 1: #load step test (change load resistance up and down and measure output voltage)
            resistor_values = ['R2', 'R3', 'R4']
            voltages = [4.3, 5, 5.5]
            for voltage in voltages:
                for resistor in resistor_values:
                    dcdc = DcDcConverterLoadTest.run(gpio, smu0, sc0, sc1, power_sup, voltage,
                                                        resistor)
                    dcdc.temperature = measurement_temperature
                    dcdc.title = dcdc.title + f", {measurement_temperature}°C"
                    database.insert(f"{chip_id}", "load jump", dcdc, "Passed", f"{voltage}V",
                                    resistor, measurement_temperature=measurement_temperature)
        if 1: #enable reset while powerd on
            resistor_values = ['R1', 'R2', 'R3']
            voltages = [4.3, 5, 5.5]
            for voltage in voltages:
                for resistor in resistor_values:
                    dcdc = DcDcConverterResetPowerOnTest.run(gpio, smu0, sc0, sc1, power_sup,
                                                                voltage, resistor)
                    dcdc.temperature = measurement_temperature
                    dcdc.title = dcdc.title + f", {measurement_temperature}°C"
                    database.insert(f"{chip_id}", "reset while powered", dcdc, "Passed",
                                    f"{voltage}V", resistor,
                                    measurement_temperature=measurement_temperature)
    tp04300_obj.flow(False)
    #TP04300_obj.headLock(False)
    tp04300_obj.headDown(False)
    tp04300_obj.close_com()
    database.delete_measurement_before("2024-03-22 15:27:21")
    database.print_table()

if __name__ == "__main__":
    main()
