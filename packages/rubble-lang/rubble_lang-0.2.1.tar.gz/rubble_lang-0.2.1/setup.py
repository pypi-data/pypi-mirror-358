from setuptools import setup

setup(
    name='rubble-lang',
    version='0.2.1',
    description='A bad programming language based on Python.',
    author='Ayaan Grover',
    author_email='ayaan@example.com',
    py_modules=['rubble'],
    entry_points={
        'console_scripts': [
            'rubble=rubble:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)