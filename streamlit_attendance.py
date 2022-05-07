import datetime
import sys
sys.path.append('search_attendance.py')
import streamlit as st
from elasticsearch import Elasticsearch
import search_attendance

es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])
from st_aggrid import AgGrid


def streamlitAttendance():
    st.title("Smartattendance Sheet")
    cameras = st.selectbox('camera', ('camera 1', 'camera 2', 'camera 3'))
    date = st.date_input("date")
    col1, col2 = st.columns(2)
    with col1:
        timefrom = st.time_input('from: ').strftime('%H:%M:%S')
    with col2:
        timeto = st.time_input('to: ', value=(datetime.datetime.now() + datetime.timedelta(minutes=1)).time()).strftime(
            '%H:%M:%S')

    submit = st.button('submit')

    if submit:
        st.write(cameras)
        df = search_attendance.searchAttendance(cameras=cameras, date=date, timefrom=timefrom, timeto=timeto)
        AgGrid(df)




