import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='dataglu',
    version='0.1',
    packages=['chartly'],
    include_package_data=True,
    license='private',  # example license
    description='A Django App for providing Data Visualization',
    long_description=README,
    url='http://www.datagluchart.com/',
    author='Matthew Feldman',
    author_email='matthew.feldman@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Information Analysis'
    ],
    install_requires=["Django==1.7","logutils","South","django-encrypted-fields","MySQL-python","django_ace","psycopg2","pandas "]
)