from ckan import model
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base(metadata=model.meta.metadata)

session = Session()
