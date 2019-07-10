# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(

    name='splash-service-alscompute',  # Required
    version='0.0.1',  # Required
    description='RESTFul splash for CRUD operations on Splash data',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://github.com/als-computing/splash-server',  # Optional
    author='Dylan McReynolds',  # Optional
    author_email='dmcreynolds@lbl.gov',  # Optional

    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.7',
    ],

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required
    python_requires='>=3.5',
    install_requires=['flask', 'flask_cors', 'pymongo', 'bokeh'],  # Optional

    entry_points={  # Optional
        'console_scripts': [
            'splash=server:main',
        ],
    },

)