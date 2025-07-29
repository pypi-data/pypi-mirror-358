
import abc
from plico.utils.decorator import returns
from six import with_metaclass


class Convergeable(with_metaclass(abc.ABCMeta, object)):

    @abc.abstractmethod
    @returns(bool)
    def hasConverged(self):
        assert False

    @abc.abstractmethod
    def performOneConvergenceStep(self):
        assert False

    @abc.abstractmethod
    def measureConvergence(self):
        assert False
