from usocket import socket
from machine import Pin,SPI
import network
import time
import sys

led = Pin(25, Pin.OUT)

spi=SPI(0,2_000_000, mosi=Pin(19),miso=Pin(16),sck=Pin(18))
nic = network.WIZNET5K(spi,Pin(17),Pin(20))

def w5x00_init():
    nic.active(True)
# If you use the Dynamic IP(DHCP), you must use the "nic.ifconfig('dhcp')".
    #nic.ifconfig(('dhcp'))
# If you use the Static IP, you must use the  "nic.ifconfig("IP","subnet","Gateway","DNS")".
    #nic.ifconfig(('192.168.100.13','255.255.255.0','192.168.100.1','8.8.8.8'))
       
    while not nic.isconnected():
        time.sleep(1)
        print(nic.regs())
        
    print('IP address :', nic.ifconfig())

    led.on()

def w5x00_reconect():
    while not nic.isconnected():
        led.off()
        sys.exit()