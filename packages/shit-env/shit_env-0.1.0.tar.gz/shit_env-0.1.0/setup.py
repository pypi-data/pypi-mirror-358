from setuptools import setup, find_packages

setup(
    name='shit-env',
    version='0.1.0',
    packages=find_packages(),
    description='A simple .env file manager for Python, inspired by NodeJS dotenv',
    author='AlexTheMueller',
    author_email='alexalexandramueller@gmx.de',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
) 