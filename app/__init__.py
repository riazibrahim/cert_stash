import argparse
from app.models import Base
from sqlalchemy import create_engine
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import signal
import os
import sys

# Defining arguments and creating the args object
parser = argparse.ArgumentParser(allow_abbrev=False, description='A tool for passive threat intel based on DNS and SSL')
parser.add_argument('-f', '--file', dest='file', type=str, help='Give input filename', required=False)
parser.add_argument('-d', '--domain', dest='domain', type=str, help='Give input domain name', required=False)
parser.add_argument('-eA', '--export_all', dest='export_all_outfile', action='store_true',
                    help='Export entire database to Excel', required=False)
parser.add_argument('-t', '--tag', dest='search_tag', type=str, help='Download results by search "tag" i.e. previous '
                                                                     'search items. Use in conjunction with -eA/ '
                                                                     '--export_all', required=False)
parser.add_argument('-e', '--export', dest='export_outfile', action='store_true',
                    help='Export current query response to Excel', required=False)
parser.add_argument('-p', '--process', dest='process', type=str, choices=['filter'],
                    help='Process the domains in sqlite database to find potential internal domains', required=False)
parser.add_argument('-if', '--internalTLDFile', dest='itld', type=str,
                    help='To use with --process. Give internal tlds in file', required=False)
parser.add_argument('-ef', '--externalTLDFile', dest='etld', type=str,
                    help='To use with --process. Give external tlds in file', required=False)

args = parser.parse_args()

# Define SQL database

# create engine
dbi_uri = Config.SQLALCHEMY_DATABASE_URI
engine = create_engine(dbi_uri, echo=False)

# create all tables
Base.metadata.create_all(engine)

# Define logging : file and console

if not os.path.exists('logs'):
    os.mkdir('logs')

if not os.path.exists('outputs'):
    os.mkdir('outputs')

# create logger with 'spam_application'
logger = logging.getLogger('collision')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
file_handler = logging.FileHandler('logs/{}'.format(Config.LOG_FILENAME))
file_handler.setLevel(Config.FILE_LOGGING_LEVEL)
# create console handler with a higher log level
console_handler = logging.StreamHandler()
console_handler.setLevel(Config.CONSOLE_LOGGING_LEVEL)
# create formatter and add it to the handlers
file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
console_formatter = logging.Formatter('%(levelname)s: %(message)s')
# console_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
file_handler.setFormatter(file_formatter)
console_handler.setFormatter(console_formatter)
# add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.debug('Collision app has started')


# Signal handler To exit on Ctrl+C
def signal_handler(sig, frame):
    print('\n\nYou pressed Ctrl+C! .. exiting..')
    sys.exit('Bye!')


signal.signal(signal.SIGINT, signal_handler)

from app import app, models
