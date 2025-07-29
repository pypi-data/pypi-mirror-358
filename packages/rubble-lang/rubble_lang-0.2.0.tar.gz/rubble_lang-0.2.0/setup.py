from setuptools import setup

setup(
    name='rubble-lang',         
    version='0.2.0',
    description='An unreadable programming language.',
    author='Ayaan Grover',
    author_email='ayaangrover@gmail.com',
    py_modules=['rubble', 'encode'],
    entry_points={
        'console_scripts': [
            'rubble=rubble:main'
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)