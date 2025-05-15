from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory,jsonify
import mysql.connector
from mysql.connector import MySQLConnection, Error 
from werkzeug.utils import secure_filename
import os
from datetime import timedelta
import base64
from PIL import Image
import io
import pymysql 
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# app = Flask(__name__)
# app.secret_key = 'secret_key'
## For using SQL CLOUD where data is transfered between 2 devices
# class AppointmentDashboard:
#     def __init__(self):
#         try:
#             self.connection = pymysql.connect(
#                 host="******************************",
#                 port=21375,
#                 user="**********",
#                 password="XXXXXXXXXXXX",
#                 database="***************",
#                 charset="utf8mb4",
#                 cursorclass=pymysql.cursors.DictCursor
#             )
#             logger.info("Successfully connected to the database")
#         except Exception as e:
#             logger.error(f"Error connecting to database: {e}")
#             raise

#     def get_all_appointments(self):
#         """Retrieve all appointments with their details"""
#         try:
#             with self.connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT * FROM appointments 
#                     ORDER BY created_at DESC
#                 """)
#                 appointments = cursor.fetchall()
#                 return appointments
#         except Exception as e:
#             logger.error(f"Error retrieving appointments: {e}")
#             return []

# # Create the dashboard instance
# dashboard = AppointmentDashboard()  # Create the dashboard instance



app = Flask(__name__)
app.secret_key = '********'
UPLOAD_FOLDER = 'hms/prescriptions'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database connection
def connect_db():
    try:
        return mysql.connector.connect(
            user='root',
            password='XXXXX',
            database='hospital',
            host='XXX.XXX.XXX.XX'
        )
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

