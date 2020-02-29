from app import logger, parser
import pandas as pd
import sys


# Takes a dataframe containing cert.sh data, exernal domains list and internal domains list as input. Outputs domains
# into exernal, internal and excluded. Returns external domains in a dataframe
def filter_domains(internal_tld_file, external_tld_file, dataframe):
    logger.info('Internal TLD  file is {} \n'.format(internal_tld_file))
    logger.info('External TLD  file is {} \n'.format(external_tld_file))
    if internal_tld_file is None or external_tld_file is None:  # Exit if input tld files are not given for --process option
        logger.warning('\nPlease give "itld" and "etld" arguments. Printing default help\n')
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
        logger.info('Generating external domains report')
        external_tld_df.to_excel('outputs/{}.xlsx'.format('016_External_Domains_Entries'))

        # Finding all the non selected ones by comparing selected dataframe with original dataframe and dumping to an
        # excel
        excluded_df = pd.concat([dataframe, external_tld_df]).drop_duplicates(keep=False)
        logger.debug('The excluded df is :')
        logger.debug(excluded_df['name_value'])
        logger.info('Generating removed entries report')
        excluded_df.to_excel('outputs/{}.xlsx'.format('016_Removed_Entries'))

        # From the excluded_df (which contains both valid internal domains as well as non domain text,
        # extract internal domains
        with open(internal_tld_file, 'r') as file:
            logger.debug('Opened external TLD file {}'.format(external_tld_file))
            for item in file.readlines():
                itld = item.rstrip().lower()
                logger.debug('\nPrinting selected dataframe .. {}'.format(itld))
                df = excluded_df[excluded_df['name_value'].str.lower().str.endswith('.{}'.format(itld))]
                logger.debug(df['name_value'])
                internal_tld_df = internal_tld_df.append(df)

        logger.debug('The internal domains df is :')
        logger.debug(internal_tld_df['name_value'])
        logger.info('Generating internal domains report')
        internal_tld_df.to_excel('outputs/{}.xlsx'.format('016_Internal_Domains_Entries'))
    return external_tld_df
