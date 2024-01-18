#!/usr/bin/env python
"""  Interface to comunicate with the Waveform Generator PXI-5402
This Python Module is used to simplify the communication with the 
Waveform Generator (Fgen)  PXI-5402 from National Instrument which 
is mounted in the PXI system. For more inforimation -> see README.md
"""


import nifgen
import logging
#from metric import to_si

class PXI_5402:
    
    def __init__(self, addr = 'PXI2Slot9', name = 'NoName', selftest=False, reset=False, log=False):
        self.log = log
        if log:
            self.logger = logging.getLogger("Fgen")
            self.logger.info("Fgen Object created")

        self.name = name
        self.addr = addr
        self.instr = None

        self.__open_com(selftest,reset)

    def __open_com(self, with_selftest: bool, with_reset: bool):
        options = '' #{'simulate': False, 'driver_setup': {'Model': '4141', 'BoardType': 'PXIe', }, }
        self.instr = nifgen.Session(self.addr, options)
        
        if with_selftest:
            self.selftest(with_reset)
        
    def selftest(self, with_reset: bool):
        self.instr.self_test()
        if self.log:
            self.logger.info("Selftest passed")
        if with_reset:
            self.reset()
    
    def reset(self):
        self.instr.reset_device()
        self.instr.disable()
        if self.log:
            self.logger.info("Device reseted")
        
    def __close_com(self):
        self.instr.abort()
        self.instr.close()

    def __del__(self):
        self.enable(False)
        self.__close_com()
        if self.log:
            self.logger.info("Object Deleted")
        
    def configure_dc(self, dc_offset:float):
        self.instr.abort()
        self.instr.output_mode = nifgen.OutputMode.FUNC
        self.instr.configure_standard_waveform(nifgen.Waveform.DC, 0.0, 0.0, dc_offset, 0.0)
        self.instr.initiate()
            
    def configure_sin(self, amplitude:float, frequency:float, dc_offset:float, start_phase:float ):
        self.instr.abort()
        self.instr.output_mode = nifgen.OutputMode.FUNC
        self.instr.configure_standard_waveform(nifgen.Waveform.SINE, amplitude, frequency, dc_offset, start_phase)
        self.instr.initiate()
        
    def configure_rect(self, amplitude:float, frequency:float, dc_offset:float, start_phase:float ):
        self.instr.abort() # Attention: Amplitude is Peak to Peak (at 50Ohm load)
        self.instr.output_mode = nifgen.OutputMode.FUNC
        self.instr.configure_standard_waveform(nifgen.Waveform.SQUARE, amplitude, frequency, dc_offset, start_phase)
        self.instr.initiate()
    
    def set_waveform(self, waveform:str):
        if waveform == 'SIN':
            self.instr.func_waveform = nifgen.Waveform.SINE
        elif waveform == 'SQUARE':
            self.instr.func_waveform = nifgen.Waveform.SQUARE
        elif waveform == 'RAMP_UP':
            self.instr.func_waveform = nifgen.Waveform.RAMP_UP
        elif waveform == 'RAMP_DOWN':
            self.instr.func_waveform = nifgen.Waveform.RAMP_DOWN
        elif waveform == 'TRIANGLE':
            self.instr.func_waveform = nifgen.Waveform.TRIANGLE
        elif waveform == 'SQUARE':
            self.instr.func_waveform = nifgen.Waveform.SQUARE
        elif waveform == 'DC':
             self.instr.func_waveform = nifgen.Waveform.DC
        else:
            raise('Waveform not Supported!')
        
    def get_waveform(self) -> str:
        waveform = self.instr.func_waveform
        if waveform == nifgen.Waveform.SINE:
            return 'SIN'
        elif waveform == nifgen.Waveform.SQUARE:
            return 'SQUARE'
        elif waveform == nifgen.Waveform.RAMP_UP:
            return 'RAMP_UP'
        elif waveform == nifgen.Waveform.RAMP_DOWN:
            return 'RAMP_DOWN'
        elif waveform == nifgen.Waveform.TRIANGLE:
            return 'TRIANGLE'
        elif waveform == nifgen.Waveform.SQUARE:
            return 'SQUARE'
        elif waveform == nifgen.Waveform.DC:
            return 'DC'
        else:
            raise('Waveform not Supported!')
    
    def set_frequency(self, frequency:float):
        self.instr.func_frequency = frequency
        
    def get_frequency(self) -> float:
        return self.instr.func_frequency
    
    def set_amplitude(self, amplitude:float):
        self.instr.func_amplitude = amplitude
        
    def get_amplitude(self) -> float:
        return self.instr.func_amplitude
    
    def set_dc_offset(self, offset:float):
        self.instr.func_dc_offset = offset
        
    def get_dc_offset(self) -> float:
        return self.instr.func_dc_offset
    
    def set_start_phase(self, phase:float):
        self.instr.func_start_phase = phase
        
    def get_start_phase(self) -> float:
        return self.instr.func_start_phase
    
    def set_output_impedance(self, impedance:float):
        # Only 50 and 75 Ohm supported!
        self.instr.output_impedance = impedance
        
    def get_output_impedance(self) -> float:
        return self.instr.output_impedance
    
    def set_load_impedance(self, impedance:float):
        self.instr.load_impedance = impedance
        
    def get_load_impedance(self) -> float:
        return self.instr.load_impedance
    
    def enable(self, enable: bool):
        self.instr.output_enabled = enable
        if self.log:
            if enable:
                self.logger.info("Output Enabled")
            else:
                self.logger.info("Output Disabled")
    
    def is_enable(self) -> bool:
        return self.instr.output_enabled
        
if __name__ == '__main__':
    import logging

    logger = logging.getLogger('') # Logger is labled as root
    logger.setLevel(logging.INFO)

    # Add File to Logger 
    fh = logging.FileHandler('TestLog.log','w')
    fh.setLevel(logging.INFO)

    # Add Console output to Logger
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Set the format for the logfile and console output
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)
    
    logger.info("Log File created")


    fg0 = PXI_5402('PXI2Slot9', name = 'fgen', selftest=True, reset=True, log=True)
    fg0.set_load_impedance(9999999999.0)#1e99)
    fg0.set_output_impedance(50.0)
    fg0.configure_sin(1.0,1000,0.5,0.0) # 1V Peak_to_Peak output, offset 0.5V (min out = 0V, max out = 1V)
    fg0.enable(True)
    
    input("Wait until user Input")


    fg0.enable(False)
    fg0.close_com()