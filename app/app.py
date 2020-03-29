from app import logger, engine, parser
from app.utilities import export_db_to_excel, create_dataframe_from_sql, resolve_domains, export_to_excel, \
    check_valid_domain_name
from app.get_certs import get_cert_ids_by_org, parse_domains_and_update_certsmasterdb, get_cert_by_domain_name
from app.filter import filter_domains
import sys
from app.globalvars import filename_prepend, input_file, input_phrase, input_domain_flag, input_org_flag, \
    export_all_outfile, export_outfile, process, search_tag, internal_tld_file, external_tld_file, output_type

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
    else:  # original dataframe containing all rows goes for processing
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
        # sys.exit('Not recommended, will be phased out soon! Sorry! \nExiting!!')
        if input_file is not None:
            logger.debug('Input file detected')
            with open(input_file, 'r') as file:
                logger.debug('Opened input file {}'.format(input_file))
                i = 1
                for item in file.readlines():
                    domain = item.rstrip()
                    logger.info('\n************************************************************\n'
                                'Processing client number {} : {}\n'
                                '************************************************************\n'.format(i, domain))
                    if check_valid_domain_name(domain):
                        get_cert_by_domain_name(domain=domain)
                    i += 1
        if input_phrase is not None:
            logger.debug('Input domain detected')
            domain = input_phrase.rstrip()
            logger.info('Processing {}\n'.format(domain))
            if check_valid_domain_name(domain):
                get_cert_by_domain_name(domain=domain)

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
                    logger.info('\n\n************************************************************\n'
                                'Processing client number {} : {}\n'
                                '************************************************************\n'.format(i, org_name))
                    certs_ref_df = get_cert_ids_by_org(org_name=org_name)
                    parse_domains_and_update_certsmasterdb(certs_ref_df=certs_ref_df, org_name=org_name)
                    i += 1
        if input_phrase is not None:
            logger.debug('Input domain detected')
            org_name = input_phrase.rstrip()
            logger.info('Processing {}\n'.format(org_name))
            certs_ref_df = get_cert_ids_by_org(org_name=org_name)  # Returns a dataframe of output

            parse_domains_and_update_certsmasterdb(certs_ref_df=certs_ref_df, org_name=org_name)

        if export_all_outfile is not False:
            logger.debug(
                'Export all option detected. Proceeding to export entire certsmaster table in database into excel')
            export_db_to_excel(engine=engine, tablename='certsmaster', outfile=export_all_outfile,
                               search_tag=search_tag)
    # i.e. if only -eA is given as option
    if export_all_outfile is not False:
        logger.debug('Export all option detected. Proceeding to export entire certsmaster table in database into excel')
        export_db_to_excel(engine=engine, tablename='certsmaster', outfile=export_all_outfile)

    # Print help if all arguments are none
    if input_file is None and export_all_outfile is False and input_phrase is None:
        logger.info('No arguments given. Printing default help\n')
        parser.print_help()  # Prints help if not argument is given to arg parse

logger.info('Cert Stash has finished processing...')
logger.info('Done!\n')
