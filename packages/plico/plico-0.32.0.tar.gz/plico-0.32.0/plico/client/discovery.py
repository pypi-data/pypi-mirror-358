'''
Utility functions for client discovery
'''

import importlib
from collections import namedtuple

ClientMapType = namedtuple('ClientType', 'modulename classname')


def plico_list(server_type, name=None, timeout_in_seconds=2):
    '''
    Return a list of servers matching a server_type
    and optionally a server_name
    '''
    from plico.utils.discovery_server import DiscoveryClient
    return DiscoveryClient().run(name=name,
                                 timeout_in_seconds=timeout_in_seconds,
                                 filter={'server_type':server_type})


def plico_get(server_type, name, default_class, *args,
              timeout_in_seconds=2, client_map=None, **kwargs):
    '''
    Get a client instance matching a server_type and a server name.
    If the server reports a class name and this name is included
    in the given client_map, a specific client instance will be used.
    '''
    server_info = plico_list(server_type, name, timeout_in_seconds)
    if client_map and server_info.device_class in client_map:
        module_name, classname = client_map[server_info.device_class]
        module = importlib.import_module(module_name)
        client_class = getattr(module, classname)
    else:
        client_class = default_class
    return plico_client(client_class, server_info.host, server_info.port, *args, **kwargs)


def plico_client(class_, hostname, port, *args, **kwargs):
    '''
    Get a client instance given the class and the connection details
    (hostname and port). Any additional argument is added to the
    client constructor
    '''
    from plico.rpc.zmq_remote_procedure_call import ZmqRemoteProcedureCall
    from plico.rpc.zmq_ports import ZmqPorts
    from plico.rpc.sockets import Sockets

    rpc= ZmqRemoteProcedureCall()
    zmq_ports = ZmqPorts(hostname, port)
    sockets= Sockets(zmq_ports, rpc)
    return class_(rpc, sockets, *args, **kwargs)


