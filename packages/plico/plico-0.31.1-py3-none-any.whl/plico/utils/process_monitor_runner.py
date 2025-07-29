#!/usr/bin/env python

import time
import sys
import signal
import os
import subprocess
import psutil
from plico.utils.base_runner import BaseRunner
from plico.utils.decorator import override
from plico.utils.logger import Logger
from plico.types.server_info import ServerInfo


# Windows old versions
if not hasattr(os, 'EX_OK'):
    os.EX_OK = 0


def RUNNING_MESSAGE(server_name):
    '''Return a running message customized for the managed server name'''
    return f'Monitor of {server_name} processes is running'


class ProcessMonitorRunner(BaseRunner):

    def __init__(self, server_process_name,
                       runner_config_section='processMonitor',
                       default_server_config_prefix=None):
        BaseRunner.__init__(self)
        self._my_config_section = runner_config_section
        self._server_process_name = server_process_name
        self._default_server_config_prefix = default_server_config_prefix

        INITIALIZED_LATER = None
        self._prefix = INITIALIZED_LATER
        self._logger= INITIALIZED_LATER
        self._processes= []
        self._timeToDie= False

    def _determineInstalledBinaryDir(self):
        try:
            self._binFolder= self._configuration.getValue(
                self._my_config_section,
                'binaries_installation_directory')
        except KeyError:
            self._binFolder= None

    def _logRunning(self):
        self._logger.notice(RUNNING_MESSAGE(self._server_process_name))
        sys.stdout.flush()

    def _setSignalIntHandler(self):
        signal.signal(signal.SIGINT, self._signalHandling)

    def _signalHandling(self, signalNumber, stackFrame):
        self._logger.notice("Received signal %d (%s)" %
                            (signalNumber, str(stackFrame)))
        if signalNumber == signal.SIGINT:
            self._timeToDie= True

    def _terminateAll(self):

        def on_terminate(proc):
            self._logger.notice(
                "process {} terminated with exit code {}".
                format(proc, proc.returncode))

        self._logger.notice("Terminating all subprocesses using psutil")
        self._logger.notice("My pid %d" % os.getpid())
        parent = psutil.Process(os.getpid())
        processes = parent.children(recursive=True)
        for process in processes:
            try:
                self._logger.notice(
                    "Killing pid %d %s" % (process.pid, process.cmdline()))
                process.send_signal(signal.SIGTERM)
            except Exception as e:
                self._logger.error("Failed killing process %s: %s" %
                                   (str(process), str(e)))
        _, alive = psutil.wait_procs(processes,
                                     timeout=10,
                                     callback=on_terminate)
        if alive:
            for p in alive:
                self._logger.notice(
                    "process %s survived SIGTERM; giving up" % str(p))

        self._logger.notice("terminated all")

    def serverInfo(self):
        sections = self._configuration.numberedSectionList(prefix=self._prefix)
        info = []
        for section in sections:
            name = self._configuration.getValue(section, 'name')
            host = self._configuration.getValue(section, 'host')
            port = self._configuration.getValue(section, 'port')
            controller_info = ServerInfo(name, 0, host, port)
            info.append(controller_info)
        return info

    def _spawnController(self, name, section):
        if self._binFolder:
            cmd= [os.path.join(self._binFolder, name)]
        else:
            cmd= [name]
        cmd += [self._configuration._filename, section]
        self._logger.notice("controller cmd is %s" % cmd)
        controller= subprocess.Popen(cmd)
        self._processes.append(controller)
        return controller

    def _setup(self):
        self._logger= Logger.of(self.name)
        self._setSignalIntHandler()
        self._logger.notice(f"Creating process {self.name}")
        self._determineInstalledBinaryDir()

        # Get the prefix for servers in configuration file, mandatory
        try:
            self._prefix = self._configuration.getValue(self._my_config_section,
                                                        'server_config_prefix')
        except KeyError:
            if not self._default_server_config_prefix:
                self._logger.error('Key "server_config_prefix" missing from process monitor configuration'
                                   ' and no default given')
                raise
            else:
                self._prefix = self._default_server_config_prefix

        # Get the spawn delay, default = 1 second
        try:
            delay = self._configuration.getValue(self._my_config_section,
                                                 'spawn_delay', getfloat=True)
        except KeyError:
            self._logger.warn('Key "spawn_delay" missing from process monitor configuration, using default delay = 1 second')
            delay = 1

        # Get the process monitor network port, mandatory
        try:
            port = self._configuration.getValue(self._my_config_section,
                                                 'port', getint=True)
        except KeyError:
            self._logger.error('Key "port" missing from process monitor configuration')
            raise

        sections = self._configuration.numberedSectionList(prefix=self._prefix)

        if len(sections) == 0:
            self._logger.warn(f'No sections with prefix {self._prefix} defined!')

        for section in sections:
            self._spawnController(self._server_process_name, section)
            time.sleep(delay)
        self._replySocket = self.rpc().replySocket(port)

    def _handleRequest(self):
        '''Handler for serverInfo'''
        self.rpc().handleRequest(self, self._replySocket, multi=True)

    def _runLoop(self):
        self._logRunning()
        while self._timeToDie is False:
            self._handleRequest()
            time.sleep(0.1)
        self._terminateAll()

    @override
    def run(self):
        self._setup()
        self._runLoop()
        return os.EX_OK

    @override
    def terminate(self, signal, frame):
        self._logger.notice("Terminating..")
        self._terminateAll()
