import pandas as pd
from app import logger, args
import os



# Use pandas to connect to the database given in argument
def export_db_to_excel(engine, tablename, outfile):
    logger.debug('Reading {} table from database {} into pandas dataframe'.format(tablename, engine))
    db_dataframe = pd.read_sql_table(table_name=tablename, con=engine)
    logger.debug('Read to dataframe from database into pandas')
    if not os.path.exists('outputs'):
        os.mkdir('outputs')
    logger.info('Generating output in excel format')
    db_dataframe.to_excel('outputs/{}.xlsx'.format(outfile))
    logger.info('Generated {}.xlsx in outputs folder'.format(outfile))


def create_dataframe_from_sql(engine, tablename):
    logger.debug('Reading {} table from database {} into pandas dataframe'.format(tablename, engine))
    db_dataframe = pd.read_sql_table(table_name=tablename, con=engine)
    logger.debug('Read to dataframe from database into pandas')
    return db_dataframe


def export_to_excel(dataframe, outfile):
    logger.debug('Checking if dataframe is None')
    if len(dataframe) > 0:  # Check if dataframe has any data in it
        if not os.path.exists('outputs'):
            os.mkdir('outputs')
        dataframe.to_excel('outputs/{}.xlsx'.format(outfile))
        logger.info('Generated {}.xlsx in outputs folder'.format(outfile))
