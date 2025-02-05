import json
from machine import Pin
import onewire
import ds18x20
import uasyncio as asyncio
import global_var

def config_load():
    try:
        config = open("config.conf", "r")
        conf = json.load(config)
    except:
        import os
        import machine
        uname = os.uname()
        config = open("config.conf", "w")
        #hw
        config.write('{\n  "hw":\n  {\n    "board": "')
        config.write(uname[4])
        config.write('",\n    "sysname": "')
        config.write(uname[1])
        config.write('",\n    "release": "')
        config.write(uname[2])
        config.write('",\n    "sw": "v0.0.1-alpha",\n    "sw_ch": "production"\n  },')
        #gpio
        config.write('\n  "gpio":\n  {')
        for i in range(29):
            if uname[4] == 'W5500-EVB-Pico with RP2040':
                if i != 16 and i != 17 and i != 18 and i != 19 and i != 20 and i != 21 and i != 23 and i != 24 and i != 25:
                    config.write('\n    "gp')
                    config.write(str(i))
                    config.write('":\n    {\n      "type": "0",\n      "resistor": "",\n      "contact": ""\n    }')
                    if i != 28:
                        config.write(',')
            elif uname[4] == "Raspberry Pi Pico W with RP2040":
                if i != 23 and i != 24 and i != 25:
                    config.write('\n    "gp')
                    config.write(str(i))
                    config.write('":\n    {\n      "type": "0",\n      "resistor": "",\n      "contact": ""\n    }')
                    if i != 28:
                        config.write(',')
            #elif
        config.write('\n  },')
        #debounce
        config.write('\n  "debounce":\n  {\n    "ms_time": "50"\n  },')
        #1wire
        config.write('\n  "1wire":\n  {\n    "s_time": "120",\n    "sensors":\n    {\n    }\n  },')
        #network
        config.write('\n  "network":\n  {')
        if uname[4] == "Raspberry Pi Pico W with RP2040":
            config.write('\n    "wifi":\n    {\n      "ssid": "",\n      "password": ""\n    },')
        config.write('\n    "type": "dhcp",\n    "ip": "",\n    "netmask": "",\n    "gateway": "",\n    ')
        config.write('"dns-1": "",\n    "dns-2": ""\n  },')
        #communication
        config.write('\n  "communication":\n  {\n    "UDP":\n    {\n      "enabled": "0",\n      ')
        config.write('"ip": "",\n      "port": "50000"\n    }\n  },')
        #security
        
        #import ubinascii
        #import hashlib
        #import binascii
        #barrier = str(ubinascii.b2a_base64('admin:%s' % ('password')).strip()).replace("b'", "").replace("'", "")
        #hash_object = hashlib.sha256()
        #hash_object.update(barrier.encode())
        #hash_barrier = binascii.hexlify(hash_object.digest())

        import security

        hash_barrier = str(security.auth_barrier('admin','password'))

        config.write('\n  "security":\n  {\n    "user": "admin",\n    "barrier": "')
        config.write(hash_barrier)
        config.write('"\n  }')

        config.write('\n}')
        config.close()
        try:
            config = open("config.conf", "r")
            conf = json.load(config)
        except:
            machine.reset()
    return conf

def pin_config(conf):
    if conf['hw']['board'] == 'W5500-EVB-Pico with RP2040':
        for i in range(29):
            if i != 16 and i != 17 and i != 18 and i != 19 and i != 20 and i != 21 and i != 23 and i != 24 and i != 25:
                pin(i, conf)
    elif conf['hw']['board'] == 'Raspberry Pi Pico W with RP2040':
        for i in range(29):
            if i != 23 and i != 24 and i != 25:
                pin(i, conf)

def pin(i, conf):
    #definire pin tip (0-NA, 1-input, 2-output, 3-1wire)
    #definire resistor (0-NA, 1-pull_up, 2-pull_down)
    #definire contact (0-NA, 1-NO, 2-NC)
    from communication import debounce_nc, debounce_no
    #Input
    if conf['gpio']['gp' + str(i)]['type'] == '1':
        if conf['gpio']['gp' + str(i)]['resistor'] == '1':
            Pin(i, Pin.IN, Pin.PULL_UP)
            if conf['gpio']['gp' + str(i)]['contact'] == '1':
                Pin(i).irq(debounce_no, Pin.IRQ_FALLING)
            if conf['gpio']['gp' + str(i)]['contact'] == '2':
                Pin(i).irq(debounce_nc, Pin.IRQ_RISING)
        if conf['gpio']['gp' + str(i)]['resistor'] == '2':
            Pin(i, Pin.IN, Pin.PULL_DOWN)
            if conf['gpio']['gp' + str(i)]['contact'] == '1':
                Pin(i).irq(debounce_nc, Pin.IRQ_RISING)
            if conf['gpio']['gp' + str(i)]['contact'] == '2':
                Pin(i).irq(debounce_no, Pin.IRQ_FALLING)
    #Output
    if conf['gpio']['gp' + str(i)]['type'] == '2':
        Pin(i, Pin.OUT)
    #1Wire
    if conf['gpio']['gp' + str(i)]['type'] == '3':
        global_var.OneWire = ds18x20.DS18X20(onewire.OneWire(Pin(i)))

def is_one_wire(conf):
    is_1wire = 0
    for i in range(29):
            try:
                if conf['gpio']['gp'+ str(i)]['type'] == '3':
                    is_1wire += 1
            except:
                is_1wire += 0
    if is_1wire == 0:
        global_var.OneWire = None
    return is_1wire

async def one_wire(OneWire, OneWireSensor):
    #from communication import send_msg
    temp = None
    try:
        OneWire.convert_temp()
        await asyncio.sleep_ms(750)
        temp = OneWire.read_temp(OneWireSensor)
        if temp == 85:
            temp = None
        """for sensor in OneWireSensors:
            if OneWire.read_temp(sensor) != 85:
                MESSAGE  = 'sensor: ' + str(sensor).replace("bytearray(b'", "").replace("')", "") + ' temp: ' + str(OneWire.read_temp(sensor))
                print (OneWire.read_temp(sensor))

                send_msg(MESSAGE)
            else:
                print('sensor err')"""
    except:
        print ("no sensor")
        temp = None
    return temp

def one_wire_scan(OneWire):
    return OneWire.scan()

def one_wire_rom_str(OneWireSensors):
    OneWireSensorsString = []
    for sensor in OneWireSensors:
        sensor_str = ''.join('%02X' % i for i in iter(sensor))
        OneWireSensorsString.append(sensor_str)
    return OneWireSensorsString

def one_wire_str_rom(OneWireSensor):
    OneWireRom = bytearray(8)
    for i in range(8):
        OneWireRom[i] = int(OneWireSensor[i * 2:i * 2 + 2], 16)
    return bytearray(OneWireRom)