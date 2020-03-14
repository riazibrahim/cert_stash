import os
import logging

basedir = os.getcwd()

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///'+os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FILE_LOGGING_LEVEL = logging.DEBUG
    CONSOLE_LOGGING_LEVEL = logging.INFO
    LOG_FILENAME = 'cert_stash.log'

    # name servers
    NAME_SERVERS = os.environ.get('NAME_SERVERS') or ['8.8.8.8', '1.1.1.1']

    # Crt.sh base urls
    CERTSH_API_URL = os.environ.get('CERTSH_API_URL') or 'https://crt.sh/?q={}&output=json'
    CERTSH_API_ORG_URL = os.environ.get('CERTSH_API_ORG_URL') or 'https://crt.sh/?o={}&output={}'
    CERTSH_API_REQUEST_ID_URL = os.environ.get('CERTSH_API_REQUEST_ID_URL') or 'https://crt.sh/?id={}&output={}'

