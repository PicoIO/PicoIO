import socket
from machine import Timer
from startup import config_load
from machine import Pin
import uasyncio as asyncio

import usocket
import uselect

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

class UDPServer:
    def __init__(self, polltimeout=1, max_packet=1024):
        self.polltimeout = polltimeout
        self.max_packet = max_packet

    async def serve(self, cb):
        if UDP_EN == '1':
            ai = usocket.getaddrinfo(UDP_IP, UDP_PORT)[0]  # blocking!
            s = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
            self.sock = s
            s.setblocking(False)
            s.bind(ai[-1])

            p = uselect.poll()
            p.register(s, uselect.POLLIN)
            to = self.polltimeout
            while True:
                try:
                    if p.poll(to):
                        buf, addr = s.recvfrom(self.max_packet)
                        ret = cb(buf, addr)
                        await asyncio.sleep(0)
                        #if ret:
                        #    s.sendto(ret, addr)  # blocking
                    await asyncio.sleep(0)
                except asyncio.CancelledError:
                    # Shutdown server
                    s.close()
                    return
                
def recive_msg(data, addr):
    try:
        print ('Received:', data.decode("utf8").rstrip(), 'from', addr)
        data_pin = int(data.decode("utf8").rstrip().replace("pin: ", "").split(" set:")[0])
        data_state = int(data.decode("utf8").rstrip().split(" set: ")[1])
        if str(Pin(data_pin)).find('OUT') > 0:
            Pin(data_pin).value(data_state)
            MESSAGE = 'pin: ' + str(data_pin) + ' state: ' + str(Pin(data_pin).value())
            send_msg(MESSAGE)
    except Exception as e:
        print (e)
        return 'Error'

timer_nc = Timer()
timer_no = Timer()
