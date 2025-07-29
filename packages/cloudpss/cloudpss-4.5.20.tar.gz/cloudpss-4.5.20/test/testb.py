import os,sys
import time

import socketio
import threading
import struct

                         
if __name__ == '__main__':
   a = [1.21,2.22,3.33]
   x = struct.pack('d'*len(a),*a)
   print(x)
   print(len(x))
   
   t = struct.unpack('d'*int(len(x)/8),x)
   
        
   print(t)