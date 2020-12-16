from app import parser, logger, args
from datetime import datetime


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
output_type = 'json'
