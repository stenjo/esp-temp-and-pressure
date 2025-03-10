# The MIT License (MIT)
#
# Copyright (c) 2022 Raul Kompass (@rkompass)
#               
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

# Todo:
#     introduce table of conversion times (depending on self.sps to be used by _wait_drdy() -> adjust max delay in _wait_drdy()
#     better time report in ads_1118_debug.py, remove printing of waiting times in fiinal version
#     better warning in config()
#     try using ustruct, compare memory consumption
    
from utime import sleep_us, ticks_us, ticks_diff

def _GETIDX_LOG_MATCH(x, tab):   # tab must have in- or decreasing values; returns index i with tab[i] closest to x in a logarithmic sense
    for i in range(len(tab)):    # may be used to adjust sps or gains according to table of possible values
        if i+1 < len(tab) and (tab[i] * tab[i+1] > x * x if tab[i+1] > tab[i] else tab[i] * tab[i+1] < x * x):  #  t_i / x < x / t_i+1 i.e. x is closer to t_i+1
            break
    return i

#  Input combinations used by ADC; Table_idx << 12 goes into ADC config register
_MUX_T = ((0,1), (0,3), (1,3), (2,3), (0,None), (1,None), (2,None), (3,None))  # (Ain_p, Ain_n) ; None ^= GND

#  Programmable gain amplifier (PGA) gain factors, Table_idx << 9 goes into ADC config register
_GAINS    =  (0.6667, 1.0,    2.0,    4.0,    8.0,    16.0)    
# _V_MAX = (6.144,  4.096,  2.048,  1.024,  0.512,  0.256) #  max input voltages wrt gains

#  Conversion rates in samples per second (SPS), Table_idx << 5 goes into ADC config register
_SPS = (8, 16, 32, 64, 128, 250, 475, 860)   #  Conversion rates (samples per second) for ads1118

_GND = None

# Micropython driver module for TI ADC ADS1118
#   (16-bit, 4 channels, internal V_ref=4.096V, programmable gain: 2/3..16, 8..860 SPS, SPI interface).
#
# Driver arguments to be used in initializer or config():
# -------------------------------------------------------
# mux: program input multiplexer:
#    allowed values: (0,1), (0,3), (1,3), (2,3), (0,None), (1,None), (2,None), (3,None), or 0, 1, 2, 3 for the latter
# vmax: maximal expected input voltage:
#    any value <= 0.6667 allowed, the gain setting will be adjusted so, that the smallest gain_vmax >= vmax is selected
# gain: gain value of internal programmable gain amplifier
#    any value allowed, the gain will be adjusted to the closest of the values 0.6667, 1.0, 2.0, 4.0, 8.0 and 16.0, in log sense.
#    if both vmax and gain are specified, vmax is used for configuration
# sps: conversion rate in samples per second
#    any value allowed, the sps will be adjusted to the closest of the values 8, 16, 32, 64, 128, 250, 475 and 860, in log sense

# Note: spi of ads1118 has polarity=0 (default in Micropython)
#                     and phase=1  (not default in Micropython),
# so initialize spi with e.g. spi = SPI(2, baudrate=1000000, phase=1)
#   or spi = SoftSPI(baudrate=1000000, sck=Pin('B13'), miso=Pin('B14'), mosi=Pin('B15'), phase=1).
# For cs you may use any pin (the cs pin belonging to an spi pin group in the pyboard pinout diagram is just a suggestion).
# The spi-miso pin is used for the data ready (drdy) signal. So you have to initialize it separately and provide
#   it as the drdy argument:
# Example:
# miso =Pin('B14', Pin.IN)    # do this before setting up spi, because the pin is redefined; miso.value() still works
# spi = SPI(2, baudrate=1000000, phase=1) # or: # spi = SoftSPI(baudrate=1000000, sck=Pin('B13'), miso=miso, mosi=Pin('B15'), phase=1)
# cs = Pin('B12', Pin.OUT_PP, value=1)
# ads = Ads1118(spi, cs, miso)

