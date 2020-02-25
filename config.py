import os
import logging

basedir = os.getcwd()

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///'+os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CERTSH_API_URL = os.environ.get('CERTSH_API_URL') or 'https://crt.sh/?q={}&output=json'
    FILE_LOGGING_LEVEL = logging.DEBUG
    CONSOLE_LOGGING_LEVEL = logging.INFO
    LOG_FILENAME = 'cert_stash.log'

    # # Internal and external TLDs domain list for filtering purposes
    # EXT_TLD_LOC = os.environ.get('EXT_TLD_LOC')
    # INT_TLD_LOC = os.environ.get('INT_TLD_LOC')
