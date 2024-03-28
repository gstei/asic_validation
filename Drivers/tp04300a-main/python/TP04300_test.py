# -*- coding: utf-8 -*-
from TP04300 import TP04300

ploton = True
with_selftest = True
with_reset = True
TP04300_obj = TP04300('Elefant', 'GPIB1::9::INSTR')
TP04300_obj.open_com(with_selftest, with_reset, ploton)
#TP04300_obj.headLock(False)
TP04300_obj.headDown(False)
TP04300_obj.flow(False)
TP04300_obj.reset()
TP04300_obj.setup(TP04300.dutSensorType.index("type K thermocouple"), 
    TP04300.dutType.index("Smallest DUT mass"), 
    TP04300.dutMode.index("dut control"), 
    dutThermalConstant = 20, 
    maxTemperatureError = 0.4, 
    soakTime = 5, llim = -15, ulim = 100)
TP04300_obj.to_string()

#TP04300_obj.waitUntilHeadDownManual(True)
TP04300_obj.flow(True)

TP04300_obj.setPointAndWait(10, ploton)
TP04300_obj.setPointAndWait(-10.58, ploton)
TP04300_obj.setPointAndWait(50, ploton)

TP04300_obj.flow(False)
#TP04300_obj.headLock(False)
TP04300_obj.headDown(False)
TP04300_obj.close_com()