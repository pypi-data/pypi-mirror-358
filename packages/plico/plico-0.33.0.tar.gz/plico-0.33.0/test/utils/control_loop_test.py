import unittest
from plico.utils.control_loop import FaultTolerantControlLoop, IntolerantControlLoop
from plico.utils.logger import DummyLogger, DummyLoggerFactory
from plico.utils.stepable import Stepable
from test.fake_time_mod import FakeTimeMod

class MyException(Exception):
    pass

class RaisingStepable(Stepable):

    def __init__(self, terminate_after_iteration=3):
        self.iter = 0
        self.max_iter = terminate_after_iteration
        
    def step(self):
        self.iter += 1
        raise MyException()
    
    def isTerminated(self):
        return self.iter >= self.max_iter

class IntolerantControlLoopTest(unittest.TestCase):

    def test_intolerant_loop_always_raises(self):
        raising_stepable = RaisingStepable()
        logger = DummyLoggerFactory().getLogger('test_logger')
        loop = IntolerantControlLoop(raising_stepable, logger, timeModule=FakeTimeMod())
        self.assertRaises(MyException, loop.start)

class FaultTolerantControlLoopTest(unittest.TestCase):

    def test_fault_tolerant_loop_never_raises(self):
        raising_stepable = RaisingStepable()
        logger = DummyLoggerFactory().getLogger('test_logger')
        loop = FaultTolerantControlLoop(raising_stepable, logger, timeModule=FakeTimeMod())
        loop.start()
        self.assertEqual(raising_stepable.iter, raising_stepable.max_iter)


if __name__ == "__main__":
    unittest.main()
