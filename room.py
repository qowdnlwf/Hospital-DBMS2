import streamlit as st
from datetime import datetime
import database as db
import pandas as pd
import patient


# function to verify department id

def verify_room_id(room_id):
    verify = False
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT room_id
            FROM room_record;
            """
        )
    for id in c.fetchall():
        if id[0] == room_id:
            verify = True
            break
    conn.close()
    return verify


def verify_room_type(room_type):
    verify = False
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT type
            FROM room_record;
            """
        )
    for name in c.fetchall():
        if name[0] == room_type:
            verify = True
            break
    conn.close()
    return verify


# function to show the details of department(s) given in a list (provided as a parameter)
def show_room_details(list_of_rooms):
    room_titles = ['Room ID', 'Room type', 'Capacity', 'Current people', 'Nurse Name']
    if len(list_of_rooms) == 0:
        st.warning('No data to show')
    elif len(list_of_rooms) == 1:
        room_details = [x for x in list_of_rooms[0]]
        series = pd.Series(data=room_details, index=room_titles)
        st.write(series)
    else:
        room_details = []
        for room in list_of_rooms:
            room_details.append([x for x in room])
        df = pd.DataFrame(data=room_details, columns=room_titles)
        st.write(df)


# function to generate unique department id using current date and time
def generate_room_id():
    id_1 = datetime.now().strftime('%S%M%H')
    id_2 = datetime.now().strftime('%Y%m%d')[2:]
    id = f'R-{id_1}-{id_2}'
    return id


# function to show the doctor id and name of doctor(s) given in a list (provided as a parameter)
def show_list_of_patients(list_of_patients):
    patient_titles = ['Patient ID', 'Name']
    if len(list_of_patients) == 0:
        st.warning('No data to show')
    else:
        patient_details = []
        for patient in list_of_patients:
            patient_details.append([x for x in patient])
        df = pd.DataFrame(data=patient_details, columns=patient_titles)
        st.write(df)


# function to fetch department name from the database for the given department id
def get_room_type(room_id):
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT type
            FROM room_record
            WHERE room_id = :room_id;
            """,
            {'room_id': room_id}
        )
    return c.fetchone()[0]


def get_room_id():
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT room_id
            FROM room_record
            WHERE current < 4;
            """
        )
    return str(c.fetchall()[0][0])

def update_room_current(room_id):
    conn, c = db.connection()
    c.execute(
        """
        UPDATE room_record
        SET current = current + 1
        WHERE room_id = :room_id
        """,
        {
            'room_id': room_id
        }
    )


