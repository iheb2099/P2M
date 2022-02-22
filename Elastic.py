from deepface.detectors import FaceDetector
import cv2
from deepface import DeepFace
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import pandas as pd
es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])
img_path = "images/iheb.jpg"

#crop and detect face
detector_name = "mtcnn"
img = cv2.imread(img_path)
detector = FaceDetector.build_model(detector_name)
models =  ["Facenet512","Dlib","ArcFace"]


def detectfaces(img_path):
    img = cv2.imread(img_path)
    obj = FaceDetector.detect_faces(detector, detector_name, img, align=True)
    [x, y, w, h] = obj[0][1]
    face = img[y:y + h, x:x + w]
    return face

#calculation of the 3  feature vectors
def storefaces():
    face = detectfaces(img_path)
    embedding_arcface = DeepFace.represent(face, model_name=models[2],enforce_detection=False )
    embedding_facenet=DeepFace.represent(face, model_name=models[0],enforce_detection=False )
    embedding_dlib = DeepFace.represent(face, model_name=models[1],enforce_detection=False )
# #
# # print("dlib",type(embedding_dlib),type(embedding_facenet),type(embedding_arcface))
    d={"face_encoding": embedding_dlib,"face_encoding1":embedding_facenet,"face_encoding2":embedding_arcface,"face_name":img_path.split("/")[1]}
#store in elasticsearch
    es.index(index="faces1", document=d ,doc_type="_doc")

#get the  feature from elasticsearch
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
               index='faces1',
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


def comparefaces(img_path_to_comp="images/iheb_bedis_imen.jpg"):


    # compare_faces( using 1 feature vector):
    img1 = cv2.imread(img_path_to_comp)
    obj1 = FaceDetector.detect_faces(detector, detector_name, img1, align=True)
    i=0
    for facei in obj1:
        i += 1
        embedding_dlib1 = DeepFace.represent(facei[0], model_name=models[1], enforce_detection=False)
        embedding_arcface1 = DeepFace.represent(facei[0], model_name=models[0], enforce_detection=False)
        embedding_facenet1 = DeepFace.represent(facei[0], model_name=models[2], enforce_detection=False)

        print("Face", i, "")
        query = {

                    "query": {
                        "script_score": {
                            "query": {
                                "match_all": {}
                            },
                            "script": {
                                "source": "1+ cosineSimilarity(params.query_vector, doc['face_encoding'])",
                                "params": {
                                    "query_vector": embedding_dlib1,
                                    "query_vector1": embedding_facenet1,
                                    "query_vector2": embedding_arcface1

                                }
                                 }
                             }
                                 }
            }
        query1 = {

            "query": {
                "script_score": {
                    "query": {
                        "match_all": {}
                    },
                    "script": {
                        "source": "1+ cosineSimilarity(params.query_vector1, doc['face_encoding1'])",
                        "params": {
                            "query_vector": embedding_dlib1,
                            "query_vector1": embedding_facenet1,
                            "query_vector2": embedding_arcface1

                        }
                    }
                }
            }
        }
        query2= {

            "query": {
                "script_score": {
                    "query": {
                        "match_all": {}
                    },
                    "script": {
                        "source": " 1+cosineSimilarity(params.query_vector2, doc['face_encoding2'])",
                        "params": {
                            "query_vector": embedding_dlib1,
                            "query_vector1": embedding_facenet1,
                            "query_vector2": embedding_arcface1

                        }
                    }
                }
            }
        }
        response = es.search(index="faces1", body=query)
        response1=es.search(index="faces1", body=query1)
        response2 = es.search(index="faces1", body=query2)
        matches= []
        for hit in response['hits']['hits']:
                    #double score=float(hit['_score'])
                    if (float(hit['_score']) > 0.93):
                        matches.append((hit['_source']['face_name'],float(hit['_score']),'dlib'))

        for hit in response1['hits']['hits']:
                    #double score=float(hit['_score'])
                    if (float(hit['_score']) > 0.93):
                        matches.append((hit['_source']['face_name'],float(hit['_score']),'facenet'))
        for hit in response2['hits']['hits']:
                    #double score=float(hit['_score'])
                    if (float(hit['_score']) > 0.93):
                        matches.append((hit['_source']['face_name'],float(hit['_score']),'arcface'))
        scores=[x[1] for x in matches]
        print(scores)
        item=matches[scores.index(max(scores))]
        names.append(item[0])
        print("==> This face  matches with ", item[0], ",the score is" ,item[1] ,' using ',item[2] )


        image=cv2.imread(img_path_to_comp)

        print("there are ", len(obj1), " faces")
obj1 = FaceDetector.detect_faces(detector, detector_name, cv2.imread('images/iheb_bedis_imen.jpg'), align=True)

def showfaces(faces,image_path):
    image=cv2.imread(image_path)
    faces = [x[1] for x in faces]
    for ((x, y, w, h), name) in zip(faces, names):
        # rescale the face coordinates
        # draw the predicted face name on the image
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, (0, 255, 0), 2)
    cv2.imshow("Frame", image)
    cv2.waitKey(0)
comparefaces('images/iheb_bedis_imen.jpg')
showfaces(obj1,'images/iheb_bedis_imen.jpg')




