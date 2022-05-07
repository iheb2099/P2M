import streamlit_authenticator as stauth
import streamlit as st
from streamlitmultipage import streamlitMultipage



names = ['iheb Belghouthi ','Rebecca Briggs']
usernames = ['iheb2099','rbriggs']
passwords = ['123','456']
hashed_passwords = stauth.hasher(passwords).generate()
authenticator = stauth.authenticate(names,usernames,hashed_passwords,
    'some_cookie_name','some_signature_key',cookie_expiry_days=0)
name, authentication_status = authenticator.login('Login','main')
if st.session_state['authentication_status']:
    streamlitMultipage()
elif st.session_state['authentication_status'] == False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] == None:
    st.warning('Please enter your username and password')
