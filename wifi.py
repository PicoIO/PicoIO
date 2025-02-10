import network
import time
from machine import Pin
import random

led = Pin("LED", Pin.OUT, value=0)

class connect_wifi:
    class station:
        wlan = network.WLAN(network.STA_IF)
        def connect(ssid, password):
            try:
                connect_wifi.station.wlan.active(True)
                connect_wifi.station.wlan.connect(ssid, password)
            except:
                print ('wifi')
            max_wait = 10
            while True:
                if connect_wifi.station.wlan.status() < 0 or connect_wifi.station.wlan.status() >= 3:
                    break
                max_wait -= 1
                print('waiting for connection...')
                led.on()
                time.sleep(0.5)
                led.off()
                time.sleep(0.5)
            if connect_wifi.station.wlan.status() != 3:
                led.off()
            else:
                print('connected')
                status = connect_wifi.station.wlan.ifconfig()
                print( 'ip = ' + status[0] )
                led.on()
        def disconnect():
            connect_wifi.station.wlan.disconnect()
            connect_wifi.station.wlan.active(False)
            led.off()
    class ap:
        led.off()
        essid = "RPI_"+str(random.randrange(1000, 9999, 1))
        wlan = network.WLAN(network.AP_IF)
        wlan.config(essid= essid)
        wlan.config(security=0)
        def connect():
            connect_wifi.ap.wlan.active(True)
        def disconnect():
            connect_wifi.ap.wlan.disconnect()
            connect_wifi.ap.wlan.active(False)
    def connection(conf):
        while not connect_wifi.station.wlan.isconnected():
            conn = connect_wifi.reconnection(conf)
            if conn > 0:
                break
            if not connect_wifi.ap.wlan.isconnected():
                connect_wifi.station.disconnect()
                connect_wifi.ap.connect()
            else:
                led.on()
                break
            led.off()
            time.sleep(0.5)
            led.on()
            time.sleep(0.5)

    def reconnection(conf):
        wifi_ap = connect_wifi.station.wlan.scan()
        rt = 0
        if connect_wifi.station.wlan.config('ssid') != conf['network']['wifi']['ssid'] and conf['network']['wifi']['password']:
            for i in range(len(wifi_ap)):
                if wifi_ap[i][0].decode("utf-8") == conf['network']['wifi']['ssid']:
                    connect_wifi.ap.disconnect()
                    
                    connect_wifi.station.connect(conf['network']['wifi']['ssid'],conf['network']['wifi']['password'])
                    rt += 1
        return rt