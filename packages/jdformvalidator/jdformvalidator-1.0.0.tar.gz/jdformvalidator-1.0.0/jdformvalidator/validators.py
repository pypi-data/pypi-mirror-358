import re
from datetime import datetime

# Email Validator
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

# Password Validator
def is_strong_password(password):
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
    return bool(re.match(pattern, password))

# Phone Validator
def is_valid_phone(phone):
    pattern = r'^[6-9]\d{9}$'
    return bool(re.match(pattern, phone))

# PAN Validator
def is_valid_pan(pan):
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
    return bool(re.match(pattern, pan))

# Aadhaar Validator
def is_valid_aadhaar(aadhaar):
    pattern = r'^[2-9]{1}[0-9]{11}$'
    return bool(re.match(pattern, aadhaar))

# File Type Validator
def is_valid_file_type(filename, allowed_extensions=['jpg', 'png', 'pdf']):
    return filename.split('.')[-1].lower() in allowed_extensions

# PIN Code Validator
def is_valid_pincode(pincode):
    pattern = r'^[1-9][0-9]{5}$'
    return bool(re.match(pattern, pincode))

# String Length Validator
def is_valid_length(input_string, min_length=1, max_length=255):
    return min_length <= len(input_string) <= max_length

# Date of Birth Validator
def is_valid_dob(dob, min_age=18):
    try:
        dob_date = datetime.strptime(dob, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
        return age >= min_age
    except ValueError:
        return False
