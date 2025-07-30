import logging
import threading
import time
import unittest
import numpy as np
import pickle
from plico.rpc.zmq_remote_procedure_call import ZmqRemoteProcedureCall
from plico.rpc.zmq_ports import ZmqPorts

logging.basicConfig(
    level=logging.DEBUG,  # o INFO, a seconda del dettaglio che vuoi
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)

class EchoServer:
    def __init__(self):
        self.stopped = False
    def echo(self, data):
        return b'ACK'
    def stop(self):
        self.stopped = True
        return b'STOP'

class SpeedIntegrationTest(unittest.TestCase):
    MSG_SIZE_MB = 10
    N_ITER = 10
    PORT = 5557
    USE_IPC = False  # Imposta a True per usare IPC, False per TCP
    IPC_NAME = "plico_speedtest"

    def server(self, stop_event):
        zmq_rpc = ZmqRemoteProcedureCall()
        if self.USE_IPC:
            reply_socket = zmq_rpc.replyIpcSocket(self.IPC_NAME)
        else:
            reply_socket = zmq_rpc.replySocket(self.PORT)
        echo_server = EchoServer()
        print(f"Server started on {'IPC' if self.USE_IPC else 'TCP'}")
        try:
            terminated = False
            while not terminated:
                zmq_rpc.handleRequest(echo_server, reply_socket, multi=False)
                if echo_server.stopped is True:
                    terminated = True
        finally:
            reply_socket.close()
            zmq_rpc._context.term()
            stop_event.set()
            print("Server stopped")

    def test_speed(self):
        stop_event = threading.Event()
        server_thread = threading.Thread(target=self.server, args=(stop_event,))
        server_thread.start()
        time.sleep(1.0)  # Give server time to bind

        zmq_rpc = ZmqRemoteProcedureCall()
        if self.USE_IPC:
            request_socket = zmq_rpc.requestIpcSocket(self.IPC_NAME)
        else:
            request_socket = zmq_rpc.requestSocket('127.0.0.1', self.PORT)
        data = np.random.bytes(self.MSG_SIZE_MB * 1024 * 1024)
        times = []
        try:
            for _ in range(self.N_ITER):
                print(f"Sending data of size {len(data)} bytes")
                t0 = time.time()
                zmq_rpc.sendRequest(request_socket, 'echo', (data,))
                t1 = time.time()
                times.append(t1 - t0)
            zmq_rpc.sendRequest(request_socket, 'stop', ())
            stop_event.wait()
            print(f"Round-trip times (s): {times}")
            print(f"Media: {np.mean(times):.4f} s, Min: {np.min(times):.4f} s, Max: {np.max(times):.4f} s")
            self.assertTrue(np.min(times) < 2)
        finally:
            request_socket.close()
            zmq_rpc._context.term()

    def test_pickle_speed(self):
        data = np.random.bytes(self.MSG_SIZE_MB * 1024 * 1024)
        ser_times = []
        deser_times = []
        for _ in range(self.N_ITER):
            t0 = time.time()
            pickled = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
            t1 = time.time()
            unpickled = pickle.loads(pickled)
            t2 = time.time()
            ser_times.append(t1 - t0)
            deser_times.append(t2 - t1)
        print(f"Pickle serialize avg: {np.mean(ser_times):.4f} s, min: {np.min(ser_times):.4f} s, max: {np.max(ser_times):.4f} s")
        print(f"Pickle deserialize avg: {np.mean(deser_times):.4f} s, min: {np.min(deser_times):.4f} s, max: {np.max(deser_times):.4f} s")

if __name__ == "__main__":
    unittest.main()