# class containing all the fields and methods required to work with the departments' table in the database
class Room:

    def __init__(self):
        self.type = str()
        self.room_id = str()
        self.capacity = int()
        self.current = int()
        self.nurse_name = str()

    # method to add a new department record to the database
    def add_room(self):
        st.write('Enter room details:')
        type = st.radio('Room type', ['ICU', 'Ward'])
        self.type = type
        self.capacity = 4
        self.current = 0
        self.nurse_name = st.text_input('Nurse name')
        self.room_id = generate_room_id()
        save = st.button('Save')

        # executing SQLite statements to save the new department record to the database
        if save:
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    INSERT INTO room_record
                    (
                        room_id, type, capacity, current, nurse_name
                    )
                    VALUES (
                        :room_id, :type, :cap, :current, :nurse_name
                    );
                    """,
                    {
                        'room_id': self.room_id, 'type': self.type, 'cap': self.capacity,
                        'current': self.current, 'nurse_name': self.nurse_name,
                    }
                )
            st.success('Room details saved successfully.')
            st.write('The Room ID is: ', self.room_id)
            conn.close()

    # method to update an existing department record in the database
    def update_room(self):
        room_id = st.text_input('Enter Room ID of the room to be updated')
        if room_id == '':
            st.empty()
        elif not verify_room_id(room_id):
            st.error('Invalid Room ID')
        else:
            st.success('Verified')
            conn, c = db.connection()

            # shows the current details of the department before updating
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM room_record
                    WHERE room_id = :room_id;
                    """,
                    {'room_id': room_id}
                )
                st.write('Here are the current details of the room:')
                show_room_details(c.fetchall())

            st.write('Enter new details of the room:')
            self.current = st.number_input('Current people', value=0, min_value=0, max_value=4)
            self.nurse_name = st.text_input('Nurse name')
            update = st.button('Update')

            # executing SQLite statements to update this department's record in the database
            if update:
                with conn:
                    c.execute(
                        """
                        UPDATE room_record
                        SET current = :current, nurse_name = :nurse_name
                        WHERE room_id = :room_id;
                        """,
                        {
                            'room_id': room_id,
                            'current': self.current,
                            'nurse_name': self.nurse_name
                        }
                    )
                st.success('Room details updated successfully.')
                conn.close()

    # method to delete an existing department record from the database
    def delete_room(self):
        room_id = st.text_input('Enter Room ID of the room to be deleted')
        if room_id == '':
            st.empty()
        elif not verify_room_id(room_id):
            st.error('Invalid Room ID')
        else:
            st.success('Verified')
            conn, c = db.connection()

            # shows the current details of the department before deletion
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM room_record
                    WHERE room_id = :room_id;
                    """,
                    {'room_id': room_id}
                )
                st.write('Here are the details of the room to be deleted:')
                show_room_details(c.fetchall())

                confirm = st.checkbox('Check this box to confirm deletion')
                if confirm:
                    delete = st.button('Delete')

                    # executing SQLite statements to delete this department's record from the database
                    if delete:
                        c.execute(
                            """
                            DELETE FROM room_record
                            WHERE room_id = :room_id;
                            """,
                            {'room_id': room_id}
                        )
                        st.success('Room details deleted successfully.')
            conn.close()

    # method to show the complete department record
    def show_all_rooms(self):
        conn, c = db.connection()
        with conn:
            c.execute(
                """
                SELECT *
                FROM room_record;
                """
            )
            show_room_details(c.fetchall())
        conn.close()

    # method to search and show a particular department's details in the database using department id
    def search_room(self):
        room_id = st.text_input('Enter Room ID of the room to be searched')
        if room_id == '':
            st.empty()
        elif not verify_room_id(room_id):
            st.error('Invalid Department ID')
        else:
            st.success('Verified')
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM room_record
                    WHERE room_id = :room_id;
                    """,
                    {'room_id': room_id}
                )
                st.write('Here are the details of the room you searched for:')
                show_room_details(c.fetchall())
            conn.close()

    # method to show the list of doctors working in a particular department (using department id)
    def list_room_patients(self):
        room_id = st.text_input('Enter Room ID to get a list of patients assigned to that room')
        if room_id == '':
            st.empty()
        elif not verify_room_id(room_id):
            st.error('Invalid Room ID')
        else:
            st.success('Verified')
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    SELECT id, name
                    FROM patient_record
                    WHERE room_id = :room_id;
                    """,
                    {'room_id': room_id}
                )
                st.write('Here is the list of patients assigned to the', get_room_type(room_id), 'department:')
                show_list_of_patients(c.fetchall())
            conn.close()

    def allocate_room_id(self):
        id = st.text_input('Enter Patient ID of the patient to be allocated a room')
        if id == '':
            st.empty()
        elif not patient.verify_patient_id(id):
            st.error('Invalid Patient ID')
        else:
            st.success('Found')
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    SELECT room_id
                    FROM room_record;
                    WHERE room_id.current < 4;
                    """
                )
                room_id = c.fetchall()[0]

                c.execute(
                    """
                    UPDATE patient_record
                    SET room_id = :room_id
                    WHERE id = :id;
                    """,
                    {
                        'id': id,
                        'room_id': room_id
                    }
                )
