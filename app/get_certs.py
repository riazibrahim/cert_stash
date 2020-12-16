import requests
import json
from app import engine, logger
from app.models import CertsMaster, OrgsCertsRefsMaster
from app.utilities import export_to_excel, check_valid_domain_name, get_tor_session, renew_tor_connection
from config import Config
from sqlalchemy.orm import sessionmaker
import pandas as pd
from bs4 import BeautifulSoup
import regex as reg
import sys
from concurrent.futures import ThreadPoolExecutor as PoolExecutor
from app.globalvars import filename_prepend, input_file, input_phrase, input_domain_flag, input_org_flag, \
    export_all_outfile, export_outfile, process, search_tag, internal_tld_file, external_tld_file, output_type
# from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request
from time import time as timer
import random
from multiprocessing.pool import ThreadPool
import requests
from threading import current_thread
import time


# proxies = get_proxies()

# Get the cert ids from domain name. To be modified.
def get_cert_by_domain_name(domain):
    logger.debug('Entered :: get_cert_by_domain_name')
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
        search_tag = domain.strip()
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
                                                  'domain_name': name_value.lower(), 'crtsh_id': crtsh_id,
                                                  'entry_timestamp': entry_timestamp, 'not_before': not_before,
                                                  'not_after': not_after, 'search_tag': search_tag.strip()},
                                                 ignore_index=True)
                    logger.debug('Dataframe appended')
                logger.debug('Adding entry to database: {} - {}'.format(
                    cert_entry.issuer_ca_id, cert_entry.domain_name))
                session.add(cert_entry)
                logger.debug('Added entry to database object in app (not committed yet)')
                counter += 1
        session.commit()
        logger.debug('Committed all entries to database')
        logger.info('The master database is updated with {} records for {}'.format(
            counter, domain))
        #  if -e or --export option is given
        if export_outfile is not None:
            logger.debug('Passing dataframe to utilities function generate excel')
            file_name = export_outfile + ' - Domains Report'
            export_to_excel(dataframe=dataframe, outfile=file_name, sheet_name=search_tag.strip())


# Extract the cert ids in json format by giving the organization name
def get_cert_ids_by_org(org_name):
    logger.debug('Entered :: get_cert_ids_by_org')
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
        logger.debug('The value of export_outfile is {}'.format(export_outfile))
        if export_outfile is not False:
            logger.debug('Passing dataframe to utilities function generate excel')
            file_name = export_outfile + ' - Certid Report'
            logger.info('Exporting current org search results to the file "{}"'.format(file_name))
            export_to_excel(dataframe=dataframe, outfile=file_name, sheet_name=search_tag.strip())
        return dataframe
    else:
        logger.info('Error! Did not recieve server response, please try again after sometime or check URL in config')
        sys.exit('Exiting!!')


# Extract the domain names by scraping the crt.sh page for each cert id
def get_domains_from_cert_ids(html):
    logger.debug('Entered :: get_domains_from_cert_ids')
    soup = BeautifulSoup(html, 'lxml')
    domain_list = []
    # obtain all entries starting with DNS: xx.com
    dns_items = soup.find_all(text=reg.compile('DNS[\s]*:[\s]*([^\s]+[.][\S]+){1,}'))
    # # obtain all entries starting with commonName = xx.com
    commonName_items = soup.find_all(text=reg.compile('commonName[\s]*=[\s]([^\s]+[.][\S]+){1,}'))
    for item in dns_items:
        domain = item.split(':')[1]
        if domain is not None:
            domain_list.append(domain.strip())
    for item in commonName_items:
        domain = item.split('=')[1]
        if domain is not None:
            domain_list.append(domain.strip())
    return domain_list


def fetch_url_tor(url):
    logger.debug('Entered fetch_url_tor')
    # logger.debug('Current thread {}'.format(current_thread().name))
    session = get_tor_session()
    ip = session.get("http://icanhazip.com").text
    logger.debug('Thread name: {} obtained tor ip {}\n'.format(current_thread().name, ip))
    try:
        user_agent = random.choice(Config.USER_AGENT_LIST)
        headers = {'User-Agent': user_agent}
        response = session.get(url=url, headers=headers)
        logger.debug('request header {}'.format(response.request.headers))
        logger.debug('User agent used is {}\n'.format(user_agent))
        renew_tor_connection(ip=ip)
        return url, response.content, None, ip
    except Exception as e:
        renew_tor_connection(ip=ip)
        return url, None, e, ip


def get_response_from_crtsh_urls(crtsh_url_list):
    logger.debug('Entered "get_response_via_crtsh_id"\n')
    logger.debug('The list of URLs for threading is :{}\n'.format(crtsh_url_list))
    crtsh_response_dict = {}
    start_time = timer()
    threads_count = int(len(crtsh_url_list) / 2) if int(
        len(crtsh_url_list) / 2) < Config.MAX_THREAD_COUNT else Config.MAX_THREAD_COUNT
    chunk_size = int(len(crtsh_url_list) / threads_count)
    logger.info('Using {} threads and chunks of size {}'.format(threads_count, chunk_size))
    results = ThreadPool(threads_count).imap(fetch_url_tor, crtsh_url_list, chunksize=chunk_size)
    for url, html, error, ip in results:
        if error is None:
            logger.debug("%r fetched in %ss -- ip used: %s" % (url, timer() - start_time, ip))
            id = url.split('=')[1].split('&')[0]
            crtsh_response_dict.update({id: html})
        else:
            logger.info("error fetching %r: %s : ip used %s" % (url, error, ip))
    logger.debug("Elapsed Time: %s" % (timer() - start_time))
    logger.info('Number of responses: {}\n'.format(len(crtsh_response_dict)))
    logger.debug('Response dictionary: \n{}'.format(crtsh_response_dict))
    logger.info(
        'Total time taken for {} threads and chunksize {} is {} minutes \n'.format(threads_count, chunk_size,
                                                                                   (timer() - start_time) / 60))
    logger.debug('Exiting "get_response_via_crtsh_id"\n')
    return crtsh_response_dict