# Home page
@app.route('/')
def index():
    db=connect_db()
    return render_template('index.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    db=connect_db()
    return render_template('admin_dashboard.html')

@app.route('/staff_dashboard')
def staff_dashboard():
    db=connect_db()
    if db is None:
        flash("Database connection error", "error")
        return redirect(url_for('index'))
    return render_template('staff_dashboard.html')


@app.route('/get_resources')
def get_resources():
    return render_template('get_resources.html')
    
# Patient data page
@app.route('/patients')
def patients():
    app.logger.info('Entering patients route')
    try:
        db = connect_db()
        if db is None:
            app.logger.error('Database connection failed')
            raise Exception("Database connection error")
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patients;")
        patients = cursor.fetchall()
        cursor.close()
        db.commit()
        app.logger.info(f'Retrieved {len(patients)} patients')
        return render_template('patients.html', endpoints='patients', patients=patients)
    except Exception as e:
        app.logger.exception(f'Error in patients route: {str(e)}')
        return f"An error occurred: {str(e)}", 500

@app.route('/add_patient', methods=['POST', 'GET'])
def add_patient():
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        name = request.form.get('patient_name')
        dob = request.form.get('dob')
        contact = request.form.get('contact')
        email = request.form.get('email')
        db = connect_db()
        
        if db is None:
            return jsonify({"success": False, "message": "Database connection error"}), 500
        
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO patients (patientID, patientName, DOB, Contact, Email) VALUES (%s, %s, %s, %s, %s);", (patient_id, name, dob, contact, email))
            db.commit()
            return redirect(url_for('patients'))
        except Error as e:
            db.rollback()
            return f"Error adding patient: {str(e)}",400
        finally:
            cursor.close()
            db.close()
    return render_template('add_patient.html', endpoints='add_patient')

def serialize_timedelta(td):
    """Convert a timedelta object to a string or a number."""
    if isinstance(td, timedelta):
        return str(td)  # or td.total_seconds() if you prefer a numeric representation
    return td

@app.route('/search_patient', methods=['POST'])
def search_patient():
    try:
        data = request.get_json()
        search_term = data.get('search_term')

        if not search_term:
            return jsonify(success=False, message="Missing search term"), 400

        db = connect_db()
        if db is None:
            return jsonify(success=False, message="Database connection error"), 500

        cursor = db.cursor(dictionary=True)
        try:
            if search_term.isdigit():
                query = "SELECT * FROM patients WHERE patientID = %s"
                cursor.execute(query, (search_term,))
            else:
                query = "SELECT * FROM patients WHERE patientName LIKE %s"
                cursor.execute(query, (f"%{search_term}%",))

            patient = cursor.fetchone()

            if patient:
                cursor.execute("SELECT * FROM appointments WHERE patientID = %s", (patient['patientID'],))
                appointments = cursor.fetchall()

                cursor.execute("SELECT * FROM medical_records WHERE patientID = %s", (patient['patientID'],))
                medical_records = cursor.fetchall()

                # Convert any timedelta objects in the results
                appointments = [{k: serialize_timedelta(v) for k, v in appointment.items()} for appointment in appointments]
                
                # Convert binary data to base64
                for record in medical_records:
                    if 'prescription' in record and record['prescription'] is not None:
                        record['prescription'] = base64.b64encode(record['prescription']).decode('utf-8')

                return jsonify({
                    "success": True,
                    "patient": patient,
                    "appointments": appointments,
                    "medical_records": medical_records
                })
            else:
                return jsonify(success=False, message="Patient not found"), 404

        except mysql.connector.Error as e:
            return jsonify(success=False, message=f"Database error: {str(e)}"), 500
        finally:
            cursor.close()
            db.close()

    except Exception as e:
        return jsonify(success=False, message=f"Server error: {str(e)}"), 500

@app.route('/update_patient', methods=['GET', 'POST'])
def update_patient():
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        patient_name = request.form.get('patient_name')
        contact = request.form.get('contact')
        email = request.form.get('email')

        db = connect_db()
        if db is None:
            return jsonify({"success": False, "message": "Database connection error"}), 500

        cursor = db.cursor(dictionary=True)
        try:
            query = """UPDATE patients
                    SET patientName = %s, Contact = %s, Email = %s
                    WHERE patientID = %s"""
            cursor.execute(query, (patient_name, contact, email, patient_id))
            db.commit()
            return jsonify({"success": True, "message": "Patient details updated successfully"})
        except Error as e:
            db.rollback()
            return jsonify({"success": False, "message": f"Error updating patient details: {str(e)}"}), 400
        finally:
            cursor.close()
            db.close()
    else:
        return render_template('update_patient.html')



# Medical records page
@app.route('/medical_records')
def medical_records():
    try:
        db = connect_db()
        if db is None:
            flash("Database connection error", "error")
            return redirect(url_for('index'))

        with db.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM medical_records")
            records = cursor.fetchall()

    except mysql.connector.Error as err:
        flash(f"Error: {err}", "error")
        return redirect(url_for('index'))
    finally:
        if db:
            db.close()

    return render_template('medical_records.html', records=records)

# Search medical records
@app.route('/search_medical_records', methods=['GET'])
def search_medical_records():
    record_id = request.args.get('record_id', '')
    patient_id = request.args.get('patient_id', '')
    db = connect_db()
    if db is None:
        return jsonify({'error': 'Database connection error'}), 500

    cursor = db.cursor(dictionary=True)
    try:
        query = "SELECT * FROM medical_records WHERE 1=1"
        params = []

        if record_id:
            query += " AND recordID = %s"
            params.append(record_id)
        
        if patient_id:
            query += " AND patientID = %s"
            params.append(patient_id)

        cursor.execute(query, params)
        records = cursor.fetchall()
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        db.close()

    return jsonify(records)

# Add medical record
@app.route('/add_medical_record', methods=['POST'])
def add_medical_record():
    record_id = request.form.get('record-id')
    patient_id = request.form.get('patient-id')
    doctor_id = request.form.get('doctor-id')
    consultation_date = request.form.get('consultation-date')
    diagnosis = request.form.get('diagnosis')
    treatment = request.form.get('treatment')
    prescription_photo = request.files.get('prescription-photo')

    db = connect_db()
    if db is None:
        flash("Database connection error", "error")
        return redirect(url_for('medical_records'))

    cursor = db.cursor()
    try:
        # Save the prescription photo
        if prescription_photo:
            prescription_data = prescription_photo.read()  # Read the file as binary data

        cursor.execute("""
        INSERT INTO medical_records (
            recordID, patientID, doctorID, consultationDate, diagnosis, treatment, prescription
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (record_id, patient_id, doctor_id, consultation_date, diagnosis, treatment, prescription_data))
        db.commit()
        flash("Medical record added successfully!", "success")
    except mysql.connector.Error as e:
        db.rollback()
        flash(f"Error adding medical record: {str(e)}", "error")
    finally:
        cursor.close()
        db.close()
    return redirect(url_for('medical_records'))


def write_file(binary_data, name, path):
    try:
        # Ensure the directory exists
        os.makedirs(path, exist_ok=True)  # Create the directory if it doesn't exist
        
        # Define the full file path
        file_path = os.path.join(path, name)
        
        # Open the file in write-binary mode and save the data
        with open(file_path, 'wb') as file:
            file.write(binary_data)
        
        print(f"File saved to {file_path}")
    except Exception as e:
        print(f"Failed to write file: {e}")

        
def readBLOB(path, name, record_id):
    connection = None
    cursor = None
    try:
        # Establish the database connection
        connection = mysql.connector.connect(
            host="192.168.110.1",
            user="root",
            password="XXXXX",
            database="hospital"
        )

        cursor = connection.cursor()
        sql_fetch_blob_query = """SELECT prescription FROM medical_records WHERE recordID=%s"""
        
        cursor.execute(sql_fetch_blob_query, (record_id,))
        record = cursor.fetchone()

        # Ensure data is not empty and extract the first row, first column
        if record is not None:
            binary_data = record[0]  # Get the first element of the tuple
            
            # Check the type of binary_data
            if isinstance(binary_data, bytes):
                # Pass the binary data to write_file
                write_file(binary_data, name, 'static/images')  # Save to the static/images folder
            else:
                print("Retrieved data is not in bytes format.")
        else:
            print("No data found for the given record_id.")
    except mysql.connector.Error as error:
        print("Failed to read BLOB data from MySQL table: {}".format(error))
    finally:
        if cursor is not None:
            cursor.close()  # Ensure cursor is closed
        if connection is not None and connection.is_connected():
            connection.close()
            print("MySQL connection is closed")


# View prescription
@app.route('/view_prescription/<int:record_id>')
def view_prescription(record_id):
    db = connect_db()
    if db is None:
        flash("Database connection error", "error")
        return redirect(url_for('medical_records'))
    
    cursor = db.cursor(dictionary=True)
    n = record_id
    name = 'output_image' + str(n) + '.png'  # Dynamically set the image name based on record_id
    readBLOB('static/images', name, record_id)  # Save the image to static/images
    image_name=f"output_image{record_id}.png"
    return render_template('pres_image.html',image_name=image_name)
    
    
    
    
    
    
    



@app.route('/new_appointments')
def new_appointments():
    # appointments = dashboard.get_all_appointments()  # Fetch latest appointments
    # logger.info(f"Fetched appointments: {appointments}")  # Log the fetched appointments
    return render_template('new_appointments.html', appointments=appointments)






@app.route('/appointments', methods=['GET', 'POST'])
def appointments():
    db = connect_db()
    if db is None:
        return jsonify({"success": False, "message": "Database connection error"}), 500

    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        doctor_id = request.form.get('doctor_id')
        department_name = request.form.get('dept_name')  # Capture the department name
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')
        phone_number = request.form.get('phone_number')
        
        try:
            cursor.execute("""
                INSERT INTO appointments (patientID, doctorID, dept_name, appointment_date, appointment_time, phone_number)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (patient_id, doctor_id, department_name, appointment_date, appointment_time, phone_number))
            db.commit()
            return jsonify({"success": True, "message": "Appointment scheduled successfully!"})
        except mysql.connector.Error as e:
            db.rollback()
            return jsonify({"success": False, "message": f"Error scheduling appointment: {str(e)}"}), 400
        finally:
            cursor.close()
            db.close()

    # Fetch and display appointments
    try:
        cursor.execute("""
            SELECT appointments.appointmentID, 
                   patients.patientName AS patient_name, 
                   patients.Contact AS contact_number, 
                   doctors.doctorName AS doctor_name, 
                   appointments.dept_name,  -- Added department name
                   appointments.appointment_date, 
                   appointments.appointment_time,
                   appointments.phone_number  -- Retrieve phone number
            FROM appointments
            JOIN patients ON appointments.patientID = patients.patientID
            JOIN doctors ON appointments.doctorID = doctors.doctorID
            WHERE appointments.appointment_date >= CURDATE()
            ORDER BY appointments.appointment_date, appointments.appointment_time
        """)
        appointments = cursor.fetchall()
    except mysql.connector.Error as e:
        flash(f"Error retrieving appointments: {str(e)}", "error")
        appointments = []
    finally:
        cursor.close()
        db.close()

    return render_template('appointments.html', appointments=appointments)
    
@app.route('/search_appointments', methods=['GET'])
def search_appointments():
    search_query = request.args.get('search_query', '').strip().lower()
    db = connect_db()
    if db is None:
        flash("Database connection error", "error")
        return redirect(url_for('index'))
    
    cursor = db.cursor(dictionary=True)
    try:
        query = """
            SELECT appointments.appointmentID, patients.patientName AS patient_name, 
            doctors.doctorName AS doctor_name, appointments.appointment_date, 
            appointments.appointment_time
            FROM appointments
            JOIN patients ON appointments.patientID = patients.patientID
            JOIN doctors ON appointments.doctorID = doctors.doctorID
            WHERE LOWER(patients.patientName) LIKE %s 
            OR LOWER(patients.patientID) LIKE %s
        """
        search_term = f"%{search_query}%"
        cursor.execute(query, (search_term, search_term))
        appointments = cursor.fetchall()
    except mysql.connector.Error as e:
        flash(f"Error retrieving appointments: {str(e)}", "error")
        return redirect(url_for('index'))
    finally:
        cursor.close()
        db.close()
    return render_template('appointments.html', appointments=appointments)

@app.route('/appointment_details', methods=['GET'])
def appointment_details():
    search_query = request.args.get('search', '').strip().lower()
    db = connect_db()
    if db is None:
        flash("Database connection error", "error")
        return redirect(url_for('index'))
    
    cursor = db.cursor(dictionary=True)
    try:
        # SQL query to fetch appointment details with optional search
        query = """
            SELECT appointments.appointmentID, patients.patientName AS patient_name, 
            patients.Contact AS contact_number, doctors.doctorName AS doctor_name, 
            appointments.appointment_date, appointments.appointment_time
            FROM appointments
            JOIN patients ON appointments.patientID = patients.patientID
            JOIN doctors ON appointments.doctorID = doctors.doctorID
        """
        
        # If a search query is provided, add a WHERE clause
        if search_query:
            query += """
                WHERE LOWER(patients.patientName) LIKE %s
                OR LOWER(doctors.doctorName) LIKE %s
            """
            search_term = f"%{search_query}%"
            cursor.execute(query, (search_term, search_term))
        else:
            cursor.execute(query)

        # Fetch all appointment details
        appointments = cursor.fetchall()
    except mysql.connector.Error as e:
        flash(f"Error retrieving appointment details: {str(e)}", "error")
        return redirect(url_for('index'))
    finally:
        cursor.close()
        db.close()

    return render_template('appointment_details.html', appointments=appointments)

@app.route('/resources', endpoint='resources')
def resources_page():
    db = connect_db()
    if db is None:
        flash("Database connection error", "error")
        return redirect(url_for('index'))

    try:
        cursor = db.cursor(dictionary=True)

        # Fetch resources
        cursor.execute("SELECT * FROM Resources")
        resources = cursor.fetchall()

        # Fetch equipment
        cursor.execute("SELECT * FROM Equipment")
        equipment = cursor.fetchall()

        # Fetch rooms
        cursor.execute("SELECT * FROM Rooms")
        rooms = cursor.fetchall()

        # Fetch supplies
        cursor.execute("SELECT * FROM Supplies")
        supplies = cursor.fetchall()

        # Fetch staff assignments
        cursor.execute("SELECT * FROM Staff_Assignment")
        staff_assignments = cursor.fetchall()

        # Fetch resource usage
        cursor.execute("SELECT * FROM Resource_Usage")
        resource_usage = cursor.fetchall()

        # Fetch resource maintenance
        cursor.execute("SELECT * FROM Resource_Maintenance")
        resource_maintenance = cursor.fetchall()

        # Fetch resource requests
        cursor.execute("SELECT * FROM Resource_Requests")
        resource_requests = cursor.fetchall()

    except mysql.connector.Error as e:
        flash(f"Error retrieving data: {str(e)}", "error")
        return redirect(url_for('index'))
    finally:
        cursor.close()
        db.close()

    return render_template('resources.html', resources=resources, equipment=equipment, rooms=rooms, supplies=supplies,
                           staff_assignments=staff_assignments, resource_usage=resource_usage,
                           resource_maintenance=resource_maintenance, resource_requests=resource_requests)



@app.route('/api/medical_records', methods=['GET'])
def get_medical_records():
    # Ensure no limit is set here
    medical_records = medical_records.query.all()  # Fetch all records
    return jsonify([medical_records.to_dict() for medical_records in medical_records])  # Convert to JSON



@app.route('/api/resources', methods=['GET'])
def get_resources_records():
    resource_records = resource_records.query.all()
    return jsonify([resource.to_dict() for resource in resource_records])

@app.route('/api/equipment', methods=['GET'])
def get_equipment():
    equipment_records = equipment_records.query.all()
    return jsonify([equipment.to_dict() for equipment in equipment_records])

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    room_records = room_records.query.all()
    return jsonify([room.to_dict() for room in room_records])

@app.route('/api/supplies', methods=['GET'])
def get_supplies():
    supply_records = supply_records.query.all()
    return jsonify([supply.to_dict() for supply in supply_records])

@app.route('/api/staff_assignments', methods=['GET'])
def get_staff_assignments():
    staff_assignment_records = staff_assignment_records.query.all()
    return jsonify([assignment.to_dict() for assignment in staff_assignment_records])

@app.route('/api/resource_usage', methods=['GET'])
def get_resource_usage():
    resource_usage_records = resource_usage_records.query.all()
    return jsonify([usage.to_dict() for usage in resource_usage_records])

@app.route('/api/resource_maintenance', methods=['GET'])
def get_resource_maintenance():
    resource_maintenance_records = resource_maintenance_records.query.all()
    return jsonify([maintenance.to_dict() for maintenance in resource_maintenance_records])

@app.route('/api/resource_requests', methods=['GET'])
def get_resource_requests():
    resource_request_records = resource_request_records.query.all()
    return jsonify([request.to_dict() for request in resource_request_records])

# Add and Edit routes for Resources
@app.route('/api/add_resourcesTable', methods=['POST'])
def add_resource():
    # Extract form data
    resource_id = request.form.get('resource_id')
    resource_type = request.form.get('resource_type')
    resource_name = request.form.get('resource_name')
    status = request.form.get('status')
    quantity = request.form.get('quantity')

    db = connect_db()
    if db is None:
        return jsonify({"success": False, "message": "Database connection error"}), 500

    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO Resources (resource_id, resource_type, resource_name, status, quantity)
            VALUES (%s, %s, %s, %s, %s)
        """, (resource_id, resource_type, resource_name, status, quantity))
        db.commit()
        return jsonify({"success": True, "message": "Resource added successfully!"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"success": False, "message": f"Error adding resource: {str(e)}"}), 400
    finally:
        cursor.close()
        db.close()

@app.route('/api/edit_resourcesTable', methods=['POST'])
def edit_resource():
    # Extract form data
    resource_id = request.form.get('resource_id')
    resource_type = request.form.get('resource_type')
    resource_name = request.form.get('resource_name')
    status = request.form.get('status')
    quantity = request.form.get('quantity')

    db = connect_db()
    if db is None:
        return jsonify({"success": False, "message": "Database connection error"}), 500

    cursor = db.cursor()
    try:
        cursor.execute("""
            UPDATE Resources
            SET resource_type = %s, resource_name = %s, status = %s, quantity = %s
            WHERE resource_id = %s
        """, (resource_type, resource_name, status, quantity, resource_id))
        db.commit()
        return jsonify({"success": True, "message": "Resource updated successfully!"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"success": False, "message": f"Error updating resource: {str(e)}"}), 400
    finally:
        cursor.close()
        db.close()

# Add and Edit routes for Equipment
@app.route('/api/add_equipmentTable', methods=['POST'])
def add_equipment():
    # Extract form data
    equipment_id = request.form.get('equipment_id')
    equipment_name = request.form.get('equipment_name')
    purchase_date = request.form.get('purchase_date')
    warranty_end_date = request.form.get('warranty_end_date')
    status = request.form.get('status')

    db = connect_db()
    if db is None:
        return jsonify({"success": False, "message": "Database connection error"}), 500

    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO Equipment (equipment_id, equipment_name, purchase_date, warranty_end_date, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (equipment_id, equipment_name, purchase_date, warranty_end_date, status))
        db.commit()
        return jsonify({"success": True, "message": "Equipment added successfully!"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"success": False, "message": f"Error adding equipment: {str(e)}"}), 400
    finally:
        cursor.close()
        db.close()

@app.route('/api/edit_equipmentTable', methods=['POST'])
def edit_equipment():
    # Extract form data
    equipment_id = request.form.get('equipment_id')
    equipment_name = request.form.get('equipment_name')
    purchase_date = request.form.get('purchase_date')
    warranty_end_date = request.form.get('warranty_end_date')
    status = request.form.get('status')

    db = connect_db()
    if db is None:
        return jsonify({"success": False, "message": "Database connection error"}), 500

    cursor = db.cursor()
    try:
        cursor.execute("""
            UPDATE Equipment
            SET equipment_name = %s, purchase_date = %s, warranty_end_date = %s, status = %s
            WHERE equipment_id = %s
        """, (equipment_name, purchase_date, warranty_end_date, status, equipment_id))
        db.commit()
        return jsonify({"success": True, "message": "Equipment updated successfully!"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"success": False, "message": f"Error updating equipment: {str(e)}"}), 400
    finally:
        cursor.close()
        db.close()

# Add and Edit routes for Rooms
@app.route('/api/add_roomsTable', methods=['POST'])
def api_add_room():
    # Extract form data
    room_id = request.form.get('room_id')
    room_type = request.form.get('room_type')
    bed_count = request.form.get('bed_count')
    status = request.form.get('status')

    db = connect_db()
    if db is None:
        return jsonify({"success": False, "message": "Database connection error"}), 500

    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO Rooms (room_id, room_type, bed_count, status)
            VALUES (%s, %s, %s, %s)
        """, (room_id, room_type, bed_count, status))
        db.commit()
        return jsonify({"success": True, "message": "Room added successfully!"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"success": False, "message": f"Error adding room: {str(e)}"}), 400
    finally:
        cursor.close()
        db.close()

