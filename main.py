"""
This is the execution script to execute the different tests
To see the functions of the different instruments go to  https://nimi-python.readthedocs.io/en/1.2.1/niscope/class.html
"""

from DCDCConverterStartupTest import DCDCConverterStartupTest
# import SMU drivers
from Drivers.pxie_4141_main.PXIe4141 import PXIe4141
# import Oscilloscope drivers
from Drivers.pxi_5142_main.PXI_5142 import PXI_5142
# import Power supply drivers
from Drivers.e3631a_main.E3631A import E3631A
# import Signal generator
from Drivers.pxi_5402_main.PXI_5402 import PXI_5402

def main():
    """
    This is the main function that initializes the PXIe4141 and PXI_5142 instruments,
    and runs the different tests.

    Args:
        None

    Returns:
        None
    """
    smu0 = PXIe4141('PXI2Slot3', name='smu', selftest=False, reset=True, log=True)
    sc0 = PXI_5142('PXI2Slot8', name='scope', selftest=False, reset=True, log=True)
    sc1 = PXI_5142('PXI2Slot7', name='scope', selftest=False, reset=True, log=True)
    
    dcdc = DCDCConverterStartupTest.run(smu0, sc0, sc1)

if __name__ == "__main__":
    main()