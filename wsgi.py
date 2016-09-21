# -*- coding: utf-8 -*-

from aore import phias

# Load config
try:
    from config import *
except ImportError:
    assert "No config"

# Create main app
phias.App(config.BasicConfig.logfile)

# Define wsgi app
application = phias.app

# Run bottle WSGI server if no external
if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8087, debug=True)
