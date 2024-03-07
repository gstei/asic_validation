#SCB-68A
import nidaqmx
from nidaqmx.constants import LineGrouping
import numpy as np
import time
#16=6   R3
#47=3 = reset
#48=7 = R1
#49=2 = R2
#51=5 = R4



class GPIOController:
    """
    A class that represents a GPIO controller.

    This class provides methods to initialize the GPIO class and set the output values for the GPIO pins.

    Attributes:
        task (nidaqmx.Task): The task for digital output.

    Methods:
        __init__(): Initializes the GPIO class.
        set_output(): Sets the output values for the GPIO pins.
    """

    def __init__(self):
        """
        Initializes the GPIO class.

        This method creates a new instance of the GPIO class and initializes the 
            task for digital output.

        Parameters:
            None

        Returns:
            None
        """
        self.task = nidaqmx.Task()
        self.task.do_channels.add_do_chan("PXI2Slot2/port0/line2:7", 
                                          line_grouping=LineGrouping.CHAN_PER_LINE)

    def set_output(self, R1=False, R2=False, R3=False, R4=False, reset=False):
        """
        Sets the output values for the GPIO pins.

        Args:
            R1 (bool): Value for R1 pin. Default is False.
            R2 (bool): Value for R2 pin. Default is False.
            R3 (bool): Value for R3 pin. Default is False.
            R4 (bool): Value for R4 pin. Default is False.
            reset (bool): Value for reset pin. Default is False.

        Returns:
            None
        """
        self.task.write([R2, reset, False, R4, R3, R1])