class ADS1118:
    def __init__(self, spi, cs, miso, mux = 0, vmax=None, gain=None, sps=8):
        self.spi = spi
        self.cs = cs
        self.miso = miso       # The driver uses spi_miso as _DRDY.
        if not (vmax or gain):
            gain = 1           # Enforce default for a complete conversion setting, even if only i2c specified.
        self._config = 0x000a  # Necessary pattern, for _config written to ADC to have effect.
        self.config(mux, vmax, gain, sps, temp = False)    # Sets bits 4 (temp), 5..7 (SPS), 9..14 (PGA, MUX)) of self._config.
        # Now self._config contains codes to be written in config register.
        # It has to be |-ed with bits 8 and 15 to specify single or continuous conversion and conversion start.
        # These are are added when preparing or starting the actual conversion.

    def __repr__(self):
        dct = self.config()
        app = ') # Cont. Mode: ' + ('On' if dct['cont'] else 'Off')
        return 'ADS1118('+''.join([s for a in ('mux','vmax','gain','sps') for s in (a,'=',str(dct[a]),', ')][:-1]) + app

    def _wr_cfg(self, config): # Write configuration
        self.cs.off()
        self.spi.write(config.to_bytes(2, 'big'))
        self.cs.on()         # CS must go high after writing 2 bytes, otherwise the _DRDY-Logic will not work (SPI expects 2 more bytes)
        
    def _rd_cfg(self):         # Read configuration
        self.cs.off()
        data=self.spi.read(4)                    # We have to read bytes 0..3
        self.cs.on()
        return int.from_bytes(data[2:], 'big')   # Bytes 2+3 are the config

    def _rd_data(self, config=0):  # Read data, may also write the config simultaneously; config=0 will be ignored by the ADC
        self.cs.off()
        rbuf = bytearray(2)
        self.spi.write_readinto(config.to_bytes(2, 'big'), rbuf)
        self.cs.on()
        return int.from_bytes(rbuf, 'big')

    def _wait_drdy(self):           # Wait for _DRDY = 0, we might evaluate self.sps to determine the max waiting period
        start = ticks_us()
        self.cs.off()
        while self.miso.value():    # As long as miso = DOUT/_DRDY = 1 conversion is not finished
            if ticks_diff(ticks_us(), start) > 130000:
                break
        self.cs.on()
        return ticks_diff(ticks_us(), start)    # if the result is >= 100000 then miso was never low -> data weren't ready

    def config(self, mux=None, vmax=None, gain=None, sps=None, temp=None):
        """Get / set conversion mode."""
        if mux is None and vmax is None and gain is None and sps is None and temp is None:
            if self._rd_cfg() != self._config | 0x0001:
                print('Warning: ads1118 not configured accordingly.', f"{self._rd_cfg():016b}")
            return {
                "mux": _MUX_T[self._config>>12 & 0x07],
                "vmax": 4.096 / self.gain,
                "gain": _GAINS[self._config>>9 & 0x07],
                "sps": _SPS[self._config>>5 & 0x07],
                "temp": bool(self._config>>4 & 0x01),
                "cont": bool(self._config>>8 & 0x01),
            }
        if mux is not None:
            if isinstance(mux, int):
                mux = (mux, None)
            if not ((isinstance(mux, tuple) or isinstance(mux, list)) and len(mux) == 2):
                raise ValueError('Input mux arg: AINp or (AINp, AINn) where None denotes GND')
            try:
                mux_idx = _MUX_T.index(mux)
            except ValueError:
                raise ValueError('Input mux setting not valid')
            self._config = self._config & 0x8fff | mux_idx<<12   # write index bits as code in _config 
        if vmax is not None or gain is not None:
            if vmax:                                            # vmax dominates gain, if both are specified
                vmx_grt = [vmax <= 4.096 / g for g in _GAINS]   # Generate table of truth values showing if vmax <= _V_MAX
                if True not in vmx_grt:                         # no gain value with vmax <= 4.096 / g
                    raise ValueError('vmax too high')
                gain_idx = vmx_grt.count(True) - 1              # last True index
            else:
                gain_idx = _GETIDX_LOG_MATCH(gain, _GAINS)  # If no vmax given, find index of closest value in gain table
            self.gain = _GAINS[gain_idx]
            self._config = self._config & 0xf1ff | gain_idx<<9   # write index bits as code in _config 
        if sps is not None:
            sps_idx = _GETIDX_LOG_MATCH(sps, _SPS)          # Find index of closest value for sample rate (in SPS-table))
            self._config = self._config & 0xff1f | sps_idx<<5    # write index bits as code in _config
        if temp is not None:
            self._config = self._config & 0xffef | (0x0010 if temp else 0x0000)

    def toV(self, raw, gain=None):
        if gain is None:
            gain = self.gain
        return raw * 4.096 / (gain * 32767)

    def read_once(self, mux=None):
        """Do (and wait for) ADC single conversion, then go into sleep mode.
           Optionally specify input. Do read_sleep() before, if you were in continuous mode."""
        if mux is not None:
            self.config(mux=mux)
        self._wr_cfg(self._config | 0x8100)        # 0x8000 bit starts conversion, 0x0100 bit for single shot mode
        t = self._wait_drdy()                      # Conversion is in progress -> wait for miso = DOUT/_DRDY to go down
        res = self._rd_data()                      # Read and do not restart
        print('waited', t, 'us')
        return res if res < 32768 else res - 65536  # Correct for negative values

    def start_single(self, mux=None):
        """Start ADC single conversion, return immediately. Prepares read_single_restart().
           Optionally specify input. Do read_sleep() before, if you were in continuous mode."""
        if mux is not None:
            self.config(mux=mux)
        self._wr_cfg(self._config | 0x8100)         # 0x8000 bit starts conversion, 0x0100 bit for single shot mode

    def read_single_restart(self, next_mux=None):
        """Wait for and read ADC conversion and restart in single mode.
           Optionally specify next input."""
        if next_mux is not None:
            self.config(mux=next_mux)
        t = self._wait_drdy()                       # Conversion is in progress -> wait for miso = DOUT/_DRDY to go down
        res = self._rd_data(self._config | 0x8100)  # Read data and at the same time start next single conversion
        print('waited', t, 'us')
        return res if res < 32768 else res - 65536

    def start_cont(self, mux=None):
        """Start continuous measurement. Optionally specify input.
           Do read_sleep() to stop continuous mode."""
        if mux is not None:
            self.config(mux=mux)
        self._wr_cfg(self._config)                  # self._config has always bit 8 (0x0100) = 0:  -> continuous mode

    def read_cont(self):
        """Read last from ongoing continuous conversions."""
        res = self._rd_data()
        return res if res < 32768 else res - 65536

    def read_sleep(self):
        """Wait for and read data in conversion, stop cont. measurement.
           Go into sleep mode."""
        self._wait_drdy()
        res = self._rd_data(self._config | 0x0100)  # Only 0x0100 bit for single shot mode; gets old invalid data
        return res if res < 32768 else res - 65536

    def temperature(self):
        """Start (and wait for) temperature measurement (°C), then go into sleep mode."""
        self.read_sleep()
        self.config(temp = True)
        res = self.read_once() >> 2
        if res >= 8192:
            res -= 16384
        self.config(temp = False)
        return res * 0.03125
