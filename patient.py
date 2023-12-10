import streamlit as st
from datetime import datetime, date
import database as db
import pandas as pd
from department import *

# function to verify patient id
def verify_patient_id(patient_id):
    verify = False
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT id
            FROM patient_record;
            """
        )
    for id in c.fetchall():
        if id[0] == patient_id:
            verify = True
            break
    conn.close()
    return verify

# function to generate unique patient id using current date and time
def generate_patient_id():
    id_1 = datetime.now().strftime('%S%M%H')
    id_2 = datetime.now().strftime('%Y%m%d')[2:]
    id = f'P-{id_1}-{id_2}'
    return id

# function to calculate age using given date of birth
def calculate_age(dob):
    today = date.today()
    age = today.year - dob.year - ((dob.month, dob.day) > (today.month, today.day))
    return age

# function to show the details of patient(s) given in a list (provided as a parameter)
def show_patient_details(list_of_patients):
    patient_titles = ['Patient ID', 'Name', 'Age', 'Gender', 'Date of birth (DD-MM-YYYY)',
                     'Blood group', 'Contact number',  'Weight (kg)', 'Height (cm)', 'Address', 'ROOM']
    if len(list_of_patients) == 0:
        st.warning('No data to show')
    elif len(list_of_patients) == 1:
        patient_details = [x for x in list_of_patients[0]]
        series = pd.Series(data = patient_details, index = patient_titles)
        st.write(series)
    else:
        patient_details = []
        for patient in list_of_patients:
            patient_details.append([x for x in patient])
        df = pd.DataFrame(data = patient_details, columns = patient_titles)
        st.write(df)


def show_doctor():
    doctor_titles = ['Name', 'Age', 'Gender', 'Contact Number']
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT name
            FROM department_record
            """
        )
    list_of_department = c.fetchall()
    # list_of_department.insert(0,'')
    new_list = []
    for x in list_of_department:
        new_list.append(x[0])

    department = st.selectbox('Select Department', new_list)
    with conn:
        c.execute(
            """
            SELECT name,age,gender,contact_number
            FROM doctor_record
            WHERE department_id = :id;
            """, {'id': get_department_id(department)}
        )
    list_of_doctor = c.fetchall()
    if len(list_of_doctor) == 0:
        st.warning('No data to show')
    elif len(list_of_doctor) == 1:
        record_details = [x for x in list_of_doctor[0]]
        series = pd.Series(data=record_details, index=doctor_titles)
        st.write(series)
    else:
        record_details = []
        for record in list_of_doctor:
            record_details.append([x for x in record])
        df = pd.DataFrame(data=record_details, columns=doctor_titles)
        st.write(df)


def show_medical_record(userID):
    record_titles = ['Patient ID', 'Doctor ID', 'Diagnosis', 'Comment', 'M1', 'M1_dosage', 'M2', 'M2_dosage', 'M3',
                     'M3_dosage']
    conn, c = db.connection()

    with conn:
        c.execute(
            """
            SELECT *
            FROM medical_record
            WHERE patient_id = :id;
            """, {'id': userID}
        )
    list_records = c.fetchall()
    if len(list_records) == 0:
        st.warning('No data to show')
    elif len(list_records) == 1:
        record_details = [x for x in list_records[0]]
        series = pd.Series(data=record_details, index=record_titles)
        st.write(series)
    else:
        record_details = []
        for record in list_records:
            record_details.append([x for x in record])
        df = pd.DataFrame(data=record_details, columns=record_titles)
        st.write(df)


def show_result(userID):
    record_titles = ['Test ID', 'Test Name', 'Patient ID', 'Doctor ID', 'Test time', 'Result time', 'Result', 'Comment',
                     'Cost']
    conn, c = db.connection()

    with conn:
        c.execute(
            """
            SELECT *
            FROM medical_test_record
            WHERE patient_id = :id;
            """, {'id': userID}
        )
    list_records = c.fetchall()
    if len(list_records) == 0:
        st.warning('No data to show')
    else:
        result_details = []
        for record in list_records:
            result_details.append([x for x in record])
        df = pd.DataFrame(data=result_details, columns=record_titles)
        st.write(df)
