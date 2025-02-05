import ubinascii
import hashlib
import binascii

def auth_barrier(user, password):
    barrier = str(ubinascii.b2a_base64("'" + user + ":" + password + "'").strip()).replace("b'", "").replace("'", "")
    hash_object = hashlib.sha256()
    hash_object.update(barrier.encode())
    hash_barrier = binascii.hexlify(hash_object.digest())
    return hash_barrier
    
