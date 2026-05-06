import re
import dateparser
from datetime import datetime

class DateTimeExtractor:
    @staticmethod
    def extract(text: str) -> tuple[str, str, str]:
        """
        Extracts date and time from a string and returns the cleaned text, date, and time.
        """
        date_info = ""
        time_info = ""

        # 1. Extract Time (Expanded to catch "before", "at", "by")
        time_pattern = r'\b(?:(?:at|before|by)\s+)?\d{1,2}(?::\d{2})?\s*(?:am|pm)\b'
        time_match = re.search(time_pattern, text, re.IGNORECASE)
        
        if time_match:
            time_str = time_match.group(0)
            parsed_time = dateparser.parse(time_str, settings={'PREFER_DATES_FROM': 'future'})
            if parsed_time:
                time_info = parsed_time.strftime('%I:%M %p') # E.g., 07:00 AM
            
            # Remove extracted time from text
            text = text.replace(time_str, "")

        # 2. Extract Date (Expanded to catch months like "april 17" or "Jan 5th")
        months = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
        date_pattern = r'\b(today|tomorrow|tonight|next\s+\w+|in\s+\d+\s+\w+|by\s+\w+|' + months + r'\s+\d{1,2}(?:st|nd|rd|th)?)\b'
        
        date_match = re.search(date_pattern, text, re.IGNORECASE)
        
        if date_match:
            date_str = date_match.group(0)
            parsed_date = dateparser.parse(date_str, settings={'PREFER_DATES_FROM': 'future'})
            if parsed_date:
                date_info = parsed_date.strftime('%b %d, %Y') # E.g., Apr 17, 2026
            
            # Remove extracted date from text
            text = text.replace(date_str, "")

        # Default to today if no date info found in input
        if not date_info:
            date_info = datetime.now().strftime('%b %d, %Y')

        # 3. Clean up the remaining text
        # Removes stray spaces and dangling commas left behind (e.g., "Finish report ,  " -> "Finish report")
        text = re.sub(r'\s+', ' ', text) 
        text = re.sub(r'(?:^[, ]+|[, ]+$)', '', text) 
        
        return text.strip(), date_info, time_info