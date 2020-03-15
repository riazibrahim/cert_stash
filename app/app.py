from app import args, logger, engine, parser
from app.utilities import export_db_to_excel, create_dataframe_from_sql, resolve_domains, export_to_excel
from app.get_certs import get_cert_ids_by_org, get_cert_by_domain_name, get_domains_from_cert_ids
from app.filter import filter_domains
from app.models import CertsMaster
from datetime import datetime
import sys
from sqlalchemy.orm import sessionmaker
import pandas as pd

filename_prepend = datetime.now().strftime("%Y%m%d-%H%M%S")

# Gather all arguments
logger.debug('Obtaining all arguments')
input_file = args.file
input_phrase = args.input
input_domain_flag = args.domain  # True or false
input_org_flag = args.org  # True or false
export_all_outfile = args.export_all_outfile
if export_all_outfile is not False:  # Create file naming if export_all option is present
    export_all_outfile = '{} - Export Master DB'.format(filename_prepend)
    # search_tag = args.search_tag  # Get the search tag if the option is given in conjunction with -eA
export_outfile = args.export_outfile
if export_outfile is not False:  # Create file naming if export option is present
    export_outfile = '{} - Export Current Query'.format(filename_prepend)
process = args.process
search_tag = args.search_tag
internal_tld_file = args.itld
external_tld_file = args.etld

# if the task is to process domains stored in the sqlite database
if process is not None:
    logger.debug('Created dataframe from the database\n')
    dataframe = create_dataframe_from_sql(engine=engine, tablename='certsmaster')
    if search_tag is not None:
        logger.info('Detected tag :"{}"'.format(search_tag))
        selected_dataframe = dataframe[dataframe['search_tag'].str.contains(r'\b{}\b'.format(search_tag))]
        # once dataframe is selected with rows containing tag, send it as input to filter_domain to do filtering and
        # get only external TLDs
        if selected_dataframe.empty:
            logger.warning('No records with the given search tag!!')
            sys.exit('Exiting!')
        else:
            logger.info('Processing only selected data from backend database, based on "{}" tag\n'.format(search_tag))
            logger.debug('Passing dataframe to filter_domains\n')
            external_tld_df = filter_domains(internal_tld_file=internal_tld_file, external_tld_file=external_tld_file,
                                             dataframe=selected_dataframe)
    else: # original dataframe containing all rows goes for processing
        # once dataframe is created from Sqlite database, send it as input to filter_domain to do filtering and get only
        # external TLDs
        logger.info('Processing all data from backend database\n')
        logger.debug('Passing dataframe to filter_domains\n')
        external_tld_df = filter_domains(internal_tld_file=internal_tld_file, external_tld_file=external_tld_file,
                                         dataframe=dataframe)
    logger.info('Proceeding to resolve IP address/ CNAME for external domain\n')
    # Resolve the IP address and CNAME for each external domain filtered INPUT: External TLD dataframe
    ns_dataframe = resolve_domains(external_tld_df)
    logger.info('Exporting the DNS results to an excel {} - {}\n'.format(filename_prepend, 'NS_Results'))
    export_to_excel(ns_dataframe, '{} - NS_Results'.format(filename_prepend))

