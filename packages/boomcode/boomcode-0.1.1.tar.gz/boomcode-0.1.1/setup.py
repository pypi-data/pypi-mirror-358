# (c) 2025 daredevilmonkeyface (AKA daredevilmonke)
# Licensed under the MIT License
from setuptools import setup, find_packages

setup(
    name='boomcode',  # Change this to your actual package name
    version='0.1.1',
    author='daredevilmonkeyface (AKA daredevilmonke)',
    description='A fun, cool prank package that is easy to code in.',
    long_description=open('README.md', encoding ='utf-8' ).read(),
    long_description_content_type='text/markdown',
    url='https://github.com/daredevilmonkeyface/boomcode',  # Optional but good
    packages=find_packages(),
    install_requires=[
        "pyautogui",
        "pywin32",
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
    ],
    python_requires='>=3.6',
)
