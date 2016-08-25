def get_db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('sqlite:///web/webplug.db')
    Session = sessionmaker(bind=engine)
    db_session = Session()

    return db_session