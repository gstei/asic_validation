# -*- coding: utf-8 -*-
"""
Created on Mon Sep 12 11:27:52 2022
@author: roman.willi
"""
import pyvisa
import time
from metric import to_si


class TP04300:
    
    dutSensorType = ["no DUT sensor", "type T thermocouple", "type K thermocouple", "RTD", "diode"]
    dutType = ["Smallest DUT mass", "1-Larger DUT mass", "2-Larger DUT mass", "3-Larger DUT mass", "System Derived", "Box"]
    dutMode = ["air control", "dut control", "TC Meter mode"]
    
    def __init__(self, name = 'NoName', addr = 'GPIB1::20::INSTR'):
        "This is a TP04300 class"
        self.addr = addr
        self.name = name
        self.rm = pyvisa.ResourceManager()
        self.tesr = 0
    
    def open_com(self, with_selftest: bool, with_reset: bool, ploton: bool):
        self.my_instrument = self.rm.open_resource(self.addr)
        self.my_instrument.clear()
        if ploton:
            idn = self.my_instrument.query('*IDN?')
            idn = idn.replace("\n", "")
            idn = idn.replace("\r", "")
            print(f'Name: {self.name}, Addr: {self.addr}, IDN: {idn}')
        if with_selftest:
            self.selftest(with_reset)
    
    def selftest(self, with_reset: bool):
        if bool(int(self.my_instrument.query('*TST?'))):
            raise Exception("selftest fail")
        if with_reset:
            self.reset()
    
    def reset(self):
        self.my_instrument.write('*RST')
        self.my_instrument.write('*CLS')
        
    def close_com(self):
        self.rm.close()
    
    def rstOperatorScreen(self):
        self.my_instrument.write('RSTO')
        time.sleep(5)

    def getStatus(self) -> int:
        """Read the status byte.
            bit 7 - ready
            bit 6 - master summary status (MSS) bit
            bit 5 - standard event status (ESB) summary bit
            bit 4 - message available (MAV) (GPIB only, always 0 for RS-232)
            bit 3 - temperature event (TESR) summary bit
            bit 2 - device specific error (EROR) summary bit
            bit 1 - not used (always 0)
            bit 0 - not used (always 0)"""
        stbx = self.my_instrument.query('*STB?')
        return int(stbx.strip())
    
    def getError(self) -> int:
        """ bit 15 – reserved
            bit 14 – no DUT sensor selected
            bit 13 – improper software version
            bit 12 – reserved
            bit 11 – reserved
            bit 10 – purge heat failure
            bit 9 -- flow sensor hardware error
            bit 8 – DUT open loop
            bit 7 -- internal error
            bit 6 – open purge temperature sensor
            bit 5 – no purge flow
            bit 4 -- low input air pressure
            bit 3 -- low flow
            bit 2 – setpoint out of range
            bit 1 -- air open loop
            bit 0 – overheat """
        err = self.my_instrument.query('EROR?')
        return int(err)
        
    def isOpen(self) -> bool:
        "my_list = self.rm.list_opened_resources()"
        return self.my_instrument.session > 0
    
    def setup(self, dutSensorType:int , dutType:int, dutMode:int, dutThermalConstant:int, maxTemperatureError:float, soakTime:int, llim: int, ulim: int):
        self.setDutSensorType(dutSensorType)
        self.setDutType(dutType)
        self.setDutMode(dutMode)
        self.setDutThermalConstant(dutThermalConstant)
        self.setSoakTime(soakTime)
        self.setSetpointWindow(maxTemperatureError)
        self.setTemperatureLimits(llim, ulim)
        
    def setTemperatureLimits(self, llim: int, ulim: int):
        """Set the lower air temperature limit."""
        self.my_instrument.write(f"LLIM {int(llim)}")
        """Set the lower air temperature limit."""
        self.my_instrument.write(f"ULIM {int(ulim)}")
    
    def setDutSensorType(self, dutSensorType: int):
        """0 – no DUT sensor
        1 – type T thermocouple
        2 – type K thermocouple
        3 – RTD
        4 – diode """
        self.my_instrument.write(f"DSNS {int(dutSensorType)}")
        
    def setDutType(self, dutType: int):
        """ 0-Smallest DUT mass
            example: a 28 pin, 350 mil, ceramic or plastic device
            1-Larger DUT mass
            example: a 32 pin, 400 mil ceramic or plastic device
            2-Larger DUT mass
            example: a 68 pin PLCC plastic device.
            3-Largest DUT mass. 
            use for larger hybrid chips.
            4- System Derived. 
            Use this parameter to Auto-tune the DUT
            5- Box 
            use with Temptronic ThermoChambers """
        self.my_instrument.write(f"DTYP {int(dutType)}")
        
    def setDutMode(self, dutMode: int):
        """ Turn DUT mode on or off.
        DUTM 0 -- off (air control)
        DUTM 1 -- on (DUT control)
        DUTM 2 -- TC Meter mode """
        self.my_instrument.write(f"DUTM {int(dutMode)}")
    
    def setDutThermalConstant(self, dutc:int):
        """Set the device thermal constant.
        DUTC nominally 100 but can range from 20 to 500.
        NOTE: Use a higher number for a higher mass device, and to
        reduce the amount of overshoot. A lower number may cause some
        overshoot, but may also reduce the transition time """
        self.my_instrument.write(f"DUTC {int(dutc)}")
    
    def headDown(self, down:bool):
        self.my_instrument.write(f"HEAD {int(down)}")
        
    def headLock(self, lock:bool):
        self.my_instrument.write(f"HDLK {int(lock)}")
    
    def flow(self, on:bool):
        self.my_instrument.write(f"FLOW {int(on)}")
    
    def setPoint(self, temperature:float):
        self.my_instrument.write("SETN 0")
        self.my_instrument.write(f"SETP {round(temperature,1)}")

    def setSoakTime(self, soakTime:int):
        self.my_instrument.write("SETN 0")
        self.my_instrument.write(f"SOAK {int(soakTime)}")

    #def setMaxTestTime(self, testTime):
    #    self.my_instrument.write(f"TTIM {int(testTime)}")
        
    def setSetpointWindow(self, maxTemperatureError: float):
        self.my_instrument.write(f"WNDW {round(maxTemperatureError,1)}")
        
    def waitUntilHeadDownManual(self, lock):
        if self.isHeadLocked():
            print("Head is locked")                
        elif self.isHeadDown():
            print("Head is down")
        else:
            print("Put the head down manually...")
            while not self.isHeadDown():
                time.sleep(0.5)
            print("Head is down")
        self.headLock(lock)

    def getDutSensorType(self) -> int:
        DutSensorTyp = self.my_instrument.query('DSNS?')
        return int(DutSensorTyp)
    
    def getDutType(self) -> int:
        dutType = self.my_instrument.query('DTYP?')
        return int(dutType)
    
    def getDutMode(self) -> int:
        dutMode = self.my_instrument.query('DUTM?')
        return int(dutMode)
    
    def getDutThermalConstant(self) -> int:
        dutc = self.my_instrument.query('DUTC?')
        return int(dutc)
    
    def getAirTemperature(self) -> float:
        """ always return air temperature (without offset) """
        temperature = self.my_instrument.query('TMPA?')
        return float(temperature.strip())
    
    def getDutTemperature(self) -> float:
        """ always return DUT temperature (without offset) """
        temperature = self.my_instrument.query('TMPD?')
        return float(temperature.strip())
    
    def getDutTemperature_and_plot(self, name:str) -> float:
        """ always return DUT temperature (without offset) """
        temperature = self.getDutTemperature()
        print(name + ' = ' + to_si(temperature) + '°C')
        return temperature
    
    def getAirTemperaturLimit(self) -> int:
        llimit = int(float(self.my_instrument.query('LLIM?')))
        ulimit = int(float(self.my_instrument.query('ULIM?')))
        return [llimit, ulimit]
    
    def getSetpointWindow(self) -> float:
        maxTemperatureError = self.my_instrument.query("WNDW?")
        return float(maxTemperatureError)
    
    def getSetpoint(self) -> float:
        self.my_instrument.write("SETN 0")
        setpoint = self.my_instrument.query('SETP?')
        return float(setpoint)
    
    def getSoakTime(self) -> int:
        self.my_instrument.write("SETN 0")
        soak = self.my_instrument.query('SOAK?')
        return int(soak)
    
    def isHeadDown(self) -> bool:
        head = self.my_instrument.query("HEAD?")
        return bool(int(head))
    
    def isHeadLocked(self) -> bool:
        lock = self.my_instrument.query("HDLK?")
        return bool(int(lock))
    
    def isFlowOn(self) -> bool:
        flowOn = self.my_instrument.query('FLOW?')
        return bool(int(flowOn))

    def isSoakTimeElapsed(self) -> bool:
        self.tesr = int(self.my_instrument.query('TESR?'))
        return (self.tesr & 1) > 0
    
    def isAtTemperature(self) -> bool:
        tecr = int(self.my_instrument.query('TECR?'))
        return (tecr & 2) == 0

    def isTestTimeElapsed(self) -> bool:
        tecr = int(self.my_instrument.query('TECR?'))
        return (tecr & 4) > 0

    def setPointAndWait(self, temperature:float, printOn:bool):
        self.isSoakTimeElapsed()
        
        
        self.my_instrument.write("SETN 0")
        self.my_instrument.write(f"SETP {round(temperature,1)}")
        window = self.getSetpointWindow()
        setpoint = self.getSetpoint()
        dutMode = self.getDutMode()
        soakOk = False
        while (not soakOk):
            time.sleep(0.5)
            soakOk = self.isSoakTimeElapsed()
            if dutMode == TP04300.dutMode.index("dut control"):
                temp = self.getDutTemperature()
            elif dutMode == TP04300.dutMode.index("air control"):
                temp = self.getAirTemperature()                
            else:
                raise Exception("dut mode not supported")
            tempInWindow = abs(setpoint-temp) <= window
            if printOn:
                print(f"SetPoint: {temperature} Air: {self.getAirTemperature()} Dut: {self.getDutTemperature()} TempinWindow: {int(tempInWindow)} isAtTemp: {int(self.isAtTemperature())} \tisSoakTime: {int(soakOk)}")

    def to_string(self):
        print(f"Name: {self.name}")
        print(f"Addr: {self.addr}")
        print(f"Open: {self.isOpen()}")
        if self.isOpen():
            idn = self.my_instrument.query('*IDN?')
            idn = idn.replace("\n", "")
            idn = idn.replace("\r", "")
            print(f"IDN: {idn.strip()}")
            print(f"Status: {bin(self.getStatus())}")
            print(f"Error: {bin(self.getError())}")
            print(f"Head down: {self.isHeadDown()}")
            print(f"Head locked: {self.isHeadLocked()}")
            print(f"Flow on: {self.isFlowOn()}")
            print(f"Dut Sensor Type: {TP04300.dutSensorType[self.getDutSensorType()]}")
            print(f"Dut Type: {TP04300.dutType[self.getDutType()]}")
            print(f"Dut Mode: {TP04300.dutMode[self.getDutMode()]}")
            print(f"Dut Thermal Constant: {self.getDutThermalConstant()}")
            print(f"Max Setpoint Temperature Error: {self.getSetpointWindow()}")
            print(f"Soak Time: {self.getSoakTime()}")
            print(f"Air Temperature Limit: {self.getAirTemperaturLimit()}")
            print(f"Air Temperature: {self.getAirTemperature()}")
            print(f"Dut Temperature: {self.getDutTemperature()}")
            print(f"SetPoint: {self.getSetpoint()} \tisAtTemp: {int(self.isAtTemperature())}")