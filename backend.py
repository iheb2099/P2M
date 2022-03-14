from deepface.detectors.FaceDetector import build_model,detect_faces
import cv2
from deepface.DeepFace import represent



def embedding(img,model):
    detector_name = 'mtcnn'

    models = ["Facenet512", "Dlib", "ArcFace"]
    if model not in models:
        raise Exception("model must be one of these:\n    Dlib,ArcFace,Facenet512")
    detector = build_model(detector_name)
    obj = detect_faces(detector, detector_name, img, align=True)
    for face in obj:
        embedding = represent(face[0], model_name=model, enforce_detection=False)
        [x, y, w, h] = face[1]
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return [embedding,len(obj)]

