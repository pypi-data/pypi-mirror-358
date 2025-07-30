from setuptools import setup, find_packages

setup(
    name='gfab',
    version='0.1.1',
    packages=find_packages(),  # this will detect "core"
    install_requires=[
        "flask",
        "questionary",
        "google-generativeai"
    ],
    entry_points={
        'console_scripts': [
            'gfab=core.ask_questions:main'  # <== FIXED HERE
        ]
    },
    author='Swarup Baral',
    author_email='swarupbaral102@gmail.com',
    description='Gemini Flask App Builder – AI-powered Flask app generator',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/swarupbaral/gfab',
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
