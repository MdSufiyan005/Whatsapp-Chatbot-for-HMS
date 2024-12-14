import pymysql
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
import traceback

load_dotenv()
logger = logging.getLogger(__name__)

class DatabaseHelper:
    def __init__(self):
        try:
            self.connection = pymysql.connect(
                host="*****************88",
                port=21305,
                user="*********8",
                password="*************",
                database="*******8",
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info("Successfully connected to Aiven MySQL database")
            self.setup_database()
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def setup_database(self):
        try:
            with self.connection.cursor() as cursor:
                # Create appointments table if it doesn't exist
                create_table_query = """
                CREATE TABLE IF NOT EXISTS appointments (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    mobile VARCHAR(15) NOT NULL,
                    address TEXT NOT NULL,
                    department VARCHAR(50) NOT NULL CHECK (department IN ('Cardiology', 'ENT', 'Orthopedics', 'General OPD')),
                    appointment_time DATETIME NOT NULL,
                    status ENUM('active', 'cancelled', 'completed') DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_mobile (mobile),
                    INDEX idx_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """
                cursor.execute(create_table_query)
                self.connection.commit()
                logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Error setting up database: {e}")
            raise

    def save_appointment(self, appointment_info: dict) -> int:
        try:
            logger.debug(f"Received appointment info: {appointment_info}")
            
            # Clean mobile number
            mobile = appointment_info['mobile'].replace('whatsapp:+', '').replace('+91', '').replace(' ', '')
            if mobile.isdigit() and len(mobile) > 10:
                mobile = mobile[-10:]
            
            # Convert appointment time to datetime if it's not already
            appointment_time = appointment_info['appointment_time']
            if isinstance(appointment_time, str):
                try:
                    # Try different time formats
                    time_formats = ['%H:%M:%S', '%H:%M', '%I:%M %p']
                    converted_time = None
                    for fmt in time_formats:
                        try:
                            time_obj = datetime.strptime(appointment_time, fmt)
                            today = datetime.now().date()
                            converted_time = datetime.combine(today, time_obj.time())
                            break
                        except ValueError:
                            continue
                    
                    if converted_time is None:
                        raise ValueError(f"Could not parse time: {appointment_time}")
                    
                    appointment_time = converted_time
                    logger.debug(f"Converted appointment time to: {appointment_time}")
                except Exception as e:
                    logger.error(f"Time conversion error: {e}")
                    raise
            
            with self.connection.cursor() as cursor:
                query = """
                INSERT INTO appointments 
                (name, mobile, address, department, appointment_time, status)
                VALUES (%s, %s, %s, %s, %s, 'active')
                """
                values = (
                    appointment_info['name'],
                    mobile,
                    appointment_info['address'],
                    appointment_info['department'],
                    appointment_time
                )
                
                logger.debug(f"Executing query with values: {values}")
                cursor.execute(query, values)
                self.connection.commit()
                appointment_id = cursor.lastrowid
                logger.info(f"Saved appointment with ID: {appointment_id}")
                return appointment_id
                
        except Exception as e:
            logger.error(f"Error saving appointment: {e}", exc_info=True)
            if self.connection:
                self.connection.rollback()
            return None

    def get_appointments_by_mobile(self, mobile: str) -> list:
        try:
            # Clean mobile number
            mobile = mobile.replace('whatsapp:+', '').replace('+91', '').replace(' ', '')
            if mobile.isdigit() and len(mobile) > 10:
                mobile = mobile[-10:]
            
            with self.connection.cursor() as cursor:
                query = """
                SELECT id, name, mobile, department, appointment_time, status
                FROM appointments 
                WHERE mobile = %s AND status = 'active'
                ORDER BY appointment_time DESC
                """
                cursor.execute(query, (mobile,))
                appointments = cursor.fetchall()
                return appointments
                
        except Exception as e:
            logger.error(f"Error retrieving appointments: {e}")
            return []

    def cancel_appointment(self, appointment_id: int) -> bool:
        try:
            cursor = self.connection.cursor()
            
            # Update the status to 'cancelled' for the given appointment ID
            query = """
            UPDATE appointments 
            SET status = 'cancelled' 
            WHERE id = %s AND status = 'active'
            """
            
            cursor.execute(query, (appointment_id,))
            self.connection.commit()
            
            # Check if the update was successful
            return cursor.rowcount > 0
            
        except pymysql.MySQLError as e:
            logger.error(f"Database error in cancel_appointment: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def update_appointment_time(self, appointment_id: int, new_time: datetime) -> bool:
        try:
            cursor = self.connection.cursor()
            logger.debug(f"Updating appointment {appointment_id} to time {new_time}")
            
            query = """
            UPDATE appointments 
            SET appointment_time = %s 
            WHERE id = %s AND status = 'active'
            """
            
            cursor.execute(query, (new_time, appointment_id))
            self.connection.commit()
            
            success = cursor.rowcount > 0
            logger.debug(f"Update appointment result: {success}")
            return success
            
        except Exception as e:
            logger.error(f"Database error in update_appointment_time: {e}")
            logger.error(traceback.format_exc())
            return False
        finally:
            if cursor:
                cursor.close()

    def __del__(self):
        if hasattr(self, 'connection'):
            self.connection.close()
            logger.info("Database connection closed") 