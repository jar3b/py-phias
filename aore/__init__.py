import logging
import os
import sys

reload(sys)
cwd = os.getcwd()
sys.path.append(cwd)
sys.setdefaultencoding("utf-8")
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
