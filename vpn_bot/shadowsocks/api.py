import socket
import random


socket.setdefaulttimeout(2)


class ServiceOpenException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


def get_sock():
    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    rand_file_name = '/tmp/vpn_bot' + \
        (''.join([chr(65+random.randint(0,25)) for _ in range(16)])) + \
        '.sock'
    s.bind(rand_file_name)
    s.connect('/run/shadowsocks-manager.sock')
    return s

def send_data(sock):
    pass

def ping():
    pass

def open_port(port, password):
    s = get_sock()
    try:
        i = int(password)
    except:
        raise ServiceOpenException('invalid password ' + password)
    data = 'add: {"server_port":%s,"password":"%s"}'\
        % (port, password)
    data = bytearray(data.encode('ascii'))
    s.send(data)
    response = s.recv(1024)
    s.close()
    if response != b'ok':
        return None
    return True


def close_port(port):
    s = get_sock()
    data = 'remove: {"server_port":%s}' % (port)
    data = bytearray(data.encode('ascii'))
    s.send(data)
    response = s.recv(1024)
    s.close()
    if response != b'ok':
        return None
    return True


def open_services():
    port = str(random.randint(50000,60000))
    password = ''.join([str(random.randint(0,9)) for _ in range(6)])
    count = 5
    while (not open_port(port,password)) and count > 0:
        port = str(random.randint(50000,60000))
        count -= 1
    if count == 0:
        raise ServiceOpenException('port cannot be opened')
    return (port, password)



def close_services(ports):
    if type(ports) == int or type(ports) == str:
        ports = [ports]
    for port in ports:
        close_port(port)