# if the task is to update sqlite database with domain list or individual domain or export the contents of database
else:  # The request is not to process but update databases from CRT.SH i.e. process arg not given
    if input_domain_flag is not False:
        sys.exit('Not recommended, will be phased out soon! Sorry! \nExiting!!')
        # TODO: check if valid domain names are given i.e. look for domain patterns in input and not just words
        if input_file is not None:
            logger.debug('Input file detected')
            with open(input_file, 'r') as file:
                logger.debug('Opened input file {}'.format(input_file))
                i = 1
                for item in file.readlines():
                    domain = item.rstrip()
                    logger.info('Processing client number {} : {}\n'.format(i, domain))
                    get_cert_by_domain_name(domain=domain, export_outfile=export_outfile)
                    i += 1
        if input_phrase is not None:
            logger.debug('Input domain detected')
            domain = input_phrase.rstrip()
            logger.info('Processing {}\n'.format(domain))
            get_cert_by_domain_name(domain=domain, export_outfile=export_outfile)

        if export_all_outfile is not False:
            logger.debug('Export all option detected. Proceeding to export entire database into excel')
            export_db_to_excel(engine=engine, tablename='certsmaster', outfile=export_all_outfile,
                               search_tag=search_tag)
    if input_org_flag is not False:
        if input_file is not None: # TODO: Do the same CertsMaster database update as in input_phrase section
            logger.debug('Input file detected')
            with open(input_file, 'r') as file:
                logger.debug('Opened input file {}'.format(input_file))
                i = 1
                for item in file.readlines():
                    org_name = item.rstrip()
                    logger.info('Processing client number {} : {}\n'.format(i, org_name))
                    certs_ref_df = get_cert_ids_by_org(org_name=org_name, output_type='json', export_outfile=export_outfile)
                    i += 1
        if input_phrase is not None:
            logger.debug('Input domain detected')
            org_name = input_phrase.rstrip()
            logger.info('Processing {}\n'.format(org_name))
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
            certs_ref_df = get_cert_ids_by_org(org_name=org_name, output_type='json', export_outfile=export_outfile)  # Returns a dataframe of output

        # If Dataframe is empty, exit
        if certs_ref_df.empty:
            logger.info('No results returned.')
            sys.exit('Exiting')
        
        # If Dataframe is not empty, first get the domains from the certs pages and update CertsMaster table
        uniq_certsh_id_list = certs_ref_df['crtsh_id'].unique()
        logger.info('Identified {} unique "crtsh ids" for resolving...\n'.format(len(uniq_certsh_id_list)))
        logger.info('Identified {} rows in certs_ref_df dataframe...\n'.format(certs_ref_df.shape[0]))
        if not len(uniq_certsh_id_list) == (certs_ref_df.shape[0]):
            sys.exit('Error! Some issue count of unique crtsh ids are not same as number of rows in certs_ref dataframe')
        logger.info('Sanity check done, continuing ....\n')
        domains_list = []
        count = 1
        logger.debug('Connecting to database')
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        logger.debug('Session to database is established')
        for index, row in certs_ref_df.iterrows():
            crtsh_id = row['crtsh_id']
            logger.info('{}. Getting domains from the certificate "{}"'.format(count, crtsh_id))
            # TODO: Threading of these calls
            domains = get_domains_from_cert_ids(crtsh_id) # Returns list of domains from the certsh html pages
            if len(domains) >0:
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
                    logger.debug('Adding entry to database: {} - {}'.format(cert_entry.issuer_ca_id, cert_entry.domain_name))
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
            export_to_excel(dataframe=temp_certsmaster_df, outfile=file_name)

        logger.info('\nFinished all cert entries...\n')
        logger.info('identified {} domains from all cert entries...\n'.format(len(domains_list)))
        logger.debug('identified {} domains from all cert entries...\n{}'.format(len(domains_list), domains_list))
        logger.debug('Removing duplicates...')
        unique_domains_list = list(dict.fromkeys(domains_list))
        logger.debug('There are {} unique domains from all cert entries...\n{}'.format(len(unique_domains_list), unique_domains_list))
        logger.info('There are {} unique domains from all cert entries...\n'.format(len(unique_domains_list)))
        logger.info('Refer the CertsMaster database for the extracted domains and cert ids!')
# TODO: Export the domains result, currently on the org table with cert is exported
        if export_all_outfile is not False:
            logger.debug('Export all option detected. Proceeding to export entire database into excel')
            export_db_to_excel(engine=engine, tablename='orgscertsrefsmaster', outfile=export_all_outfile,
                               search_tag=search_tag)

    # Print help if all arguments are none
    if input_file is None and export_all_outfile is False and input_phrase is None:
        logger.info('No arguments given. Printing default help\n')
        parser.print_help()  # Prints help if not argument is given to arg parse

logger.info('Cert Stash has finished processing...')
logger.info('Done!\n')
