import streamlit as st
import database as db
from patient import *
from department import Department
from doctor import *
from prescription import Prescription
from medical_test import Medical_Test
import sqlite3 as sql

def verify_password(id, password):
    if id == 'root':
        return password == '123456', 'Admin'
    verify = False
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT password,auth_type
            FROM account
            WHERE user_id = :id;
            """,
            {"id": id}
        )
    type = ''
    for pd, tp in c.fetchall():
        if pd == password:
            verify = True
            type = tp
            break
    conn.close()

    return verify, type

def login():
    if st.session_state.access:
        st.sidebar.success(f'Welcome {st.session_state.auth_type}')
        home(st.session_state.auth_type,st.session_state.user)
    elif password == '':
        st.empty()
    else:
        st.sidebar.error("Wrong Password")



# function to perform various operations of the patient module (according to user's selection)
def patients():
    st.header('PATIENTS')
    option_list = ['', 'Add patient', 'Update patient', 'Delete patient', 'Show complete patient record',
                   'Search patient']
    option = st.sidebar.selectbox('Select function', option_list)
    p = Patient()
    if (option == option_list[1] or option == option_list[2] or option == option_list[
        3]):
        if option == option_list[1]:
            st.subheader('ADD PATIENT')
            p.add_patient()
        elif option == option_list[2]:
            st.subheader('UPDATE PATIENT')
            p.update_patient()
        elif option == option_list[3]:
            st.subheader('DELETE PATIENT')
            try:
                p.delete_patient()
            except sql.IntegrityError:  # handles foreign key constraint failure issue (due to integrity error)
                st.error('This entry cannot be deleted as other records are using it.')
    elif option == option_list[4]:
        st.subheader('COMPLETE PATIENT RECORD')
        p.show_all_patients()
    elif option == option_list[5]:
        st.subheader('SEARCH PATIENT')
        p.search_patient()

def edit_account(auth_type,id):
    if auth_type == 'Patient':
        st.header('PATIENTS')
        p = Patient()
        st.subheader('Update PATIENT')
        p.update_patient()
    elif auth_type == 'Doctor':
        st.header('Doctor\'s Personal Information')
        d = Doctor()
        d.update_doctor(id)

def query_1():
    st.header('Medical Record')

    show_medical_record(st.session_state.user)

def query_2():
    st.header('Medical test')
    show_result(st.session_state.user)

def query_3():
    st.header('Doctor Information')
    show_doctor()

# function to perform various operations of the doctor module (according to user's selection)
def doctors():
    st.header('DOCTORS')
    option_list = ['', 'Add doctor', 'Update doctor', 'Delete doctor', 'Show complete doctor record', 'Search doctor',
                   'Verification']
    option = st.sidebar.selectbox('Select function', option_list)
    dr = Doctor()
    if (option == option_list[1] or option == option_list[2] or option == option_list[
        3]):
        if option == option_list[1]:
            st.subheader('ADD DOCTOR')
            dr.add_doctor()
        elif option == option_list[2]:
            st.subheader('UPDATE DOCTOR')
            dr.update_doctor()
        elif option == option_list[3]:
            st.subheader('DELETE DOCTOR')
            try:
                dr.delete_doctor()
            except sql.IntegrityError:  # handles foreign key constraint failure issue (due to integrity error)
                st.error('This entry cannot be deleted as other records are using it.')
    elif option == option_list[4]:
        st.subheader('COMPLETE DOCTOR RECORD')
        dr.show_all_doctors()
    elif option == option_list[5]:
        st.subheader('SEARCH DOCTOR')
        dr.search_doctor()
    elif option == option_list[6]:
        st.subheader("VERIFICATION")
        dr.verify_doctor()

# function to perform various operations of the prescription module (according to user's selection)
def prescriptions():
    st.header('PRESCRIPTIONS')
    option_list = ['', 'Add prescription', 'Update prescription', 'Delete prescription',
                   'Show prescriptions of a particular patient']
    option = st.sidebar.selectbox('Select function', option_list)
    m = Prescription()
    if (option == option_list[1] or option == option_list[2] or option == option_list[3]):
        if option == option_list[1]:
            st.subheader('ADD PRESCRIPTION')
            m.add_prescription()
        elif option == option_list[2]:
            st.subheader('UPDATE PRESCRIPTION')
            m.update_prescription()
        elif option == option_list[3]:
            st.subheader('DELETE PRESCRIPTION')
            m.delete_prescription()
    elif option == option_list[4]:
        st.subheader('PRESCRIPTIONS OF A PARTICULAR PATIENT')
        m.prescriptions_by_patient()

# function to perform various operations of the medical_test module (according to user's selection)
def medical_tests():
    st.header('MEDICAL TESTS')
    option_list = ['', 'Add medical test', 'Update medical test', 'Delete medical test',
                   'Show medical tests of a particular patient']
    option = st.sidebar.selectbox('Select function', option_list)
    t = Medical_Test()
    if (option == option_list[1] or option == option_list[2] or option == option_list[3]):
        if option == option_list[1]:
            st.subheader('ADD MEDICAL TEST')
            t.add_medical_test()
        elif option == option_list[2]:
            st.subheader('UPDATE MEDICAL TEST')
            t.update_medical_test()
        elif option == option_list[3]:
            st.subheader('DELETE MEDICAL TEST')
            t.delete_medical_test()
    elif option == option_list[4]:
        st.subheader('MEDICAL TESTS OF A PARTICULAR PATIENT')
        t.medical_tests_by_patient()

# function to perform various operations of the department module (according to user's selection)
def departments():
    st.header('DEPARTMENTS')
    option_list = ['', 'Add department', 'Update department', 'Delete department', 'Show complete department record',
                   'Search department', 'Show doctors of a particular department']
    option = st.sidebar.selectbox('Select function', option_list)
    d = Department()
    if (option == option_list[1] or option == option_list[2] or option == option_list[3]):
        if option == option_list[1]:
            st.subheader('ADD DEPARTMENT')
            d.add_department()
        elif option == option_list[2]:
            st.subheader('UPDATE DEPARTMENT')
            d.update_department()
        elif option == option_list[3]:
            st.subheader('DELETE DEPARTMENT')
            try:
                d.delete_department()
            except sql.IntegrityError:  # handles foreign key constraint failure issue (due to integrity error)
                st.error('This entry cannot be deleted as other records are using it.')
    elif option == option_list[4]:
        st.subheader('COMPLETE DEPARTMENT RECORD')
        d.show_all_departments()
    elif option == option_list[5]:
        st.subheader('SEARCH DEPARTMENT')
        d.search_department()
    elif option == option_list[6]:
        st.subheader('DOCTORS OF A PARTICULAR DEPARTMENT')
        d.list_dept_doctors()

# function to implement and initialise home/main menu on successful user authentication
def home(auth_type,id):
    if auth_type == 'Admin':
        option = st.sidebar.selectbox('Select Module',
                                      ['', 'Patients', 'Doctors', 'Prescriptions', 'Medical Tests', 'Departments'])
        if option == 'Patients':
            patients()
        elif option == 'Doctors':
            doctors()
        elif option == 'Prescriptions':
            prescriptions()
        elif option == 'Medical Tests':
            medical_tests()
        elif option == 'Departments':
            departments()

    if auth_type == 'Patient':
        option = st.sidebar.selectbox('Select function', ['', 'Edit', 'Query','Test Result', 'Doctor Information'])
        if option == 'Edit':
            edit_account('Patient',id)
        if option == 'Query':
            query_1()
        if option == 'Test Result':
            query_2()
        if option == 'Doctor Information':
            query_3()

    if auth_type == 'Doctor':
        option = st.sidebar.selectbox('Select function', ['', 'Personal Information', 'Patient Information'])
        if option == 'Personal Information':
            edit_account('Doctor',id)
        if option == 'Patient Information':
            show_patient()

def login_clicked():
    st.session_state.access, st.session_state.auth_type = verify_password(user_id, password)
    if st.session_state.access:
        st.session_state.login = True
        st.session_state.user = user_id
    else:
        st.sidebar.error('Invalid username or password')


if 'login' not in st.session_state:
    st.session_state.login = False
if 'user' not in st.session_state:
    st.session_state.user = None




st.title('HEALTHCARE INFORMATION MANAGEMENT SYSTEM')
db.db_init()  # establishes connection to the database and create tables (if they don't exist yet)



if st.session_state.login == True:
    login()
else:
    user_id = st.sidebar.text_input('Enter your id')
    password = st.sidebar.text_input('Enter password', type='password')  # user password authentication
    login_button = st.sidebar.button('Login', on_click=login_clicked)
