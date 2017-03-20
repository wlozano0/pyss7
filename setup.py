'''
Archivo para generar la version exe, para correrlo ejecutar
python setup.py py2exe
'''

from distutils.core import setup
import py2exe

setup(console=['pyss7.py'])
