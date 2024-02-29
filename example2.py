import argparse
import niscope
import nitclk
import sys
import time
import numpy as np
import matplotlib.pyplot as plt

def example(resource_name1, resource_name2, options):
    with niscope.Session(resource_name=resource_name1, options=options) as session1, niscope.Session(resource_name=resource_name2, options=options) as session2:
        session_list = [session1, session2]
        for session in session_list:
            session.configure_vertical(range=5.0, coupling=niscope.VerticalCoupling. DC)
            session.configure_horizontal_timing(min_sample_rate=50000000, min_num_pts=1000, ref_position=50.0, num_records=1, enforce_realtime=True)
        session1.trigger_type = niscope.TriggerType.SOFTWARE
        nitclk.configure_for_homogeneous_triggers(session_list)
        nitclk.synchronize(session_list, 200e-9)
        nitclk.initiate(session_list)
        time.sleep(2)
        session1.send_software_trigger_edge(niscope.WhichTrigger.START)
        waveforms1 = session2.channels[0].fetch(num_samples=1000)
        waveforms2 = session2.channels[1].fetch(num_samples=1000)
        waveforms3 = session1.channels[0].fetch(num_samples=1000)
        waveforms4 = session1.channels[1].fetch(num_samples=1000)
        waveform1= np.array(waveforms1[0].samples.obj)
        waveform2= np.array(waveforms2[0].samples.obj)
        waveform3= np.array(waveforms3[0].samples.obj)
        waveform4= np.array(waveforms4[0].samples.obj)
        plt.plot(waveform1, label="1")
        plt.plot(waveform2, label="2")
        plt.plot(waveform3, label="3")
        plt.plot(waveform4, label="4")
        plt.legend()
        plt.show()
        for i in range(len(waveforms)):
            print('Waveform {0} information:'.format(i))
            print(str(waveforms[i]) + '\n\n')


def _main(argsv):
    parser = argparse.ArgumentParser(description='Synchronizes multiple instruments to one trigger.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-n1', '--resource-name1', default='PXI2Slot8', help= 'Resource name of a NI Digitizer')
    parser.add_argument('-n2', '--resource-name2', default='PXI2Slot7', help= 'Resource name of a NI Digitizer')
    parser.add_argument('-op', '--option-string', default='', type=str, help='Option string')
    args = parser.parse_args(argsv)
    example(args.resource_name1, args.resource_name2, args.option_string)
    
def main():
    _main(sys.argv[1:])


def test_example():
    # options = {'simulate': True, 'driver_setup': {'Model': '5164', 'BoardType': 'PXIe', }, }
    options = {'simulate': False, 'driver_setup': {'Model': '5142', 'BoardType': 'PXIe', },}
    example('PXI2Slot8', 'PXI2Slot7', options)


def test_main():
    cmd_line = ['--option-string', 'Simulate=1, DriverSetup=Model:5163; BoardType:PXIe', ]
    _main(cmd_line)


if __name__ == '__main__':
    test_example()