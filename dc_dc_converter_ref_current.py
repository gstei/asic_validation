"""
This module contains the DCDCConverterLoadTest class which is used to perform load tests 
on a DC-DC converter.
"""
import concurrent.futures
import time
import os
# import SMU drivers
from Drivers.pxie_4141_main.PXIe4141 import PXIe4141
# import Oscilloscope drivers
from Drivers.pxi_5142_main.PXI_5142 import PXI_5142
# Control GPIOs
from Drivers.pxi_6363_main.GPIO import GPIOController
# import Power supply drivers
from Drivers.e3631a_main.E3631A import E3631A
# import FTDI SPI
from Drivers.FTDI.ftdi_spi import FtdiSpi
# import elefant
from Drivers.tp04300a_main.python.TP04300 import TP04300

import matplotlib.pyplot as plt

import pickle

NORMAL_MODE=False

class DcDcConverterRefCurrent:
    """
    Class for performing load tests on a DC-DC converter.
    """
    def __init__(self):
        print("init")
    
    @staticmethod
    def get_ref_current(power_sup: E3631A, smu0: PXIe4141, spi: FtdiSpi, voltage=5):
        # Power chip
        power_sup.set_P25V(voltage, 0.4)
        time.sleep(0.1)
        power_sup.en_output(True)
        time.sleep(0.3)
        spi.output_cur_ref()
        smu0.configure_channel_idc(0, 0.000002, 0.000, -6, 6)
        smu0.enable(0, True)
        time.sleep(0.1)
        voltage_measured = smu0.measure(0)[0]
        smu0.enable(0, False)
        power_sup.en_output(False)
        return voltage_measured
    @staticmethod
    def run(gpio: GPIOController, smu0: PXIe4141, sc0: PXI_5142, sc1: PXI_5142, power_sup: E3631A, spi: FtdiSpi,
            voltage: float):
        print("Connect SMU0 to analog test pin ")
        print("Connect Power supply to the PCB (6V output)")

        return_value_scope.plot_all_data()
        return return_value_scope
    
    # if main
if __name__ == "__main__":
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
        maxTemperatureError = 0.5,
        soakTime = 2, llim = -15, ulim = 100)
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
    input_voltages=[4.3, 5, 5.5]
    voltages = {"4.3": [], "5": [], "5.5": []}
    temperatures= {"4.3": [], "5": [], "5.5": []}
    for measurement_temperature in range(0, 71, 1):
        tp04300_obj.headDown(True)
        tp04300_obj.flow(True)
        tp04300_obj.setPointAndWait(measurement_temperature, ploton)
        for input_voltage in input_voltages:
            voltages[str(input_voltage)].append(DcDcConverterRefCurrent.get_ref_current(power_sup, smu0, spi, input_voltage)*10*10e-6)
            temperatures[str(input_voltage)].append(measurement_temperature)
    tp04300_obj.flow(False)
    tp04300_obj.headDown(False)
    current_directory = os.getcwd()
    with open(f'{current_directory}\\images\\02_Ref_current\\ref_current_vs_temperature.pkl', "wb") as f:
        pickle.dump((temperatures, voltages), f)
    for input_voltage in input_voltages:
        plt.plot(temperatures[str(input_voltage)], voltages[str(input_voltage)], label=f"{input_voltage}V input voltage")
    plt.xlabel("Temperature [°C]")
    plt.ylabel("Reference current [A]")
    plt.title("Reference current vs temperature")
    plt.legend()

    plt.savefig(f'{current_directory}\\images\\02_Ref_current\\{"Current"}.png', dpi=300)
    plt.show()
    # safe data as pickle
    

    print("done")
    
    
