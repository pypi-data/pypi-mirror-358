# JD Form Validator

![PyPI version](https://img.shields.io/pypi/v/jdformvalidator)

JD Form Validator is a professional and reusable Python library for validating common form inputs like email, phone number, PAN card, Aadhaar, file types, PIN codes, string lengths, and date of birth.

## Installation
```bash
pip install jdformvalidator
```

## Available Validators
- Email Validation
- Password Strength Validation
- Phone Number Validation
- PAN Card Validation
- Aadhaar Number Validation
- File Type Validation
- PIN Code Validation
- String Length Validation
- Date of Birth Validation (Age Check - Customizable)

## Usage Example
```python
from jdformvalidator.validators import (
    is_valid_email, is_strong_password, is_valid_phone,
    is_valid_pan, is_valid_aadhaar, is_valid_file_type,
    is_valid_pincode, is_valid_length, is_valid_dob
)

# Email Validation
print(is_valid_email('test@gmail.com'))          # ✅ True
print(is_valid_email('invalid-email'))           # ❌ False

# Password Validation
print(is_strong_password('Password1'))           # ✅ True
print(is_strong_password('weak'))                # ❌ False

# Phone Number Validation
print(is_valid_phone('9876543210'))              # ✅ True
print(is_valid_phone('1234567890'))              # ❌ False

# PAN Card Validation
print(is_valid_pan('ABCDE1234F'))                # ✅ True
print(is_valid_pan('ABCDE123F'))                 # ❌ False

# Aadhaar Number Validation
print(is_valid_aadhaar('234567890123'))          # ✅ True
print(is_valid_aadhaar('123456789012'))          # ❌ False

# File Type Validation
print(is_valid_file_type('document.pdf'))        # ✅ True
print(is_valid_file_type('malware.exe'))         # ❌ False

# PIN Code Validation
print(is_valid_pincode('600001'))                # ✅ True
print(is_valid_pincode('012345'))                # ❌ False

# String Length Validation
print(is_valid_length('Jalal', min_length=3))    # ✅ True
print(is_valid_length('Hi', min_length=3))       # ❌ False

# Date of Birth Validator - Customizable Minimum Age
print(is_valid_dob('2000-01-01'))                # ✅ True (default min_age=18)
print(is_valid_dob('2005-01-01', min_age=21))    # ❌ False (custom min_age=21)
print(is_valid_dob('2010-01-01', min_age=18))    # ❌ False
```


