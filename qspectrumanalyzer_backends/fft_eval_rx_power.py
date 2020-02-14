import subprocess, pprint, shlex

import numpy as np
from Qt import QtCore

from qspectrumanalyzer.backends import BaseInfo, BasePowerThread

class Info(BaseInfo):
    """fft_eval_rx_power device metadata"""
    pass


class PowerThread(BasePowerThread):
    """Thread which runs fft_eval_rx_power process"""
    def setup(self, start_freq, stop_freq, bin_size, interval=10.0, gain=-1, ppm=0, crop=0,
              single_shot=False, device=0, sample_rate=2560000, bandwidth=0, lnb_lo=0):
        """Setup fft_eval_rx_power params"""
        self.params = {
            "start_freq": start_freq,
            "stop_freq": stop_freq,
            "bin_size": bin_size,
            "interval": interval,
            "device": device,
            "hops": 0,
            "gain": gain,
            "ppm": ppm,
            "crop": crop,
            "single_shot": single_shot
        }

        self.min_freq = 10000000000
        self.databuffer = {}
        self.last_timestamp = ""

        print("fft_eval_rx_power params:")
        pprint.pprint(self.params)
        print()

    def process_start(self):
        """Start fft_eval_rx_power process"""
        if not self.process and self.params:
            settings = QtCore.QSettings()
            cmdline = shlex.split(settings.value("executable", "fft_eval_rx_power"))

            self.process = subprocess.Popen(cmdline, stdout=subprocess.PIPE,
                                            universal_newlines=True)

    def parse_output(self, line):
        """Parse one line of output from fft_eval_rx_power"""

        line = [col.strip() for col in line.split(",")]
        
        if line and line != '':
            print(line)
            timestamp = " ".join(line[:2])
            if line[2]:
                start_freq = int(line[2])
                if line[2]:
                    stop_freq = int(line[3])
                    if line[4]:
                        step = float(line[4])
                        if line[5]:
                            samples = float(line[5])

                            x_axis = list(np.arange(start_freq, stop_freq, step))
                            y_axis = [float(y) for y in line[6:]]
                            if len(x_axis) != len(y_axis):
                                print("ERROR: len(x_axis) != len(y_axis)!")
                                if len(x_axis) > len(y_axis):
                                    print("Trimming x_axis...")
                                    x_axis = x_axis[:len(y_axis)]
                                else:
                                    print("Trimming y_axis...")
                                    y_axis = y_axis[:len(x_axis)]
                                    
                            if self.min_freq <= start_freq:
                                self.min_freq = start_freq
                                self.data_storage.update(self.databuffer)                                

                            if timestamp != self.last_timestamp:
                                self.last_timestamp = timestamp
                                self.databuffer = {"timestamp": [], "x": [], "y": []}
                        
                            self.databuffer = {"timestamp": timestamp,
                                                "x": x_axis,
                                                "y": y_axis}
                            
                            self.databuffer["x"].extend(x_axis)
                            self.databuffer["y"].extend(y_axis)
                            
                            #self.data_storage.update(self.databuffer)
