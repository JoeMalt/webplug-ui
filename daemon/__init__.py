import socket

from core.orm_template import db_host, db_plugSocket
from core import get_db_session


def msg_worker(command, host_id, plug_id):
    message = bytes(command + str(plug_id), 'UTF-8')

    db_session = get_db_session()
    try:
        query = db_session.query(db_plugSocket, db_host).filter(db_plugSocket.host_id == host_id, db_plugSocket.plug_id == plug_id).join(db_host).first()
        ip_address = query.db_host.ip_address
        port = query.db_host.port
    finally:
        db_session.close

    print('Creating socket.')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Connecting to worker - {} {}'.format(ip_address, port))
    s.connect((ip_address, port))
    print('Sending message.')
    s.send(message)
    print('Waiting for message.')
    returned = s.recv(1)
    print(returned)
    print('Closing socket.')
    s.close()
