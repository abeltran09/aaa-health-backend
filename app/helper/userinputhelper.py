import re

def format_phone_number(phone_number: str) -> str:
    cleaned = re.sub(r'\D', '', phone_number)
    if len(cleaned) == 10:
        return f"({cleaned[:3]})-{cleaned[3:6]}-{cleaned[6:]}"
    raise ValueError("Invalid phone number format")

def format_height(height: str) -> str:
    cleaned = re.sub(r'\D', '', height)
    if len(cleaned) == 2 or len(cleaned) == 3:
        return f'''{cleaned[:1]}'{cleaned[1:]}"'''
    raise ValueError("Invalid height format")