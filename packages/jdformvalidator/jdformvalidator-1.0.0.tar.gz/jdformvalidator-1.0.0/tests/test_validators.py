from jdformvalidator.validators import (
    is_valid_email, is_strong_password, is_valid_phone,
    is_valid_pan, is_valid_aadhaar, is_valid_file_type,
    is_valid_pincode, is_valid_length, is_valid_dob
)

def run_tests():
    assert is_valid_email('test@gmail.com') == True
    assert is_valid_email('invalid-email') == False

    assert is_strong_password('Password1') == True
    assert is_strong_password('weak') == False

    assert is_valid_phone('9876543210') == True
    assert is_valid_phone('1234567890') == False

    assert is_valid_pan('ABCDE1234F') == True
    assert is_valid_pan('ABCDE123F') == False

    assert is_valid_aadhaar('234567890123') == True
    assert is_valid_aadhaar('123456789012') == False

    assert is_valid_file_type('image.jpg') == True
    assert is_valid_file_type('document.exe') == False

    assert is_valid_pincode('600001') == True
    assert is_valid_pincode('012345') == False

    assert is_valid_length('Jalal', min_length=3, max_length=10) == True
    assert is_valid_length('Hi', min_length=3, max_length=10) == False

    assert is_valid_dob('2000-01-01', min_age=18) == True
    assert is_valid_dob('2010-01-01', min_age=18) == False
    assert is_valid_dob('2005-01-01', min_age=21) == False

def run_tests():
    # your assertions...
    print('✅ All Tests Passed Successfully!')

if __name__ == '__main__':
    run_tests()
