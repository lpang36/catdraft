from metric import GaussianMetric
from utils import all_cats, add_stats

from collections import defaultdict
from copy import copy

class Roster:
    def __init__(self, id, positions, autodraft):
        self._id = id
        self._positions = positions
        self._max_players = sum(positions.values())
        self._players = []
        self._position_counts = defaultdict(int)
        self._num_players = 0
        self._autodraft = autodraft
        # TODO: support polymorphism properly
        self._cached_sums = defaultdict(GaussianMetric)
        self._num_cached = 0

    def _copy(self):
        cpy = Roster(self._id, self._positions, self._autodraft)
        cpy._players = copy(self._players)
        cpy._position_counts = copy(self._position_counts)
        cpy._num_players = self._num_players
        cpy._cached_sums = copy(self._cached_sums)
        cpy._num_cached = self._num_cached
        return cpy

    def draft_from(self, pool):
        player = None
        while player is None:
            print('Enter draft pick:')
            player = pool.find(input())
        pool.draft(player.id)
        self.add(player, False)

    def add(self, player, simulated=True):
        self._players.append(player)
        self._position_counts[player.pos] += 1
        self._num_players += 1
        if not simulated:
            self._num_cached += 1
            self._cached_sums = add_stats(self._cached_sums, player.expected())

    def with_player(self, player):
        output = self._copy()
        output.add(player)
        return output

    def with_placeholders(self, pool):
        if not pool.has_placeholders:
            return self
        output = self._copy()
        # could be optimized
        # only need diff between num placeholders in each posn
        counts = defaultdict(int)
        for position, limit in self._positions.items():
            num_at_pos = min(max(limit - self._position_counts[position], 0),
                    output._max_players - output._num_players)
            output.add(pool.placeholder(position) * num_at_pos)
            if output._num_players >= output._max_players:
                break
        return output

    def with_autodraft(self, autodraftees, opp, player):
        if not self._autodraft:
            return self
        # could be optimized
        output = self._copy()
        for p in autodraftees:
            if not p.autodrafted and p != player:
                output.add(p)
                p.autodrafted = True
            if opp._num_players < output._num_players:
                break
        return output

    def versus(self, opp):
        opp_metrics = opp._expected()
        score = 0
        for k, v in self._expected().items():
            score += v.score(opp_metrics[k])
        return score

    def full_positions(self):
        output = []
        for k, v in self._position_counts.items():
            if self._positions[k] <= v:
                output.append(k)
        return output

    def _expected(self):
        output = self._cached_sums
        for p in self._players[self._num_cached:]:
            output = add_stats(output, p.expected())
        return output

    def __eq__(self, other):
        return self._id == other._id

    def __repr__(self):
        return f'{self._expected()}\n{self._players}'