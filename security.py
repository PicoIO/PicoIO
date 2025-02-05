import ubinascii
import hashlib
import binascii

def auth_barrier(password):
    barrier = str(ubinascii.b2a_base64('admin:%s' % (password)).strip()).replace("b'", "").replace("'", "")
    hash_object = hashlib.sha256()
    hash_object.update(barrier.encode())
    hash_barrier = binascii.hexlify(hash_object.digest())
    print (hash_barrier)
    return hash_barrier
    