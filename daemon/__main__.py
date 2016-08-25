import logging
from logging.handlers import SysLogHandler
import time

import select

from service import find_syslog, Service


class webplug_daemon(Service):
    def __init__(self, *args, **kwargs):
        super(webplug_daemon, self).__init__(*args, **kwargs)
        self.logger.addHandler(SysLogHandler(address=find_syslog(),
                                             facility=SysLogHandler.LOG_DAEMON))
        self.logger.setLevel(logging.INFO)

    def run(self):
        """
        # Create the server socket for receiving commands from the web interface.
        s = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 3126))
        # become a server socket
        s.listen(5)

        try:
            while not self.got_sigterm():
                ready_to_read, ready_to_write, in_error = \
                    select.select(
                        [s],
                        [],
                        [],
                        10)

                for socket in ready_to_read:
                    returned = socket.recv(1024)

                self.logger.warn(returned)

                self.logger.info("I'm working...")
                time.sleep(5)
        finally:
            s.close()
        """
        while not self.got_sigterm():
            self.logger.info("I'm working...")
            time.sleep(5)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        sys.exit('Syntax: %s COMMAND' % sys.argv[0])

    cmd = sys.argv[1].lower()
    service = webplug_daemon('webplug_daemon', pid_dir='/tmp')

    if cmd == 'start':
        service.start()
    elif cmd == 'stop':
        service.stop()
    elif cmd == 'status':
        if service.is_running():
            print("Service is running.")
        else:
            print("Service is not running.")
    else:
        sys.exit('Unknown command "%s".' % cmd)