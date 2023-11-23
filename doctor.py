import streamlit as st
from datetime import datetime, date
import database as db
import pandas as pd
import department


# function to verify doctor id
def verify_doctor_id(doctor_id):
    verify = False
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT id
            FROM doctor_record;
            """
        )
    for id in c.fetchall():
        if id[0] == doctor_id:
            verify = True
            break
    conn.close()
    return verify


# function to show the details of doctor(s) given in a list (provided as a parameter)
def show_doctor_details(list_of_doctors):
    doctor_titles = ['Doctor ID', 'Name', 'Age', 'Gender', 'Date of birth (DD-MM-YYYY)',
                     'Contact number', 'Department ID', 'Department name','verified']
    if len(list_of_doctors) == 0:
        st.warning('No data to show')
    elif len(list_of_doctors) == 1:
        doctor_details = [x for x in list_of_doctors[0]]
        series = pd.Series(data=doctor_details, index=doctor_titles)
        st.write(series)
    else:
        doctor_details = []
        for doctor in list_of_doctors:
            doctor_details.append([x for x in doctor])
        df = pd.DataFrame(data=doctor_details, columns=doctor_titles)
        st.write(df)


# function to calculate age using given date of birth
def calculate_age(dob):
    today = date.today()
    age = today.year - dob.year - ((dob.month, dob.day) > (today.month, today.day))
    return age


# function to generate unique doctor id using current date and time
def generate_doctor_id():
    id_1 = datetime.now().strftime('%S%M%H')
    id_2 = datetime.now().strftime('%Y%m%d')[2:]
    id = f'DR-{id_1}-{id_2}'
    return id


# function to fetch department name from the database for the given department id
def get_department_name(dept_id):
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT name
            FROM department_record
            WHERE id = :id;
            """,
            {'id': dept_id}
        )
    return c.fetchone()[0]