@app.route('/api/edit_roomsTable', methods=['POST'])
def edit_room():
    # Extract form data
    room_id = request.form.get('room_id')
    room_type = request.form.get('room_type')
    bed_count = request.form.get('bed_count')
    status = request.form.get('status')

    db = connect_db()
    if db is None:
        return jsonify({"success": False, "message": "Database connection error"}), 500

    cursor = db.cursor()
    try:
        cursor.execute("""
            UPDATE Rooms
            SET room_type = %s, bed_count = %s, status = %s
            WHERE room_id = %s
        """, (room_type, bed_count, status, room_id))
        db.commit()
        return jsonify({"success": True, "message": "Room updated successfully!"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"success": False, "message": f"Error updating room: {str(e)}"}), 400
    finally:
        cursor.close()
        db.close()

# Add and Edit routes for Supplies
@app.route('/api/add_suppliesTable', methods=['POST'])
def add_supply():
    # Extract form data
    supply_id = request.form.get('supply_id')
    supply_name = request.form.get('supply_name')
    quantity = request.form.get('quantity')
    unit = request.form.get('unit')
    last_restock_date = request.form.get('last_restock_date')

    db = connect_db()
    if db is None:
        return jsonify({"success": False, "message": "Database connection error"}), 500

    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO Supplies (supply_id, supply_name, quantity, unit, last_restock_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (supply_id, supply_name, quantity, unit, last_restock_date))
        db.commit()
        return jsonify({"success": True, "message": "Supply added successfully!"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"success": False, "message": f"Error adding supply: {str(e)}"}), 400
    finally:
        cursor.close()
        db.close()

