#!/usr/bin/env python
"""  Interface to comunicate with the Scope PXI-5142 This Python Module is 
used to simplify the communication with the Scope PXI-5142 from National 
Instrument which is mounted in the PXI system. 
For more inforimation -> see README.md

There are some functions included only as comments. These are there to easily
include in this class but are not ported to the new style and are not tested
"""


import niscope
import logging
import numpy as np

import math
import hightime
import time


class PXI_5142:
    
    NISCOPE_VAL_BANDWIDTH_FULL              =        -1.0
    NISCOPE_VAL_BANDWIDTH_DEVICE_DEFAULT    =         0.0
    NISCOPE_VAL_20MHZ_BANDWIDTH             =  20000000.0
    NISCOPE_VAL_100MHZ_BANDWIDTH            = 100000000.0
    NISCOPE_VAL_20MHZ_MAX_INPUT_FREQUENCY   =  20000000.0
    NISCOPE_VAL_100MHZ_MAX_INPUT_FREQUENCY  = 100000000.0
    #                                       =  35000000.0
    
    def __init__(self, addr = 'PXI2Slot7', name = 'NoName', selftest=False, reset=False, log=False):
        self.log = log
        if log:
            self.logger = logging.getLogger("Scope")
            self.logger.info("Scope Object created")

        self.name = name
        self.addr = addr
        self.instr = None

        self.__open_com(selftest,reset)

    def __open_com(self, with_selftest: bool, with_reset: bool):
        #options = '' #{'simulate': False, 'driver_setup': {'Model': '4141', 'BoardType': 'PXIe', }, }
        self.instr = niscope.Session(self.addr) #, options)
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
        
    # def abort(self):
    #     self.instr.abort()
        
    # def autosetup(self):
    #     self.instr.auto_setup()
        
    def configure_vertical(self, channel_nr:int, vrange:float, coupling:str, offset:float, probe_attenuation:float, enabled:bool):
        coupling = niscope.VerticalCoupling[coupling]
        self.instr.channels[channel_nr].configure_vertical(vrange, coupling, 
                                                           offset=offset, 
                                                           probe_attenuation=probe_attenuation, 
                                                           enabled=enabled)

    def configure_horizontal(self, min_sample_rate:float, min_num_pts:int, num_records:int):
        ref_position = 50.0
        enforce_realtime = True
        self.instr.configure_horizontal_timing(min_sample_rate, min_num_pts, ref_position, num_records, enforce_realtime)

    def configure_chan_characteristics(self, channel_nr:int, input_impedance:float, max_input_frequency:float ):
        self.instr.channels[channel_nr].configure_chan_characteristics(input_impedance, max_input_frequency)

    def configure_trigger_edge(self, trigger_source_channel_nr:int, trigger_coupling:str, level:float, slope:str):
        trigger_source = self.addr + '/' + str(trigger_source_channel_nr)
        trigger_coupling = niscope.TriggerCoupling[trigger_coupling]
        slope = niscope.TriggerSlope[slope]
        holdoff = hightime.timedelta(seconds=0.0)
        delay = hightime.timedelta(seconds=0.0)
        self.instr.configure_trigger_edge(trigger_source, level, trigger_coupling, slope=slope, holdoff=holdoff, delay=delay)

    def initiate(self):
        self.instr.commit()
        self.instr.initiate()

    def wait_until_acquisition_done(self, max_sec:int):
        i = 0
        while not (self.is_acquisition_done() or (i >= max_sec*10)):
            time.sleep(0.1); i = i + 1
        if not self.is_acquisition_done():
            if self.log:
                self.logger.info("acquisition is not done!!!!")

    def is_acquisition_done(self) -> bool:
        return self.instr.acquisition_status() == niscope.AcquisitionStatus.COMPLETE

    def measure(self, channel_nr:int, record_number:int) -> float:
        horz_sample_rate = self.instr.horz_sample_rate
        num_channels = 1
        num_samples = self.instr.horz_min_num_pts
        num_records = 1
        
        dt = 1/horz_sample_rate
        t_min = -num_samples/2*dt
        t_max = num_samples/2*dt
        time = np.linspace(t_min, t_max, num=num_samples)
        waveform = np.ndarray(num_channels * num_samples * num_records, dtype=np.float64)
        relative_to = niscope.FetchRelativeTo.PRETRIGGER #PRETRIGGER # READ_POINTER PRETRIGGER NOW START TRIGGER
        offset = 0 # Offset in samples
        timeout = hightime.timedelta(seconds=5.0)
        #self.instr.channels[channel_nr].fetch_into(waveform, num_records=num_records)
        self.instr.channels[channel_nr].fetch_into(waveform, 
                                                   relative_to=relative_to, 
                                                   offset=offset, 
                                                   record_number=record_number, 
                                                   num_records=num_records, 
                                                   timeout=timeout)
        return [time, waveform]

    def configure_simple_ac(self, amplitude_to_meas:float, freq_to_meas:float, nr_of_periods:int, num_records:int, sample_rate:float,trigger=0,hysteresis=None,triggerlevel=0):
        if type(amplitude_to_meas) == list:
            vrange0 = amplitude_to_meas[0]
            vrange1 = amplitude_to_meas[1]
        else:
            vrange0 = amplitude_to_meas
            vrange1 = amplitude_to_meas    
        dt = 1/sample_rate
        meas_time = 1/freq_to_meas*nr_of_periods
        num_pts = math.ceil(meas_time/dt)
        self.configure_vertical(channel_nr=0, vrange=vrange0, coupling='AC', offset=0, probe_attenuation=1.0, enabled=True)
        self.configure_vertical(channel_nr=1, vrange=vrange1, coupling='AC', offset=0, probe_attenuation=1.0, enabled=True)
        self.configure_horizontal(min_sample_rate=sample_rate, min_num_pts=num_pts, num_records=num_records)
        self.configure_chan_characteristics(channel_nr=0, input_impedance=1000000.0, max_input_frequency=100e3) #self.NISCOPE_VAL_20MHZ_MAX_INPUT_FREQUENCY
        self.configure_chan_characteristics(channel_nr=1, input_impedance=1000000.0, max_input_frequency=100e3)
        self.configure_trigger_edge(trigger_source_channel_nr=trigger, trigger_coupling='DC', level=triggerlevel, slope='POSITIVE')
        trigger_source = self.addr + '/' + str(trigger)
        if hysteresis != None:
            self.instr.configure_trigger_hysteresis(trigger_source=trigger_source,level=0,hysteresis=hysteresis,trigger_coupling=niscope.TriggerCoupling['DC'])

        self.initiate()

    def __close_com(self):
        self.instr.abort()
        self.instr.close()

    def __del__(self):
        self.__close_com()
        if self.log:
            self.logger.info("Object Deleted")
    def trigger(self):
        # self.instr.channels[0].configure_trigger_immediate()
        self.instr.configure_trigger_software(holdoff=0, delay=0)
        


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

    import matplotlib.pyplot as plt
    
    sc0 = PXI_5142('PXI2Slot7', name = 'scope', selftest=True, reset=True, log=True)
    
    vrange = 2.0
    freq_to_meas = 1000
    nr_of_periods = 10
    num_records = 100
    #amplitude_to_meas is the peak voltage (not peak to peak)
    if 0:
        sc0.configure_simple_ac(amplitude_to_meas=1.1, freq_to_meas=10e3, nr_of_periods=3, num_records=1, sample_rate=10e6,hysteresis=None)
        
        
        sc0.wait_until_acquisition_done(1)
    sc0.configure_vertical(channel_nr=0, vrange=0.2, coupling='AC', offset=0, probe_attenuation=1.0, enabled=True)
    sc0.trigger()
    # sc0.configure_trigger_immediate() #https://nimi-python.readthedocs.io/en/1.2.1/niscope/class.html
    sc0.wait_until_acquisition_done(2)
    record_number = 0
    [t, waveform] = sc0.measure(channel_nr=0, record_number=record_number)
    plt.plot(t, waveform)
    plt.grid()
    plt.show()
    
    
