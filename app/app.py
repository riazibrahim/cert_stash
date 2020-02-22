from app import args, logger, engine, parser
from app.utilities import export_db_to_excel
from app.get_certs import get_cert
import os
import sys

# Gather all arguments
logger.debug('Obtaining all arguments')
input_file = args.file
input_domain = args.domain
export_all_outfile = args.export_all_outfile
export_outfile = args.export_outfile

if os.path.exists('outputs/{}.xlsx'.format(export_outfile)):
    logger.info('The output file {}.xlsx already exists'.format(export_outfile))
    print('Message: Please provide a different output file name')
    sys.exit('Finished!')

if os.path.exists('outputs/{}.xlsx'.format(export_all_outfile)):
    logger.info('The output file {}.xlsx already exists'.format(export_all_outfile))
    print('Message: Please provide a different output file name')
    sys.exit('Finished!')

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

if export_all_outfile is not None:
    logger.debug('Export all option detected. Proceeding to export entire database into excel')
    export_db_to_excel(engine=engine, tablename='certsmaster', outfile=export_all_outfile)

# Print help if all arguments are none
if input_file is None and export_all_outfile is None and input_domain is None:
    logger.debug('No arguments given. Printing default help')
    parser.print_help()  # Prints help if not argument is given to arg parse

logger.debug('Collision has finished processing.')
logger.info('Done!')
