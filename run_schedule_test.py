import datetime
from core.orm_template import db_scheduleRule, db_plugSocket
from core import msg_worker


def run_schedule(last_run_time):
    current_time = datetime.datetime.now().time()
    # get the time of the last run of this program from the file
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('sqlite:////home/pi/webplug-ui/web/webplug.db')
    Session = sessionmaker(bind=engine)
    db_session = Session()

    try:
        jobs_switch_on = db_session.query(db_scheduleRule, db_plugSocket).join(db_plugSocket).filter(db_scheduleRule.on_time <= current_time,
                                                                  db_scheduleRule.on_time >= last_run_time).all()
        jobs_switch_off = db_session.query(db_scheduleRule, db_plugSocket).join(db_plugSocket).filter(db_scheduleRule.off_time <= current_time,
                                                                   db_scheduleRule.off_time >= last_run_time).all()
        jobs_switch_on = db_session.query(db_scheduleRule, db_plugSocket).join(db_plugSocket).all()
        jobs_switch_off = db_session.query(db_scheduleRule, db_plugSocket).join(db_plugSocket).all()
        print(jobs_switch_on)
        print(jobs_switch_off)

    finally:
        db_session.close()

    for job in jobs_switch_off:
        msg_worker('F', 2, 1)
        print("Switching off" + job.device_id)

    for job in jobs_switch_on:
        msg_worker('N', 2, 1)
        print("Switching on" + job.device_id)

run_schedule(datetime.datetime.now().time())