@app.route('/api/edit_suppliesTable', methods=['POST'])
def edit_supply():
    # Extract form data
    supply_id = request.form.get('supply_id')
    supply_name = request.form.get('supply_name')
    quantity = request.form.get('quantity')
    unit = request.form.get('unit')
    last_restock_date = request.form.get('last_restock_date')

    db = connect_db()
    if db is None:
        return jsonify({"success": False, "message": "Database connection error"}), 500

    cursor = db.cursor()
    try:
        cursor.execute("""
            UPDATE Supplies
            SET supply_name = %s, quantity = %s, unit = %s, last_restock_date = %s
            WHERE supply_id = %s
        """, (supply_name, quantity, unit, last_restock_date, supply_id))
        db.commit()
        return jsonify({"success": True, "message": "Supply updated successfully!"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"success": False, "message": f"Error updating supply: {str(e)}"}), 400
    finally:
        cursor.close()
        db.close()

# Add and Edit routes for Staff Assignments
@app.route('/api/add_staffAssignmentsTable', methods=['POST'])
def add_staff_assignment():
    # Extract form data
    assignment_id = request.form.get('assignment_id')
    staffID = request.form.get('staffID')
    resource_id = request.form.get('resource_id')
    assigned_on = request.form.get('assigned_on')
    shift_start_time = request.form.get('shift_start_time')
    shift_end_time = request.form.get('shift_end_time')

    db = connect_db()
    if db is None:
        return jsonify({"success": False, "message": "Database connection error"}), 500

    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO Staff_Assignment (assignment_id, staffID, resource_id, assigned_on, shift_start_time, shift_end_time)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (assignment_id, staffID, resource_id, assigned_on, shift_start_time, shift_end_time))
        db.commit()
        return jsonify({"success": True, "message": "Staff assignment added successfully!"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"success": False, "message": f"Error adding staff assignment: {str(e)}"}), 400
    finally:
        cursor.close()
        db.close()

