from core.orm_template import db_user, db_host, db_plugSocket, db_scheduleRule
from core import get_db_session, msg_worker

from datetime import datetime, time


def run_schedule():
    current_time = datetime.datetime.now().time()
    
    #get the time of the last run of this program from the file
        
    db_session = get_db_session()
    try:
        jobs_switch_on = db_session.query(db_scheduleRule).filter(db_scheduleRule.on_time <= current_time, db_scheduleRule.on_time >= last_run_time)
        jobs_switch_off = db_session.query(db_scheduleRule).filter(db_scheduleRule.off_time <= current_time, db_scheduleRule.off_time >= last_run_time)
        
        print(jobs_switch_on)
        print(jobs_switch_off)
    
    finally:
        db_session.close()
        
        
    for job in jobs_switch_off:
        #TODO: make this do something
        print("Switching off" + job.device_id)
    
    for job in jobs_switch_on:
        #TODO: make this do something
        print("Switching on" + job.device_id)

        
    #write the current time to last_run_time
    global last_run_time = current_time
    
