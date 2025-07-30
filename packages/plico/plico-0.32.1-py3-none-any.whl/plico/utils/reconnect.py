'''
Base class for dynamic reconnection
'''

class ConnectionException(Exception):
    pass


class ReconnectInfo:

    def __init__(self, connect_func, disconnect_func, exc_to_catch_list):
        self.connect_func = connect_func
        self.disconnect_func = disconnect_func
        self.exceptions_to_catch = (OSError,)
        if exc_to_catch_list:
             self.exceptions_to_catch += tuple(exc_to_catch_list)
        self.connected = False


class Reconnecting:

    def __init__(self, connect_func, disconnect_func, exc_to_catch_list=None):
        '''
        Base class for dynamic reconnection


        connect_func: function with no arguments that will connect to device.
        disconnect_func: function with no arguments that disconnects from device
        exc_to_catch_list: optional sequence of communication exceptions that
                           must be catched and cause a disconnection event.
                           By default only OSError is catched.
        '''
        self._reconnectInfo = ReconnectInfo(connect_func, disconnect_func, exc_to_catch_list)


def reconnect(method):
    '''
    Decorator to make sure that a method is executed
    after connecting to the device, and trigger
    a reconnect in the next command if any error occurs.

    Any communication problem will raise a ConnectionException
    '''
    def wrapped(*args, **kwargs):
        self = args[0]
        info = self._reconnectInfo
        try:
            if not info.connected:
                info.connect_func()
                info.connected = True
            return method(*args, **kwargs)
        except info.exceptions_to_catch as e:
            info.disconnect_func()
            info.connected = False
            raise ConnectionException('Error communicating with device: %s. Will retry...' % str(e))

    return wrapped

# ___oOo___
