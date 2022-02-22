from deepface.detectors import FaceDetector
import cv2
from deepface import DeepFace
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import pandas as pd

es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])

# crop and detect face
detector_name = "mtcnn"
detector = FaceDetector.build_model(detector_name)
models = ["Facenet512", "Dlib", "ArcFace"]


def detectfaces(img_path):
    img = cv2.imread(img_path)
    obj = FaceDetector.detect_faces(detector, detector_name, img, align=True)
    [x, y, w, h] = obj[0][1]
    face = img[y:y + h, x:x + w]
    return face


# calculation of the 3  feature vectors
def storefaces(img_path):
    face = detectfaces(img_path)
    embedding_arcface = DeepFace.represent(face, model_name=models[2], enforce_detection=False)
    embedding_facenet = DeepFace.represent(face, model_name=models[0], enforce_detection=False)
    embedding_dlib = DeepFace.represent(face, model_name=models[1], enforce_detection=False)
    # #
    # # print("dlib",type(embedding_dlib),type(embedding_facenet),type(embedding_arcface))
    d = {"Dlib": embedding_dlib, "Facenet512": embedding_facenet, "ArcFace": embedding_arcface,
         "fname": img_path.split("/")[1].split('.')[0], 'classgroup': 'INDP2', 'classlevel': 'A',
         'dateadded': '2022-02-25', 'department': 'AIM', 'email': 'mohamediheb.belghouthi@supcom.tn', 'facetype': '',
         'isActive': True, 'lname': 'Belghouthi', 'usertype': 'Studenet'}
    # store in elasticsearch
    es.index(index="knnfaces", document=d, doc_type="_doc")


names = []


def comparefaces(img_path_to_comp="images/iheb_bedis_imen.jpg"):
    # compare_faces( using 1 feature vector):
    img1 = cv2.imread(img_path_to_comp)
    obj1 = FaceDetector.detect_faces(detector, detector_name, img1, align=True)
    i = 0
    for facei in obj1:
        i += 1
        print("Face", i, "")

        embedding_dlib1 = DeepFace.represent(facei[0], model_name=models[1], enforce_detection=False)
        embedding_arcface1 = DeepFace.represent(facei[0], model_name=models[0], enforce_detection=False)
        embedding_facenet1 = DeepFace.represent(facei[0], model_name=models[2], enforce_detection=False)
        print(embedding_facenet1)
        query = {

            "query": {
                "elastiknn_nearest_neighbors": {
                    "field": "Dlib",
                    "vec": {
                        "values": embedding_dlib1
                    },
                    "similarity": "l2",
                    "model": "exact",

                }
            }

        }
        query1 = {

            "query": {
                "elastiknn_nearest_neighbors": {
                    "field": "Facenet512",
                    "vec": {
                        "values": embedding_facenet1
                    },
                    "similarity": "l2",
                    "model": "exact",

                }
            }

        }
        query2 = {

            "query": {
                "elastiknn_nearest_neighbors": {
                    "field": "ArcFace",
                    "vec": {
                        "values": embedding_arcface1
                    },
                    "similarity": "l2",
                    "model": "exact",

                }
            }

        }
        response = es.search(index="knnfaces", body=query)
        response1 = es.search(index="knnfaces", body=query1)
        response2 = es.search(index="knnfaces", body=query2)
        matchesdlib = []
        matchesfacenet = []
        matchesarcface = []
        for hit in response['hits']['hits']:
            # double score=float(hit['_score'])
            if float(hit['_score']) > 0.5:
                matchesdlib.append((hit['_source']['fname'], float(hit['_score']), 'dlib'))
        print('matchesdlib= ', matchesdlib)
        distdlib = [x[1] for x in matchesdlib]
        position = distdlib.index(max(distdlib))
        print("==> This face  matches with ", matchesdlib[position][0], ",the score is", matchesdlib[position][1],
              ' using ', matchesdlib[position][2])

        for hit in response1['hits']['hits']:
            # double score=float(hit['_score'])
            # if (float(hit['_score']) > 0.93):
            matchesfacenet.append((hit['_source']['fname'], float(hit['_score']), 'facenet'))
        print('matchesfacenet= ', matchesfacenet)

        distfacenet = [x[1] for x in matchesfacenet]
        position = distfacenet.index(min(distfacenet))
        print("==> This face  matches with ", matchesfacenet[position][0], ",the score is", matchesfacenet[position][1],
              ' using ', matchesfacenet[position][2])

        for hit in response2['hits']['hits']:
            # double score=float(hit['_score'])
            # if (float(hit['_score']) > 0.93):
            matchesarcface.append((hit['_source']['fname'], float(hit['_score']), 'arcface'))
        print('matchesarcface= ', matchesarcface)

        distarcface = [x[1] for x in matchesarcface]
        position = distarcface.index(min(distarcface))
        print("==> This face  matches with ", matchesarcface[position][0], ",the score is", matchesarcface[position][1],
              ' using ', matchesarcface[position][2])

        # dist=[x[1] for x in matches]
        # item=matches[dist.index(max(dist))]
        # names.append(item[0])
        # print("==> This face  matches with ", item[0], ",the score is" ,item[1] ,' using ',item[2] )
        # print("there are ", len(obj1), " faces")


obj1 = FaceDetector.detect_faces(detector, detector_name, cv2.imread('images/iheb_bedis_imen.jpg'), align=True)


def showfaces(faces, image_path):
    image = cv2.imread(image_path)
    faces = [x[1] for x in faces]
    for ((x, y, w, h), name) in zip(faces, names):
        # rescale the face coordinates
        # draw the predicted face name on the image
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, (0, 255, 0), 2)
    cv2.imshow("Frame", image)
    cv2.waitKey(0)


# storefaces('images/bedis.jpg')
comparefaces('images/iheb_bedis_imen.jpg')
showfaces(obj1, 'images/iheb_bedis_imen.jpg')
