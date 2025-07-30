# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='bio_tool_version_manager', 
    version='1.2.0',  
    author='Patrick Hyden',  
    author_email='patrick.hyden@ages.at',  
    description='Allows management of tool and workflow version in database and json',
    long_description=open('README.md').read(),  
    long_description_content_type='text/markdown', 
    url='https://github.com/ages-bioinformatics/bio_tool_version_manager', 
    packages=find_packages(),  
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    entry_points={ 
        'console_scripts': [
            'bio_tool_version_manager=bio_tool_version_manager.cli:main',  # Ersetze dies durch den tatsächlichen CLI-Befehl und die Funktion
        ],
    },
)