
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class user(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    pwd_hash = Column(String)

    def __repr__(self):
        return "<User(name='%s', fullname='%s', password='%s')>" % (self.name, self.fullname, self.password)


class host(Base):
    __tablename__ = 'hosts'

    id = Column(Integer, primary_key=True)
    ip_address = Column(String)
    port = Column(String)


class plugSocket(Base):
    __tablename__ = 'plug_sockets'

    id = Column(Integer, primary_key=True)
    host_id = Column(String, ForeignKey("hosts.id"))
    plug_id = Column(String)
    name = Column(String)
    status = Column(Integer)

if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('sqlite:///webplug.db')

    Session = sessionmaker(bind=engine)
    db_session = Session()
    Base.metadata.create_all(engine)
