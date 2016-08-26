import sys
from scheduling_daemon import webplug_daemon

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
