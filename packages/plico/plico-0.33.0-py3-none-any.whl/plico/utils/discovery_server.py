import json
import time
import socket
import logging
from dataclasses import dataclass, fields

DISCOVER_PORT = 9999
DISCOVER_COMMAND = 'DISCOVER'
BROADCAST_IP = '255.255.255.255'

@dataclass
class LocalServerInfo():
    '''Description of a plico server running locally'''
    name: str
    port: int
    server_type: str
    device_class: str


@dataclass
class ServerInfo():
    '''Description of a remote plico server'''
    name: str
    host: str
    port: int
    server_type: str
    device_class: str


class DiscoveryServer():
    '''UDP discovery server.'''
    def __init__(self, logger=None):
        self._data = None
        self._time_to_die = False
        if logger:
            self._logger = logger
        else:
            self._logger = logging.getLogger()

    def _myip(self):
        return socket.gethostbyname(socket.gethostname())

    def configure(self, local_server_info):
        '''Configure the information to be sent back to discover requests'''
        assert isinstance(local_server_info, LocalServerInfo), \
                    'server_info must be an instance of the LocalServerInfo dataclass'
        self._data = ServerInfo(host=self._myip(), **local_server_info.__dict__)

    def run(self):
        '''Loop serving discovery requests.

        This function is intended to be started as a
        separate thread. Use the self.die() method to stop.
        '''
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if hasattr(socket, 'SO_REUSEPORT'):
            # Linux
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        else:
            # Windows
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(False)
        sock.bind(('', DISCOVER_PORT))   # Listen for broadcasts
        while not self._time_to_die:
            try:
                data, addr = sock.recvfrom(1024)
                if DISCOVER_COMMAND in data.decode():
                    if not self._data:
                        # Server not configured yet, do not answer broadcast
                        continue
                    self._logger.info('Sending: %s', self._data)
                    sock.sendto(json.dumps(self._data.__dict__).encode(), addr)
            except BlockingIOError:
                time.sleep(1)
                continue
            except UnicodeDecodeError:
                # Random broadcasts sometimes cause decode() to raise this
                pass

    def die(self):
        '''Stop the server loop (if started in a different thread)'''
        self._time_to_die = True


class DiscoveryClient():
    '''UDP discovery client'''

    def __init__(self, logger=None):
        if logger:
            self._logger = logger
        else:
            self._logger = logging.getLogger()

    def run(self, name=None, timeout_in_seconds=2, filter={}):
        '''
        Broadcast a discovery request and wait for server replies
        for up to <timeout_in_seconds>. If *name* is set,
        will return the server info for that specific name, otherwise
        it will return a list of discovered servers.
        Each server info is a ServerInfo instance.
        Will raise a TimeoutError if no servers answer, or if
        no server with the specified name answers.
        '''
        allowed_filters = [x.name for x in fields(ServerInfo)]
        for k in filter:
            if not k in allowed_filters:
                raise ValueError(f'Invalid filter keyword {k}')

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(timeout_in_seconds)

        message = DISCOVER_COMMAND
        sock.sendto(message.encode(), (BROADCAST_IP, DISCOVER_PORT))

        # Collect responses from servers
        discovered_servers = []
        start_time = time.time()

        while True:
            try:
                data, addr = sock.recvfrom(1024)
                server_info = ServerInfo(**json.loads(data.decode()))
                if not all(getattr(server_info, k) == v for k, v in filter.items()):
                    continue
                self._logger.info('Received: %s', server_info)
                discovered_servers.append(server_info)
                if name is not None:
                    if server_info.name == name:
                        return server_info
            except socket.timeout:
                pass
            if time.time() - start_time > timeout_in_seconds:
                if name is None:
                    if len(discovered_servers) > 0:
                        return discovered_servers
                    else:
                        raise TimeoutError('No servers found')
                else:
                    raise TimeoutError(f'No server with name {name} found')
