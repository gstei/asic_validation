"""
This module provides a class to communicate with an FTDI SPI device.
"""

import time
import pyftdi.spi as spi
from pyftdi.ftdi import Ftdi

class ftdi_spi:
    """
    A class representing an FTDI SPI interface.

    This class provides methods to configure and communicate with an FTDI SPI device.

    Attributes:
        spi (SpiController): The SPI controller object.
        slave (SpiPort): The SPI port to the slave device.
        gpio (GpioController): The GPIO controller object.

    Methods:
        __init__(): Initializes the ftdi_spi object.
        configure(cs, freq, mode): Configures the SPI port with the specified parameters.
        write(data): Writes data to the SPI port.
        close(): Closes the SPI port.

    """

    def __init__(self):
        self.spi = spi.SpiController()
        self.spi.configure('ftdi://::/1')
        print(Ftdi.show_devices())
        self.slave = None
        self.gpio = None
        print("Connect SPI clock to orange cable")
        print("Connect SPI Chip Select to brown cable")
        print("Connect SPI Master Out to yellow cable")
        print("Connect SPI Master In to green cable")

    def configure(self, cs=0, freq=100e3, mode=0):
        """
        Configures the SPI port with the specified parameters.

        Args:
            cs (int): The chip select value.
            freq (float): The frequency of the SPI clock in Hz.
            mode (int): The SPI mode.

        """
        # Get a SPI port to a SPI slave w/ /CS on A*BUS3 and SPI mode 0 @ 100kHz
        self.slave = self.spi.get_port(cs=cs, freq=freq, mode=mode)
        # Get GPIO port to manage extra pins, use A*BUS4 as GPO, A*BUS4 as GPI
        self.gpio = self.spi.get_gpio()
        self.gpio.set_direction(0x30, 0x10)
        self.gpio.write(0x10)

    def write(self, data=0x10):
        """
        Writes data to the SPI port.

        Args:
            data (int): The data to be written.

        """
        # Assert GPO pin
        self.slave.write([data])

    def close(self):
        """
        Closes the SPI port.

        """
        pass
if __name__ == "__main__":
    ftdi_spi = ftdi_spi()
    ftdi_spi.configure()
    time.sleep(0.2)
    ftdi_spi.write(0x12)
    time.sleep(0.2)
    ftdi_spi.write(0x14)