import os

DEBUG = os.environ.get('DEBUG', False)
DEBUG_TB_INTERCEPT_REDIRECTS = False
MYSQL_HOST = 'localhost'
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'q')
MYSQL_DB = 'ptbakery'
MYSQL_CURSORCLASS = 'DictCursor'

SECRET_KEY = "\xe2\x88\xf2\x10\xf1\x02\xf2O\x19)~\xa6\xd6\xe1f\x1d"
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'mysql://root:q@localhost:3306/ptbakery')
SQLALCHEMY_TRACK_MODIFICATIONS = True
