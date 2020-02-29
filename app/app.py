from app import args, logger, engine, parser
from app.utilities import export_db_to_excel, create_dataframe_from_sql, resolve_domains, export_to_excel
from app.get_certs import get_cert
from app.filter import filter_domains
from datetime import datetime

filename_prepend = datetime.now().strftime("%Y%m%d-%H%M%S")

# Gather all arguments
logger.debug('Obtaining all arguments')
input_file = args.file
input_domain = args.domain
export_all_outfile = args.export_all_outfile
if export_all_outfile is not False:
    export_all_outfile = '{} - Export Master DB'.format(filename_prepend)
export_outfile = args.export_outfile
if export_outfile is not False:
    export_outfile = '{} - Export Current Query'.format(filename_prepend)
process = args.process
internal_tld_file = args.itld
external_tld_file = args.etld

# if the task is to process domains stored in the sqlite database
if process is not None:
    logger.info('\nCreated dataframe from the database')
    dataframe = create_dataframe_from_sql(engine=engine, tablename='certsmaster')
    # once dataframe is created from Sqlite database, send it as input to filter_domain to do filtering and get only external TLDs
    logger.info('\nPassing dataframe to filter_domains')
    external_tld_df = filter_domains(internal_tld_file=internal_tld_file, external_tld_file=external_tld_file, dataframe=dataframe)
    logger.info('\nProceeding to resolve IP address/ CNAME for external domain')
    # Resolve the IP address and CNAME for each external domain filtered INPUT: External TLD dataframe
    ns_dataframe = resolve_domains(external_tld_df)
    logger.info('\nExporting the resolution results to an excel {}'.format('01_NS_Results'))
    export_to_excel(ns_dataframe, '01_NS_Results')

# if the task is to update sqlite database with client queries or export the contents of database
else:
    if input_file is not None:
        logger.debug('Input file detected')
        with open(input_file, 'r') as file:
            logger.debug('Opened input file {}'.format(input_file))
            i = 1
            for item in file.readlines():
                domain = item.rstrip()
                logger.info('Processing client number {} : {}'.format(i, domain))
                get_cert(domain=domain, export_outfile=export_outfile)
                i += 1
    elif input_domain is not None:
        logger.debug('Input domain detected')
        domain = input_domain.rstrip()
        logger.info('Processing {}'.format(domain))
        get_cert(domain=domain, export_outfile=export_outfile)

    if export_all_outfile is not False:
        logger.debug('Export all option detected. Proceeding to export entire database into excel')
        export_db_to_excel(engine=engine, tablename='certsmaster', outfile=export_all_outfile)

    # Print help if all arguments are none
    if input_file is None and export_all_outfile is False and input_domain is None:
        logger.info('No arguments given. Printing default help')
        parser.print_help()  # Prints help if not argument is given to arg parse

logger.debug('Collision has finished processing.')
logger.info('Done!')
