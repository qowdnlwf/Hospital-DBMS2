import sqlite3 as sql
import config

# function to establish connection to the database, enable foreign key constraint support, and create cursor
def connection():
    conn = sql.connect(config.database_name + '.db')
    conn.execute("PRAGMA foreign_keys = ON;")
    c = conn.cursor()
    return conn, c

# function to establish connection to the database and create tables (if they don't exist yet)
def db_init():
    conn, c = connection()
    with conn: #病人
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS patient_record (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                blood_group TEXT NOT NULL,
                contact_number TEXT NOT NULL,
                #这里删掉了投票id
                weight INTEGER NOT NULL,
                height INTEGER NOT NULL,
                address TEXT NOT NULL,
                room_id TEXT,

            );
            """
        )
    with conn: #病房
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS room_record (
                room_id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                capacity INT NOT NULL,
                current INT NOT NULL, 
                nurse_id TEXT NOT NULL,
            );
            """
        )
    with conn:  #医生
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS doctor_record (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INT NOT NULL,
                gender INT NOT NULL, 
                date_of_birth TEXT NOT NULL,
                contact_number TEXT NOT NULL,
                department_id TEXT NOT NULL,
                FOREIGN KEY (department_id) REFERENCES department_record(id)
                ON UPDATE CASCADE
                ON DELETE RESTRICT 
            );
            """
        )
    with conn:  #科室
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS department_record (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL,
                contact_number TEXT NOT NULL,
                address TEXT NOT NULL,
            );
            """
        )
    with conn:  #病历
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS medical_record (
                patient_id TEXT NOT NULL,
                doctor_id TEXT NOT NULL,
                diagnosis TEXT NOT NULL,
                comments TEXT,
                medicine_1_name TEXT NOT NULL,
                medicine_1_dosage_description INT NOT NULL,
                medicine_2_name TEXT,
                medicine_2_dosage_description INT,
                medicine_3_name TEXT,
                medicine_3_dosage_description INT,
                FOREIGN KEY (patient_id) REFERENCES patient_record(id)
                ON UPDATE CASCADE
                ON DELETE RESTRICT,
                FOREIGN KEY (doctor_id) REFERENCES doctor_record(id)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
                FOREIGN KEY (medicine_1_name) REFERENCES pharmacy_record(medicine_name)
                FOREIGN KEY (medicine_2_name) REFERENCES pharmacy_record(medicine_name)
                FOREIGN KEY (medicine_3_name) REFERENCES pharmacy_record(medicine_name)

            );
            """
        )
    with conn:  #检查结果
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS medical_test_record (
                id TEXT PRIMARY KEY,
                test_name TEXT NOT NULL,
                patient_id TEXT NOT NULL,
                doctor_id TEXT NOT NULL,
                test_date_time TEXT NOT NULL,
                result_date_time TEXT NOT NULL,
                result_and_diagnosis TEXT,
                comments TEXT,
                cost INTEGER NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patient_record(id)
                ON UPDATE CASCADE
                ON DELETE RESTRICT,
                FOREIGN KEY (doctor_id) REFERENCES doctor_record(id)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
            );
            """
        )
    with conn:  #药房
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS pharmacy_record (
                medicine_name INT NOT NULL,
                medicine_number INT NOT NULL
            );
            """
        )
    with conn:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS account(
            id TEXT PRIMARY KEY, 
            auth_type TEXT NOT NULL,
            password TEXT NOT NULL
            );
            """
        )
    with conn:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS room_record(
                room_id TEXT PRIMARY KEY,
                room_type TEXT NOT NULL,
                num_beds INTEGER NOT NULL,
                patient_names TEXT[],
                patient_ids TEXT[]
                charge_nurse TEXT NOT NULL
            );
            """
        )
    conn.close()