def get_department_id(dept_name):
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT id
            FROM department_record
            WHERE name = :name;
            """,
            {'name': dept_name}
        )
    return c.fetchone()[0]


# class containing all the fields and methods required to work with the doctors' table in the database
class Doctor:

    def __init__(self):
        self.name = str()
        self.id = str()
        self.age = int()
        self.gender = str()
        self.date_of_birth = str()
        self.contact_number = str()
        self.password = str()

    # method to add a new doctor record to the database
    def add_doctor(self):
        st.write('Enter doctor details:')
        self.name = st.text_input('Full name')
        gender = st.radio('Gender', ['Female', 'Male'])
        self.gender = gender
        dob = st.date_input('Date of birth (YYYY/MM/DD)')
        st.info('If the required date is not in the calendar, please type it in the box above.')
        self.date_of_birth = dob.strftime('%d-%m-%Y')  # converts date of birth to the desired string format
        self.age = calculate_age(dob)
        department_name = st.text_input('Department Name')
        if department_name == '':
            st.empty()
        elif not department.verify_department_name(department_name):
            st.error('Invalid Department Name')
        else:
            st.success('Verified')
            self.department_name = department_name
            self.department_id = get_department_id(department_name)
        self.contact_number = st.text_input('Contact number')
        self.id = generate_doctor_id()
        save = st.button('Save')

        # executing SQLite statements to save the new doctor record to the database
        if save:
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    INSERT INTO doctor_record
                    (
                        id, name, age, gender, date_of_birth,
                        contact_number,department_id, department_name, verified      
                    )
                    VALUES (
                        :id, :name, :age, :gender, :dob, :phone, :dept_id, :dept_name,  :verified
                    );
                    """,
                    {
                        'id': self.id, 'name': self.name, 'age': self.age,
                        'gender': self.gender, 'dob': self.date_of_birth,
                        'phone': self.contact_number,
                        'dept_id': self.department_id,
                        'dept_name': self.department_name,
                        'verified': False
                    }
                )
            st.success('Doctor details saved successfully.')
            st.write('The New Doctor ID is: ', self.id, '\nWaiting to be verified')
            conn.close()


    def add_doctor_account(self):
        st.write('Enter doctor details:')
        self.name = st.text_input('Full name')
        gender = st.radio('Gender', ['Female', 'Male'])
        self.gender = gender
        dob = st.date_input('Date of birth (YYYY/MM/DD)')
        st.info('If the required date is not in the calendar, please type it in the box above.')
        self.date_of_birth = dob.strftime('%d-%m-%Y')  # converts date of birth to the desired string format
        self.age = calculate_age(dob)
        department_name = st.text_input('Department Name')
        if department_name == '':
            st.empty()
        elif not department.verify_department_name(department_name):
            st.error('Invalid Department Name')
        else:
            st.success('Verified')
            self.department_id = get_department_id(department_name)
        self.contact_number = st.text_input('Contact number')
        self.id = generate_doctor_id()
        self.password = st.text_input('Enter password',type="password")
        password_confirm = st.text_input('Confirm password',type='password')
        save = st.button('Save')

        # executing SQLite statements to save the new doctor record to the database
        if save:
            if self.password != password_confirm:
                st.error('Password Confirmation Error')
                return
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    INSERT INTO doctor_record
                    (
                        id, name, age, gender, date_of_birth,
                        department_id,  contact_number,verified      
                    )
                    VALUES (
                        :id, :name, :age, :gender, :dob,  :dept_id,  :phone, :verified
                    );
                    """,
                    {
                        'id': self.id, 'name': self.name, 'age': self.age,
                        'gender': self.gender, 'dob': self.date_of_birth,
                        'dept_id': self.department_id,
                        'phone': self.contact_number,
                        'verified': False
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
                        'id': self.id, 'type': "Doctor", 'passwd': self.password
                    }

                )
            st.success('Doctor details saved successfully.')
            st.write('The New Doctor ID is: ', self.id, '\nWaiting to be verified')
            conn.close()



    # method to update an existing doctor record in the database
    def update_doctor(self):
        id = st.text_input('Enter Doctor ID of the doctor to be updated')
        if id == '':
            st.empty()
        elif not verify_doctor_id(id):
            st.error('Invalid Doctor ID')
        else:
            st.success('Verified')
            conn, c = db.connection()

            # shows the current details of the doctor before updating
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM doctor_record
                    WHERE id = :id;
                    """,
                    {'id': id}
                )
                st.write('Here are the current details of the doctor:')
                show_doctor_details(c.fetchall())

            st.write('Enter new details of the doctor:')
            department_id = st.text_input('Department ID')
            if department_id == '':
                st.empty()
            elif not department.verify_department_id(department_id):
                st.error('Invalid Department ID')
            else:
                st.success('Verified')
                self.department_id = department_id
                self.department_name = get_department_name(department_id)
            self.contact_number = st.text_input('Contact number')
            update = st.button('Update')

            # executing SQLite statements to update this doctor's record in the database
            if update:
                with conn:
                    c.execute(
                        """
                        SELECT date_of_birth
                        FROM doctor_record
                        WHERE id = :id;
                        """,
                        {'id': id}
                    )

                    # converts date of birth to the required format for age calculation
                    dob = [int(d) for d in c.fetchone()[0].split('-')[::-1]]
                    dob = date(dob[0], dob[1], dob[2])
                    self.age = calculate_age(dob)

                with conn:
                    c.execute(
                        """
                        UPDATE doctor_record
                        SET age = :age, contact_number = :phone,
                        department_id = :dept_id, department_name = :dept_name, 
                        WHERE id = :id;
                        """,
                        {
                            'id': id, 'age': self.age,
                            'phone': self.contact_number,
                            'dept_id': self.department_id,
                            'dept_name': self.department_name,

                        }
                    )
                st.success('Doctor details updated successfully.')
                conn.close()

    # method to delete an existing doctor record from the database
    def delete_doctor(self):
        id = st.text_input('Enter Doctor ID of the doctor to be deleted')
        if id == '':
            st.empty()
        elif not verify_doctor_id(id):
            st.error('Invalid Doctor ID')
        else:
            st.success('Verified')
            conn, c = db.connection()

            # shows the current details of the doctor before deletion
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM doctor_record
                    WHERE id = :id;
                    """,
                    {'id': id}
                )
                st.write('Here are the details of the doctor to be deleted:')
                show_doctor_details(c.fetchall())

                confirm = st.checkbox('Check this box to confirm deletion')
                if confirm:
                    delete = st.button('Delete')

                    # executing SQLite statements to delete this doctor's record from the database
                    if delete:
                        c.execute(
                            """
                            DELETE FROM doctor_record
                            WHERE id = :id;
                            """,
                            {'id': id}
                        )
                        st.success('Doctor details deleted successfully.')
            conn.close()

    # method to show the complete doctor record
    def show_all_doctors(self):
        conn, c = db.connection()
        with conn:
            c.execute(
                """
                SELECT *
                FROM doctor_record;
                """
            )
            show_doctor_details(c.fetchall())
        conn.close()

    # method to search and show a particular doctor's details in the database using doctor id
    def search_doctor(self):
        id = st.text_input('Enter Doctor ID of the doctor to be searched')
        if id == '':
            st.empty()
        elif not verify_doctor_id(id):
            st.error('Invalid Doctor ID')
        else:
            st.success('Verified')
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM doctor_record
                    WHERE id = :id;
                    """,
                    {'id': id}
                )
                st.write('Here are the details of the doctor you searched for:')
                show_doctor_details(c.fetchall())
            conn.close()

    def verify_doctor(self):
        conn, c = db.connection()
        with conn:
            c.execute(
                """
                SELECT name
                FROM doctor_record
                WHERE verified = FALSE;
                """,
        )


