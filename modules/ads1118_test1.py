import gc
from utime import sleep_ms
# from pyb import Pin, SPI 
from machine import Pin, I2C, SPI, SoftSPI 

gc.collect(); last_m = gc.mem_free(); print('Free Memory:               {:d}'.format(last_m))


from ads1118 import ADS1118
# miso =Pin('A6', Pin.IN)
# spi = SPI(1, baudrate=100000, phase=1)
# spi = SoftSPI(baudrate=1000000, sck=Pin('A5'), miso=Pin('A6'), mosi=Pin('A7'), phase=1)
misopin = Pin('B14', Pin.IN)
# spi = SPI(2, baudrate=100000, phase=1)
spi = SoftSPI(baudrate=100000, sck=Pin('B13'), miso=misopin, mosi=Pin('B15'), phase=1)
# miso =Pin('A6', mode=Pin.ALT, pull=Pin.PULL_NONE, af=Pin.AF5_SPI1) # do this before setting up spi, because the pin is redefined; miso.value() still works

spi.write(b"\xff")  # should not be necessary

cs = Pin('B12', Pin.OUT_PP, value=1) # cs = Pin('B12', Pin.OUT_PP, value=1)

adc = ADS1118(spi, cs, misopin, sps=250)
gc.collect(); new_m = gc.mem_free(); print('ads1118 used Memory:        {:d}'.format(last_m-new_m)); last_m = new_m

print('-----------------------------')
print('ADC-Temperature: {:4.2f}°C'.format(adc.temperature()))
print('-----------------------------')
print('adc.read_once()')
print('A0: {:5.4f}V'.format(adc.toV(adc.read_once(0))))
print('A1: {:5.4f}V'.format(adc.toV(adc.read_once(1))))
print('A1: {:5.4f}V'.format(adc.toV(adc.read_once((2, None)))))
print('A3: {:5.4f}V'.format(adc.toV(adc.read_once((3, None)))))

print('-----------------------------')
print('adc.start_cont(); adc.read_cont()')
adc.start_cont((0, None)); sleep_ms(10)    # we have to care for the conversion time ourselves
print('A0: {:5.4f}V'.format(adc.toV(adc.read_cont())))
adc.start_cont((1, None)); sleep_ms(10)
print('A1: {:5.4f}V'.format(adc.toV(adc.read_cont())))
adc.start_cont((2, None)); sleep_ms(10)
print('A1: {:5.4f}V'.format(adc.toV(adc.read_cont())))
adc.start_cont((3, None)); sleep_ms(10)
print('A3: {:5.4f}V'.format(adc.toV(adc.read_cont())))
adc.read_sleep()                           # stop contiuous mode

print('-----------------------------')
print('adc.start_single(); adc.read_single_restart()')
from array import array
res = array('H', [0,0,0,0])
adc.start_single((0, None))
res[0] = adc.read_single_restart((1, None))
res[1] = adc.read_single_restart((2, None))
res[2] = adc.read_single_restart((3, None))
res[3] = adc.read_sleep()
for i in range(4):
    print('A0: {:5.4f}V'.format(adc.toV(res[i])))

print('-----------------------------')
print('adc.read_once()')
adc.start_single((0, None))
print('A0: {:5.4f}V'.format(adc.toV(adc.read_once(0))))
print('A1: {:5.4f}V'.format(adc.toV(adc.read_once(1))))
print('A1: {:5.4f}V'.format(adc.toV(adc.read_once((2, None)))))
print('A3: {:5.4f}V'.format(adc.toV(adc.read_once((3, None)))))


# we note perhaps a very small increase of read values in continuous mode