# Python FTDI SPI example from iosoft.blog
# Compatible with Python 2.7 or 3.x
# Drives a MikroElektronika UT-L 7-SEG R display
#
# v0.01 JPB 8/12/18
 
FTD2XX       = True  # Set False if using pylibftdi
FTDI_TIMEOUT = 1000  # Timeout for D2XX read/write (msec)
 
if FTD2XX:
    import sys, time, ftd2xx as ftd
else:
    import sys, time, pylibftdi as ftdi
 
# Segment bit values for digits 0 - 9
dig_segs = 0x3F,0x06,0x5B,0x4F,0x66,0x6D,0x7D,0x07,0x7F,0x6F
 
DIG1 = 0    # Digits to be displayed
DIG2 = 1
OPS  = 0x03 # Bit mask for SPI clock and data out
OE   = 0x08 #              display output enable
LE   = 0x10 #              display latch enable
 
# Set mode (bitbang / MPSSE)
def set_bitmode(d, bits, mode):
    return (d.setBitMode(bits, mode) if FTD2XX else
            d.ftdi_fn.ftdi_set_bitmode(bits, mode))
    
# Open device for read/write
def ft_open(n=0):
    if FTD2XX:
        d = ftd.open(n)
        d.setTimeouts(FTDI_TIMEOUT, FTDI_TIMEOUT)
    else:
        d = ftdi.Device(device_index=n)
    return d
 
# Set SPI clock rate
def set_spi_clock(d, hz):
    div = int((12000000 / (hz * 2)) - 1)  # Set SPI clock
    ft_write(d, (0x86, div%256, div//256)) 
 
# Read byte data into list of integers
def ft_read(d, nbytes):
    s = d.read(nbytes)
    return [ord(c) for c in s] if type(s) is str else list(s)
 
# Write list of integers as byte data
def ft_write(d, data):
    s = str(bytearray(data)) if sys.version_info<(3,) else bytes(data)
    return d.write(s)
 
# Write MPSSE command with word-value argument
def ft_write_cmd_bytes(d, cmd, data):
    n = len(data) - 1
    ft_write(d, [cmd, n%256, n//256] + list(data))
 
if __name__ == "__main__":
    dev = ft_open(0)
    if dev:
        print("FTDI device opened")
        set_bitmode(dev, OPS, 2)              # Set SPI mode
        set_spi_clock(dev, 1000000)           # Set SPI clock
        ft_write(dev, (0x80, 0, OPS+OE+LE))   # Set outputs
        data = dig_segs[DIG1], dig_segs[DIG2] # Convert digits to segs
        ft_write_cmd_bytes(dev, 0x11, data)   # Write seg bit data
        ft_write(dev, (0x80, LE, OPS+OE+LE))  # Latch = 1
        ft_write(dev, (0x80, OE, OPS+OE+LE))  # Latch = 0, disp = 1
        print("Displaying '%u%u'" % (DIG2, DIG1))
        time.sleep(1)
        ft_write(dev, (0x80, 0,  OPS+OE+LE))  # Latch = disp = 0
        print("Display off")
        dev.close()
# EOF