# class containing all the fields and methods required to work with the patients' table in the database
class Patient:

    def __init__(self):
        self.name = str()
        self.id = str()
        self.gender = str()
        self.age = int()
        self.contact_number = str()
        self.date_of_birth = str()
        self.blood_group = str()
        self.height = int()
        self.weight = int()
        self.address = str()
        self.password = str()
        self.room = str()

    # method to add a new patient record to the database
    def add_patient(self):
        st.write('Enter patient details:')
        self.name = st.text_input('Full name')
        gender = st.radio('Gender', ['Female', 'Male'])

        self.gender = gender
        dob = st.date_input('Date of birth (YYYY/MM/DD)')
        st.info('If the required date is not in the calendar, please type it in the box above.')
        self.date_of_birth = dob.strftime('%d-%m-%Y')       # converts date of birth to the desired string format
        self.age = calculate_age(dob)
        self.blood_group = st.text_input('Blood group')
        self.contact_number = st.text_input('Contact number')
        self.weight = st.number_input('Weight (in kg)', value = 0, min_value = 0, max_value = 400)
        self.height = st.number_input('Height (in cm)', value = 0, min_value = 0, max_value = 275)
        self.address = st.text_area('Address')
        self.password = st.text_input("Enter password", type="password")
        self.id = generate_patient_id()
        save = st.button('Save')

        # executing SQLite statements to save the new patient record to the database
        if save:
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    INSERT INTO patient_record
                    (
                        id, name, age, gender, date_of_birth, blood_group,
                        contact_number, 
                        weight, height, address, room_id
                    )
                    VALUES (
                        :id, :name, :age, :gender, :dob, :blood_group,
                        :phone, :weight, :height,
                        :address, :room
                    );
                    """,
                    {
                        'id': self.id, 'name': self.name, 'age': self.age,
                        'gender': self.gender, 'dob': self.date_of_birth,
                        'blood_group': self.blood_group,
                        'phone': self.contact_number,
                        'weight': self.weight,
                        'height': self.height, 'address': self.address,
                        'room': None
                    }
                )
                c.execute(
                    """
                    INSERT INTO account
                    (
                        user_id, auth_type,password
                    )
                    VALUES (
                        :id, :type, :passwd
                    );
                    """,
                    {
                        'id': self.id, 'type': "Patient", 'passwd': '123456'
                    }

                )
            st.success('Patient details saved successfully.')
            st.write('The Patient ID is: ', self.id)
            st.write('The Default Password is: 123456', self.id)
            conn.close()

    def add_patient_account(self):
        st.write('Enter patient details:')
        self.name = st.text_input('Full name')
        gender = st.radio('Gender', ['Female', 'Male'])

        self.gender = gender
        dob = st.date_input('Date of birth (YYYY/MM/DD)')
        st.info('If the required date is not in the calendar, please type it in the box above.')
        self.date_of_birth = dob.strftime('%d-%m-%Y')  # converts date of birth to the desired string format
        self.age = calculate_age(dob)
        self.blood_group = st.text_input('Blood group')
        self.contact_number = st.text_input('Contact number')
        self.weight = st.number_input('Weight (in kg)', value=0, min_value=0, max_value=400)
        self.height = st.number_input('Height (in cm)', value=0, min_value=0, max_value=275)
        self.address = st.text_area('Address')
        self.password = st.text_input("Enter password", type="password")
        password_confirm = st.text_input("Confirm password", type="password")
        self.id = generate_patient_id()
        save = st.button('Save')

        # executing SQLite statements to save the new patient record to the database
        if save:
            if self.password != password_confirm:
                st.error('Password Confirmation Error')
                return
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    INSERT INTO patient_record
                    (
                        id, name, age, gender, date_of_birth, blood_group,
                        contact_number, 
                        weight, height, address, room_id
                    )
                    VALUES (
                        :id, :name, :age, :gender, :dob, :blood_group,
                        :phone, :weight, :height,
                        :address, :room
                    );
                    """,
                    {
                        'id': self.id, 'name': self.name, 'age': self.age,
                        'gender': self.gender, 'dob': self.date_of_birth,
                        'blood_group': self.blood_group,
                        'phone': self.contact_number,
                        'weight': self.weight,
                        'height': self.height, 'address': self.address,
                        'room': None
                    }
                )

                c.execute(
                    """
                    INSERT INTO account
                    (
                        user_id, auth_type,password
                    )
                    VALUES (
                        :id, :type, :passwd
                    );
                    """,
                    {
                        'id' : self.id, 'type':"Patient", 'passwd':self.password
                    }

                )
            st.success('Patient details saved successfully.')
            st.write('Your Patient ID is: ', self.id)
            conn.close()

    # method to update an existing patient record in the database
    def update_patient(self):
        id = st.text_input('Enter Patient ID of the patient to be updated')
        if id == '':
            st.empty()
        elif not verify_patient_id(id):
            st.error('Invalid Patient ID')
        else:
            st.success('Found')
            conn, c = db.connection()

            # shows the current details of the patient before updating
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM patient_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Here are the current details of the patient:')
                show_patient_details(c.fetchall())
            st.write('Enter new details of the patient:')
            self.contact_number = st.text_input('Contact number')
            self.weight = st.number_input('Weight (in kg)', value = 0, min_value = 0, max_value = 400)
            self.height = st.number_input('Height (in cm)', value = 0, min_value = 0, max_value = 275)
            self.address = st.text_area('Address')
            update = st.button('Update')

            # executing SQLite statements to update this patient's record in the database
            if update:
                with conn:
                    c.execute(
                        """
                        SELECT date_of_birth
                        FROM patient_record
                        WHERE id = :id;
                        """,
                        { 'id': id }
                    )

                    # converts date of birth to the required format for age calculation
                    dob = [int(d) for d in c.fetchone()[0].split('-')[::-1]]
                    dob = date(dob[0], dob[1], dob[2])
                    self.age = calculate_age(dob)

                with conn:
                    c.execute(
                        """
                        UPDATE patient_record
                        SET age = :age, contact_number = :phone,
                         weight = :weight,
                        height = :height, address = :address,room_id = :room
                        WHERE id = :id;
                        """,
                        {
                            'id': id, 'age': self.age,
                            'phone': self.contact_number,
                            'weight': self.weight, 'height': self.height,
                            'address': self.address,  'room' : self.room
                        }
                    )
                st.success('Patient details updated successfully.')
                Refresh()
                conn.close()

    # method to delete an existing patient record from the database
    def delete_patient(self):
        id = st.text_input('Enter Patient ID of the patient to be deleted')
        if id == '':
            st.empty()
        elif not verify_patient_id(id):
            st.error('Invalid Patient ID')
        else:
            st.success('Verified')
            conn, c = db.connection()

            # shows the current details of the patient before deletion
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM patient_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Here are the details of the patient to be deleted:')
                show_patient_details(c.fetchall())

                confirm = st.checkbox('Check this box to confirm deletion')
                if confirm:
                    delete = st.button('Delete')

                    # executing SQLite statements to delete this patient's record from the database
                    if delete:
                        c.execute(
                            """
                            DELETE FROM patient_record
                            WHERE id = :id;
                            """,
                            { 'id': id }
                        )
                        c.execute(
                            """
                            DELETE FROM account
                            WHERE user_id = :user_id;
                            """,
                            {'user_id': id}
                        )
                        st.success('Patient details deleted successfully.')
            conn.close()

    # method to show the complete patient record
    def show_all_patients(self):
        conn, c = db.connection()
        with conn:
            c.execute(
                """
                SELECT *
                FROM patient_record;
                """
            )
            show_patient_details(c.fetchall())
        conn.close()

    # method to search and show a particular patient's details in the database using patient id
    def search_patient(self):
        id = st.text_input('Enter Patient ID of the patient to be searched')
        if id == '':
            st.empty()
        elif not verify_patient_id(id):
            st.error('Invalid Patient ID')
        else:
            st.success('Verified')
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM patient_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Here are the details of the patient you searched for:')
                show_patient_details(c.fetchall())
            conn.close()

def Refresh():
    button = st.button("Click me to refresh the page")

    if button:
        st.experimental_rerun()