import cv2
import io
import socket
import struct
import time
import pickle
import numpy as np
import imutils

cameraId='camera 1'
def sendImage():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client_socket.connect(('0.tcp.ngrok.io', 19194))
    client_socket.connect(('192.168.228.66', 8485))

    cam = cv2.VideoCapture(0)
    img_counter = 0

    # encode to jpeg format
    # encode param image quality 0 to 100. default:95
    # if you want to shrink data size, choose low image quality.
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 100]

    ret, frame = cam.read()
    frame = imutils.resize(frame, width=720)
    frame = cv2.flip(frame, 180)
    result, image = cv2.imencode('.jpg', frame, encode_param)
    d={'image':image,'Id':cameraId}
    data = pickle.dumps(d, 0)
    size = len(data)

    if img_counter % 10 == 0:
        client_socket.sendall(struct.pack(">L", size) + data)
        img_counter += 1

    cam.release()
