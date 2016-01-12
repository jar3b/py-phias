# -*- coding: utf-8 -*-

import os
import sys

# append current dir to module path
reload(sys)
cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cwd)
sys.setdefaultencoding("utf-8")
sys.path.append('/home/i/interc7j/.local/lib/python2.7/site-packages')

from fias import fias

application = fias.app
