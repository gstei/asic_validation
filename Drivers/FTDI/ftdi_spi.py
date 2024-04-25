"""
This module provides a class to communicate with an FTDI SPI device.
"""

import time
from pyftdi import spi
from pyftdi.ftdi import Ftdi

class FtdiSpi:
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
        """
        Initializes the FTDI SPI controller.

        This method sets up the SPI controller using the FTDI library.
        It configures the SPI controller with the FTDI device at address 'ftdi://::/1'.
        It also prints instructions for connecting the SPI clock, chip select, master out, master in,
        and GPIO0 signals to the corresponding cables.

        Args:
            None

        Returns:
            None
        """
        self.spi = spi.SpiController()
        self.spi.configure('ftdi://::/1')
        print(Ftdi.show_devices())
        self.slave = None
        self.gpio = None
        print("Connect SPI clock to orange cable")
        print("Connect SPI Chip Select to brown cable")
        print("Connect SPI Master Out to yellow cable")
        print("Connect SPI Master In to green cable")
        print("Grey cable is GPIO0 CLK")
        print("Purple cable is GPIO0 CS")
        print("White cable is GPIO0 MOSI")
        print("Blue cable is GPIO0 MISO")
    def generate_signal(self, clock:int, cs:int, mosi:int, miso:int)->int:
        """
        Generates a signal on the GPIO port.

        Args:
            signal (int): The signal to be generated.

        """
        return (clock | cs<<1 | mosi<<2 | miso<<3) << 4
    def configure(self, chip_slect=0, freq=100e3, mode=3):
        """
        Configures the SPI port with the specified parameters.

        Args:
            cs (int): The chip select value.
            freq (float): The frequency of the SPI clock in Hz.
            mode (int): The SPI mode.

        """
        # Get a SPI port to a SPI slave w/ /CS on A*BUS3 and SPI mode 0 @ 100kHz
        self.slave = self.spi.get_port(cs=chip_slect, freq=freq, mode=mode)
        # Get GPIO port to manage extra pins, use A*BUS4 as GPO, A*BUS4 as GPI
        self.gpio = self.spi.get_gpio()
        # Activate all GPIOS
        self.gpio.set_direction(0xf0, 0x70)
        self.gpio.write(0x20)

    def write(self, data=0x10):
        """
        Writes data to the SPI port.

        Args:
            data (int): The data to be written.

        """
        # Assert GPO pin
        self.slave.write([data])
    def get_nth_bit(self, n:int, bit_index:int)->int:
        """
        Returns the value of the nth bit in the given number.

        Parameters:
        - n (int): The number from which to extract the bit.
        - bit_index (int): The index of the bit to extract (0-based).

        Returns:
        - int: The value of the nth bit (0 or 1).
        """
        return (n >> bit_index) & 1
    def write2(self, data=0x10) -> int:
        """
        Writes data to the SPI interface.

        Args:
            data (int): The data to be written. Default is 0x10.

        Returns:
            int: The value read from the SPI interface.

        """
        self.gpio.write(self.generate_signal(clock=0, cs=0, mosi=0, miso=0))
        self.gpio.write(self.generate_signal(clock=1, cs=0, mosi=0, miso=0))
        val_read = 0
        # for loop 7 ..0
        for i in range(7, -1, -1):
            self.gpio.write(self.generate_signal(clock=1, cs=0, mosi=self.get_nth_bit(data, i), miso=0))
            self.gpio.write(self.generate_signal(clock=0, cs=0, mosi=self.get_nth_bit(data, i), miso=0))
            val_read += (self.gpio.read(0x80) >> 7 & 1) << i
            self.gpio.write(self.generate_signal(clock=0, cs=0, mosi=self.get_nth_bit(data, i), miso=0))
            self.gpio.write(self.generate_signal(clock=1, cs=0, mosi=self.get_nth_bit(data, i), miso=0))
        self.gpio.write(self.generate_signal(clock=1, cs=1, mosi=self.get_nth_bit(data, 0), miso=0))
        self.gpio.write(self.generate_signal(clock=0, cs=1, mosi=0, miso=0))
        return val_read
    def close(self):
        """
        Closes the SPI port.

        """
    def write_register(self, address, value):
        """
        Writes a register value to the SPI port.

        Args:
            address (int): The register address.
            value (int): The register value.

        """
        self.slave.write(data=address)
        self.slave.write(data=value)
    def read_register(self, address) -> int:
        """
        Reads a register value from the SPI port.

        Args:
            address (int): The register address.

        Returns:
            int: The register value.

        """
        self.slave.write(data=address)
        return self.slave.read(1)[0]
        
if __name__ == "__main__":
    ftdi_spi = FtdiSpi()
    ftdi_spi.configure()
    time.sleep(0.2)
    print("Value read back was: "+bin(ftdi_spi.write2(0x7<<1 | 0x1)))
    ftdi_spi.write2(0x1<<1 | 0x1)
    ftdi_spi.write2(0x7<<1 | 0x1)
    ftdi_spi.write2(0x2<<1 | 0x1)
    # ftdi_spi.write(0xAA)
    # ftdi_spi.write(0x5)
    # ftdi_spi.write(0x2)
    # time.sleep(0.2)
    # ftdi_spi.write(0x14)
    # time.sleep(0.2)
    # ftdi_spi.write(0x16)
