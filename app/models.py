from sqlalchemy import Column, Integer, String
from config import Config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class CertsMaster(Base):
    """Data model example."""
    __tablename__ = 'certsmaster'
    # __table_args__ = {'schema': 'certsmaster'}

    id = Column(Integer, primary_key=True, nullable=False)
    issuer_ca_id = Column(Integer, index=True)
    issuer_name = Column(String(500), index=True)
    crtsh_id = Column(Integer, index=True)
    domain_name = Column(String(500), index=True)
    entry_timestamp = Column(String(100))
    not_before = Column(String(100))
    not_after = Column(String(100))
    search_tag = Column(String(100))

    def __repr__(self):
        return 'This is the row id: {} , crtsh_id: {}, name_value: {}'.format(self.id, self.crtsh_id, self.name_value)


# table for storing interim cert id data when organization name is given. This table is later used to find out domains per cert id and update master
class OrgsCertsRefsMaster(Base):
    """Data model example."""
    __tablename__ = 'orgscertsrefsmaster'
    # __table_args__ = {'schema': 'orgscertsrefsmaster'}

    id = Column(Integer, primary_key=True, nullable=False)
    issuer_ca_id = Column(Integer, index=True)
    issuer_name = Column(String(500), index=True)
    crtsh_id = Column(Integer, index=True)
    org_name = Column(String(500), index=True)
    entry_timestamp = Column(String(100))
    not_before = Column(String(100))
    not_after = Column(String(100))
    search_tag = Column(String(100))

    def __repr__(self):
        return 'This is the row id: {} , crtsh_id: {}, name_value: {}'.format(self.id, self.crtsh_id, self.name_value)
