import ctypes
import sys
import os

if sys.platform == "linux" or sys.platform == "linux2":
    _superfasthash = ctypes.CDLL(os.path.join(os.getcwd(), "superfasthash.so"))
elif sys.platform == "win32":
    _superfasthash = ctypes.CDLL(os.path.join(os.getcwd(), "superfasthash.dll"))
else:
    raise OSError("Unrecognized operating system.")
_superfasthash.hash.argtypes = (ctypes.c_char_p, ctypes.c_int)
_superfasthash.hash.restype = ctypes.c_uint

def c_superfasthash(content):
    length = len(content)
    global _superfasthash
    result = _superfasthash.hash(ctypes.create_string_buffer(content, length), ctypes.c_int(length))
    return int(result)
