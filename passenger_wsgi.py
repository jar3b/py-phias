# -*- coding: utf-8 -*-

from aore import phias

# Load config
try:
    from config import *
except ImportError:
    assert "No config"

# Define main app
application = phias.App()

# Run bottle WSGI server if no external
if __name__ == '__main__':
    application.start('0.0.0.0', 8087)
