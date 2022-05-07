import socket
import cv2
import pickle
import struct
from deepface.detectors.FaceDetector import build_model
from elasticKnn import comparefaces
from elasticKnn import storeInDB
from elasticsearch import Elasticsearch
import shutil
es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])
detector_name = "mtcnn"
detector = build_model(detector_name)
models = ["Facenet512", "Dlib", "ArcFace"]
def server(HOST,PORT):
    HOST='192.168.228.66'
    PORT=8485

    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print('Socket created')

    s.bind((HOST,PORT))
    print('Socket bind complete')
    s.listen(10)
    print('Socket now listening')
    while True:
        try:
            conn,addr=s.accept()

            data = b""
            payload_size = struct.calcsize(">L")
            print("payload_size: {}".format(payload_size))
            while len(data) < payload_size:
                data += conn.recv(4096)
            # receive image row data form client socket
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack(">L", packed_msg_size)[0]
            while len(data) < msg_size:
                data += conn.recv(4096)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            # unpack image using pickle
            frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
            Id=frame['Id']
            image=frame['image']
            dateTaken=frame['datetaken']
            timeTaken=frame['timetaken']

            print(frame)
            print(Id)
            frame = cv2.imdecode(image, cv2.IMREAD_COLOR)
            cv2.imwrite('../frame.jpg', frame)
            if frame.any():
                print("comparing")
                result=comparefaces('../frame.jpg', Id)
                if result == 1:
                    continue
                for e in result:
                    if e['fname']=='unknown':
                        print('writing unknown face')
                        shutil.copy("../frame.jpg", f"images/unknowns/unknown{dateTaken} {str(timeTaken).replace(':', '-')}.jpg")

                if result!=1:
                    storeInDB(result,Id,dateTaken,timeTaken)
        except Exception as e:
            print('an error has occured',e)


