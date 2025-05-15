import pymysql
import pandas as pd
import logging
from flask import Flask, jsonify, request, render_template

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppointmentDashboard:
    def __init__(self):
        try:
            # Database connection
            self.connection = pymysql.connect(
                host="XXXXXXXXXXX",
                port=21216,
                user="avnadmin",
                password="XXXXXXXXXXXX",
                database="defaultdb",
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info("Successfully connected to the database")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def get_all_appointments(self):
        """Retrieve all appointments with their details"""
        try:
            query = """
            SELECT 
                id,
                name,
                mobile,
                address,
                department,
                appointment_time,
                status,
                created_at
            FROM appointments
            ORDER BY appointment_time DESC
            """
            df = pd.read_sql(query, self.connection)
            return df.to_dict(orient='records')  # Convert DataFrame to list of dictionaries
        except Exception as e:
            logger.error(f"Error retrieving appointments: {e}")
            return []

# Flask app setup
app = Flask(__name__)
dashboard = AppointmentDashboard()

@app.route('/appointments', methods=['GET'])
def appointments():
    appointments = dashboard.get_all_appointments()
    return jsonify({'appointments': appointments})

@app.route('/new_appointments')
def new_appointments():
    return render_template('new_appointments.html', appointments=dashboard.get_all_appointments())

if __name__ == '__main__':
    app.run(debug=True)