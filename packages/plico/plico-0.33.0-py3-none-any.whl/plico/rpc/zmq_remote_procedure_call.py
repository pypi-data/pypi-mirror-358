import time
import sys
import zmq
import pickle
from plico.utils.decorator import cacheResult, override, returnsNone
from plico.utils.logger import Logger
from plico.utils.barrier import Barrier, FunctionPredicate, BarrierTimeout
from plico.utils.constants import Constants
from plico.rpc.abstract_remote_procedure_call import \
    AbstractRemoteProcedureCall

if sys.version_info[0] >= 3:
    pickle_options = {'encoding': 'latin1'}
else:
    pickle_options = {}


class ZmqRpcTimeoutError(Exception):
    pass


class ZmqRemoteProcedureCall(AbstractRemoteProcedureCall):

    def __init__(self, timeModule=time):
        self._context = zmq.Context()
        self._logger = Logger.of("ZmqRPC")
        self._timeMod = timeModule

    def ipcAddress(self, name):
        """Restituisce l'indirizzo IPC per il socket."""
        return f"ipc:///tmp/{name}.sock"

    @cacheResult
    def replyIpcSocket(self, name):
        """Crea un socket REP su IPC per il server."""
        try:
            socket = self._context.socket(zmq.REP)
            socket.bind(self.ipcAddress(name))
        except Exception as e:
            newMsg = f"{str(e)} {self.ipcAddress(name)}"
            raise (type(e))(newMsg)
        return socket

    @cacheResult
    def requestIpcSocket(self, name):
        """Crea un socket REQ su IPC per il client."""
        socket = self._context.socket(zmq.REQ)
        socket.connect(self.ipcAddress(name))
        return socket

    @override
    @returnsNone
    def publishPickable(self, socket, pickableObject):
        resPickled = pickle.dumps(pickableObject, Constants.PICKLE_PROTOCOL)
        self._logger.debug("sending %s (pickle size: %d)" %
                           (str(pickableObject), len(resPickled)))
        socket.send(resPickled, zmq.NOBLOCK)

    @override
    def receivePickable(self, socket, timeoutInSec=10):
        toBeReturned = self.receiveWithTimeout(socket, timeoutInSec)
        retObj = pickle.loads(toBeReturned, **pickle_options)
        if isinstance(retObj, Exception):
            raise retObj
        else:
            return retObj

    @override
    @returnsNone
    def sendCameraFrame(self, socket, frame):
        self.publishPickable(socket, frame)

    @override
    def recvCameraFrame(self, socket, timeoutInSec=10):
        return self.receivePickable(socket, timeoutInSec)

    def publisherSocket(self,
                        port,
                        connect=False,
                        host='*',
                        hwm=1):
        '''
        Create a PUB-style socket for data publishers.
        If <connect> is true, connects to a XPUB/XSUB forwarding device.
        '''
        socket = self._context.socket(zmq.PUB)
        socket.setsockopt(zmq.SNDHWM, hwm)
        socket.setsockopt(zmq.LINGER, 0)

        try:
            if connect:
                socket.connect(self.tcpAddress(host, port))
            else:
                socket.bind(self.tcpAddress(host, port))
        except Exception as e:
            newMsg = str("%s %s:%d" % (str(e), host, port))
            raise (type(e))(newMsg)
        return socket

    def tcpAddress(self, host, port):
        return "tcp://%s:%d" % (host, port)

    def subscriberSocket(self, host, port, filt=b'', conflate=False):
        '''
        Create a SUB-style socket for data receivers
        '''
        socket = self._context.socket(zmq.SUB)
        if conflate:
            socket.setsockopt(zmq.CONFLATE, 1)

        socket.connect(self.tcpAddress(host, port))
        socket.setsockopt(zmq.SUBSCRIBE, filt)
        return socket

    def xpubsubSockets(self, hostSub, portSub, hostPub, portPub):
        '''
        Creates frontend and backend for a XPUB/XSUB forwarding device
        '''
        frontend_addr = self.tcpAddress(hostSub, portSub)
        backend_addr = self.tcpAddress(hostPub, portPub)

        frontendSocket = self._context.socket(zmq.SUB)
        frontendSocket.bind(frontend_addr)
        frontendSocket.setsockopt(zmq.SUBSCRIBE, b'')

        backendSocket = self._context.socket(zmq.PUB)
        backendSocket.bind(backend_addr)

        return frontendSocket, backendSocket

    @cacheResult
    def replySocket(self, port, host='*'):
        '''
        Create a REP-style socket for servers
        '''
        try:
            socket = self._context.socket(zmq.REP)
            socket.bind(self.tcpAddress(host, port))
        except Exception as e:
            newMsg = str("%s %s:%d" % (str(e), host, port))
            raise (type(e))(newMsg)
        return socket

    @cacheResult
    def requestSocket(self, host, port):
        '''
        Create a REQ-style socket for clients
        '''
        socket = self._context.socket(zmq.REQ)
        socket.connect(self.tcpAddress(host, port))
        return socket

    def _discardPendingAnswers(self, socket):
        try:
            buf = socket.recv(zmq.NOBLOCK)
            self._logger.debug("got pending buffer %d bytes (%s)" %
                               (len(buf), buf))
        except zmq.ZMQError:
            return
        except Exception as e:
            self._logger.debug("got Exception %s" % str(e))

    def _hasSendMultiPartSucceded(self, socket, multiPartMsg):
        try:
            self._discardPendingAnswers(socket)
            socket.send_multipart(multiPartMsg, zmq.NOBLOCK)
            return True
        except zmq.ZMQError as e:
            self._logger.debug("trapped ZMQError on cmd %s: %s" %
                               (multiPartMsg[0].decode(), str(e)))
            return False

    def _sendMultiPartWithBarrierTimeout(self, socket,
                                         multiPartMsg, timeoutSec):
        try:
            Barrier(timeoutSec, 0.1, self._timeMod).waitFor(
                FunctionPredicate.create(self._hasSendMultiPartSucceded,
                                         socket, multiPartMsg))
        except BarrierTimeout as e:
            raise ZmqRpcTimeoutError(str(e))

    def sendRequest(self, socket, cmd, args=(), timeout=10):
        '''
        Perform client request/reply
        Request is a ZMQ multipart message:
         - command string
         - pickled argument list
        Reply is a pickled object
        '''
        self._logger.debug("sending request %s %s" % (cmd, self._safe_args_repr(args)))
        t0 = time.time()
        self._sendMultiPartWithBarrierTimeout(
            socket,
            [cmd.encode(),
             pickle.dumps(args, Constants.PICKLE_PROTOCOL)],
            timeout)
        toBeReturned = self.receiveWithTimeout(socket, timeout)
        retObj = pickle.loads(toBeReturned, **pickle_options)
        self._logger.debug("%s received %s in %.3fs" % (
            cmd, self._safe_args_repr(retObj), time.time() - t0))
        if isinstance(retObj, Exception):
            raise retObj
        else:
            return retObj

    def receiveWithTimeout(self, socket, timeoutInSeconds=1):
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        msgs = dict(poller.poll(timeoutInSeconds * 1000))
        if socket in msgs and msgs[socket] == zmq.POLLIN:
            return socket.recv(zmq.NOBLOCK)
        else:
            self._logger.debug("raising ZmqRpcTimeoutError")
            raise ZmqRpcTimeoutError()

    @override
    def handleRequest(self, obj, socket, multi=False):
        '''
        Handle one or more requests on a REP socket, with the format
        sent by sendRequest()
        '''
        while 1:
            try:
                msg = socket.recv_multipart(zmq.NOBLOCK)
                method = msg[0].decode()
                try:
                    args = pickle.loads(msg[1], **pickle_options)
                except ValueError as err:
                    self._logger.notice('Request %s failed. Caught %s %s' %
                                        (method, type(err), str(err)))
                    self._sendAnswer(socket, err)
                self._logger.debug("received request %s %s" % (method, self._safe_args_repr(args)))
                try:
                    res = getattr(obj, method).__call__(*args)
                except Exception as e:
                    self._logger.notice('Request %s %s failed. Caught %s %s' %
                                        (method, str(args), type(e), str(e)))
                    res = e
                self._sendAnswer(socket, res)
            except zmq.ZMQError:
                return
            except Exception as e:
                self._logger.error("Unknown error %s" % str(e))
            if not multi:
                break

    def _sendAnswer(self, socket, answer):
        resPickled = pickle.dumps(answer, Constants.PICKLE_PROTOCOL)
        self._logger.debug("answering %s (pickle size: %d)" %
                           (str(answer), len(resPickled)))
        socket.send(resPickled, zmq.NOBLOCK)

    def _safe_args_repr(self, args, maxlen=100):
        """Restituisce una stringa leggibile per il log, evitando di stampare array grandi."""
        try:
            if isinstance(args, (list, tuple)):
                if len(args) == 1 and hasattr(args[0], 'shape'):
                    # Probabile numpy array
                    arr = args[0]
                    return f"<{type(arr).__name__} shape={getattr(arr, 'shape', '?')} dtype={getattr(arr, 'dtype', '?')} size={arr.size}>"
                elif len(args) < 5 and all(isinstance(a, (int, float, str, bool)) for a in args):
                    return str(args)
                else:
                    return f"<args of type {type(args).__name__} len={len(args)}>"
            elif hasattr(args, 'shape'):
                # numpy array o simile
                return f"<{type(args).__name__} shape={getattr(args, 'shape', '?')} dtype={getattr(args, 'dtype', '?')} size={args.size}>"
            elif isinstance(args, (int, float, str, bool)):
                return str(args)
            else:
                s = str(args)
                if len(s) > maxlen:
                    return s[:maxlen] + "..."
                return s
        except Exception as e:
            return f"<unprintable args: {e}>"

    def terminate(self):
        """Explicitly terminate the ZeroMQ context."""
        self._context.term()
