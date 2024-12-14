import os
from groq import Groq
import requests  # Import requests to make API calls
from dotenv import load_dotenv
import ast
import logging

load_dotenv()

# Set your Grok API key
grok_api_key = os.getenv('GROK_API_KEY')
client = Groq(api_key=grok_api_key)

logger = logging.getLogger(__name__)

def text_complition(prompt: str) -> dict:
    try:
        logger.debug(f"Sending query to Groq: {prompt}")
        
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": '''You are a helpful assistant for City General Hospital. Answer questions based on the following information:

Hospital Information:
- Name: City General Hospital
- Type: Multi-specialty tertiary care hospital

Departments and OPD Information:
1. Cardiology Department
   - Location: Block A, 2nd Floor
   - Timings: Mon-Fri: 9:00 AM - 5:00 PM, Sat: 9:00 AM - 1:00 PM

2. ENT Department
   - Location: Block B, 1st Floor
   - Timings: Mon-Sat: 10:00 AM - 6:00 PM

3. Orthopedics Department
   - Location: Block A, Ground Floor
   - Timings: Mon-Sat: 9:00 AM - 4:00 PM

4. General OPD
   - Location: Block C, Ground Floor
   - Timings: Mon-Sun: 8:00 AM - 8:00 PM
   - Walk-in consultations available

Valid departments: Cardiology, ENT, Orthopedics, General OPD'''
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=200,
            top_p=1,
            stream=False
        )
        
        response = completion.choices[0].message.content.strip()
        logger.debug(f"Groq response: {response}")
        
        return {
            'status': 1,
            'response': response
        }
    except Exception as e:
        logger.error(f"Error calling Groq API: {e}")
        return {
            'status': 0,
            'response': ''
        }

# def Parsing(prompt: str) -> dict:
#     try:
#         logger.debug(f"Parsing input prompt: {prompt}")
        
#         completion = client.chat.completions.create(
#             model="llama3-8b-8192",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": '''
#                     You are a helpful assistant that extracts appointment information from user messages.
#                     Extract the following information and return it ONLY as a valid Python dictionary:
#                     - name
#                     - mobile (phone number)
#                     - address
#                     - department
#                     - appointment_time (convert to 24-hour format)

#                     Example inputs:
#                     1. "my name is John Smith, mobile 1234567890, address 123 Main St, need cardiology appointment at 2:30 pm"
#                     2. "नाम राम कुमार है, मोबाइल 9876543210, पता दिल्ली, ईएनटी विभाग में शाम 4 बजे"

#                     Example output: 
#                     {"name": "John Smith", "mobile": "1234567890", "address": "123 Main St", "department": "Cardiology", "appointment_time": "14:30:00"}

#                     Rules:
#                     1. Always convert time to 24-hour format with seconds (HH:MM:SS)
#                     2. Capitalize proper nouns (name, department, address)
#                     3. Return ONLY the dictionary, no other text
#                     4. Ensure all fields are present
#                     5. Format time as HH:MM:SS (e.g., "14:30:00" not "14:30")
#                     6. Valid departments: Cardiology, ENT, Orthopedics
#                     '''
#                 },
#                 {
#                     "role": "user",
#                     "content": prompt
#                 }
#             ],
#             temperature=0,
#             max_tokens=200,
#             top_p=1,
#             stream=False
#         )
        
#         response_content = completion.choices[0].message.content.strip()
#         logger.debug(f"Raw Groq response: {response_content}")
        
#         # Clean the response
#         response_content = response_content.replace("```python", "").replace("```", "").strip()
        
#         try:
#             parsed_dict = ast.literal_eval(response_content)
#             logger.debug(f"Successfully parsed dictionary: {parsed_dict}")
            
#             # Ensure time format is correct
#             if 'appointment_time' in parsed_dict:
#                 time_str = parsed_dict['appointment_time']
#                 if len(time_str.split(':')) == 2:
#                     parsed_dict['appointment_time'] = f"{time_str}:00"
            
#             # Validate all required fields
#             required_fields = ['name', 'mobile', 'address', 'department', 'appointment_time']
#             if all(field in parsed_dict for field in required_fields):
#                 return parsed_dict
#             else:
#                 missing_fields = [field for field in required_fields if field not in parsed_dict]
#                 logger.error(f"Missing required fields: {missing_fields}")
#                 return None
                
#         except (ValueError, SyntaxError) as e:
#             logger.error(f"Failed to parse Groq response as dictionary: {e}")
#             logger.error(f"Problematic response content: {response_content}")
#             return None
            
#     except Exception as e:
#         logger.error(f"Error in Parsing function: {e}", exc_info=True)
#         return None