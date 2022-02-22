import streamlit as st
import cv2
import pandas as pd
import numpy as np
import re
from PIL import Image
import time
from backend import embedding
from elasticsearch import Elasticsearch
from deepface.detectors import FaceDetector
from datetime import datetime
import os
from fastapi import FastAPI,Path
from typing import Optional
from pydantic import BaseModel
models =  ["Facenet512","Dlib","ArcFace"]

es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])

detector_name = "mtcnn"
detector = FaceDetector.build_model(detector_name)


regex = re.compile(r'^[a-z0-9](\.?[a-z0-9]){5,}@supcom\.tn$')

def is_email_valid(email):
    return re.fullmatch(regex,email)
def load_image(image_file):
	img = Image.open(image_file)
	return img
parent_dir='C:/Users/iheb9/PycharmProjects/Streamlit'
@st.cache(allow_output_mutation=True)
def get_data():
    return []


st.set_page_config(
    page_title="Smart attendance",
    layout="wide",
    initial_sidebar_state="expanded"
)

def form():
    st.title("Welcome to smart Attendance System")
    col1, col2= st.columns(2)

    with col1:
        first_name = st.text_input(label='First Name')
        last_name = st.text_input(label='Second Name')
        email = st.text_input(label='Email',value="something@supcom.tn")

        status = st.radio("Status", ("Student", "Teacher", "Administrative"))

        if status == 'Student':
            classes = st.selectbox('class', ("INDP1", "INDP2", "INDP3"))
            if classes == "INDP1":
                choix=st.selectbox('choix', ("A", "B", "C", "D", "E", "F"))
            elif classes == "INDP2":
                choix=st.selectbox('choix', ("A", "B", "C", "D", "E", "F"))

            else:
                option = st.radio('Option', ('Systic', 'AIM', 'Cybersecurity', 'MIT'))

        if status == 'Teacher':
            department = st.selectbox('Department', ("MASC", "EPP", "IR", "EGDHL"))

        st.subheader("Webcam Live frame")

        if 'count' not in st.session_state:
            st.session_state.count = 0

    def increment_counter(increment_value=0):
        st.session_state.count += increment_value

    def decrement_counter(decrement_value=0):
        st.session_state.count -= decrement_value


    with col2:
        show_camera=st.checkbox("Show camera")
        if show_camera:
            img_file_buffer = st.camera_input("Take a picture")



    def uploadImageWebcam():
             if img_file_buffer is not None:
                bytes_data = img_file_buffer.getvalue()
                cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

                return (cv2_img)

    if st.text("pick a picture "):
        uploaded_files = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg"],
                                          accept_multiple_files=True)


    def uploadPhotoFile():
        if uploaded_files is not None:

            bytes_data = uploaded_files[0].getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

            return (cv2_img)
    if st.button("Submit"):
        if first_name == "" or last_name == "" or status == "" :
            st.write('data not complete')
        if not (is_email_valid(email)):
            st.write("invalid email please use a supcom email")
        if ( uploaded_files) is None:
            st.write('you must take a picture')
        else:
            # if (img_file_buffer is not None):
            #     x=embedding(uploadImageWebcam(),'Facenet512')[1]
            #     result=[embedding(uploadImageWebcam(),'Facenet512')[0],embedding(uploadImageWebcam(),'Dlib')[0],embedding(uploadImageWebcam(),'ArcFace')[0]]
            #     facesNumber=x
            if (uploaded_files is not None):
                x = embedding(uploadPhotoFile(), 'Facenet512')[1]
                result = [embedding(uploadPhotoFile(), 'Facenet512')[0],
                          embedding(uploadPhotoFile(), 'Dlib')[0], embedding(uploadPhotoFile(), 'ArcFace')[0]]
                facesNumber = x
                if facesNumber!=1:
                    st.write('there must be only 1 face')
                else:

                    if status == "Student":
                        if classes=='INDP3':
                            d={"fname": first_name, "lname": last_name, "email": email, "usertype": status,
                             'classgroup': classes+' '+option, 'dateadded': datetime.today().strftime('%Y-%m-%d'),'Dlib':result[1],'Facenet512': result[0],'ArcFace':result[2]}
                            es.index(index="knnfaces", document=d, doc_type="_doc")
                        else:
                            d = {"fname": first_name, "lname": last_name, "email": email, "usertype": status,
                                 'classgroup': classes,'classlevel':choix, 'dateadded': datetime.today().strftime('%Y-%m-%d'),
                                 'Dlib': result[1], 'Facenet512': result[0], 'ArcFace': result[2]}

                            es.index(index="knnfaces", document=d, doc_type="_doc")

                    if status == 'Teacher':
                        d={"fname": first_name, "lname": last_name, "email": email, "usertype": status,
                                           'department': department,'dateadded':datetime.today().strftime('%Y-%m-%d'),'Dlib':result[1],'Facenet512': result[0],'ArcFace':result[2]}
                        es.index(index="knnfaces", document=d, doc_type="_doc")
                        st.write("Done")


                    if status == 'Administrative':
                        d={"fname": first_name, "lname": last_name, "email": email, "usertype": status,
                                           'dateadded': datetime.today().strftime('%Y-%m-%d'),'Dlib':result[1],'Facenet512': result[0],'ArcFace':result[2]}
                        es.index(index="knnfaces", document=d, doc_type="_doc")
                        st.write("Done")




