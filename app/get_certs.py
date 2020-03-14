import requests
import json
from app import engine, logger
from app.models import CertsMaster, OrgsCertsRefsMaster
from app.utilities import export_to_excel
from config import Config
from sqlalchemy.orm import sessionmaker
import pandas as pd
from bs4 import BeautifulSoup
import lxml
import regex as reg
import sys


def get_cert_by_domain_name(domain, export_outfile):
    logger.debug('Getting cert.sh URL from config.py')
    base_url = Config.CERTSH_API_URL
    counter = 0
    url = base_url.format(domain.strip())
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
        logger.info(
            'Obtained the certificates list from cert.sh for {} domain'.format(domain))
        certs = json.loads(response.content)  # returns a dictionary
        logger.debug('Creating dataframe in the event export option is given')
        # Creating dataframe in the event export option is given
        dataframe = pd.DataFrame(
            columns=['issuer_ca_id', 'issuer_name', 'name_value', 'crtsh_id', 'entry_timestamp', 'not_before',
                     'not_after', 'search_tag'])
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
            search_tag = domain.strip()
            for name_value in name_values.splitlines():
                cert_entry = CertsMaster(issuer_ca_id=issuer_ca_id, issuer_name=issuer_name.strip(),
                                         domain_name=name_value.strip().lower(), crtsh_id=crtsh_id,
                                         entry_timestamp=entry_timestamp.strip(), not_before=not_before.strip(),
                                         not_after=not_after.strip(), search_tag=search_tag.strip())
                if export_outfile is not False:  # if -e or --export option is given
                    logger.debug(
                        'Detected excel output. Appending dataframe as --export or -e given')
                    dataframe = dataframe.append({'issuer_ca_id': issuer_ca_id, 'issuer_name': issuer_name,
                                                  'name_value': name_value.lower(), 'crtsh_id': crtsh_id,
                                                  'entry_timestamp': entry_timestamp, 'not_before': not_before,
                                                  'not_after': not_after, 'search_tag': search_tag.strip()},
                                                 ignore_index=True)
                    logger.debug('Dataframe appended')
                logger.debug('Adding entry to database: {} - {}'.format(
                    cert_entry.issuer_ca_id, cert_entry.name_value))
                session.add(cert_entry)
                logger.debug(
                    'Added entry to database object in app (not committed yet)')
                counter += 1
        session.commit()
        logger.debug('Committed all entries to database')
        logger.info('The master database is updated with {} records for {}'.format(
            counter, domain))
        #  if -e or --export option is given
        if export_outfile is not None:
            logger.debug(
                'Passing dataframe to utilities function generate excel')
            export_to_excel(dataframe=dataframe, outfile=export_outfile)


def get_cert_refs_by_org(org_name, output_type, export_outfile):
    logger.debug('Getting cert.sh URL from config.py')
    base_url = Config.CERTSH_API_ORG_URL
    counter = 0
    url = base_url.format('%20'.join(org_name.strip().split(' ')), output_type)
    logger.info('Requesting cert.sh for {} org'.format(org_name))
    logger.debug('Requesting the URL {}'.format(url))
    response = requests.get(url)
    '''
        # format of the json response:
            issuer_ca_id : 1191
            issuer_name : "C=US, O=DigiCert Inc, CN=DigiCert SHA2 Secure Server CA"
            name_value : "Infosys Limited.."
            id : 2574327583
            entry_timestamp : "2020-03-13T17:13:51.802"
            not_before : "2020-03-03T00:00:00"
            not_after : "2021-03-03T12:00:00"
    '''
    logger.debug('Troubleshoot: obtained response {}'.format(response.content))
    if response.ok:
        logger.info(
            'Obtained the certificates references list from cert.sh for {} organisation'.format(org_name))
        certs = json.loads(response.content)  # returns a dictionary
        logger.debug('Creating dataframe in the event export option is given')
        # Creating dataframe in the event export option is given
        dataframe = pd.DataFrame(
            columns=['issuer_ca_id', 'issuer_name', 'org_name', 'crtsh_id', 'entry_timestamp', 'not_before',
                     'not_after', 'search_tag'])
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
            # Additional search tag being added so we can use store searched org_name to filter out results by previous searches
            search_tag = org_name.strip()
            for name_value in name_values.splitlines():
                cert_refs_entry = OrgsCertsRefsMaster(issuer_ca_id=issuer_ca_id, issuer_name=issuer_name.strip(),
                                                      org_name=name_value.strip().lower(), crtsh_id=crtsh_id,
                                                      entry_timestamp=entry_timestamp.strip(),
                                                      not_before=not_before.strip(),
                                                      not_after=not_after.strip(), search_tag=search_tag.strip())
                # if export_outfile is not False:  # if -e or --export option is given
                logger.debug(
                    'Appending dataframe which needs to be used for updating CertsMaster')
                dataframe = dataframe.append({'issuer_ca_id': issuer_ca_id, 'issuer_name': issuer_name,
                                                'org_name': name_value.lower(), 'crtsh_id': crtsh_id,
                                                'entry_timestamp': entry_timestamp, 'not_before': not_before,
                                                'not_after': not_after, 'search_tag': search_tag.strip()},
                                                ignore_index=True)
                logger.debug('Dataframe appended')
                logger.debug('Adding entry to database: {} - {}'.format(
                    cert_refs_entry.issuer_ca_id, cert_refs_entry.org_name))
                session.add(cert_refs_entry)
                logger.debug(
                    'Added entry to database object in app (not committed yet)')
                counter += 1
        session.commit()
        logger.debug('Committed all entries to database')
        logger.info('The master database is updated with {} records for {}'.format(
            counter, org_name))
        #  if -e or --export option is given
        if export_outfile is not None:
            logger.debug(
                'Passing dataframe to utilities function generate excel')
            export_to_excel(dataframe=dataframe, outfile=export_outfile)
        return dataframe
    else:
        logger.info('Error! Did not recieve server response, please check URL')
        sys.exit('Exiting!!')


def get_domains_by_cert_ref(cert_ref_id):
    logger.debug('Entered "get_domains_by_cert_ref" function...')
    logger.info('Getting domains from the certificate "{}"'.format(cert_ref_id))
    baseurl = Config.CERTSH_API_REQUEST_ID_URL
    # https://crt.sh/?id=2574327583
    # id = '2526431183'
    id = str(cert_ref_id).strip()
    output_format = 'html'  # Hard coded
    curr_cert_url = baseurl.format(id, output_format)
    response = requests.get(curr_cert_url)
    soup = BeautifulSoup(response.content, 'lxml')
    # items = soup.find_all(text=reg.compile('DNS:[A-Za-z0-9]*[.][a-zA-Z0-9]*'))
    domain_list = []
    dns_items = soup.find_all(text=reg.compile('DNS[\s]*:[\s]*([^\s]+[.][\S]+){1,}'))
    # commonName_items = soup.find_all(text=reg.compile('commonName[\s]*=[\s]([A-Za-z0-9]*[.]*[a-zA-Z0-9]*){1,}'))
    commonName_items = soup.find_all(text=reg.compile('commonName[\s]*=[\s]([^\s]+[.][\S]+){1,}'))
    for item in dns_items:
        domain = item.split(':')[1]
        # logger.info('identifed {}'.format(item))
        print('identifed DNS:{}'.format(domain))
    for item in commonName_items:
        domain = item.split('=')[1]
        # logger.info('identifed {}'.format(item))
        print('identifed commonName:{}'.format(domain))