def parse_domains_and_update_certsmasterdb(certs_ref_df, org_name):
    logger.debug('Entered :: parse_domains_and_update_certsmasterdb')
    # If Dataframe is empty, exit
    if certs_ref_df.empty:
        logger.info('No results returned.')
        sys.exit('Exiting')

    temp_certsmaster_df = pd.DataFrame(
        columns=[
            'issuer_ca_id',
            'issuer_name',
            'domain_name',
            'crtsh_id',
            'entry_timestamp',
            'not_before',
            'not_after',
            'search_tag'])
    # If Dataframe is not empty, first get the domains from the certs pages and update CertsMaster table
    uniq_certsh_id_list = certs_ref_df['crtsh_id'].unique()
    logger.info('Identified {} unique "crtsh ids" for resolving...\n'.format(len(uniq_certsh_id_list)))
    logger.debug('Identified {} rows in certs_ref_df dataframe...\n'.format(certs_ref_df.shape[0]))
    if not len(uniq_certsh_id_list) == (certs_ref_df.shape[0]):
        sys.exit('Error! Some issue count of unique crtsh ids are not same as number of rows in certs_ref dataframe')
    logger.info('Sanity check done, continuing ....\n')
    domains_list = []
    count = 1
    logger.debug('Connecting to database')
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    logger.debug('Session to database is established')

    crtsh_id_list = certs_ref_df['crtsh_id'].to_list()
    logger.debug('crtsh_ids list is :\n{}'.format(crtsh_id_list))
    crtsh_url_list = []
    for crt_id in crtsh_id_list:
        crtsh_url_list.append(Config.CERTSH_API_REQUEST_ID_URL.format(str(crt_id).strip(), 'html'))

    # logger.info('The URL list is: {}\n'.format(crtsh_url_list))
    crtsh_response_dict = get_response_from_crtsh_urls(crtsh_url_list)

    for index, row in certs_ref_df.iterrows():
        crtsh_id = row['crtsh_id']
        html = crtsh_response_dict.get(str(crtsh_id))
        logger.debug('Value for key {} is\n {}'.format(crtsh_id, html))
        logger.debug('{}. Getting domains from the certificate "{}"'.format(count, crtsh_id))
        domains = get_domains_from_cert_ids(html)  # Returns list of domains from the certsh html pages
        logger.debug('Domains extracted from {} are {}'.format(crtsh_id, domains))
        if len(domains) > 0:
            logger.debug('identified {} domains from current cert entry...\n{}'.format(len(domains), domains))
            domains_list.extend(domains)
            for domain in domains:
                issuer_ca_id = row['issuer_ca_id']
                issuer_name = row['issuer_name']
                domain_name = str(domain).strip().lower()
                crtsh_id = row['crtsh_id']
                entry_timestamp = row['entry_timestamp'].strip()
                not_before = row['not_before'].strip()
                not_after = row['not_after'].strip()
                search_tag = row['search_tag'].strip()
                cert_entry = CertsMaster(issuer_ca_id=issuer_ca_id, issuer_name=issuer_name.strip(),
                                         domain_name=domain_name.strip().lower(), crtsh_id=crtsh_id,
                                         entry_timestamp=entry_timestamp.strip(), not_before=not_before.strip(),
                                         not_after=not_after.strip(), search_tag=search_tag.strip())
                logger.debug(
                    'Adding entry to database: {} - {}'.format(cert_entry.issuer_ca_id, cert_entry.domain_name))
                session.add(cert_entry)
                logger.debug('Added entry to database object in app (not committed yet)')
                if export_outfile is not False:  # if -e or --export option is given
                    logger.debug('Detected excel output. Appending dataframe as --export or -e given')
                    temp_certsmaster_df = temp_certsmaster_df.append({
                        'issuer_ca_id': issuer_ca_id,
                        'issuer_name': issuer_name,
                        'domain_name': domain_name.lower(),
                        'crtsh_id': crtsh_id,
                        'entry_timestamp': entry_timestamp,
                        'not_before': not_before,
                        'not_after': not_after,
                        'search_tag': search_tag.strip()},
                        ignore_index=True)
                    logger.debug('Temp dataframe appended')
        else:
            logger.debug('identified {} domains from current cert entry...\n{}'.format(len(domains), domains))
        count += 1
    logger.debug('Done looping through all certids and domains proceeding to commit changes to database..')
    session.commit()
    logger.debug('Committed all entries to database')
    logger.debug('The master database is updated with {} records for {}'.format(len(domains), org_name))

    if export_outfile is not False:
        logger.debug('Passing dataframe to utilities function to generate excel')
        file_name = export_outfile + ' - Domains Report'
        logger.info('Exporting current org search results to the file "{}"'.format(file_name))
        export_to_excel(dataframe=temp_certsmaster_df, outfile=file_name, sheet_name=org_name.strip())

    logger.info('\nFinished all cert entries...\n')
    logger.info('identified {} domains from all cert entries...\n'.format(len(domains_list)))
    logger.debug('identified {} domains from all cert entries...\n{}'.format(len(domains_list), domains_list))
    logger.debug('Removing duplicates...')
    unique_domains_list = list(dict.fromkeys(domains_list))
    logger.debug('There are {} unique domains from all cert entries...\n{}'.format(len(unique_domains_list),
                                                                                   unique_domains_list))
    logger.info('There are {} unique domains from all cert entries...\n'.format(len(unique_domains_list)))
    logger.info('Refer the CertsMaster database for the extracted domains and cert ids!')
