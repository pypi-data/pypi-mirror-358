from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='shit-env',
    version='0.1.1',
    packages=find_packages(),
    description='A simple .env file manager for Python, inspired by NodeJS dotenv',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='AlexTheMueller',
    author_email='alexalexandramueller@gmx.de',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
) 