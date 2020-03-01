from app import logger, parser
from datetime import datetime
import pandas as pd
import sys

filename_prepend = datetime.now().strftime("%Y%m%d-%H%M%S")


# Takes a dataframe containing cert.sh data, external domains list and internal domains list as input. Outputs domains
# into exernal, internal and excluded. Returns external domains in a dataframe
def filter_domains(internal_tld_file, external_tld_file, dataframe):
    logger.info('Internal TLD  file is {} \n'.format(internal_tld_file))
    logger.info('External TLD  file is {} \n'.format(external_tld_file))
    if internal_tld_file is None or external_tld_file is None:  # Exit if input tld files are not given for --process
        # option
        logger.warning('Please give "itld" and "etld" arguments. Printing default help\n')
        parser.print_help()  # Prints help if not argument is given to arg parse
        sys.exit()
    else:
        #  Creating dataframe models for temporary use
        external_tld_df = pd.DataFrame(
            columns=['issuer_ca_id', 'issuer_name', 'name_value', 'crtsh_id', 'entry_timestamp', 'not_before',
                     'not_after'])
        excluded_df = pd.DataFrame(
            columns=['issuer_ca_id', 'issuer_name', 'name_value', 'crtsh_id', 'entry_timestamp', 'not_before',
                     'not_after'])
        internal_tld_df = pd.DataFrame(
            columns=['issuer_ca_id', 'issuer_name', 'name_value', 'crtsh_id', 'entry_timestamp', 'not_before',
                     'not_after'])

        # fill external_tld_df dataframe with selected rows based on each TLD in domain list
        with open(external_tld_file, 'r') as file:
            logger.debug('Opened external TLD file {}'.format(external_tld_file))
            for item in file.readlines():
                etld = item.rstrip().lower()
                logger.debug('\nPrinting selected dataframe .. .{}'.format(etld))
                df = dataframe[dataframe['name_value'].str.lower().str.endswith('.{}'.format(etld))]
                logger.debug(df['name_value'])
                external_tld_df = external_tld_df.append(df)
        logger.debug('The included df is :')
        logger.debug(external_tld_df)
        filename_external_domains = '{} - {}.xlsx'.format(filename_prepend, 'External_Domains_Entries')
        logger.info('Generating external domains report "{}" in outputs folder\n'.format(filename_external_domains))
        external_tld_df.to_excel('outputs/{}.xlsx'.format(filename_external_domains))

        # Finding all the non selected ones by comparing selected dataframe with original dataframe and dumping to an
        # excel
        excluded_df = pd.concat([dataframe, external_tld_df]).drop_duplicates(keep=False)
        logger.debug('The excluded df is :')
        logger.debug(excluded_df['name_value'])
        filename_removed_items = '{} - {}'.format(filename_prepend, 'Removed_Entries')
        logger.info('Generating removed entries report "{}" in outputs folder\n'.format(filename_removed_items))
        excluded_df.to_excel('outputs/{}.xlsx'.format(filename_removed_items))

        # From the excluded_df (which contains both valid internal domains as well as non domain text,
        # extract internal domains
        with open(internal_tld_file, 'r') as file:
            logger.debug('Opened internal TLD file {}\n'.format(internal_tld_file))
            for item in file.readlines():
                itld = item.rstrip().lower()
                logger.debug('Printing selected dataframe .. {}\n'.format(itld))
                df = excluded_df[excluded_df['name_value'].str.lower().str.endswith('.{}'.format(itld))]
                logger.debug(df['name_value'])
                internal_tld_df = internal_tld_df.append(df)

        logger.debug('The internal domains df is :')
        logger.debug(internal_tld_df['name_value'])
        filename_internal_domains = '{} - {}.xlsx'.format(filename_prepend, 'Internal_Domains_Entries')
        logger.info('Generating internal domains report "{}" in outputs folder\n'.format(filename_internal_domains))
        internal_tld_df.to_excel('outputs/{}.xlsx'.format(filename_internal_domains))
    return external_tld_df
