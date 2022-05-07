import streamlit as st

from uknownimages import searchUnkowns
import numpy as np
from PIL import Image
import datetime
def streamlitUnkown():
    col1,col2,col3,col4,col5=st.columns(5)
    st.title('unknowns')
    with col1:
        cameras = st.selectbox('camera', ('camera 1', 'camera 2', 'camera 3'))
    with col2:
        datefrom=st.date_input(label="from")
    with col3:
        dateto=st.date_input(label="to")

    with col4:
        timefrom = st.time_input('from: ',value=datetime.time(hour=0,minute=0,second=0)).strftime('%H:%M:%S')
    with col5:
        timeto = st.time_input('to: ', value=(datetime.datetime.now() + datetime.timedelta(minutes=1)).time()).strftime(
            '%H:%M:%S')

    submit=st.button('submit')
    if submit:
        l=searchUnkowns(datefrom=datefrom,dateto=dateto,timefrom=timefrom,timeto=timeto,cameras=cameras)
        if l!={}:
            for e in l['raw_data']:
                ind=l['raw_data'].index(e)
                data=np.uint8(np.array(e))
                img=Image.fromarray(data)
                st.image(img,caption=f"{l['datedetected'][ind]}  {l['timedetected'][ind]}",use_column_width=True)
        else:
            st.write('no images to be shown')
