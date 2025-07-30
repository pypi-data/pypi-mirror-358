from setuptools import setup, find_packages

setup(
    name='jdformvalidator',
    version='1.0.0',
    description='JD Form Validator - A Professional Python Library for Input Validations',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Jalaludheen H (JD)',
    author_email='jalaludheen2303@gmail.com',
    url='https://github.com/jalal2303/jdformvalidator',
    packages=find_packages(),
    install_requires=[],
    keywords=['validation', 'form', 'email', 'phone', 'python', 'pan', 'aadhaar', 'file type', 'dob'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
)
