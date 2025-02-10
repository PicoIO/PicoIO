import startup
import machine
import uasyncio as asyncio
import time

import free_mem

from machine import Pin
import socket

import global_var

import network

import gc

import web
import communication

async def main():
    
    global_var.init()

    conf = startup.config_load()
    startup.pin_config(conf)

    network.hostname(conf['hw']['sysname'])

    if conf['hw']['board'] == 'Raspberry Pi Pico W with RP2040':
        from wifi import connect_wifi
        
        if conf['network']['wifi']['ssid'] == '':
            connect_wifi.ap.connect()
        elif conf['network']['wifi']['password'] == '':
            connect_wifi.ap.connect()
        else:
            connect_wifi.station.connect(conf['network']['wifi']['ssid'],conf['network']['wifi']['password'])
            if conf['network']['type'] == 'static':                
                connect_wifi.station.wlan.ifconfig((conf['network']['ip'], conf['network']['netmask'], conf['network']['gateway'] , conf['network']['dns']))
            await asyncio.sleep(1)
            try:
                update = open('update.conf', 'r')
                version = update.read()
                from web_fn import upadte_fn
                upadte_fn(conf, version)
            except:
                print ('no update')

        asyncio.create_task(asyncio.start_server(web.serve_client, "0.0.0.0", 80))
        
        server = communication.UDPServer()
        await server.serve(communication.recive_msg)

    elif conf['hw']['board'] == 'W5500-EVB-Pico with RP2040':
        import net

        net.w5x00_init()
        if conf['network']['type'] == 'static':
            net.nic.ifconfig((conf['network']['ip'], conf['network']['netmask'], conf['network']['gateway'] , conf['network']['dns']))
        try:
            update = open('update.conf', 'r')
            version = update.read()
            from web_fn import upadte_fn
            upadte_fn(conf, version)
        except:
            print ('no update')
        asyncio.create_task(asyncio.start_server(web.serve_client, "0.0.0.0", 80))
        
        server = communication.UDPServer()
        await server.serve(communication.recive_msg)
        
    time_sleep = 0.1
    time_temp = int(conf['1wire']['s_time'])*(1/time_sleep)

    while True:
        gc.collect()

        if global_var.config_load:
            conf = startup.config_load()
            global_var.config_load = None

        if conf['hw']['board'] == 'Raspberry Pi Pico W with RP2040':
            connect_wifi.connection(conf)
        elif conf['hw']['board'] == 'W5500-EVB-Pico with RP2040':
            net.w5x00_reconect()


        #await startup.one_wire(global_var.OneWire, global_var.OneWireSensors)
        #print('temp')
        is_1wire = startup.is_one_wire(conf) 
        if is_1wire > 0 and time_temp >= (int(conf['1wire']['s_time'])/13)*(1/time_sleep):
            for sen in conf['1wire']['sensors']:
                if sen:
                    OneWireSensors = startup.one_wire_str_rom(conf['1wire']['sensors'][sen]['rom'])
                    temp = await startup.one_wire(global_var.OneWire, OneWireSensors)
                    if temp:
                        MESSAGE  = 'sensor: ' + conf['1wire']['sensors'][sen]['name'] + ' temp: ' +  str("%.2f" % temp)
                        print (MESSAGE)
                        communication.send_msg(MESSAGE)
            time_temp = 0
        else:
            time_temp = time_temp + 1
        
        await asyncio.sleep(time_sleep)
    
try:
    asyncio.run(main())
    
finally:
    asyncio.new_event_loop()