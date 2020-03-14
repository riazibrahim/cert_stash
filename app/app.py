from app import args, logger, engine, parser
from app.utilities import export_db_to_excel, create_dataframe_from_sql, resolve_domains, export_to_excel
from app.get_certs import get_cert_refs_by_org, get_cert_by_domain_name, get_domains_by_cert_ref
from app.filter import filter_domains
from datetime import datetime
import sys

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
        if input_file is not None:
            logger.debug('Input file detected')
            with open(input_file, 'r') as file:
                logger.debug('Opened input file {}'.format(input_file))
                i = 1
                for item in file.readlines():
                    org_name = item.rstrip()
                    logger.info('Processing client number {} : {}\n'.format(i, org_name))
                    get_cert_refs_by_org(org_name=org_name, export_outfile=export_outfile)
                    i += 1
        if input_phrase is not None:
            logger.debug('Input domain detected')
            org_name = input_phrase.rstrip()
            logger.info('Processing {}\n'.format(org_name))
            certs_ref_df = get_cert_refs_by_org(org_name=org_name, output_type='json', export_outfile=export_outfile)  # Returns a dataframe of output
            ''' 
                Dataframe format:
                dataframe = pd.DataFrame(
                    columns=[
                        'issuer_ca_id', 
                        'issuer_name', 
                        'org_name', 
                        'crtsh_id', 
                        'entry_timestamp', 
                        'not_before', 
                        'not_after', 
                        'search_tag'])
            '''
            if certs_ref_df.empty:
                logger.info('No results returned.')
                sys.exit('Exiting')
            
            # If Dataframe is not empty, Dataframe to update CertsMaster table
            uniq_certsh_id_list = certs_ref_df['crtsh_id'].unique()
            logger.info(
                'Identified {} unique "crtsh ids" for resolving...\n'.format(len(uniq_certsh_id_list)))
            for crtsh_id in uniq_certsh_id_list:
                get_domains_by_cert_ref(crtsh_id)


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
