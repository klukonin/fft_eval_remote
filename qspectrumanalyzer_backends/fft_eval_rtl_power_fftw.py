import subprocess, math, pprint, shlex

from Qt import QtCore
import numpy as np
from qspectrumanalyzer.backends import BaseInfo, BasePowerThread


class Info(BaseInfo):
    """fft_eval_rtl_power_fftw device metadata"""
    pass


class PowerThread(BasePowerThread):
    """Thread which runs fft_eval_rtl_power_fftw process"""
    def setup(self, start_freq, stop_freq, bin_size, interval=10.0, gain=-1, ppm=0, crop=0,
              single_shot=False, device=0, sample_rate=2560000, bandwidth=0, lnb_lo=0):
        """Setup fft_eval_rtl_power_fftw params"""

        self.params = {
            "start_freq": start_freq,
            "stop_freq": stop_freq,
        }
        self.databuffer = {"timestamp": [], "x": [], "y": []}
        self.databuffer_hop = {"timestamp": [], "x": [], "y": []}
        self.hop = 0
        self.prev_line = ""

        print("fft_eval_rtl_power_fftw params:")
        pprint.pprint(self.params)
        print()

    def process_start(self):
        """Start fft_eval_rtl_power_fftw process"""
        if not self.process and self.params:
            settings = QtCore.QSettings()
            cmdline = shlex.split(settings.value("executable", "fft_eval_rtl_power_fftw"))
            cmdline.extend([])
            additional_params = ""

            self.process = subprocess.Popen(cmdline, stdout=subprocess.PIPE,
                                            universal_newlines=True)

    def parse_output(self, line):
        """Parse one line of output from rtl_power_fftw"""
        line = line.strip()
        
        
        if not line and self.prev_line:
            self.databuffer["x"].extend(self.databuffer_hop["x"])
            self.databuffer["y"].extend(self.databuffer_hop["y"])
            # Flush frequencies for new hop
            self.databuffer_hop = {"timestamp": [], "x": [], "y": []}        
        
        # New set
        elif not line and not self.prev_line:
            
            self.data_storage.update(self.databuffer)
            # Flush databuffer for new set
            self.databuffer = {"timestamp": [], "x": [], "y": []}
            
      
        elif line:
            # Get timestamp for new hop and set
            #if line.startswith("# Acquisition start:"):
            if line.startswith("# Acquisition start:"):
                timestamp = line.split(":", 1)[1].strip()
                if not self.databuffer_hop["timestamp"]:
                    self.databuffer_hop["timestamp"] = timestamp
                if not self.databuffer["timestamp"]:
                    self.databuffer["timestamp"] = timestamp
                
            # Skip other comments
            elif line.startswith("#"):
                pass

            # Parse frequency and power
            elif line[0].isdigit:
                freq, power = line.split()
                freq, power = float(freq), float(power)
                
                if np.isinf(power):
                    power = -110.0

                if power > 0:
                    print("Positive power value !!!", power)
                    power = power * -1
                    
                if power < -120.0:
                    power = -120.0

                self.databuffer_hop["x"].append(freq)
                self.databuffer_hop["y"].append(power)

                
            else:
                pass
            
        self.prev_line = line

