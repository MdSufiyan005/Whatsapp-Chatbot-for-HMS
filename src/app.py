from chatbot.helper.LLM_api import text_complition
from helper.twilio_api import send_message
from flask import Flask, request
from dotenv import load_dotenv
import re
from datetime import datetime
import logging
#import ast
import os
from groq import Groq
import requests  # Import requests to make API calls
from helper.language_handler import LanguageHandler
from helper.session_handler import SessionHandler

from helper.database import DatabaseHelper

load_dotenv()
# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize database
db = DatabaseHelper()

app = Flask(__name__)

one = '''
        Your responsibility is to parse the provided message and provide details like 
            - Name of the person
            - Mobile Number
            - Address
            - Department "Type of OPD" 
        if provided in the message by the user. Also remember to provide the output in a form of dictionary.
'''
grok_api_key = os.getenv('GROK_API_KEY')
client = Groq(api_key=grok_api_key)

language_handler = LanguageHandler()
session_handler = SessionHandler()


def get_welcome_message(language_code: str) -> str:
    welcome_messages = {
        'en': """Welcome to City General Hospital! Please select your preferred language:
1. English
2. हिंदी (Hindi)
3. मराठी (Marathi)""",
        'hi': """सिटी जनरल अस्पताल में आपका स्वागत है! कृपया अपनी पसंदीदा भाषा चुनें:
1. English
2. हिंदी (Hindi)
3. मराठी (Marathi)""",
        'mr': """सिटी जनरल हॉस्पिटलमध्ये आपले स्वागत आहे! कृपया आपली पसंतीची भाषा निवडा:
1. English
2. हिंदी (Hindi)
3. मराठी (Marathi)"""
    }
    return welcome_messages.get(language_code, welcome_messages['en'])

def get_menu_message(language_code: str) -> str:
    menu_messages = {
        'en': """Please select an option:
1. Hospital Information
2. Book Appointment
3. Manage Appointment (Reschedule/Cancel)""",
        'hi': """कृपया एक विकल्प चुनें:
1. अस्पताल की जानकारी
2. अपॉइंटमेंट बुक करें
3. अपॉइंटमेंट प्रबंधन (पुनर्निर्धारण/रद्द)""",
        'mr': """कृपया एक पर्ाय निवडा:
1. रुग्णालयाची माहिती
2. अपॉइंटमेंट बुक करा
3. अपॉइंटमेंट व्यवस्थापन (पुनर्नियोजन/रद्द)"""
    }
    return menu_messages.get(language_code, menu_messages['en'])

@app.route('/')
def home():
    return 'Hospital Management System is running...'

