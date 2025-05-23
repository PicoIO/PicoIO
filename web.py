import ubinascii
import hashlib
import binascii

from machine import Pin
from lib.Url_encode import url_encode
import startup


from time import sleep

import global_var

import free_mem

import urequests
from os import listdir
from os import remove
from os import mkdir
from machine import reset
#import json

import gc

import asyncio

async def serve_client(reader, writer):
    url = url_encode()
    
    print("Client connected")
    request_line = await reader.readline()
    print("Request:", request_line)
    auth = 0
    html = ''

    conf = startup.config_load()

    while True:
        header = await reader.readline()
        if header.decode("utf8").find("Authorization: Basic ") >= 0:
            barrier = header.decode("utf8").replace("Authorization: Basic ", "").rstrip()
            hash_object = hashlib.sha256()
            hash_object.update(barrier.encode())
            hash_barrier = binascii.hexlify(hash_object.digest())
            if hash_barrier.decode("utf8") == conf['security']['barrier']:
                
                auth = 1
                
                pass
            elif header == b'\r\n':
                if auth == 0:
                    writer.write('HTTP/1.0 401 Unauthorized\r\nWWW-Authenticate: Basic realm="User Visible Realm"\r\n\r\n')
                break
        elif header == b'\r\n':
            if auth == 0:
                writer.write('HTTP/1.0 401 Unauthorized\r\nWWW-Authenticate: Basic realm="User Visible Realm"\r\n\r\n')
            break

    request = str(request_line)

    if auth == 1:

        style = request.find('/style.css')
        script_gpio = request.find('/script_gpio.js')
        script_network = request.find('/script_network.js')
        script_communication = request.find('/script_communication.js')
        script_system = request.find('/script_system.js')

        root = request.find('/ ')
        gp_stat = request.find('/gp_stat')
        gp_act = request.find('/gp_act?')
        gp_save = request.find('/gpio_config?')
        wifi_scan = request.find('/wifi_scan')
        net_config = request.find('/network_config?')
        comm_config = request.find('/communication?')
        update = request.find('/update?')
        sys_config = request.find('/system?')
        save_conf = request.find('/config.conf')
        up_conf = request.find('/up_conf')
        factory_reset = request.find('/factory_reset')

        if root == 6:
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            with open("index.html", "r") as file:
                html = file.read()
            response = html
            writer.write(response)

            await writer.drain()
            await writer.wait_closed()
            print("Client disconnected")
            pass

        elif gp_stat == 6:
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            input = []
            output = []
            onewire = []
            for item in conf['gpio']:
                if conf['gpio'][item]['type'] == '1':
                    type = [item, Pin(int(item.replace('gp', ''))).value()]
                    input.append(type)
                elif conf['gpio'][item]['type'] == '2':
                    type = [item, Pin(int(item.replace('gp', ''))).value()]
                    output.append(type)
            jsi = '  "input":\n  {\n'
            i = 0
            for item in input:
                jsi += '    "' + item[0] + '": ' + str(item[1])
                i += 1
                if len(input) != i:
                    jsi += ',\n'
            jsi += '\n  }'
            jso = '  "output":\n  {\n'
            i = 0
            for item in output:
                jso += '    "' + item[0] + '": ' + str(item[1])
                i += 1
                if len(output) != i:
                    jso += ',\n'
            jso += '\n  }'

            if global_var.OneWire:
                OneWireSensors = (startup.one_wire_rom_str(startup.one_wire_scan(global_var.OneWire)))
                for OneWireSensor in OneWireSensors:
                    sensor = startup.one_wire_str_rom(OneWireSensor)
                    name = None
                    ds = None
                    new = None
                    temp = await startup.one_wire(global_var.OneWire, sensor)

                    if conf['1wire']['sensors']:
                        for item in conf['1wire']['sensors']:
                            if conf['1wire']['sensors'][item]['rom'] == OneWireSensor:
                                ds = item
                    if ds:
                        name = conf['1wire']['sensors'][ds]['name']
                        new = '0'
                    else:
                        name = 'ds-' + OneWireSensor[-4:]
                        new = '1'

                    if temp:
                        onewire.append([OneWireSensor, name, str("%.2f" % temp), new])
                    else:
                        onewire.append([OneWireSensor, name, 'err', new])

                for item in conf['1wire']['sensors']:
                    if len(OneWireSensors) > 0:
                        for OneWireSensor in OneWireSensors:
                            if conf['1wire']['sensors'][item]['rom'] != OneWireSensor:
                                name = conf['1wire']['sensors'][item]['name']
                                OneWireSensor = conf['1wire']['sensors'][item]['rom']
                                onewire.append([OneWireSensor, name, 'offline', '0'])
                    else:
                        name = conf['1wire']['sensors'][item]['name']
                        OneWireSensor = conf['1wire']['sensors'][item]['rom']
                        onewire.append([OneWireSensor, name, 'offline', '0'])

            js1w = '  "1wire":\n  [\n'
            i = 0
            for item in onewire:
                js1w += '    {\n      "rom": "' + item[0] + '",\n      "name": "' + item[1] + '",\n      "temp": "' + item[2]
                js1w += '",\n      "new": "' + item[3] + '"\n    }'
                i += 1
                if len(onewire) != i:
                    js1w += ',\n'
            js1w += '\n  ]'

            js = '{\n' + jsi + ',\n' + jso + ',\n' + js1w + '\n}'
            
            response = js
            writer.write(response)

            await writer.drain()
            await writer.wait_closed()
            print("Client disconnected")
            pass

        elif gp_act == 6:
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            gp = url.decode(request).replace("b'GET /gp_act?", "").split("=")[0]
            stat = url.decode(request).replace("b'GET /gp_act?", "").split("=")[1].replace(" HTTP/1.1\\r\\n'", "")
            Pin(int(gp)).value(int(stat))

        elif gp_save == 6:
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            gp_conf = url.decode(request).replace("b'GET /gpio_config?", "").replace(" HTTP/1.1\\r\\n'", "").split('&')

            gpio_conf = ""
            debounce_conf = ""
            wire_conf = ""
            wire_s_conf = ""

            debounce_match = 0
            wire_match = 0

            for items in gp_conf:
                if items.split('=')[0].startswith('type'):
                    gpio_num = int(items.split('=')[0].replace('type', ''))
                    gpio_conf += '\n    "gp' + str(gpio_num) + '":\n    {\n'
                    if items.split('=')[1] == '1':
                        gpio_conf += '      "type": "1",\n      "resistor": "'
                        for it in gp_conf:
                            if it.split('=')[0] == 'resistor' + str(gpio_num):
                                gpio_conf += it.split('=')[1]
                        gpio_conf += '",\n      "contact": "'
                        for it in gp_conf:
                            if it.split('=')[0] == 'contact' + str(gpio_num):
                                gpio_conf += it.split('=')[1]
                        gpio_conf += '"\n    },'
                    elif items.split('=')[1] == '2':
                        gpio_conf += '      "type": "2"\n    },'
                    elif items.split('=')[1] == '3':
                        gpio_conf += '      "type": "3"\n    },'
                    elif items.split('=')[1] == '0':
                        gpio_conf += '      "type": "0"\n    },'

                if items.split('=')[0].startswith('debounce'):
                    debounce_conf = '{\n      "ms_time": "' + items.split('=')[1] + '"\n    },'
                    debounce_match += 1
                elif debounce_match == 0:
                    debounce_conf = str(conf['debounce']).replace("'", '"')

                if items.split('=')[0].startswith('1wire_refresh'):
                    wire_conf = '{\n    "s_time": "' + items.split('=')[1] + '",'#\n    "sensors":\n    {\n    '
                    wire_match += 1
                elif wire_match == 0:
                    wire_conf = '{\n    "s_time": "' + conf['1wire']['s_time'] + '",'#\n    "sensors":\n    {\n    '

                if items.split('=')[0].startswith('1w_sensor_id'):
                    sensor_num = int(items.split('=')[0].replace('1w_sensor_id', ''))
                    wire_s_conf += '      "ds' + str(sensor_num) + '":\n      {\n        "rom": "' + items.split('=')[1] + '",\n        "name": "'
                    for it in gp_conf:
                        if it.split('=')[0] == '1w_sensor_name' + str(sensor_num):
                            wire_s_conf += it.split('=')[1]
                    wire_s_conf += '"\n      },\n'

            hw_conf = str(conf['hw']).replace("'", '"')
            network_conf = str(conf['network']).replace("'", '"')
            communication_conf = str(conf['communication']).replace("'", '"')
            security_conf = str(conf['security']).replace("'", '"')

            config_str = '{\n  "hw":\n  ' + hw_conf + ',\n  "gpio":\n  {' + gpio_conf + '\n  },\n  "debounce":\n  '
            config_str += debounce_conf + ',\n  "1wire":\n  ' + wire_conf + '    "sensors":\n    {\n' + wire_s_conf + '    }\n  },\n  "network":\n  '
            config_str += network_conf + ',\n  "communication":\n  ' + communication_conf + ',\n  "security":\n  '
            config_str += security_conf + ',\n}'

            config = open("config.conf", "w")
            config.write(config_str)
            config.close()

            hw_conf = None
            debounce_conf = None
            wire_conf = None
            network_conf = None
            communication_conf = None
            security_conf = None

            sleep(1)

            conf = startup.config_load()
            startup.pin_config(conf)
            global_var.config_load = 1

            #response = html % conf

            response = "<script>window.location.href = window.location.protocol + '//' + window.location.host;</script>"
            writer.write(response)
    
        elif wifi_scan == 6:
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            from wifi import connect_wifi
            wifis = connect_wifi.station.wlan.scan()
            wifi_list = []
            for wifi in wifis:
                if not str(wifi[0]).startswith("b'\\x00") or str(wifi[0].decode("utf8")) == "":
                    wifi_list.append([wifi[0].decode("utf8"), wifi[3], wifi[4]])

            wifi_scaned = '['
            i = 1
            for item in wifi_list:
                wifi_scaned += '{"ssid": "' + item[0] + '","rssi": "'
                wifi_scaned += str(item[1]) + '","security": "' + str(item[2]) + '"}'
                if i < len(wifi_list):
                    wifi_scaned += ','
                    i += 1
                
            wifi_scaned += ']'

            response = wifi_scaned
            writer.write(response)

            wifis = None
            wifi = None
            item = None
            wifi_scaned = None
            wifi_list = None

            await writer.drain()
            await writer.wait_closed()
            print("Client disconnected")
            pass

        elif net_config == 6:
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            net_conf = url.decode(request).replace("b'GET /network_config?", "").replace(" HTTP/1.1\\r\\n'", "").split("&")

            network_conf = ''

            for items in net_conf:
                if items.split('=')[0] == 'net_method':
                    if items.split('=')[1] == '0':
                        network_conf += '"type": "dhcp", '
                    elif items.split('=')[1] == '1':
                        network_conf += '"type": "static",'
                if items.split('=')[0] == 'ipaddress':
                    network_conf += ' "ip": "'
                    network_conf += items.split('=')[1]
                    network_conf += '",'
                if items.split('=')[0] == 'netmask':
                    network_conf += ' "netmask": "'
                    network_conf += items.split('=')[1]
                    network_conf += '",'
                if items.split('=')[0] == 'gateway':
                    network_conf += ' "gateway": "'
                    network_conf += items.split('=')[1]
                    network_conf += '",'
                if items.split('=')[0] == 'dns':
                    network_conf += ' "dns": "'
                    network_conf += items.split('=')[1]
                    network_conf += '",'
                if items.split('=')[0] == 'ssid':
                    network_conf += '"wifi": {"ssid": "'
                    network_conf += items.split('=')[1]
                    ssid = items.split('=')[1]
                    network_conf += '",'
                if items.split('=')[0] == 'wifi_password':
                    if len(items.split('=')[1]) >= 8:
                        network_conf += '"password": "'
                        network_conf += items.split('=')[1]
                        network_conf += '"}'
                    else:
                        if ssid == conf['network']['wifi']['ssid']:
                            network_conf += '"password": "'
                            network_conf += conf['network']['wifi']['password']
                            network_conf += '"}'
                        else:
                            network_conf += '"password": ""}'
                        
            hw_conf = str(conf['hw']).replace("'", '"')
            gpio_conf = str(conf['gpio']).replace("'", '"')
            debounce_conf = str(conf['debounce']).replace("'", '"')
            wire_conf = str(conf['1wire']).replace("'", '"')
            communication_conf = str(conf['communication']).replace("'", '"')
            security_conf = str(conf['security']).replace("'", '"')

            config_str = '{\n  "hw":\n  ' + hw_conf + ',\n  "gpio":\n' + gpio_conf + '\n,\n  "debounce":\n  '
            config_str += debounce_conf + ',\n  "1wire":\n  ' + wire_conf + ',\n  "network": {\n  '
            config_str += network_conf + '},\n  "communication":\n  ' + communication_conf + ',\n  "security":\n  '
            config_str += security_conf + ',\n}'

            config = open("config.conf", "w")
            config.write(config_str)
            config.close()

            response = "<script>window.location.href = window.location.protocol + '//' + window.location.host;</script>"
            writer.write(response)

            await writer.drain()
            await writer.wait_closed()
            print("Client disconnected")
            pass

            import machine
            machine.reset()

        elif comm_config == 6:
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            comm_conf = url.decode(request).replace("b'GET /communication?", '').replace(" HTTP/1.1\\r\\n'", '').split('&')

            communication_conf = '{"UDP": {'

            for items in comm_conf:
                if items.split('=')[0] == 'udp':
                    if items.split('=')[1] == 'on':
                        communication_conf += '"enabled": "1",'
                elif items.split('=')[0] == 'udp_ip':
                    communication_conf += '"ip": "'
                    communication_conf += items.split('=')[1]
                    communication_conf += '",'
                elif items.split('=')[0] == 'udp_port':
                    communication_conf += '"port": "'
                    communication_conf += items.split('=')[1]
                    communication_conf += '"'
                else:
                    communication_conf += '"enabled": "0","ip": "'
                    communication_conf += conf['communication']['UDP']['ip']
                    communication_conf += '","port": "'
                    communication_conf += conf['communication']['UDP']['port']
                    communication_conf += '"'

            communication_conf += '} }'

            hw_conf = str(conf['hw']).replace("'", '"')
            gpio_conf = str(conf['gpio']).replace("'", '"')
            debounce_conf = str(conf['debounce']).replace("'", '"')
            wire_conf = str(conf['1wire']).replace("'", '"')
            network_conf = str(conf['network']).replace("'", '"')
            security_conf = str(conf['security']).replace("'", '"')

            config_str = '{\n  "hw":\n  ' + hw_conf + ',\n  "gpio":\n' + gpio_conf + '\n,\n  "debounce":\n  '
            config_str += debounce_conf + ',\n  "1wire":\n  ' + wire_conf + ',\n  "network": \n  '
            config_str += network_conf + ',\n  "communication":\n  ' + communication_conf + ',\n  "security":\n  '
            config_str += security_conf + ',\n}'

            config = open("config.conf", "w")
            config.write(config_str)
            config.close()

            response = "<script>window.location.href = window.location.protocol + '//' + window.location.host;</script>"
            writer.write(response)

            await writer.drain()
            await writer.wait_closed()
            print("Client disconnected")
            pass

            import machine
            machine.reset()

        elif update == 6:
            version = url.decode(request).replace("b'GET /update?", '').replace(" HTTP/1.1\\r\\n'", '').split('=')[1]
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')

            response = "<script>window.location.href = window.location.protocol + '//' + window.location.host;</script>"
            writer.write(response)

            await writer.drain()
            await writer.wait_closed()
            print("Client disconnected")
            
            update = open('update.conf', 'w')
            update.write(version)
            update.close()

            await asyncio.sleep(10)

            reset()

        elif sys_config == 6:
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            sys_conf = url.decode(request).replace("b'GET /system?", '').replace(" HTTP/1.1\\r\\n'", '').split('&')

            host = ''
            #sys_user = ''
            sys_pass = ''
            sw_ch = ''
            for items in sys_conf:
                if items.split('=')[0] == 'host':
                    host = items.split('=')[1]
                #if items.split('=')[0] == 'sys_user':
                #    sys_user = items.split('=')[1]
                if items.split('=')[0] == 'sys_pass':
                    sys_pass = items.split('=')[1]
                if items.split('=')[0] == 'sw_ch':
                    if items.split('=')[1] == '1':
                        sw_ch = 'test'
                    elif items.split('=')[1] == '0':
                        sw_ch = 'production'
                
            hw_conf = '{"board": "' + conf['hw']['board'] + '", "release": "' + conf['hw']['release'] + '", "sw": "'
            hw_conf += conf['hw']['sw'] + '", "sw_ch": "' + sw_ch + '", "sysname": "' + host + '"}'

            gpio_conf = str(conf['gpio']).replace("'", '"')
            debounce_conf = str(conf['debounce']).replace("'", '"')
            wire_conf = str(conf['1wire']).replace("'", '"')
            network_conf = str(conf['network']).replace("'", '"')
            communication_conf = str(conf['communication']).replace("'", '"')

            barrier = str(ubinascii.b2a_base64('admin:%s' % (sys_pass)).strip()).replace("b'", "").replace("'", "")
            hash_object = hashlib.sha256()
            hash_object.update(barrier.encode())
            hash_barrier = binascii.hexlify(hash_object.digest())
            
            security_conf = '{"user": "' + conf['security']['user'] + '", "barrier": "' + str(hash_barrier).replace("b'",'').replace("'",'') + '"}'

            config_str = '{\n  "hw":\n  ' + hw_conf + ',\n  "gpio":\n' + gpio_conf + '\n,\n  "debounce":\n  '
            config_str += debounce_conf + ',\n  "1wire":\n  ' + wire_conf + ',\n  "network":\n  '
            config_str += network_conf + ',\n  "communication":\n  ' + communication_conf + ',\n  "security":\n  '
            config_str += security_conf + ',\n}'

            config = open("config.conf", "w")
            config.write(config_str)
            config.close()

            response = "<script>window.location.href = window.location.protocol + '//' + window.location.host;</script>"
            writer.write(response)

            await writer.drain()
            await writer.wait_closed()
            print("Client disconnected")
            pass

            reset()

        elif save_conf == 6:
            writer.write('HTTP/1.0 200 OK\r\nContent-type: application/octet-stream .conf\r\n\r\n')
            with open("config.conf", "r") as file:
                html = file.read()
            response = html

            writer.write(response)

            await writer.drain()
            await writer.wait_closed()
            print("Client disconnected")
            pass

        elif up_conf == 7:
            line = []
            while True:
                l = await reader.readline()
                l = l.decode("utf8")
                if l.find('EOF') < 0:
                    line.append(l)
                else:
                    break

            config_str = ''
            for item in line:
                config_str += item

            config = open("config.conf", "w")
            config.write(config_str)
            config.close()

            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')

            await writer.drain()
            await writer.wait_closed()
            print("Client disconnected")
            pass

            reset()

        elif factory_reset == 6:
            import os
            os.remove('config.conf')

            reset()


        elif style == 6:
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/css\r\n\r\n')
            with open("style.css", "r") as file:
                html = file.read()
            response = html

            writer.write(response)

            await writer.drain()
            await writer.wait_closed()
            print("Client disconnected")
            pass

        elif script_gpio == 6:
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/js\r\n\r\n')
            with open("script_gpio.js", "r") as file:
                html = file.read()
            response = html % conf

            writer.write(response)

            await writer.drain()
            await writer.wait_closed()
            print("Client disconnected")
            pass

        elif script_network == 6:
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/js\r\n\r\n')
            with open("script_network.js", "r") as file:
                html = file.read()
            response = html

            writer.write(response)

            await writer.drain()
            await writer.wait_closed()
            print("Client disconnected")
            pass

        elif script_communication == 6:
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/js\r\n\r\n')
            with open("script_communication.js", "r") as file:
                html = file.read()
            response = html

            writer.write(response)

            await writer.drain()
            await writer.wait_closed()
            print("Client disconnected")
            pass

        elif script_system == 6:
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/js\r\n\r\n')
            with open("script_system.js", "r") as file:
                html = file.read()
            response = html

            writer.write(response)

            await writer.drain()
            await writer.wait_closed()
            print("Client disconnected")
            pass


        else:
            writer.write('HTTP/1.0 404 Not Found\r\n\r\n')          
            await writer.drain()
            await writer.wait_closed()
            print("Client disconnected")
            pass  

    else:
        with open("unauthorized.html", "r") as file:
                html = file.read()
        response = html
        writer.write(response)

    free_mem.free_mem()
    #writer.write(response)

    request_line = None
    auth = None
    html = None
    conf = None
    header = None
    barrier = None
    hash_object = None
    hash_barrier = None
    request = None
    gp_stat = None
    gp_act = None
    response =None
    gp = None
    stat = None

    writer = None
    reader = None