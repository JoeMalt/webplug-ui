import socket

def msg_daemon(command):
    message = bytes(command, 'UTF-8')
    ip_address = '127.0.0.1'
    port = 3126
    print('Creating socket.')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Connecting to worker - {} {}'.format(ip_address, port))
    s.connect((ip_address, port))
    print('Sending message.')
    s.send(message)
    print('Waiting for message.')
    returned = s.recv(1024)
    print(returned)
    print('Closing socket.')
    s.close()


msg_daemon("test")