@app.route('/twilio/receiveMessage', methods=['POST'])
def receive_message():
    try:
        message = request.form['Body'].strip().lower()
        sender_id = request.form['From']
        mobile = sender_id.split(':')[1]
        
        logger.debug(f"Received message: '{message}' from {mobile}")
        
        # Get or create session
        session = session_handler.get_session(mobile)
        if not session:
            session = session_handler.create_session(mobile, 'en')
        
        # List of greetings and menu commands
        menu_triggers = ['menu', 'hi', 'hello', 'hey', 'hii', 'start', 'restart']
        
        # Check if message is a menu trigger
        if message in menu_triggers:
            welcome_message = get_welcome_message('en')
            send_message(sender_id, welcome_message)
            session_handler.create_session(mobile, 'en')
            return 'OK', 200

        # Handle language selection
        if session['state'] == 'LANGUAGE_SELECTION' and message.isdigit():
            choice = int(message)
            if 1 <= choice <= 3:
                languages = ['en', 'hi', 'mr']
                selected_language = languages[choice - 1]
                session['language'] = selected_language
                session_handler.update_session_state(mobile, 'AWAITING_CHOICE')
                menu_message = get_menu_message(selected_language)
                send_message(sender_id, menu_message)
                return 'OK', 200

        # Handle main menu choices
        if session['state'] == 'AWAITING_CHOICE' and message.isdigit():
            choice = int(message)
            language_code = session['language']

            if choice == 1:  # Hospital Information
                hospital_info = language_handler.translate_from_english(
                    "🏥 *City General Hospital Information*\n\n"
                    "*Address:* 123 Health Avenue, Pune, Maharashtra 411001\n\n"
                    "*Working Hours:*\n"
                    "Monday to Saturday: 9:00 AM - 6:00 PM\n"
                    "Emergency Services: 24/7\n\n"
                    "*Departments:*\n"
                    "1. Cardiology (Block A, 2nd Floor)\n"
                    "   - Dr. Anjali Sharma (Mon, Wed, Fri)\n"
                    "   - Dr. Rajesh Patel (Tue, Thu, Sat)\n\n"
                    "2. ENT (Block B, 1st Floor)\n"
                    "   - Dr. Priya Kumar (Mon, Wed, Fri)\n"
                    "   - Dr. Suresh Mehta (Tue, Thu, Sat)\n\n"
                    "3. Orthopedics (Block A, Ground Floor)\n"
                    "   - Dr. Rahul Singh (Mon, Wed, Fri)\n"
                    "   - Dr. Meera Desai (Tue, Thu, Sat)\n\n"
                    "*Contact Numbers:*\n"
                    "📞 Reception: +91 20 1234 5678\n"
                    "🚑 Ambulance: +91 20 1234 5600\n\n"
                    "Type 'menu' to return to main menu or ask any specific questions about our services.",
                    language_code
                )
                send_message(sender_id, hospital_info)
                session_handler.update_session_state(mobile, 'ASKING_HOSPITAL_INFO')
                return 'OK', 200

            elif choice == 2:  # Book Appointment
                mobile_prompt = language_handler.translate_from_english(
                    "Please enter your mobile number to proceed with booking:",
                    language_code
                )
                send_message(sender_id, mobile_prompt)
                session_handler.update_session_state(mobile, 'BOOKING_MOBILE')
                return 'OK', 200

            elif choice == 3:  # Manage Appointment
                prompt_msg = language_handler.translate_from_english(
                    "Please enter your registered mobile number to access your appointments:",
                    language_code
                )
                send_message(sender_id, prompt_msg)
                session_handler.update_session_state(mobile, 'VERIFY_MOBILE')
                return 'OK', 200

            else:
                invalid_msg = language_handler.translate_from_english(
                    "Invalid choice. Please select a number between 1 and 3.",
                    language_code
                )
                send_message(sender_id, invalid_msg)
            
            return 'OK', 200

        # Handle mobile input for booking
        elif session['state'] == 'BOOKING_MOBILE':
            try:
                # Clean and validate mobile number
                input_mobile = message.strip().replace(' ', '').replace('+', '')
                
                if not input_mobile.isdigit() or len(input_mobile) != 10:
                    error_msg = language_handler.translate_from_english(
                        "Please enter a valid 10-digit mobile number.",
                        session['language']
                    )
                    send_message(sender_id, error_msg)
                    return 'OK', 200
                    
                # Store mobile in session
                session['booking_mobile'] = input_mobile
                logger.debug(f"Stored mobile number in session: {input_mobile}")
                
                # Show department options
                dept_msg = language_handler.translate_from_english(
                    "Please select department for appointment:\n"
                    "1. Cardiology\n"
                    "2. ENT\n"
                    "3. Orthopedics\n"
                    "4. General OPD",
                    session['language']
                )
                send_message(sender_id, dept_msg)
                session_handler.update_session_state(mobile, 'AWAITING_DEPARTMENT', booking_mobile=input_mobile)
                
            except Exception as e:
                logger.error(f"Error in mobile input: {e}", exc_info=True)
                error_msg = language_handler.translate_from_english(
                    "An error occurred. Please try again.",
                    session['language']
                )
                send_message(sender_id, error_msg)
            return 'OK', 200

        # Handle department selection
        elif session['state'] == 'AWAITING_DEPARTMENT' and message.isdigit():
            choice = int(message)
            departments = {
                1: 'Cardiology',
                2: 'ENT',
                3: 'Orthopedics',
                4: 'General OPD'
            }
            
            if choice in departments:
                session['department'] = departments[choice]
                name_prompt = language_handler.translate_from_english(
                    "Please enter patient's full name:",
                    session['language']
                )
                send_message(sender_id, name_prompt)
                session_handler.update_session_state(mobile, 'AWAITING_NAME')
            else:
                error_msg = language_handler.translate_from_english(
                    "Invalid choice. Please select a number between 1 and 4.",
                    session['language']
                )
                send_message(sender_id, error_msg)
            return 'OK', 200

        # Handle name input
        elif session['state'] == 'AWAITING_NAME':
            language_code = session['language']
            # Translate name to English if not already in English
            translated_name, success = language_handler.translate_to_english(message, language_code)
            if not success:
                logger.error("Failed to translate name to English")
                error_msg = language_handler.translate_from_english(
                    "An error occurred. Please try again.",
                    language_code
                )
                send_message(sender_id, error_msg)
                return 'OK', 200
            
            session['name'] = translated_name
            address_prompt = language_handler.translate_from_english(
                "Please enter your complete address:",
                language_code
            )
            send_message(sender_id, address_prompt)
            session_handler.update_session_state(mobile, 'AWAITING_ADDRESS')
            return 'OK', 200

        # Handle address input
        elif session['state'] == 'AWAITING_ADDRESS':
            language_code = session['language']
            # Translate address to English
            translated_address, success = language_handler.translate_to_english(message, language_code)
            if not success:
                logger.error("Failed to translate address to English")
                error_msg = language_handler.translate_from_english(
                    "An error occurred. Please try again.",
                    language_code
                )
                send_message(sender_id, error_msg)
                return 'OK', 200
            
            session['address'] = translated_address
            time_prompt = language_handler.translate_from_english(
                "Please enter preferred appointment time (HH:MM in 24-hour format):",
                language_code
            )
            send_message(sender_id, time_prompt)
            session_handler.update_session_state(mobile, 'AWAITING_TIME')
            return 'OK', 200

        # Handle time input and complete booking
        elif session['state'] == 'AWAITING_TIME':
            try:
                # Validate time format
                time_str = message.strip()
                datetime.strptime(time_str, '%H:%M')
                
                logger.debug("Session data before saving:")
                logger.debug(f"Name: {session.get('name')}")
                logger.debug(f"Mobile: {session.get('booking_mobile')}")
                logger.debug(f"Address: {session.get('address')}")
                logger.debug(f"Department: {session.get('department')}")
                logger.debug(f"Time: {time_str}")
                
                # Prepare appointment data
                appointment_data = {
                    'name': session.get('name'),
                    'mobile': session.get('booking_mobile', ''),  # Get the stored mobile number
                    'address': session.get('address'),
                    'department': session.get('department'),
                    'appointment_time': f"{time_str}:00"
                }
                
                # Validate all required fields are present
                required_fields = ['name', 'mobile', 'address', 'department', 'appointment_time']
                missing_fields = [field for field in required_fields if not appointment_data.get(field)]
                
                if missing_fields:
                    logger.error(f"Missing required fields: {missing_fields}")
                    error_msg = language_handler.translate_from_english(
                        "Some required information is missing. Please start the booking process again.",
                        session['language']
                    )
                    send_message(sender_id, error_msg)
                    session_handler.update_session_state(mobile, 'MENU')
                    return 'OK', 200
                    
                logger.debug(f"Attempting to save appointment: {appointment_data}")
                
                # Save to database
                appointment_id = db.save_appointment(appointment_data)
                
                if appointment_id:
                    # Show confirmation in user's preferred language
                    success_msg = language_handler.translate_from_english(
                        f"✅ Appointment booked successfully!\n\n"
                        f"Appointment Details:\n"
                        f"ID: {appointment_id}\n"
                        f"Name: {appointment_data['name']}\n"
                        f"Mobile: {appointment_data['mobile']}\n"
                        f"Department: {appointment_data['department']}\n"
                        f"Time: {time_str}\n\n"
                        f"Type 'menu' to return to main menu.",
                        session['language']
                    )
                    send_message(sender_id, success_msg)
                    session_handler.update_session_state(mobile, 'MENU')
                else:
                    logger.error("Failed to save appointment to database")
                    error_msg = language_handler.translate_from_english(
                        "Failed to book appointment. Please try again.",
                        session['language']
                    )
                    send_message(sender_id, error_msg)
                    
            except ValueError as e:
                logger.error(f"Time format error: {e}")
                error_msg = language_handler.translate_from_english(
                    "Invalid time format. Please enter time in HH:MM format (e.g., 14:30).",
                    session['language']
                )
                send_message(sender_id, error_msg)
            except Exception as e:
                logger.error(f"Error in appointment booking: {e}", exc_info=True)
                error_msg = language_handler.translate_from_english(
                    "An error occurred. Please try again.",
                    session['language']
                )
                send_message(sender_id, error_msg)
            return 'OK', 200

        # Handle hospital information queries
        elif session['state'] == 'ASKING_HOSPITAL_INFO':
            try:
                logger.debug(f"Processing hospital info query: {message}")
                
                # First translate query to English if needed
                translated_query, success = language_handler.translate_to_english(
                    message, 
                    session['language']
                )
                
                if not success:
                    logger.error("Failed to translate query")
                    error_msg = language_handler.translate_from_english(
                        "Sorry, I couldn't process your query. Please try again.",
                        session['language']
                    )
                    send_message(sender_id, error_msg)
                    return 'OK', 200
                
                # Get response from Groq
                response = text_complition(translated_query)
                logger.debug(f"Groq response: {response}")
                
                if response['status'] == 1 and response['response']:
                    # Translate response back to user's language
                    translated_response = language_handler.translate_from_english(
                        response['response'],
                        session['language']
                    )
                    send_message(sender_id, translated_response)
                    
                    # Ask if they have more questions
                    follow_up = language_handler.translate_from_english(
                        "Do you have any other questions? Or type 'menu' to return to main menu.",
                        session['language']
                    )
                    send_message(sender_id, follow_up)
                else:
                    error_msg = language_handler.translate_from_english(
                        "I apologize, but I couldn't process your query. Please try asking in a different way.",
                        session['language']
                    )
                    send_message(sender_id, error_msg)
                    
            except Exception as e:
                logger.error(f"Error processing hospital info query: {e}", exc_info=True)
                error_msg = language_handler.translate_from_english(
                    "An error occurred. Please try again.",
                    session['language']
                )
                send_message(sender_id, error_msg)

        # Handle mobile verification for managing appointments
        elif session['state'] == 'VERIFY_MOBILE':
            try:
                # Clean and validate mobile number
                input_mobile = message.strip().replace(' ', '').replace('+', '')
                logger.debug(f"Verifying mobile number: {input_mobile}")
                
                # Basic mobile number validation
                if not input_mobile.isdigit() or len(input_mobile) != 10:
                    error_msg = language_handler.translate_from_english(
                        "Please enter a valid 10-digit mobile number.",
                        session['language']
                    )
                    send_message(sender_id, error_msg)
                    return 'OK', 200
                
                # Check for appointments in database
                appointments = db.get_appointments_by_mobile(input_mobile)
                
                if not appointments:
                    not_found_msg = language_handler.translate_from_english(
                        "No appointments found for this mobile number.\n\n"
                        "Please verify your number or book a new appointment.\n\n"
                        "Type 'menu' to return to main menu.",
                        session['language']
                    )
                    send_message(sender_id, not_found_msg)
                    session_handler.update_session_state(mobile, 'MENU')
                    return 'OK', 200
                
                # Show appointments and options
                appointments_list = "Your appointments:\n\n"
                for apt in appointments:
                    appointments_list += (
                        f"🏥 Appointment ID: {apt['id']}\n"
                        f"👨‍⚕️ Department: {apt['department']}\n"
                        f"🕒 Time: {apt['appointment_time']}\n"
                        f"📋 Status: {apt['status']}\n"
                        "-------------------\n"
                    )
                
                options_msg = language_handler.translate_from_english(
                    f"{appointments_list}\n"
                    "Please choose an option:\n"
                    "1. Cancel appointment\n"
                    "2. Change appointment time\n\n"
                    "Type 'menu' to go back to main menu.",
                    session['language']
                )
                
                # Store verified mobile and appointments in session
                session['verified_mobile'] = input_mobile
                session['appointments'] = appointments
                
                send_message(sender_id, options_msg)
                session_handler.update_session_state(mobile, 'MANAGE_CHOICE')
                
            except Exception as e:
                logger.error(f"Error in mobile verification: {e}", exc_info=True)
                error_msg = language_handler.translate_from_english(
                    "An error occurred. Please try again.",
                    session['language']
                )
                send_message(sender_id, error_msg)
            return 'OK', 200

        # Handle management choice (cancel/reschedule)
        elif session['state'] == 'MANAGE_CHOICE':
            if message.isdigit():
                choice = int(message)
                appointments = session.get('appointments', [])
                
                if choice == 1:  # Cancel appointment
                    if len(appointments) == 1:
                        # Only one appointment - cancel directly
                        try:
                            apt_id = appointments[0]['id']
                            logger.debug(f"Attempting to cancel appointment: {apt_id}")
                            
                            if db.cancel_appointment(apt_id):
                                success_msg = language_handler.translate_from_english(
                                    "✅ Your appointment has been cancelled successfully.\n\n"
                                    "Type 'menu' to return to main menu.",
                                    session['language']
                                )
                                send_message(sender_id, success_msg)
                            else:
                                error_msg = language_handler.translate_from_english(
                                    "❌ Failed to cancel appointment. Please try again.",
                                    session['language']
                                )
                                send_message(sender_id, error_msg)
                            session_handler.update_session_state(mobile, 'MENU')
                        except Exception as e:
                            logger.error(f"Error cancelling appointment: {e}", exc_info=True)
                            error_msg = language_handler.translate_from_english(
                                "An error occurred. Please try again.",
                                session['language']
                            )
                            send_message(sender_id, error_msg)
                    else:
                        # Multiple appointments - ask which one to cancel
                        prompt_msg = language_handler.translate_from_english(
                            "Please enter the Appointment ID you want to cancel:",
                            session['language']
                        )
                        send_message(sender_id, prompt_msg)
                        session_handler.update_session_state(mobile, 'CANCEL_APPOINTMENT')
                elif choice == 2:  # Reschedule appointment
                    if appointments:
                        # Store the appointment ID in session for later use
                        session['selected_appointment_id'] = appointments[0]['id']
                        prompt_msg = language_handler.translate_from_english(
                            "Please enter the new appointment time (YYYY-MM-DD HH:MM):",
                            session['language']
                        )
                        send_message(sender_id, prompt_msg)
                        session_handler.update_session_state(mobile, 'RESCHEDULE_TIME')
                    else:
                        error_msg = language_handler.translate_from_english(
                            "No active appointments found.",
                            session['language']
                        )
                        send_message(sender_id, error_msg)
                return 'OK', 200

        # Handle appointment cancellation
        elif session['state'] == 'CANCEL_APPOINTMENT':
            try:
                apt_id = int(message)
                if db.cancel_appointment(apt_id):
                    success_msg = language_handler.translate_from_english(
                        "✅ Appointment cancelled successfully.\n\n"
                        "Type 'menu' to return to main menu.",
                        session['language']
                    )
                    send_message(sender_id, success_msg)
                else:
                    error_msg = language_handler.translate_from_english(
                        "❌ Failed to cancel appointment. Please verify the ID and try again.",
                        session['language']
                    )
                    send_message(sender_id, error_msg)
                session_handler.update_session_state(mobile, 'MENU')
            except ValueError:
                error_msg = language_handler.translate_from_english(
                    "Please enter a valid Appointment ID.",
                    session['language']
                )
                send_message(sender_id, error_msg)
            return 'OK', 200

        # Handle time change
        elif session['state'] == 'CHANGE_TIME':
            try:
                # Validate time format
                new_time = message.strip()
                datetime.strptime(new_time, '%H:%M')
                apt_id = session.get('appointment_to_change')
                
                logger.debug(f"Attempting to update appointment {apt_id} to time {new_time}")
                
                if db.update_appointment_time(apt_id, f"{new_time}:00"):
                    success_msg = language_handler.translate_from_english(
                        f"✅ Appointment time updated successfully to {new_time}.\n\n"
                        f"Type 'menu' to return to main menu.",
                        session['language']
                    )
                    send_message(sender_id, success_msg)
                else:
                    error_msg = language_handler.translate_from_english(
                        "❌ Failed to update appointment time. Please try again.",
                        session['language']
                    )
                    send_message(sender_id, error_msg)
                session_handler.update_session_state(mobile, 'MENU')
                
            except ValueError:
                error_msg = language_handler.translate_from_english(
                    "Invalid time format. Please enter time in HH:MM format (e.g., 14:30).",
                    session['language']
                )
                send_message(sender_id, error_msg)
            except Exception as e:
                logger.error(f"Error in time update: {e}", exc_info=True)
                error_msg = language_handler.translate_from_english(
                    "An error occurred. Please try again.",
                    session['language']
                )
                send_message(sender_id, error_msg)
            return 'OK', 200

        # Handle time change
        elif session['state'] == 'RESCHEDULE_TIME':
            try:
                # Parse the new time
                new_time = datetime.strptime(message, '%Y-%m-%d %H:%M')
                appointment_id = session.get('selected_appointment_id')
                
                if appointment_id and db.update_appointment_time(appointment_id, new_time):
                    success_msg = language_handler.translate_from_english(
                        "✅ Appointment rescheduled successfully!\n"
                        f"New appointment time: {new_time.strftime('%Y-%m-%d %H:%M')}\n\n"
                        "Type 'menu' to return to main menu.",
                        session['language']
                    )
                    send_message(sender_id, success_msg)
                    session_handler.update_session_state(mobile, 'MAIN_MENU')
                else:
                    error_msg = language_handler.translate_from_english(
                        "❌ Failed to reschedule appointment. Please try again.",
                        session['language']
                    )
                    send_message(sender_id, error_msg)
            except ValueError:
                error_msg = language_handler.translate_from_english(
                    "Invalid time format. Please enter the time in YYYY-MM-DD HH:MM format.",
                    session['language']
                )
                send_message(sender_id, error_msg)
            return 'OK', 200

    except Exception as e:
        logger.error(f"Error in main handler: {e}", exc_info=True)
        error_msg = "An error occurred. Please try again."
        if 'session' in locals() and session and 'language' in session:
            error_msg = language_handler.translate_from_english(
                error_msg,
                session['language']
            )
        send_message(sender_id, error_msg)
    
    return 'OK', 200

def get_menu_message(language_code):
    menu_text = "Please select an option:\n1. Hospital Information\n2. Book Appointment\n3. Manage Appointment (Reschedule/Cancel)"
    return language_handler.translate_from_english(menu_text, language_code)

def get_welcome_message(language_code):
    welcome_text = (
        "Welcome to City General Hospital!\n"
        "Please select your preferred language:\n"
        "1. English\n"
        "2. हिंदी (Hindi)\n"
        "3. मराठी (Marathi)"
    )
    return language_handler.translate_from_english(welcome_text, language_code)

if __name__ == '__main__':
    db.setup_database()
    app.run(debug=True)
