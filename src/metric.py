import abc

import scipy.stats as stats

class Metric(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __add__(self, other):
        pass

    @abc.abstractmethod
    def __mul__(self, other):
        pass

    @abc.abstractmethod
    def score(self, other):
        pass

class GaussianMetric(Metric):
    def __init__(self, mean=0, stdev=0):
        self.mean = mean
        self.stdev = stdev

    def __add__(self, other):
        return GaussianMetric(self.mean + other.mean, self.stdev + other.stdev)

    def __mul__(self, n):
        return GaussianMetric(self.mean * n, self.stdev * n)

    def score(self, other):
        if self.stdev + other.stdev == 0:
            return self.mean > other.mean
        return stats.norm.cdf((self.mean - other.mean) / (self.stdev + other.stdev))

    def __repr__(self):
        return f'N({self.mean}, {self.stdev})'