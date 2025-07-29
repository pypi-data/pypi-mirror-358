import os
import sys
import subprocess
import shutil
import unittest
import logging
from functools import wraps

from test.test_helper import TestHelper, Poller, MessageInFileProbe
from plico.utils.logger import Logger
from plico.utils.configuration import Configuration
from plico.utils.process_monitor_runner import RUNNING_MESSAGE



runner_main = '''#!/usr/bin/env python
import sys
from plico.utils.process_monitor_runner import ProcessMonitorRunner

if __name__ == '__main__':
    runner = ProcessMonitorRunner(server_process_name='plico',
                                  runner_config_section='processMonitor')
    sys.exit(runner.start(sys.argv))
'''


def _dumpEnterAndExit(enterMessage, exitMessage, f, self, *args, **kwds):
    doDump = True
    if doDump:
        print(enterMessage)
    res = f(self, *args, **kwds)
    if doDump:
        print(exitMessage)
    return res


def dumpEnterAndExit(enterMessage, exitMessage):

    def wrapperFunc(f):

        @wraps(f)
        def wrapper(self, *args, **kwds):
            return _dumpEnterAndExit(enterMessage, exitMessage,
                                     f, self, *args, **kwds)

        return wrapper

    return wrapperFunc


@unittest.skipIf(sys.platform == "win32",
                 "Integration test doesn't run on Windows. Fix it!")
class IntegrationTest(unittest.TestCase):

    TEST_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            "./tmp/")
    LOG_DIR = os.path.join(TEST_DIR, "log")
    CONF_FILE = 'test/integration/conffiles/plico.conf'
    CALIB_FOLDER = 'test/integration/calib'
    CONF_SECTION = 'processMonitor'
    RUNNING_MESSAGE = RUNNING_MESSAGE(server_name='plico')
    SERVER_LOG_PATH = os.path.join(LOG_DIR, "%s.log" % CONF_SECTION)
    SERVER_PREFIX = 'test_server'
    BIN_DIR = os.path.join(TEST_DIR, "apps", "bin")
    RUN_FILE = os.path.join(BIN_DIR, 'run_integration_test.py')
    SOURCE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                              "../..")

    def setUp(self):
        self._setUpBasicLogging()
        self.server = None
        self._wasSuccessful = False

        self._removeTestFolderIfItExists()
        self._makeTestDir()
        self.configuration = Configuration()
        self.configuration.load(self.CONF_FILE)

        calibrationRootDir = self.configuration.calibrationRootDir()
        self._setUpCalibrationTempFolder(calibrationRootDir)
        print("Setup completed")

    def _setUpBasicLogging(self):
        logging.basicConfig(level=logging.DEBUG)
        self._logger = Logger.of('Integration Test')

    def _makeTestDir(self):
        os.makedirs(self.TEST_DIR)
        os.makedirs(self.LOG_DIR)
        os.makedirs(self.BIN_DIR)

    def _setUpCalibrationTempFolder(self, calibTempFolder):
        shutil.copytree(self.CALIB_FOLDER,
                        calibTempFolder)

    def _removeTestFolderIfItExists(self):
        if os.path.exists(self.TEST_DIR):
            shutil.rmtree(self.TEST_DIR)

    @dumpEnterAndExit("tearing down", "teared down")
    def tearDown(self):
        TestHelper.dumpFileToStdout(self.SERVER_LOG_PATH)

        if self.server is not None:
            TestHelper.terminateSubprocess(self.server)

        if self._wasSuccessful:
            self._removeTestFolderIfItExists()

    @dumpEnterAndExit("creating starter scripts", "starter scripts created")
    def _createStarterScripts(self):
        with open(self.RUN_FILE, 'w') as f:
            f.write(runner_main)
        if not sys.platform == "win32":
            subprocess.call(f'chmod +x "{self.RUN_FILE}"', shell=True)

    @dumpEnterAndExit("starting processes", "processes started")
    def _startProcesses(self):
        serverLog = open(self.SERVER_LOG_PATH, "wb")
        self.server = subprocess.Popen(
            [self.RUN_FILE,
             self.CONF_FILE,
             self.CONF_SECTION],
            stdout=serverLog, stderr=serverLog)
        Poller(5).check(MessageInFileProbe(
            self.RUNNING_MESSAGE, self.SERVER_LOG_PATH))

    def test_main(self):
        self._createStarterScripts()
        self._startProcesses()
        self._wasSuccessful = True


if __name__ == "__main__":
    unittest.main()

