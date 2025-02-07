from gc import collect
from os import listdir, remove, mkdir, rename
from urequests import get
from machine import reset

def update_conf_fn(new_conf_id, new_conf, conf):
    hw_conf = str(conf['hw']).replace("'", '"')
    gpio_conf = str(conf['gpio']).replace("'", '"')
    debounce_conf = str(conf['debounce']).replace("'", '"')
    wire_conf = str(conf['1wire']).replace("'", '"')
    network_conf = str(conf['network']).replace("'", '"')
    communication_conf = str(conf['communication']).replace("'", '"')
    security_conf = str(conf['security']).replace("'", '"')

    if new_conf_id == 1:
            hw_conf = new_conf
    elif new_conf_id == 2:
            gpio_conf = new_conf
    elif new_conf_id == 3:
            debounce_conf = new_conf
    elif new_conf_id == 4:
            wire_conf = new_conf
    elif new_conf_id == 5:
            network_conf = new_conf
    elif new_conf_id == 6:
            communication_conf = new_conf
    elif new_conf_id == 7:
            security_conf = new_conf

    config_str = '{\n  "hw":\n  ' + hw_conf + ',\n  "gpio":\n  ' + gpio_conf + ',\n  "debounce":\n  '
    config_str += debounce_conf + ',\n  "1wire":\n  ' + wire_conf + ',\n  "network":\n  '
    config_str += network_conf + ',\n  "communication":\n  ' + communication_conf + ',\n  "security":\n  '
    config_str += security_conf + ',\n}'

    config = open("config.conf", "w")
    config.write(config_str)
    config.close()

    del hw_conf, gpio_conf, debounce_conf, wire_conf, network_conf, communication_conf, security_conf, config_str, config
    collect()

def upadte_fn(conf, version):
    #download update
    mkdir('update')
    download_suc = 0
    try:
        sw = get_files('', version)

        for items in sw:
            collect()
            if items['type'] == 'dir' and items['path'] != '.github':
                print ("create directory: update/" + items['path'])
                mkdir('update/' + items['path'])
                sw1 = get_files(items['path'], version)
                for item in sw1:
                    if item['type'] == 'file':
                        url = item['download_url']
                        fl = get(url)
                        print ('download file: update/' + item['path'])
                        with open('update/' + item['path'], 'wb') as fd:
                            fd.write(fl.content)
                        fd.close()
            elif items['type'] == 'file':
                url = items['download_url']
                fl = get(url)
                print ('download file: update/' + items['name'])
                with open('update/' + items['name'], 'wb') as fd:
                    fd.write(fl.content)
                fd.close()
        download_suc += 1
    except:
         download_suc = 0
    
    if download_suc > 0:
        for items in listdir():
            if items != 'update' and not items.endswith('.conf'):
                try:
                    for item in listdir(items):
                        print ('remove: ' + items + '/' + item)
                        remove(items + '/' + item)
                    print ('remove: ' + items)
                    remove(items)
                except:
                    print ('remove: ' + items)
                    remove(items)

        del items
        del item
        collect()

        for items in listdir('update'):
            try:
                for item in listdir('update/' + items):
                    print ('move: update/' + items + '/' + item + ' to: ' + items + '/' + item)
                    rename('update/' + items + '/' + item, items + '/' + item)
                print ('move: update/' + items + ' to: ' + items)
                rename('update/' + items, items)
            except:
                print ('move: update/' + items + ' to: ' + items)
                rename('update/' + items, items)

        remove('update')
        remove('update.conf')

        #update config with new version
        hw_conf = '{"board": "' + conf['hw']['board'] + '", "release": "' + conf['hw']['release'] + '", "sw": "'
        hw_conf += version + '", "sw_ch": "' + conf['hw']['sw_ch'] + '", "sysname": "' + conf['hw']['sysname'] + '"}'

        update_conf_fn(1, hw_conf, conf)
    
        del hw_conf
        collect()
    else:
        #if download faild delete update
        for items in listdir('update'):
            try:
                for item in listdir('update/' + items):
                    print ('remove: update/' + items + '/' + item)
                    remove('update/' + items + '/' + item)
                print ('remove: update/' + items + ' to: ' + items)
                remove('update/' + items)
            except:
                print ('remove: update/' + items + ' to: ' + items)
                remove('update/' + items)

        remove('update')
        remove('update.conf')

    reset()

def get_files(path, version):
    url = "https://api.github.com/repos/picoio/picoio/contents/" + path + "?ref=refs/tags/" + version
    sw = get(url, headers = {'User-Agent': 'Mozilla/5.0'}).json()
    
    return sw