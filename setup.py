from setuptools import setup

setup(
    name='py-phias',
    version='0.0.1',
    packages=['aore', 'aore.fias', 'aore.config', 'aore.dbutils', 'aore.updater', 'aore.miscutils'],
    url='https://github.com/jar3b/py-phias',
    license='BSD',
    author='hellotan',
    author_email='hellotan@live.ru',
    description='Python application that can operate with FIAS (Russian Address Object DB)',
    install_requires=
        ['lxml',
         'psycopg2>=2.6.0',
         'bottle>=0.12.0',
         'pysimplesoap',
         'python-Levenshtein',
         'enum34',
         'rarfile',
         'requests']
)
