#!/usr/bin/env python
"""  
Interface to comunicate with the Bench Power Supply E3631A
This Python Moduele is used to simplify the communication with the Power Supply
E3631A. For more information -> see README.md
"""



import pyvisa
import logging

class E3631A():
    
    def __init__(self,address:int, log=False):
        if type(address) != int:
            raise ValueError("address must be of Type int")
        self.rm = pyvisa.ResourceManager()
        self.instr = self.rm.open_resource('GPIB0::'+str(address)+'::INSTR')

        # Test Connection
        self.ID = self.instr.query("*IDN?")
        if not("E3631A" in self.ID):
            raise ValueError("E3631A not found, maybe address was wrong or Device not connected")
        
        self.__enStatus = False

        self.log = log
        if log:
            self.logger = logging.getLogger('E3631A')
            self.logger.info("E3631A Object created")

        self.instr.write("OUTP OFF")
        

    def set_6V(self, voltage:float, ILimit:float=5.0):
        if voltage > 6 or voltage < 0:
            print("Power_Supply: Invalid Voltage, Must be between 0V and 6V, is set to 0")
            voltage = 0
        if ILimit > 5 or ILimit < 0:
            print("Power_Supply: Invalid Current Limit, Must be between 0A and 6A, is set to 0")
            ILimit = 0
        v_string = str(voltage)
        i_string = str(ILimit)
        command = "APPL P6V, " + v_string + ", " + i_string
        self.instr.write(command)
        if self.log:
            self.logger.info("Set 6V output to {v:.2f}V with current limit of {i:2f}A".format(v=voltage,i=ILimit))

    def set_P25V(self, voltage:float, ILimit:float=1.0):
        if voltage > 25 or voltage < 0:
            print("Power_Supply: Invalid Voltage, Must be between 0V and 25V, is set to 0")
            voltage = 0
        if ILimit > 1 or ILimit < 0:
            print("Power_Supply: Invalid Current Limit, Must be between 0A and 1A, is set to 0")
            ILimit = 0
        v_string = str(voltage)
        i_string = str(ILimit)
        command = "APPL P25V, " + v_string + ", " + i_string
        self.instr.write(command)
        if self.log:
            self.logger.info("Set P25V output to {v:.2f}V with current limit of {i:2f}A".format(v=voltage,i=ILimit))

    def set_N25V(self, voltage:float, ILimit:float=1.0):
        if voltage < -25 or voltage > 0:
            print("Power_Supply: Invalid Voltage, Must be between 0V and -25V, is set to 0")
            voltage = 0
        if ILimit > 1 or ILimit < 0:
            print("Power_Supply: Invalid Current Limit, Must be between 0A and 1A, is set to 0")
            ILimit = 0
        v_string = str(voltage)
        i_string = str(ILimit)
        command = "APPL N25V, " + v_string + ", " + i_string
        self.instr.write(command)
        if self.log:
            self.logger.info("Set N25V output to {v:.2f}V with current limit of {i:2f}A".format(v=voltage,i=ILimit))

    def en_output(self, en=True):
        if en == True:
            self.instr.write("OUTP ON")
            self.__enStatus = True
        else:
            self.instr.write("OUTP OFF")
            self.__enStatus = False
        if self.log:
            if en:
                self.logger.info("Alle outputs turned on")
            else:
                self.logger.info("Alle outputs turned off")


    def meas_6V(self):
        command_I = "MEAS:CURR? P6V"
        I = self.instr.query(command_I)
        command_V = "MEAS:VOLT? P6V"
        V = self.instr.query(command_V)

        if self.log:
            self.logger.info("6V output is: {v:.4f}V, {i:.4f}A ".format(v=float(V),i=float(I)))

        return([float(V), float(I)])
    
    def meas_P25V(self):
        command_I = "MEAS:CURR? P25V"
        I = self.instr.query(command_I)
        command_V = "MEAS:VOLT? P25V"
        V = self.instr.query(command_V)

        if self.log:
            self.logger.info("P25V output is: {v:.4f}V, {i:.4f}A ".format(v=V,i=I))
        
        return([float(V), float(I)])
    
    def meas_N25V(self):
        command_I = "MEAS:CURR? N25V"
        I = self.instr.query(command_I)
        command_V = "MEAS:VOLT? N25V"
        V = self.instr.query(command_V)

        if self.log:
            self.logger.info("N25V output is: {v:.4f}V, {i:.4f}A ".format(v=V,i=I))
        
        return([float(V), float(I)])
    
    def display_select(self, select="6V"):
        if select == "6V":
            self.instr.write("INST:SEL P6V")
        elif select == "P25V":
            self.instr.write("INST P25V")
        elif select == "N25V":
            self.instr.write("INST N25V")
        else:
            print("Power_Supply: Invalid display selection")
    
    def __del__(self):
        if self.__enStatus:
            print("Power_Supply: !!!Attention!!! PowerSupply was not turned off!!!")
        self.instr.close()

        if self.log:
            self.logger.info("E3631A Object deleted")


if __name__ == '__main__':
    import time

    PS = E3631A(address=5)

    PS.set_6V(2,0.4)
    PS.set_P25V(5)
    PS.set_N25V(-3)

    


    PS.en_output()
    time.sleep(1)
    

    [V,I] = PS.meas_6V()
    print("Voltage = "+ str(V) + "V, Current = " + str(I*1000)+"mA")
    [V,I] = PS.meas_P25V()
    print("Voltage = "+ str(V) + "V, Current = " + str(I*1000)+"mA")
    [V,I] = PS.meas_N25V()
    print("Voltage = "+ str(V) + "V, Current = " + str(I*1000)+"mA")

    PS.display_select("N25")
    time.sleep(1)
    PS.en_output(False)

    



