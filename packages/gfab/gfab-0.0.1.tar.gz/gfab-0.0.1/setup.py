from setuptools import setup, find_packages
import os

def read_file(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name), encoding='utf-8') as f:
        return f.read()

setup(
    name='gfab',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        "flask",
        "questionary",
        "google-generativeai"
    ],
    entry_points={
        'console_scripts': [
            'gfab=.ask_questions:main'
        ]
    },
    author='Swarup Baral',
    author_email='swarupbaral102@gmail.com',
    description='Gemini Flask App Builder – AI-powered Flask app generator',
    long_description=read_file("README.md"),
    long_description_content_type='text/markdown',
    url='https://swarup-developer.github.io/gfab-gemini/',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Code Generators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
