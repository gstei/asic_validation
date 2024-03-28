"""
This is the execution script to execute the different tests
To see the functions of the different instruments go to  https://nimi-python.readthedocs.io/en/1.2.1/niscope/class.html
"""

from DCDCConverterStartupTest import DCDCConverterStartupTest
from DCDCConverterResetTest import DCDCConverterResetTest
from DCDCConverterStepTest import DCDCConverterStepTest
from DCDCConverterLoadTest import DCDCConverterLoadTest
from DCDCConverterResetPowerOnTest import DCDCConverterResetPowerOnTest
# import SMU drivers
from Drivers.pxie_4141_main.PXIe4141 import PXIe4141
# import Oscilloscope drivers
from Drivers.pxi_5142_main.PXI_5142 import PXI_5142
# import Power supply drivers
from Drivers.e3631a_main.E3631A import E3631A
# import Signal generator
from Drivers.pxi_5402_main.PXI_5402 import PXI_5402
# Control GPIOs
from Drivers.pxi_6363_main.GPIO import GPIOController
# import Power supply drivers
from Drivers.e3631a_main.E3631A import E3631A
# import Database
from database import Database, MeasurementField

def main():
    """
    This is the main function that initializes the PXIe4141 and PXI_5142 instruments,
    and runs the different tests.

    Args:
        None

    Returns:
        None
    """
    # Create instruments
    smu0 = PXIe4141('PXI2Slot3', name='smu', selftest=False, reset=True, log=True)
    sc0 = PXI_5142('PXI2Slot8', name='scope', selftest=False, reset=True, log=True)
    sc1 = PXI_5142('PXI2Slot7', name='scope', selftest=False, reset=True, log=True)
    # Create gpio controller
    gpio = GPIOController()
    power_sup = E3631A(address=5)
    
    # Create database
    database = Database("measurements")
    chip_id= "TI"
    measurement_temperature=22.0
    if 1: #normal startup test (no reset active)
        resistor_values = ['R1', 'R2', 'R3', 'R4']
        voltages = [4.3, 5, 5.5]
        for voltage in voltages:
            for resistor in resistor_values:
                dcdc = DCDCConverterStartupTest.run(smu0, sc0, sc1, power_sup, gpio, voltage, resistor)
                dcdc.temperature = measurement_temperature
                dcdc.title = dcdc.title + f", {measurement_temperature}°C"
                database.insert(f"{chip_id}", "normal startup", dcdc, "Passed", f"{voltage}V", resistor, measurement_temperature=measurement_temperature)
    if 1: 
        if 1: #reset startup test (reset active and then released)
            resistor_values = ['R1', 'R2', 'R3', 'R4']
            voltages = [4.3, 5, 5.5]
            for voltage in voltages:
                for resistor in resistor_values:
                    dcdc = DCDCConverterResetTest.run(gpio, smu0, sc0, sc1, power_sup, voltage, resistor)
                    dcdc.temperature = measurement_temperature
                    dcdc.title = dcdc.title + f", {measurement_temperature}°C"
                    database.insert(f"{chip_id}", "reset startup", dcdc, "Passed", f"{voltage}V", resistor, measurement_temperature=measurement_temperature)
        if 1: #input step test (change input voltage up and down and measure output voltage)
            resistor_values = ['R1', 'R2', 'R3']
            steps = [[4.3,4.8], [4.3,5], [4.3,5.3]]
            for step in steps:
                for resistor in resistor_values:
                    dcdc = DCDCConverterStepTest.run(gpio, smu0, sc0, sc1, power_sup, step, resistor)
                    dcdc.temperature = measurement_temperature
                    dcdc.title = dcdc.title + f", {measurement_temperature}°C"
                    database.insert(f"{chip_id}", "input voltage jump", dcdc, "Passed", f"{step[0]}V to {step[1]}V", resistor, measurement_temperature=measurement_temperature)
        if 1: #load step test (change load resistance up and down and measure output voltage)
            resistor_values = ['R1', 'R2', 'R3', 'R4']
            voltages = [4.3, 5, 5.5]
            for voltage in voltages:
                for resistor in resistor_values:
                    dcdc = DCDCConverterLoadTest.run(gpio, smu0, sc0, sc1, power_sup, voltage, resistor)
                    dcdc.temperature = measurement_temperature
                    dcdc.title = dcdc.title + f", {measurement_temperature}°C"
                    database.insert(f"{chip_id}", "load jump", dcdc, "Passed", f"{voltage}V", resistor, measurement_temperature=measurement_temperature)
        if 1: #enable reset while powerd on
            resistor_values = ['R1', 'R2', 'R3']
            voltages = [4.3, 5, 5.5]
            for voltage in voltages:
                for resistor in resistor_values:
                    dcdc = DCDCConverterResetPowerOnTest.run(gpio, smu0, sc0, sc1, power_sup, voltage, resistor)
                    dcdc.temperature = measurement_temperature
                    dcdc.title = dcdc.title + f", {measurement_temperature}°C"
                    database.insert(f"{chip_id}", "reset while powered", dcdc, "Passed", f"{voltage}V", resistor, measurement_temperature=measurement_temperature)
    
    database.delete_measurement_before("2024-03-22 15:27:21")
    database.print_table()

if __name__ == "__main__":
    main()