@app.route('/api/edit_staffAssignmentsTable', methods=['POST'])
def edit_staff_assignment():
    # Extract form data
    assignment_id = request.form.get('assignment_id')
    staffID = request.form.get('staffID')
    resource_id = request.form.get('resource_id')
    assigned_on = request.form.get('assigned_on')
    shift_start_time = request.form.get('shift_start_time')
    shift_end_time = request.form.get('shift_end_time')

    db = connect_db()
    if db is None:
        return jsonify({"success": False, "message": "Database connection error"}), 500

    cursor = db.cursor()
    try:
        cursor.execute("""
            UPDATE Staff_Assignment
            SET staffID = %s, resource_id = %s, assigned_on = %s, shift_start_time = %s, shift_end_time = %s
            WHERE assignment_id = %s
        """, (staffID, resource_id, assigned_on, shift_start_time, shift_end_time, assignment_id))
        db.commit()
        return jsonify({"success": True, "message": "Staff assignment updated successfully!"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"success": False, "message": f"Error updating staff assignment: {str(e)}"}), 400
    finally:
        cursor.close()
        db.close()

# Add and Edit routes for Resource Usage
@app.route('/api/add_resourceUsageTable', methods=['POST'])
def add_resource_usage():
    # Extract form data
    usage_id = request.form.get('usage_id')
    resource_id = request.form.get('resource_id')
    used_by = request.form.get('used_by')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    status = request.form.get('status')

    db = connect_db()
    if db is None:
        return jsonify({"success": False, "message": "Database connection error"}), 500

    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO Resource_Usage (usage_id, resource_id, used_by, start_time, end_time, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (usage_id, resource_id, used_by, start_time, end_time, status))
        db.commit()
        return jsonify({"success": True, "message": "Resource usage added successfully!"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"success": False, "message": f"Error adding resource usage: {str(e)}"}), 400
    finally:
        cursor.close()
        db.close()

