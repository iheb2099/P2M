# Import necessary libraries


from multipage import MultiPage
import streamlit as st

# Custom imports
from streamlit_attendance import streamlitAttendance
from streamlitUnkown import streamlitUnkown


# Create an instance of the app
def streamlitMultipage():
    app = MultiPage()

    # Title of the main page
    st.title("SmartAttendance Application")

    # Add all your applications (pages) here
    app.add_page("check attendance",streamlitAttendance)
    app.add_page("check unknowns",streamlitUnkown)



    # The main app
    app.run()