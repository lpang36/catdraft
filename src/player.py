from utils import is_count, is_empty
from metric import GaussianMetric
from constants import *

from functools import lru_cache
from math import sqrt
from collections import defaultdict
from copy import copy

import numpy as np

class Player:
    LOOKAHEAD = 1

    def __init__(self, id, age, rank, pos, metrics, gps):
        self.id = id
        self.age = age
        self.rank = rank
        self.pos = pos
        self.metrics = metrics
        self.gps = gps
        self.drafted = False
        self.autodrafted = False
        self.multiplier = 1

    @lru_cache(maxsize=None)
    def expected(self):
        output = defaultdict(GaussianMetric)
        total_gp = sum(i * season for i, season in zip(self.gps, SEASON_DECAY) \
                if not is_empty(i))
        if total_gp < MIN_GP:
            return output
        age_coeff = AGE_CURVE[self.age + Player.LOOKAHEAD] / AGE_CURVE[self.age]
        # print(self.metrics, self.gps, total_gp)
        # might not cache if copied
        for k, v in self.metrics.items():
            valid = 0
            mean = 0
            iscount = is_count(k)
            # could be optimized
            for m, gp, season in zip(v, self.gps, SEASON_DECAY):
                # this zeros by default which could be bad for negative stats
                if is_empty(m):
                    continue
                valid += 1
                if iscount:
                    mean += m * season
                else:
                    mean += gp * m * season
            mean /= total_gp
            # use age curve if counting stat
            if iscount:
                mean *= age_coeff
            # TODO: handle one season cases
            # TODO: should goalie wins be per game?
            var = 0
            if valid > 1:
                for m, gp, season in zip(v, self.gps, SEASON_DECAY):
                    if is_empty(m):
                        continue
                    # TODO: verify these formulas
                    if iscount:
                        var += (gp * season) ** 2 * (m * season / gp - mean) ** 2
                    else:
                        var += (gp * season) ** 2 * (m * season - mean) ** 2      
                var *= valid / (valid - 1) / total_gp ** 2
                if iscount:
                    var *= age_coeff ** 2
            output[k] = GaussianMetric(mean, sqrt(var)) * self.multiplier
            # print(self, k, output[k], iscount)
        return output

    def __mul__(self, n):
        cpy = copy(self)
        cpy.multiplier = n
        return cpy

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return self.id

    def __lt__(self, other):
        # arbitrary
        return False