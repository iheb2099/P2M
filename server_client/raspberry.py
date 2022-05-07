import io
import socket
import struct
from PIL import Image
import picamera
import time

s = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
ip = '192.168.1.2'
port = 12345
print("ok")
s.connect(('192.168.1.2', 12345))
print("ok")
connection = s.makefile('wb')
print("ok")
try:
    camera = picamera.PiCamera()
    camera.resolution = (640, 480)
    camera.start_preview()
    time.sleep(2)
    stream = io.BytesIO()
    camera.capture(stream , format='jpeg')
    connection.write(struct.pack('<L', stream.tell()))
    connection.flush()
    stream.seek(0)
    connection.write(stream.read())
    stream.seek(0)
    stream.truncate()
finally:
#    camera = picamera.PiCamera()
    camera.stop_preview()
    connection.close()
    socket.client_socket.close()