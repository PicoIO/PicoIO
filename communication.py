import socket
from machine import Timer
from startup import config_load
from machine import Pin

conf = config_load()

debounce_conf = conf['debounce']['ms_time']

UDP_EN = conf['communication']['UDP']['enabled']
UDP_IP = conf['communication']['UDP']['ip']
UDP_PORT = int(conf['communication']['UDP']['port'])

conf = None

global PIN

def debounce_nc(pin):
    global PIN
    PIN = pin
    timer_nc.init(mode=Timer.ONE_SHOT, period=int(debounce_conf), callback=send_nc)
def debounce_no(pin):
    global PIN
    PIN = pin
    timer_no.init(mode=Timer.ONE_SHOT, period=int(debounce_conf), callback=send_no)
def send_nc(timer_nc):
    global PIN
    print (str(PIN))
    if PIN.value() == 1:
        MESSAGE  = 'pin: ' + str(PIN).replace('Pin(GPIO', '').split(',')[0] + ' state: 1'

        send_msg(MESSAGE)
def send_no(timer_no):
    global PIN
    print (str(PIN))
    if PIN.value() == 0:
        MESSAGE  = 'pin: ' + str(PIN).replace('Pin(GPIO', '').split(',')[0] + ' state: 1'

        send_msg(MESSAGE)

def send_msg(message):
    if UDP_EN == '1':
        sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        sock.sendto( message, (UDP_IP, UDP_PORT) )
        sock.close()

timer_nc = Timer()
timer_no = Timer()
