import streamlit as st
import database as db
from patient import Patient
from department import Department
from doctor import Doctor
from prescription import Prescription
from medical_test import Medical_Test
import sqlite3 as sql



# def Register():
#     if password != c_password:
#         st.error("Passwords are different")

identity = st.radio('What is your identity',['Patient','Doctor'])

if identity == 'Doctor':
    new_doc = Doctor()
    new_doc.add_doctor()
elif identity == 'Patient':
    new_pat = Patient()
    new_pat.add_patient()
# user_id = st.text_input('Enter your id')
#
# password = st.text_input('Enter password', type='password')  # user password authentication
# c_password = st.text_input('Confirm your password', type='password')  # user password authentication
# register_button = st.button('Register',on_click=Register)




