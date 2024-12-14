from datetime import datetime, timedelta
import random
import string
import logging

logger = logging.getLogger(__name__)

class SessionHandler:
    def __init__(self):
        self.sessions = {}
    
    def create_session(self, mobile: str, language: str) -> dict:
        """Create a new session"""
        session = {
            'language': language,
            'state': 'LANGUAGE_SELECTION',
            'last_activity': datetime.now(),
            'booking_mobile': None,
            'name': None,
            'address': None,
            'department': None,
            'appointment_time': None
        }
        self.sessions[mobile] = session
        return session
    
    def get_session(self, mobile: str) -> dict:
        """Get existing session or None"""
        session = self.sessions.get(mobile)
        logger.debug(f"Retrieved session for {mobile}: {session}")
        return session
    
    def update_session_state(self, mobile: str, state: str, **kwargs) -> None:
        """Update session state and additional data"""
        if mobile in self.sessions:
            self.sessions[mobile]['state'] = state
            self.sessions[mobile]['last_activity'] = datetime.now()
            # Update any additional fields passed
            for key, value in kwargs.items():
                self.sessions[mobile][key] = value
            logger.debug(f"Updated session for {mobile}: {self.sessions[mobile]}")
    
    def set_pending_appointment(self, mobile: str, appointment_info: dict) -> None:
        if mobile in self.sessions:
            self.sessions[mobile]['pending_appointment'] = appointment_info
            logger.debug(f"Set pending appointment for {mobile}: {appointment_info}")
    
    def generate_otp(self) -> str:
        return ''.join(random.choices(string.digits, k=6)) 