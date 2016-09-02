import logging
from logging.handlers import SysLogHandler

import select
import datetime

from service import find_syslog, Service

from core.orm_template import db_scheduleRule, db_plugSocket
from core import get_db_session, msg_worker


class webplug_daemon(Service):
    def __init__(self, *args, **kwargs):
        super(webplug_daemon, self).__init__(*args, **kwargs)
        self.logger.addHandler(SysLogHandler(address=find_syslog(),
                                             facility=SysLogHandler.LOG_DAEMON))
        self.logger.setLevel(logging.INFO)

    def run(self):
        import socket
        # Create the server socket for receiving commands from the web interface.
        s = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 3126))
        # become a server socket
        s.listen(5)

        try:
            # Set the last schedule run time to now so that the first time round it won't run anything.
            last_schedule_run_time = datetime.datetime.now().time()
            while not self.got_sigterm():
                ready_to_read, ready_to_write, in_error = \
                    select.select(
                        [s],
                        [],
                        [],
                        10)

                for socket in ready_to_read:
                    conn, addr = socket.accept()
                    returned = conn.recv(1024)
                    self.logger.warn(returned)
                    conn.send(bytes("Confirmed", 'UTF-8'))
                    conn.close()

                run_schedule(last_schedule_run_time, self.logger)
                last_schedule_run_time = datetime.datetime.now().time()

                self.logger.info("I'm working...")
        finally:
            s.close()


def run_schedule(last_run_time, logger):
    current_time = datetime.datetime.now().time()
    db_session = get_db_session()

    try:
        jobs_switch_on = db_session.query(db_scheduleRule.on_time, db_plugSocket.host_id, db_plugSocket.plug_id).join(
            db_plugSocket).filter(
            db_scheduleRule.on_time <= current_time,
            db_scheduleRule.on_time >= last_run_time).all()
        jobs_switch_off = db_session.query(db_scheduleRule.on_time, db_plugSocket.host_id, db_plugSocket.plug_id).join(
            db_plugSocket).filter(
            db_scheduleRule.off_time <= current_time,
            db_scheduleRule.off_time >= last_run_time).all()

        logger.warn('Switching on: ' + str(jobs_switch_on))
        logger.warn('Switching off: ' + str(jobs_switch_off))

    finally:
        db_session.close()

    for job in jobs_switch_on:
        msg_worker('N', job.host_id, job.plug_id)
        print("Switching on plug " + job.plug_id + ' on host ' + job.host_id + '.')

    for job in jobs_switch_off:
        msg_worker('F', job.host_id, job.plug_id)
        print("Switching off plug " + job.plug_id + ' on host ' + job.host_id + '.')
