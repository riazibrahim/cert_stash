import pandas as pd
from pandas import ExcelWriter
from app import logger, args
import os
import dns.resolver
from config import Config
import sys
import regex as re
import requests
from lxml.html import fromstring
from stem.control import Controller
from stem import Signal
from threading import current_thread
import random


def get_tor_session():
    logger.debug('Entered :: get_tor_session')
    session = requests.Session()
    creds = str(random.randint(10000, 0x7fffffff)) + ":" + "foobar"
    session.proxies = {'http': 'socks5h://{}@localhost:9050'.format(creds),
                       'https': 'socks5h://{}@localhost:9050'.format(creds)}
    logger.debug('Exiting :: get_tor_session')
    return session


def renew_tor_connection(ip):
    logger.debug('Thread {} Resetting IP address {}'.format(current_thread().name, ip))
    with Controller.from_port(port=9051) as c:
        c.authenticate(password="password")
        # send NEWNYM signal to establish a new clean connection through the Tor network
        c.signal(Signal.NEWNYM)


# Use pandas to connect to the database given in argument
def export_db_to_excel(engine, tablename, outfile, **kwargs):
    logger.debug('Entered :: export_db_to_excel')
    search_tag = kwargs.get('search_tag', None)
    if search_tag is not None:
        logger.info('Exporting results for search tag :"{}"'.format(search_tag))
        logger.debug('Reading {} table from database {} into pandas dataframe'.format(tablename, engine))
        db_dataframe = pd.read_sql_table(table_name=tablename, con=engine)
        logger.debug('Read to dataframe from database into pandas')
        if not os.path.exists('outputs'):
            os.mkdir('outputs')
        excel_dataframe = db_dataframe[db_dataframe['search_tag'].str.contains(r'\b{}\b'.format(search_tag))]
        if excel_dataframe.empty:
            logger.warning('No records with the given search tag!!')
            sys.exit('Exiting!')
        else:
            records_number = excel_dataframe.shape[0]
            logger.info('Selected {} records for export ...'.format(records_number))
            logger.info('Generating output in excel format')
            excel_dataframe.to_excel('outputs/{}.xlsx'.format(outfile))
            logger.info('Generated {}.xlsx in outputs folder'.format(outfile))
    else:
        logger.info('No search tag is given. Proceeding to download entire database')
        logger.debug('Reading {} table from database {} into pandas dataframe'.format(tablename, engine))
        db_dataframe = pd.read_sql_table(table_name=tablename, con=engine)
        logger.debug('Read to dataframe from database into pandas')
        if not os.path.exists('outputs'):
            os.mkdir('outputs')
        logger.info('Generating output in excel format\n')
        db_dataframe.to_excel('outputs/{}.xlsx'.format(outfile))
        logger.info('Generated {}.xlsx in outputs folder\n'.format(outfile))


def create_dataframe_from_sql(engine, tablename):
    logger.debug('Entered :: create_dataframe_from_sql')
    logger.debug('Reading {} table from database {} into pandas dataframe'.format(tablename, engine))
    db_dataframe = pd.read_sql_table(table_name=tablename, con=engine)
    logger.debug('Read to dataframe from database into pandas')
    return db_dataframe


# TODO: Put sheet names in case this is called inside a loop
def export_to_excel(dataframe, outfile, **kwargs):
    logger.debug('Entered :: export_to_excel')
    logger.debug('Check if sheet_name is given')
    sheet_name = kwargs.get('sheet_name', None)
    logger.debug('Check if sheet_name is given')

    logger.debug('Checking if dataframe is None')
    if len(dataframe) > 0:  # Check if dataframe has any data in it
        try:
            if not os.path.exists('outputs'):
                os.mkdir('outputs')
        except Exception as e:
            logger.debug('Error creating outputs directory. Please check permissions. Details \n{}'.format(e))
            sys.exit('Error creating outputs directory. Please check permissions. Details \n{}'.format(e))
        try:
            filename = 'outputs/{}.xlsx'.format(outfile)
            if os.path.exists(filename):
                logger.debug(
                    'Output file already exists. Appending results')  # TODO: Add to existing sheet, currently it is another sheet
                with ExcelWriter(filename, mode='a') as writer:
                    if sheet_name is not None:
                        dataframe.to_excel(writer, sheet_name=sheet_name)
                    else:
                        dataframe.to_excel(writer)
                    logger.info('Added results to {}.xlsx in outputs folder\n'.format(outfile))
            else:
                if sheet_name is not None:
                    dataframe.to_excel('outputs/{}.xlsx'.format(outfile), sheet_name=sheet_name)
                else:
                    dataframe.to_excel('outputs/{}.xlsx'.format(outfile))
                logger.info('Generated {}.xlsx in outputs folder\n'.format(outfile))
        except Exception as e:
            logger.debug('Error creating outputs directory. Please check permissions. details: \n {}'.format(e))
            sys.exit('Error creating outputs directory. Please check permissions. details: \n {}'.format(e))


# Resolved the domains in the dataframe and returns the results in another dataframe
def resolve_domains(dataframe):
    # initiate nameservers for dns resolver
    logger.debug('Entered :: resolve_domains')
    logger.debug('Initiating resolver object from dnspython')
    ns_resolver = dns.resolver.Resolver(configure=False)
    logger.debug('Setting names servers as in the Config')
    ns_resolver.nameservers = Config.NAME_SERVERS

    # initiate a dataframe to hold dns resolving results
    logger.debug('Initiating dataframe to hold dns resolution results')
    ns_dataframe = pd.DataFrame(
        columns=['Domain Name', 'IP address', 'CNAME'])
    # initiating other variables to hold answers
    logger.info('Extracting unique domains/ urls into a list\n')
    uniq_domain_list = dataframe['name_value'].unique()
    logger.info('Identified {} unique domains/ urls for resolving...\n'.format(len(uniq_domain_list)))
    logger.debug('Iterating through the unique domain list')
    for item in uniq_domain_list:
        ns_a_result = 'NULL'
        ns_cname_result = 'NULL'
        ip_list = []
        cname_list = []
        domain = item.rstrip()
        logger.debug('Selected domain {}:'.format(domain))
        try:
            ns_a_result = ns_resolver.query(domain, 'A')
            logger.debug('Resolved A record {}:'.format(ns_a_result.response.to_text()))
            for ip in ns_a_result:
                ip_list.append(ip.to_text())
        except:
            logger.debug('Error in resolving A record for {} ... moving on'.format(domain))
        try:
            ns_cname_result = ns_resolver.query(domain, 'CNAME')
            logger.debug('Resolved CNAME record {}:'.format(ns_cname_result.response.to_text()))
            for cname in ns_cname_result:
                cname_list.append(cname.to_text())
        except:
            logger.warning('Error in resolving CNAME record for {} ... moving on'.format(domain))
        logger.debug('Appending row to ns dataframe')
        ns_dataframe = ns_dataframe.append({'Domain Name': domain,
                                            'IP address': ip_list,
                                            'CNAME': cname_list}, ignore_index=True)
        logger.debug('Appended row to ns dataframe {}'.format(ns_dataframe['Domain Name']))
    return ns_dataframe


def check_valid_domain_name(domain):
    logger.debug('Entered :: check_valid_domain_name')
    # ([\S]+[.][\S]+){1, }
    pattern = re.compile('([\S]+[.][\S]+){1,}')
    if pattern.match(domain.strip()):
        logger.info('{} is a valid domain name'.format(domain.strip()))
        return True
    else:
        logger.info('{} is not a valid domain name. Skipping...'.format(domain.strip()))
        return False
