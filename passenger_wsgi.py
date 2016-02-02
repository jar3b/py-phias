# -*- coding: utf-8 -*-

from aore import phias

application = phias.app

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=55001, debug=True)
