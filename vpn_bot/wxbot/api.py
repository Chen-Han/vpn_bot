# coding: utf-8

# provide socket api for other process to communicate with bot
import subprocess
import multiprocessing
import collections
import logging
from threading import Thread
SOCKET_FILE = '/run/vpn_bot.sock'
UNIX_SOCK = 'unix://'+SOCKET_FILE

Wechat_msg = collections.namedtuple('Wechat_message',['wechat_id','msg'])
# TODO, add authentication
class Bot_api(object):
    def __init__(self):
        self.client = multiprocessing.Client(UNIX_SOCK)

    def send_msg(self, wechat_id, msg):
        self.client.send(Wechat_msg(wechat_id,msg))

class Bot_server(object):
    '''
    listens for request from other processes and perform
    corresponding bot actions
    '''
    def __init__(self):
        # remove socket file so that new one can be created
        subprocess.run('rm ' + SOCKET_FILE)
        self.listener = multiprocessing.Listener(UNIX_SOCK)
        self.listening_thread = None

    def register_msg_handler(self, func):
        self._msg_handler = func

    def start_listening(self):
        self.listening_thread = Thread(target=self._conn_handler, args=(self))
        self.listening_thread.start()

    def _conn_handler(self):
        while True:
            conn = self.listener.accept()
            t = Thread(target=self._event_handler, args=(self, conn))
            t.start()

    def _event_handler(self, conn):
        while True:
            data = None
            try:
                data = conn.recv()
            except:
                logging.debug('connection closed', conn)
                return
            if type(data) == Wechat_msg:
                try:
                    self._msg_handler(data.wechat_id, data.msg)
                except:
                    logging.error(\
                        'Error handling wechat message send for'\
                        ' user {}, msg: {}'.format(data.wechat_id, data.msg))
            else:
                logging.error(
                    'Unexpected object received, wechat_msg expected', data)

