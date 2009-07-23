#!/usr/bin/python
# -*- coding: UTF-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
# Author: Huang Jiahua <jhuangjiahua@gmail.com>
# License: GNU LGPL
# Last modified:

app = 'rtedit'

import os, sys
import gettext

if os.path.isdir(os.path.dirname(sys.argv[0]) + '/messages'):
    gettext.install(app, os.path.dirname(sys.argv[0]) + '/messages', unicode=True)
else:
    gettext.install(app, os.path.dirname(os.path.dirname( sys.argv[0])) + '/share/locale', unicode=True)

if __name__=="__main__":
	print _('')



