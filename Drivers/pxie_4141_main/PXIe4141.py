#!/usr/bin/env python
"""  Interface to comunicate with the SMU PXIe-4141
This Python Moduele is used to simplify the communication with the Source
Measurement Unit (SMU)  PXIe-4141 from National Instrument which is mounted
in the PXI system. For more inforimation -> see README.md
"""


import nidcpower
import numpy as np
import logging

class PXIe4141:
    
    def __init__(self, addr = 'PXI2Slot3', name = 'NoName', selftest=False, reset=False, log=False):
        self.log = log
        if log:
            self.logger = logging.getLogger('SMU')
            self.logger.info("SMU Object created")
        
        self.name = name
        self.addr = addr
        self.instr = None
        self.__open_com(selftest, reset)

    def __open_com(self, with_selftest: bool, with_reset: bool):
        self.instr = nidcpower.Session(self.addr)

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
        
    def set_aperture(self, channel_nr: int, delay: float, aperture_plc: float):
        """
        Sets the aperture time for a specific channel.

        Args:
            channel_nr (int): The channel number.
            delay (float): The delay time in seconds.
            aperture_plc (float): The aperture time in power line cycles (PLC).

        Returns:
            None
        """
        self.instr.channels[channel_nr].abort()
        self.instr.channels[channel_nr].source_delay = delay
        self.instr.channels[channel_nr].configure_aperture_time(aperture_plc, nidcpower.ApertureTimeUnits.POWER_LINE_CYCLES)
        self.instr.channels[channel_nr].initiate()
    
    def configure_channel_vdc(self, channel_nr: int, voltage_range: float, voltage: float,
                              current_limit_low: float, current_limit_high: float):
        self.instr.channels[channel_nr].abort()
        self.instr.channels[channel_nr].power_line_frequency = 50.0
        self.instr.channels[channel_nr].source_mode = nidcpower.SourceMode.SINGLE_POINT
        self.instr.channels[channel_nr].output_function = nidcpower.OutputFunction.DC_VOLTAGE
        self.instr.channels[channel_nr].instrument_mode = nidcpower.InstrumentMode.SMU_PS
        self.instr.channels[channel_nr].measure_when = nidcpower.MeasureWhen.ON_DEMAND
        self.instr.channels[channel_nr].dc_noise_rejection = nidcpower.DCNoiseRejection.NORMAL
        # self.instr.channels[channel_nr].cable_length = nidcpower.CableLength.NI_STANDARD_2M # Not supported
        self.instr.channels[channel_nr].auto_zero = nidcpower.AutoZero.OFF # Only OFF is supported!
        
        # Voltage Range
        self.instr.channels[channel_nr].voltage_level_autorange = False
        self.instr.channels[channel_nr].voltage_level_range = voltage_range
        
        # Voltage
        self.instr.channels[channel_nr].voltage_level = voltage
        
        # Current Compliance
        self.instr.channels[channel_nr].sense = nidcpower.Sense.REMOTE
        self.instr.channels[channel_nr].compliance_limit_symmetry = nidcpower.ComplianceLimitSymmetry.ASYMMETRIC
        self.instr.channels[channel_nr].current_limit_autorange = False
        self.instr.channels[channel_nr].current_limit_range = max([abs(current_limit_low), abs(current_limit_high)])
        self.instr.channels[channel_nr].current_limit_low = current_limit_low
        self.instr.channels[channel_nr].current_limit_high = current_limit_high
        
        self.instr.channels[channel_nr].initiate()
        
    def configure_channel_idc(self, channel_nr: int, current_range: float, current: float,
                              voltage_limit_low: float, voltage_limit_high: float):
        self.instr.channels[channel_nr].abort()
        self.instr.channels[channel_nr].power_line_frequency = 50.0
        self.instr.channels[channel_nr].source_mode = nidcpower.SourceMode.SINGLE_POINT
        self.instr.channels[channel_nr].output_function = nidcpower.OutputFunction.DC_CURRENT
        self.instr.channels[channel_nr].instrument_mode = nidcpower.InstrumentMode.SMU_PS
        self.instr.channels[channel_nr].measure_when = nidcpower.MeasureWhen.ON_DEMAND
        self.instr.channels[channel_nr].dc_noise_rejection = nidcpower.DCNoiseRejection.NORMAL
        # self.instr.channels[channel_nr].cable_length = nidcpower.CableLength.NI_STANDARD_2M # Not supported
        self.instr.channels[channel_nr].auto_zero = nidcpower.AutoZero.OFF # Only OFF is supported!
        
        # Current Range
        self.instr.channels[channel_nr].current_level_autorange = False
        self.instr.channels[channel_nr].current_level_range = current_range
        
        # Current
        self.instr.channels[channel_nr].current_level = current
        
        # Voltage Compliance
        self.instr.channels[channel_nr].sense = nidcpower.Sense.REMOTE
        self.instr.channels[channel_nr].compliance_limit_symmetry = nidcpower.ComplianceLimitSymmetry.ASYMMETRIC
        self.instr.channels[channel_nr].voltage_limit_autorange = False
        self.instr.channels[channel_nr].voltage_limit_range = max([abs(voltage_limit_low), abs(voltage_limit_high)])
        self.instr.channels[channel_nr].voltage_limit_low = voltage_limit_low
        self.instr.channels[channel_nr].voltage_limit_high = voltage_limit_high
        
        self.instr.channels[channel_nr].initiate()
        
    def set_voltage(self, channel_nr: int, voltage: float, enable : bool):
        # output_connected : Not supported
        self.instr.channels[channel_nr].voltage_level = voltage
        self.instr.channels[channel_nr].output_enabled = enable
        
    def set_current(self, channel_nr: int, current: float, enable : bool):
        # output_connected : Not supported
        self.instr.channels[channel_nr].current_level = current
        self.instr.channels[channel_nr].output_enabled = enable
        
    def enable(self, channel_nr, enable: bool):
        self.instr.channels[channel_nr].output_enabled = enable
        if self.log:
            if enable:
                self.logger.info("Channel {nr} was enabled".format(nr = channel_nr))
            else:
                self.logger.info("Channel {nr} was disabled".format(nr = channel_nr))

    def enable_all(self, enable: bool):
        for channel_nr in range(0, self.instr.channel_count-1):
            self.instr.channels[channel_nr].output_enabled = enable
        if self.log:
            if enable:
                self.logger.info("All Channels were enabled")
            else:
                self.logger.info("All Channels were disabled")
        
    def measure(self, channel_nr: int) -> float:
        st = self.instr.channels[channel_nr].measure_multiple()
        resistance = st[0].voltage/st[0].current
        power = st[0].voltage*st[0].current
        if self.is_output_function_dc_voltage(channel_nr):
            mode = 'VDC'
        elif self.is_output_function_dc_current(channel_nr):
            mode = 'IDC'
        else:
            mode = 'UNDEF'  
        enable = self.is_enable(channel_nr)
        tripped = self.is_tripped(channel_nr)

        if self.log:
            self.logger.info("Measure: Ch{nr}, V={v:.4f}V, I={i:.4f}A, R={r:.4f}Ohm, P={p:.4f}W: mode={mode:s}".format(nr=st[0].channel[-1], 
                                                                                                                      v=st[0].voltage,
                                                                                                                      i=st[0].current,
                                                                                                                      r=resistance,
                                                                                                                      p=power,
                                                                                                                      mode=mode))
            if tripped:
                self.logger.info("Output is tripped!")
        return [st[0].voltage, st[0].current, resistance, power, mode, enable, tripped]
    
    
    def is_task_running(self, channel_nr: int) -> bool:
        try:
            return self.is_in_voltage_mode(channel_nr) or self.is_in_current_mode(channel_nr)
        except:
            return False
        
    def is_enable(self, channel_nr: int) -> bool:
        return self.instr.channels[channel_nr].output_enabled
        
    def is_tripped(self, channel_nr: int) -> bool: #is_in_compliance
        if self.is_enable(channel_nr):
            return self.instr.channels[channel_nr].query_in_compliance()
        else:
            return False
    
    def is_in_voltage_mode(self, channel_nr: int) -> bool:
        return self.instr.channels[channel_nr].query_output_state(nidcpower.OutputStates.VOLTAGE)
    
    def is_in_current_mode(self, channel_nr: int) -> bool:
        return self.instr.channels[channel_nr].query_output_state(nidcpower.OutputStates.CURRENT)

    def is_output_function_dc_voltage(self, channel_nr: int) -> bool:
        output_function = self.instr.channels[channel_nr].output_function
        return output_function == nidcpower.OutputFunction.DC_VOLTAGE
    
    def is_output_function_dc_current(self, channel_nr: int) -> bool:
        output_function = self.instr.channels[channel_nr].output_function
        return output_function == nidcpower.OutputFunction.DC_CURRENT
       
    def __close_com(self):
        self.instr.abort()
        self.instr.close()

    def __del__(self):
        self.__close_com()
        self.logger.info("Object Deleted")

    def configure_channel_sine(self, channel_nr: int,
                               frequency: float,
                               amplitude: float, # not peak to peak (peak to peak = amplitude x 2)
                               offset: float, 
                               current_limit_low: float, 
                               current_limit_high: float):
        # Configures the channel to be a sine source with fixed characteristics


        # Calculate voltage range
        voltage_range = offset + amplitude + 0.1
        
        self.instr.channels[channel_nr].abort()
        self.instr.channels[channel_nr].power_line_frequency = 50.0
        self.instr.channels[channel_nr].source_mode = nidcpower.SourceMode.SEQUENCE

        self.instr.channels[channel_nr].output_function = nidcpower.OutputFunction.DC_VOLTAGE
        self.instr.channels[channel_nr].instrument_mode = nidcpower.InstrumentMode.SMU_PS
        self.instr.channels[channel_nr].measure_when = nidcpower.MeasureWhen.ON_DEMAND
        self.instr.channels[channel_nr].dc_noise_rejection = nidcpower.DCNoiseRejection.NORMAL
        self.instr.channels[channel_nr].auto_zero = nidcpower.AutoZero.OFF # Only OFF is supported!
        
        # Voltage Range
        self.instr.channels[channel_nr].voltage_level_autorange = False
        self.instr.channels[channel_nr].voltage_level_range = voltage_range
        
        # Current Compliance
        self.instr.channels[channel_nr].sense = nidcpower.Sense.REMOTE
        self.instr.channels[channel_nr].compliance_limit_symmetry = nidcpower.ComplianceLimitSymmetry.ASYMMETRIC
        self.instr.channels[channel_nr].current_limit_autorange = False
        self.instr.channels[channel_nr].current_limit_range = max([abs(current_limit_low), abs(current_limit_high)])
        self.instr.channels[channel_nr].current_limit_low = current_limit_low
        self.instr.channels[channel_nr].current_limit_high = current_limit_high

        # self.instr.channels[channel_nr].create_advanced_sequence(sequence_name="Sine Channel"+str(channel_nr),property_names=["voltage_level"],set_as_active_sequence=True)
        # self.instr.channels[channel_nr].create_advanced_sequence_commit_step()
        
        # List of values for 50 periods
               
        Ts = 12e-6

        T = 1/frequency
        # T = Ts*100
        numSamples = int(22*(T/Ts)) 
        print("numSamples =",numSamples)
        values = np.zeros(numSamples)
        t = np.arange(0,numSamples*Ts,Ts)

        frequency = 1/T

        
        
        values = offset + np.sin(2*np.pi*frequency*t)*amplitude
            
        # self.instr.channels[channel_nr].current_gain_bandwidth = 2e6
        # self.instr.channels[channel_nr].transient_response = nidcpower.TransientResponse.FAST

        self.instr.channels[channel_nr].sequence_loop_count_is_finite = False

        self.instr.channels[channel_nr].set_sequence(values=values,source_delays=np.ones(numSamples)*100e-9) # maybe source_delay should be a list

        

        self.instr.channels[channel_nr].sequence_step_delta_time = Ts
        self.instr.channels[channel_nr].sequence_step_delta_time_enabled = True

        
        # self.instr.channels[channel_nr].initiate()

        pass

    def enable_sine(self, channel_nr: int, enable: bool):
        # self.instr.channels[channel_nr].sequence_step_delta_time_enabled = enable
        # time.sleep(2)
        if enable:
            self.instr.channels[channel_nr].initiate()
        else:
            self.instr.channels[channel_nr].abort()
            


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

    smu0 = PXIe4141('PXI2Slot3', name = 'smu', selftest=True,reset=True,log=True)

    
    smu0.set_aperture(1, 0.001, 2)
    smu0.configure_channel_vdc(1, 2.0, 1.0, -0.001, 0.0025)
    smu0.enable(1, True)

    smu0.measure(1)
    smu0.set_voltage(1, 2.0, True)
    smu0.measure(1)
    smu0.set_voltage(1, 3.0, True)
    smu0.measure(1)
    smu0.enable(1, False)
    
    smu0.set_aperture(0, 0.001, 2)
    smu0.set_aperture(1, 0.001, 2)
    smu0.configure_channel_vdc(0, 2.0, 1.0, -0.001, 0.0025)
    smu0.configure_channel_idc(1, 0.002, 0.001, -2, 2)
    smu0.enable(0, True)
    smu0.enable(1, True)
    
    smu0.measure(0)
    smu0.measure(1)
    smu0.set_voltage(0, 2.0, True)
    smu0.set_current(1, 0.002, True)
    smu0.measure(0)
    smu0.measure(1)
    smu0.enable(0, False)
    smu0.enable(1, False)


    
