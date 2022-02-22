from deepface.detectors import FaceDetector
import cv2
from deepface import DeepFace



def embedding(img,model):
    detector_name = 'mtcnn'

    models = ["Facenet512", "Dlib", "ArcFace"]
    if model not in models:
        raise Exception("model must be one of these:\n    Dlib,ArcFace,Facenet512")
    detector = FaceDetector.build_model(detector_name)
    obj = FaceDetector.detect_faces(detector, detector_name, img, align=True)
    for face in obj:
        embedding = DeepFace.represent(face[0], model_name=model, enforce_detection=False)
        [x, y, w, h] = face[1]
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return [embedding,len(obj)]

