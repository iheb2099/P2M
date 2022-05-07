from deepface.detectors.FaceDetector import detect_faces,build_model
from cv2 import imread,imshow,waitKey,FONT_HERSHEY_SIMPLEX,rectangle,putText
from deepface.DeepFace import represent
from elasticsearch import Elasticsearch
from datetime import datetime
from uknownimages import storeImageElastic
from PIL import Image

es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])
detector_name = "mtcnn"
detector = build_model(detector_name)
models = ["Dlib", "ArcFace","Facenet512"]



def detectfaces(img_path):
    img = imread(img_path)
    obj = detect_faces(detector, detector_name, img, align=True)
    [x, y, w, h] = obj[0][1]
    face = img[y:y + h, x:x + w]
    return face


def storefaces(img_path):
    face = detectfaces(img_path)
    embedding_arcface = represent(face, model_name=models[2], enforce_detection=False)
    embedding_facenet = represent(face, model_name=models[0], enforce_detection=False)
    embedding_dlib = represent(face, model_name=models[1], enforce_detection=False)
    # #
    # # print("dlib",type(embedding_dlib),type(embedding_facenet),type(embedding_arcface))
    d = {"fname": img_path.split("/")[1].split('.')[0], 'lname': 'Belghouthi', 'classgroup': 'INDP2', 'classlevel': 'A',
         'dateadded': '2022-02-25', 'department': 'AIM', 'email': 'mohamediheb.belghouthi@supcom.tn', 'facetype': '',
         'isActive': True, 'usertype': 'Studenet', "Dlib": embedding_dlib, "Facenet512": embedding_facenet,
         "ArcFace": embedding_arcface}
    # store in elasticsearch
    es.index(index="knnfaces", document=d, doc_type="_doc")


def embeddings(face):
    return {'dlib':represent(face, model_name=models[0], enforce_detection=False ,align=True),'arcface':represent(face, model_name=models[1], enforce_detection=False,align=True),'facenet':represent(face, model_name=models[2], enforce_detection=False,align=True)}
def comparefaces(img_path_to_comp,camera='camera 1'):
    img1 = imread(img_path_to_comp)
    img=Image.open(img_path_to_comp)
    obj1 = detect_faces(detector, detector_name, img1, align=True)
    if len(obj1)==0:
        print('no faces detected')
        return 1
    if (len(obj1) == 1):
        print("there is ", len(obj1), " face")
    else:
        print("there are ", len(obj1), " faces")
    i = 0
    attendies=[]
    for facei in obj1:
        i += 1
        faceEmbeddings=embeddings(facei[0])
        embedding_dlib1 = faceEmbeddings['dlib']
        embedding_arcface1 = faceEmbeddings['arcface']
        embedding_facenet1 = faceEmbeddings['facenet']

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
            l = {}
            # double score=float(hit['_score'])
            # if (float(hit['_score']) > 0.93):
            l['fname']=hit['_source']['fname']
            l['lname']=hit['_source']['lname']
            l['classgroup']=hit['_source']['classgroup']
            l['classlevel']=hit['_source']['classlevel']
            l['dateadded']=hit['_source']['dateadded']
            l['email']=hit['_source']['email']
            l['usertype']=hit['_source']['usertype']
            l['datedetected'] = datetime.today().strftime('%Y-%m-%d')
            l['timedetected'] = datetime.today().strftime('%H:%M:%S')
            l['model']='Dlib'
            l['distance']=1-float(hit['_score'])

            matches.append(l)









        for hit in responseFacenet['hits']['hits']:
            l = {}
            # double score=float(hit['_score'])
            # if (float(hit['_score']) > 0.93):
            l['fname'] = hit['_source']['fname']
            l['lname'] = hit['_source']['lname']
            l['classgroup'] = hit['_source']['classgroup']
            l['classlevel'] = hit['_source']['classlevel']
            l['dateadded'] = hit['_source']['dateadded']
            l['email'] = hit['_source']['email']
            l['usertype'] = hit['_source']['usertype']
            l['datedetected'] = datetime.today().strftime('%Y-%m-%d')
            l['timedetected'] = datetime.today().strftime('%H:%M:%S')
            l['model'] = 'facenet'
            l['distance'] = float(hit['_score'])-1
            matches.append(l)


        for hit in responseArcface['hits']['hits']:
            l = {}
            # double score=float(hit['_score'])
            # if (float(hit['_score']) > 0.93):
            l['fname'] = hit['_source']['fname']
            l['lname'] = hit['_source']['lname']
            l['classgroup'] = hit['_source']['classgroup']
            l['classlevel'] = hit['_source']['classlevel']
            l['dateadded'] = hit['_source']['dateadded']
            l['email'] = hit['_source']['email']
            l['usertype'] = hit['_source']['usertype']
            l['datedetected']= datetime.today().strftime('%Y-%m-%d')
            l['timedetected']=datetime.today().strftime('%H:%M:%S')
            l['model'] = 'arcface'
            l['distance'] =  float(hit['_score'])-1
            matches.append(l)



        dist = [x['distance'] for x in matches]
        item = matches[dist.index(max(dist))]
        if item['distance']<0.47:
            print("==> This face is unkown")
            attendies.append({'fname':'unknown','datedetected':datetime.today().strftime('%Y-%m-%d')})
        else:
            attendies.append(item)
            print("==> This face  matches with ", item['fname'], ",the score is", item['distance'], ' using ', item['model'])
    for x in attendies:
        if x['fname']=='unknown':
            storeImageElastic(img,'unknowns',camera)
            break
        else:
            continue
    return attendies
def storeInDB(l,cameraId,dateTaken,timeTaken):
    for e in l:
        print(e)
        e['cameraId']=cameraId
        if e['fname']!='unknown':
            es.index(index="attendance", document=e, doc_type="_doc")
        else:
            es.index(index="attendance", document={'fname':'unknown','datedetected':datetime.today().strftime('%Y-%m-%d'),'timedetected':datetime.today().strftime('%H:%M:%S')}, doc_type="_doc")
    print('stored into attendance database')






def showfaces(image_path):
    obj1 = detect_faces(detector, detector_name,imread(image_path), align=True)
    attendies=comparefaces(image_path)
    image = imread(image_path)
    faces = [x[1] for x in obj1]
    names=[e['fname'] for e in attendies]
    for ((x, y, w, h), name) in zip(faces, names):
        # rescale the face coordinates
        # draw the predicted face name on the image
       rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
       putText(image, name, (x, y), FONT_HERSHEY_SIMPLEX,
                    0.75, (0, 255, 0), 2)
    imshow("Frame", image)
    waitKey(0)
