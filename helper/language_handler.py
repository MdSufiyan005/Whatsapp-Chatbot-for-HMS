from deep_translator import GoogleTranslator
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class LanguageHandler:
    def __init__(self):
        self.supported_languages = {
            'english': 'en',
            'hindi': 'hi',
            'marathi': 'mr'
        }
        
    def detect_language(self, text: str) -> str:
        # Since deep_translator doesn't have language detection,
        # we'll return 'en' by default or implement basic detection based on content
        return 'en'
    
    def translate_to_english(self, text: str, source_language: str) -> Tuple[str, bool]:
        try:
            if source_language == 'en':
                return text, True
                
            translator = GoogleTranslator(source=source_language, target='en')
            translated = translator.translate(text)
            return translated, True
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text, False
    
    def translate_from_english(self, text: str, target_language: str) -> str:
        try:
            if target_language == 'en':
                return text
                
            translator = GoogleTranslator(source='en', target=target_language)
            return translator.translate(text)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text  # Return original text on error
    
    def get_language_code(self, language: str) -> str:
        return self.supported_languages.get(language.lower(), 'en')