#!/usr/bin/python

from babel.messages import frontend as babel
from distutils.core import setup
#from setuptools import setup, find_packages
import glob



data_files = [ ]

setup(name='rtedit',
      version='0.0.1',
      description='Rich Text Editor based on GTK2',
      long_description ="""RTEdit is a simple rich text editor base on Gtk2.

Features include:

   1. HTML Format
   2. Indexes and Tables
   3. Headings order processor
   4. Hyper links
   5. Images resize / scale
   6. Base64 URL scheme inline images
   7. Font size and styles
   8. undo/redo
   9. Inline pixel margin setting on paragraph / span / block attributes
  10. Bullet list / Orderet list
  11. Paste image direct from from other application
  12. Paste html direct from firefox browser image included
  13. Paste excel formated table section copy from openoffice
  14. Paste full html page direct from browser image included       
      """,
      author='Jiahua Huang',
      author_email='jhuangjiahua@gmail.com',
      license='LGPL',
      url="http://code.google.com/p/rtedit",
      download_url="http://code.google.com/p/rtedit/downloads/list",
      platforms = ['Linux'],
      scripts=['scripts/rtedit'],
      packages = ['rtedit'], 
      data_files = data_files,
      cmdclass = {'compile_catalog': babel.compile_catalog,
                  'extract_messages': babel.extract_messages,
                  'init_catalog': babel.init_catalog,
                  'update_catalog': babel.update_catalog}      
      )
