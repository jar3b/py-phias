from setuptools import setup

setup(
    name='py-phias',
    version='0.0.1',
    packages=['aore', 'aore.fias', 'aore.config', 'aore.dbutils', 'aore.updater', 'aore.miscutils'],
    url='https://github.com/jar3b/py-phias',
    license='',
    author='hellotan',
    author_email='hellotan@live.ru',
    description='Python application that can operate with FIAS (Russian Address Object DB)',
    requires=['lxml',
              'psycopg2',
              'bottle',
              'pysimplesoap',
              'python-Levenshtein',
              'enum34',
              'rarfile',
              'requests']
)
