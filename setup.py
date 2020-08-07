# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'requirements.txt')) as requirements_file:
    # Parse requirements.txt, ignoring any commented-out lines.
    requirements = [line for line in requirements_file.read().splitlines()
                    if not line.startswith('#')]
setup(

    name='splash-server',  
    version='0.0.1',
    description='RESTFul splash for CRUD operations on Splash data', 
    long_description=long_description,  
    long_description_content_type='text/markdown', 
    url='https://github.com/als-computing/splash-server',  
    author='Dylan McReynolds', 
    author_email='dmcreynolds@lbl.gov',  

    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.7',
    ],

    packages=find_packages(exclude=['contrib', 'docs', 'tests']), 
    python_requires='>=3.5',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'splash=server:main',
        ],
    },

)
