import requests
import json
from app import engine, logger
from app.models import CertsMaster
from app.utilities import export_to_excel
from config import Config
from sqlalchemy.orm import sessionmaker
import pandas as pd


def get_cert(domain, export_outfile):
    logger.debug('Getting cert.sh URL from config.py')
    base_url = Config.CERTSH_API_URL
    counter = 0
    url = base_url.format(domain.rstrip())
    logger.info('Requesting cert.sh for {} domain'.format(domain))
    response = requests.get(url)
    '''
        # format of the json response
        issuer_ca_id : 39
        issuer_name : "O=VeriSign Trust Network, OU="VeriSign, Inc.", OU=VeriSign International Server CA - Class 3, OU=www.verisign.com/CPS Incorp.by Ref. LIABILITY LTD.(c)97 VeriSign"
        name_value : "bpocareers.infosys.com"
        id : 2372219466
        entry_timestamp : "2020-01-24T21:29:17.044"
        not_before : "2009-12-22T00:00:00"
        not_after : "2010-12-08T23:59:59"
    '''
    # print('Troubleshoot: obtained response {}'.format(response.content))
    if response.ok:
        logger.info('Obtained the certificates list from cert.sh for {} domain'.format(domain))
        certs = json.loads(response.content)  # returns a dictionary
        logger.debug('Creating dataframe in the event export option is given')
        # Creating dataframe in the event export option is given
        dataframe = pd.DataFrame(
            columns=['issuer_ca_id', 'issuer_name', 'name_value', 'crtsh_id', 'entry_timestamp', 'not_before',
                     'not_after'])
        logger.debug('Connecting to database')
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        logger.debug('Session to database is established')
        for cert in certs:
            issuer_ca_id = cert['issuer_ca_id']
            issuer_name = cert['issuer_name']
            name_values = cert['name_value']
            crtsh_id = cert['id']
            entry_timestamp = cert['entry_timestamp']
            not_before = cert['not_before']
            not_after = cert['not_after']
            for name_value in name_values.splitlines():
                cert_entry = CertsMaster(issuer_ca_id=issuer_ca_id, issuer_name=issuer_name,
                                         name_value=name_value, crtsh_id=crtsh_id,
                                         entry_timestamp=entry_timestamp, not_before=not_before,
                                         not_after=not_after)
                if export_outfile is not None:  # if -e or --export option is given
                    logger.debug('Detected excel output. Appending dataframe as --export or -e given')
                    dataframe = dataframe.append({'issuer_ca_id': issuer_ca_id, 'issuer_name': issuer_name,
                                                  'name_value': name_value, 'crtsh_id': crtsh_id,
                                                  'entry_timestamp': entry_timestamp, 'not_before': not_before,
                                                  'not_after': not_after}, ignore_index=True)
                    logger.debug('Dataframe appended')
                logger.debug('Adding entry to database: {} - {}'.format(cert_entry.issuer_ca_id, cert_entry.name_value))
                session.add(cert_entry)
                logger.debug('Added entry to database object in app (not committed yet)')
                counter += 1
        session.commit()
        logger.debug('Committed all entries to database')
        logger.info('The master database is updated with {} records for {}'.format(counter, domain))
        #  if -e or --export option is given
        if export_outfile is not None:
            logger.debug('Passing dataframe to utilities funtion generate excel')
            export_to_excel(dataframe=dataframe, outfile=export_outfile)