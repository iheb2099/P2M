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
face_to_store = 'images/facetostore/benzarti.jpg'
face_to_compare = 'images/comparaison/forum.jpg'


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
    d = {"fname": img_path.split("/")[1].split('.')[0], 'lname': 'Belghouthi', 'classgroup': 'INDP2', 'classlevel': 'A',
         'dateadded': '2022-02-25', 'department': 'AIM', 'email': 'mohamediheb.belghouthi@supcom.tn', 'facetype': '',
         'isActive': True, 'usertype': 'Studenet', "Dlib": embedding_dlib, "Facenet512": embedding_facenet,
         "ArcFace": embedding_arcface}
    # store in elasticsearch
    es.index(index="knnfaces", document=d, doc_type="_doc")


# get the  feature from elasticsearch
def get_data_from_elastic():
    # query: The elasticsearch query.
    query = {
        "query": {
            "match_all": {

            }
        }
    }
    # Scan function to get all the data.
    rel = scan(client=es,
               query=query,
               scroll='3m',
               index='knnfaces',
               raise_on_error=True,
               preserve_order=False,
               clear_scroll=True)
    #  response in a list.
    result = list(rel)
    temp = []
    for hit in result:
        temp.append(hit['_source'])
    # Create a dataframe.
    df = pd.DataFrame(temp)
    return df


df = get_data_from_elastic()
# # df.to_csv(r'C:\Users\ASUS\Desktop\elastic\test.csv')
#
print(df.head(50))
names = []


def comparefaces(img_path_to_comp="images/"):
    # compare_faces( using 1 feature vector):
    img1 = cv2.imread(img_path_to_comp)
    obj1 = FaceDetector.detect_faces(detector, detector_name, img1, align=True)
    i = 0
    for facei in obj1:
        i += 1
        embedding_dlib1 = DeepFace.represent(facei[0], model_name=models[1], enforce_detection=False ,align=True)
        embedding_arcface1 = DeepFace.represent(facei[0], model_name=models[2], enforce_detection=False,align=True)
        embedding_facenet1 = DeepFace.represent(facei[0], model_name=models[0], enforce_detection=False,align=True)

        print("Face", i, "")
        queryDlib = {

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
        queryFacenet = {

            "query": {
                "elastiknn_nearest_neighbors": {
                    "field": "Facenet512",
                    "vec": {
                        "values": embedding_facenet1
                    },
                    "similarity": "cosine",
                    "model": "exact",

                }
            }

        }
        queryArcface = {

            "query": {
                "elastiknn_nearest_neighbors": {
                    "field": "ArcFace",
                    "vec": {
                        "values": embedding_arcface1
                    },
                    "similarity": "cosine",
                    "model": "exact",

                }
            }

        }
        responseDlib = es.search(index="knnfaces", body=queryDlib)
        responseFacenet = es.search(index="knnfaces", body=queryFacenet)
        responseArcface = es.search(index="knnfaces", body=queryArcface)
        matches = []
        for hit in responseDlib['hits']['hits']:
            # double score=float(hit['_score'])
            # if (float(hit['_score']) > 0.93):
            matches.append((hit['_source']['fname'], 2*float(hit['_score']), 'dlib'))

        for hit in responseFacenet['hits']['hits']:
            # double score=float(hit['_score'])
            # if (float(hit['_score']) > 0.93):
            matches.append((hit['_source']['fname'], float(hit['_score']), 'facenet'))

        for hit in responseArcface['hits']['hits']:
            # double score=float(hit['_score'])
            # if (float(hit['_score']) > 0.93):
            matches.append((hit['_source']['fname'], float(hit['_score']), 'arcface'))

        dist = [x[1] for x in matches]
        item = matches[dist.index(max(dist))]
        if item[1]<1.55:
            print("==> This face is unkown")
            names.append('unkown')
        else:
            names.append(item[0])
            print("==> This face  matches with ", item[0], ",the score is", item[1], ' using ', item[2])
            print("there are ", len(obj1), " faces")


obj1 = FaceDetector.detect_faces(detector, detector_name, cv2.imread(face_to_compare), align=True)


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

# storefaces(face_to_store)
comparefaces(face_to_compare)
showfaces(obj1, face_to_compare)
