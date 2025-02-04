import gc
import machine

def free_mem():
    gc.collect()
    mem = 0
    if gc.mem_free() < 100000:
        mem = mem + 1
    else:
        mem = 0
    if mem > 1:
        machine.reset()