@app.route('/api/edit_resourceUsageTable', methods=['POST'])
def edit_resource_usage():
    # Extract form data
    usage_id = request.form.get('usage_id')
    resource_id = request.form.get('resource_id')
    used_by = request.form.get('used_by')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    status = request.form.get('status')

    db = connect_db()
    if db is None:
        return jsonify({"success": False, "message": "Database connection error"}), 500

    cursor = db.cursor()
    try:
        cursor.execute("""
            UPDATE Resource_Usage
            SET resource_id = %s, used_by = %s, start_time = %s, end_time = %s, status = %s
            WHERE usage_id = %s
        """, (resource_id, used_by, start_time, end_time, status, usage_id))
        db.commit()
        return jsonify({"success": True, "message": "Resource usage updated successfully!"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"success": False, "message": f"Error updating resource usage: {str(e)}"}), 400
    finally:
        cursor.close()
        db.close()

# Add and Edit routes for Resource Maintenance
@app.route('/api/add_resourceMaintenanceTable', methods=['POST'])
def add_resource_maintenance():
    # Extract form data
    maintenance_id = request.form.get('maintenance_id')
    resource_id = request.form.get('resource_id')
    maintenance_type = request.form.get('maintenance_type')
    maintenance_date = request.form.get('maintenance_date')
    next_maintenance_due = request.form.get('next_maintenance_due')

    db = connect_db()
    if db is None:
        return jsonify({"success": False, "message": "Database connection error"}), 500

    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO Resource_Maintenance (maintenance_id, resource_id, maintenance_type, maintenance_date, next_maintenance_due)
            VALUES (%s, %s, %s, %s, %s)
        """, (maintenance_id, resource_id, maintenance_type, maintenance_date, next_maintenance_due))
        db.commit()
        return jsonify({"success": True, "message": "Resource maintenance added successfully!"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"success": False, "message": f"Error adding resource maintenance: {str(e)}"}), 400
    finally:
        cursor.close()
        db.close()

@app.route('/api/edit_resourceMaintenanceTable', methods=['POST'])
def edit_resource_maintenance():
    # Extract form data
    maintenance_id = request.form.get('maintenance_id')
    resource_id = request.form.get('resource_id')
    maintenance_type = request.form.get('maintenance_type')
    maintenance_date = request.form.get('maintenance_date')
    next_maintenance_due = request.form.get('next_maintenance_due')

    db = connect_db()
    if db is None:
        return jsonify({"success": False, "message": "Database connection error"}), 500

    cursor = db.cursor()
    try:
        cursor.execute("""
            UPDATE Resource_Maintenance
            SET resource_id = %s, maintenance_type = %s, maintenance_date = %s, next_maintenance_due = %s
            WHERE maintenance_id = %s
        """, (resource_id, maintenance_type, maintenance_date, next_maintenance_due, maintenance_id))
        db.commit()
        return jsonify({"success": True, "message": "Resource maintenance updated successfully!"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"success": False, "message": f"Error updating resource maintenance: {str(e)}"}), 400
    finally:
        cursor.close()
        db.close()

# Add and Edit routes for Resource Requests
@app.route('/api/add_resourceRequestsTable', methods=['POST'])
def add_resource_request():
    # Extract form data
    request_id = request.form.get('request_id')
    requested_by = request.form.get('requested_by')
    resource_id = request.form.get('resource_id')
    request_date = request.form.get('request_date')
    status = request.form.get('status')

    db = connect_db()
    if db is None:
        return jsonify({"success": False, "message": "Database connection error"}), 500

    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO Resource_Requests (request_id, requested_by, resource_id, request_date, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (request_id, requested_by, resource_id, request_date, status))
        db.commit()
        return jsonify({"success": True, "message": "Resource request added successfully!"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"success": False, "message": f"Error adding resource request: {str(e)}"}), 400
    finally:
        cursor.close()
        db.close()

@app.route('/api/edit_resourceRequestsTable', methods=['POST'])
def edit_resource_request():
    # Extract form data
    request_id = request.form.get('request_id')
    requested_by = request.form.get('requested_by')
    resource_id = request.form.get('resource_id')
    request_date = request.form.get('request_date')
    status = request.form.get('status')

    db = connect_db()
    if db is None:
        return jsonify({"success": False, "message": "Database connection error"}), 500

    cursor = db.cursor()
    try:
        cursor.execute("""
            UPDATE Resource_Requests
            SET requested_by = %s, resource_id = %s, request_date = %s, status = %s
            WHERE request_id = %s
        """, (requested_by, resource_id, request_date, status, request_id))
        db.commit()
        return jsonify({"success": True, "message": "Resource request updated successfully!"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"success": False, "message": f"Error updating resource request: {str(e)}"}), 400
    finally:
        cursor.close()
        db.close()
        
        

@app.route('/doctors_dashboard')
def doctors_dashboard():
    db = connect_db()
    if db is None:
        flash("Database connection error", "error")
        return redirect(url_for('index'))
    try:
        cursor = db.cursor(dictionary=True)  # Use dictionary=True for easier access to columns by name
        query = '''SELECT appointmentID, patientID, dept_name, doctorID, appointment_date, appointment_time, status FROM appointments;'''
        cursor.execute(query)
        appointments = cursor.fetchall()  # Fetch all results
    except mysql.connector.Error as e:
        flash(f"Error retrieving appointments: {str(e)}", "error")
        appointments = []  # Set to empty list on error
    finally:
        cursor.close()  # Ensure cursor is closed
        db.close()  # Ensure database connection is closed

    return render_template('doctors_dashboard.html', appointments=appointments)  # Pass appointments to the template


@app.route('/current_appointment')
def current_appoinment():
    return render_template('ca1.html')

@app.route('/api/current-appointment')
def get_current_appointment():
    # Fetch current appointment for the logged-in doctor
    # This should return the active appointment or None
    # Assuming doctorID is available from session or request context
    doctor_id = request.args.get('doctorID')
    current_appointment = None  # Replace with actual database query
    patient_details = None  # Replace with actual database query
    return jsonify({
        'appointment': current_appointment,
        'patient': patient_details
    })

@app.route('/api/patient/search')
def search_patients():
    search_term = request.args.get('term')
    # Implement patient search logic
    found_patient_id = None  # Replace with actual database query
    return jsonify({'patientId': found_patient_id})

@app.route('/api/patient/<int:patient_id>/history')
def get_patient_history(patient_id):
    # Fetch patient's appointment history
    appointments = []  # Replace with actual database query
    return jsonify({'appointments': appointments})

@app.route('/api/upload-document', methods=['POST'])
def upload_document():
    if 'document' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['document']
    document_type = request.form.get('documentType')
    patient_id = request.form.get('patientID')
    doctor_id = request.form.get('doctorID')
    
    if file and patient_id and doctor_id:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Save file information to database
        # Ensure to handle the foreign key constraints with patientID and doctorID
        return jsonify({'message': 'Upload successful'})
    
    return jsonify({'error': 'Invalid request'}), 400

@app.route('/api/save-prescription', methods=['POST'])
def save_prescription():
    prescription_text = request.form.get('prescription')
    patient_id = request.form.get('patientID')
    doctor_id = request.form.get('doctorID')
    
    if prescription_text and patient_id and doctor_id:
        # Save prescription to database
        # Ensure to handle the foreign key constraints with patientID and doctorID
        return jsonify({'message': 'Prescription saved successfully'})
    
    return jsonify({'error': 'Invalid request'}),400

@app.route('/patient_history', methods=['GET', 'POST'])
def patient_history():
    import re
    db = connect_db()
    patient = None
    appointments = []
    medical_records = []

    if request.method == 'POST':
        search_term = request.form['search_term'].strip()
        
        # SQL query to find the patient by ID or Name
        patient_query = db.session.execute(
            "SELECT * FROM patient WHERE patientID = :search_term OR patientName LIKE :name",
            {'search_term': search_term, 'name': f'%{search_term}%'}
        )
        
        patient = patient_query.fetchone()
        
        if patient:
            # Fetch appointments for the found patient
            appointments_query = db.session.execute(
                "SELECT * FROM appointment WHERE patientID = :patient_id",
                {'patient_id': patient.patientID}
            )
            appointments = appointments_query.fetchall()
            
            # Fetch medical records for the found patient
            medical_records_query = db.session.execute(
                "SELECT * FROM medical_record WHERE patientID = :patient_id",
                {'patient_id': patient.patientID}
            )
            medical_records = medical_records_query.fetchall()

    return render_template('patient_history.html', patient=patient, appointments=appointments, medical_records=medical_records)




@app.route('/allocate_resources', methods=['GET'])
def allocate_resources():
    db = connect_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM patients_resources")
        resources = cursor.fetchall()
    except mysql.connector.Error as e:
        flash(f"Error retrieving resources: {str(e)}", "error")
        resources = []
    finally:
        cursor.close()
        db.close()

    return render_template('allocate_resources.html', patients_resources=resources)

# Route to allocate resources
@app.route('/allocate_resources/allocate', methods=['POST'])
def allocate():
    db = connect_db()
    if db is None:
        flash("Database connection error", "error")
        return redirect(url_for('allocate_resources'))

    cursor = db.cursor()

    # Fetching form data
    patient_id = request.form.get('patientID')
    resource_id = request.form.get('resource_id')
    quantity = request.form.get('quantity')
    request_date = request.form.get('request_date')

    # Debugging: Log the received form data
    print("Form data received:")
    print(f"Patient ID: {patient_id}")
    print(f"Resource ID: {resource_id}")
    print(f"Quantity: {quantity}")
    print(f"Request Date: {request_date}")

    # Validation: Check if form data is not empty
    if not all([patient_id, resource_id, quantity, request_date]):
        flash("All fields are required!", "error")
        return redirect(url_for('allocate_resources'))

    try:
        # Check if the resource is available in the required quantity
        cursor.execute("SELECT available_quantity FROM resources WHERE resource_id = %s", (resource_id,))
        available_quantity = cursor.fetchone()
        if available_quantity is None or available_quantity[0] < int(quantity):
            flash("Insufficient resources available", "error")
            return redirect(url_for('allocate_resources'))

        # Executing the INSERT query
        query = """
            INSERT INTO patients_resources (patientID, resource_id, quantity, request_date, status)
            VALUES (%s, %s, %s, %s, 'Allocated')
        """
        cursor.execute(query, (patient_id, resource_id, quantity, request_date))
        db.commit()

        # Debugging: Confirm successful insertion
        print("Insert successful")
        flash("Resource allocated successfully!", "success")

    except mysql.connector.IntegrityError as e:
        db.rollback()
        print("Integrity Error:", str(e))
        flash(f"Integrity error: {str(e)}", "error")

    except mysql.connector.DataError as e:
        db.rollback()
        print("Data Error:", str(e))
        flash(f"Data error: {str(e)}", "error")

    except mysql.connector.Error as e:
        db.rollback()
        print("MySQL Error:", str(e))
        flash(f"Error allocating resource: {str(e)}", "error")

    finally:
        # Closing the cursor and database connection
        cursor.close()
        db.close()

    return redirect(url_for('allocate_resources'))


# Route to return resources
@app.route('/allocate_resources/return', methods=['POST'])
def return_resource():
    db = connect_db()
    cursor = db.cursor()

    return_patient_id = request.form.get('patientID')
    return_resource_id = request.form.get('resource_id')
    return_quantity = int(request.form.get('quantity'))  # Ensure integer
    return_date = request.form.get('returned_date')

    try:
        # Check if the quantity can be updated without going negative
        cursor.execute("""
            SELECT quantity 
            FROM patients_resources
            WHERE patientID = %s AND resource_id = %s AND status = 'Allocated'
        """, (return_patient_id, return_resource_id))
        result = cursor.fetchone()
        if result and result[0] >= return_quantity:
            cursor.execute("""
                UPDATE patients_resources
                SET status = 'Returned', returned_date = %s, quantity = quantity - %s
                WHERE patientID = %s AND resource_id = %s AND status = 'Allocated'
            """, (return_date, return_quantity, return_patient_id, return_resource_id))
            db.commit()
            flash("Resource returned successfully!", "success")
        else:
            flash("Error: Insufficient quantity to return.", "error")
    except mysql.connector.Error as e:
        db.rollback()
        flash(f"MySQL Error: {str(e)}", "error")
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('allocate_resources'))


 # Adjust the import based on your file structure


    
if __name__ == '__main__':
    app.run(debug=True)

for rule in app.url_map.iter_rules():
    print(rule.endpoint, rule.rule)