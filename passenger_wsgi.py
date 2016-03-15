# -*- coding: utf-8 -*-

from aore import phias

# Load config
try:
    from config import *
except ImportError:
    assert "No config"

# Define main app
phias_app = phias.App(config.basic.logfile)
# Define wsgi app
application = phias_app.get_app()

# Run bottle WSGI server if no external
if __name__ == '__main__':
    phias_app.start(host='0.0.0.0', port=8087, debug=True)
