from sqlalchemy import Column, Integer, String, ForeignKey, Time
from sqlalchemy.ext.declarative import declarative_base
from passlib.apps import custom_app_context as pwd_context

Base = declarative_base()


class db_user(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    pwd_hash = Column(String)
    is_admin = Column(Integer, default=0)

    def __repr__(self):
        return "<User(username='%s', pwd_hash='%s')>" % (self.username, self.pwd_hash)


class db_host(Base):
    __tablename__ = 'hosts'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    ip_address = Column(String)
    port = Column(Integer)

    def __repr__(self):
        return "<Host(name='%s', ip_address='%s', port='%s')>" % (self.name, self.ip_address, self.port)


class db_plugSocket(Base):
    __tablename__ = 'plug_sockets'

    id = Column(Integer, primary_key=True)
    host_id = Column(String, ForeignKey("hosts.id"))
    plug_id = Column(String)
    name = Column(String)
    status = Column(Integer)

    def __repr__(self):
        return "<Plug Socket(host_id='%s', plug_id='%s', name='%s', status='%s')>" % (self.host_id, self.plug_id, self.name, self.status)

class db_scheduleRule(Base):
    __tablename__ = "schedule_rules"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("plug_sockets.id"))
    on_time = Column(Time)
    off_time = Column(Time)
    days = Column(String)


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('sqlite:///../web/webplug.db')

    Base.metadata.create_all(engine)

    # add_test_user()

    Session = sessionmaker(bind=engine)
    db_session = Session()

    pwd_hash = pwd_context.encrypt("asdf1234")

    print(db_session.query(db_user).filter(db_user.username == "test").first())
    db_session.close()
