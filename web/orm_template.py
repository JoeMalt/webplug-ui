from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from passlib.apps import custom_app_context as pwd_context

Base = declarative_base()


class db_user(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    pwd_hash = Column(String)

    def __repr__(self):
        return "<User(username='%s', pwd_hash='%s')>" % (self.username, self.pwd_hash)


class db_host(Base):
    __tablename__ = 'hosts'

    id = Column(Integer, primary_key=True)
    ip_address = Column(String)
    port = Column(String)


class db_plugSocket(Base):
    __tablename__ = 'plug_sockets'

    id = Column(Integer, primary_key=True)
    host_id = Column(String, ForeignKey("hosts.id"))
    plug_id = Column(String)
    name = Column(String)
    status = Column(Integer)


def add_test_user():
    Session = sessionmaker(bind=engine)
    db_session = Session()

    pwd_hash = pwd_context.encrypt("asdf1234")

    new_user = db_user(username="test", pwd_hash=pwd_hash)
    db_session.add(new_user)
    db_session.commit()
    db_session.close()


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('sqlite:///webplug.db')

    Base.metadata.create_all(engine)

    # add_test_user()

    Session = sessionmaker(bind=engine)
    db_session = Session()

    pwd_hash = pwd_context.encrypt("asdf1234")

    print(db_session.query(db_user).filter(db_user.username == "test").first())
    db_session.close()
