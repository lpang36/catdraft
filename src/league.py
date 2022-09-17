from roster import Roster
from utils import is_empty, all_cats
from constants import *

from collections import defaultdict

import pandas as pd
import numpy as np
from tqdm import tqdm

class League:
    def __init__(self, pool, order, positions, nrecs, separate, autodraft):
        self._pool = pool
        order_df = pd.read_csv(order, header=None)
        self._order = [(row[0], row[1]) if len(order_df.columns) > 1 else (row[0], None) \
                for _, row in order_df.iterrows()]
        self._nrecs = nrecs
        self._separate = separate
        self._rosters = {}
        for i, _ in self._order:
            if i not in self._rosters:
                self._rosters[i] = Roster(i, positions, autodraft)

    def draft(self):
        for i, (r, p) in enumerate(self._order):
            print(f'Pick {i + 1} for {r}:')
            roster = self._rosters[r]
            print(roster)
            if is_empty(p):
                self._recommend_for(roster)
                roster.draft_from(self._pool)
            else:
                print(f'{p} was selected')
                player = self._pool.find(p)
                if player is not None:
                    roster.add(player, False)
                    self._pool.draft(player.id)
                else:
                    roster.draft_from(self._pool)
    
    def _recommend_for(self, roster):
        # +1 accounts for candidate player
        num_autodraft = sum(max(roster._num_players + 1 - opp._num_players, 0) \
                for opp in self._rosters.values() if opp != roster) + 1
        autodraftees = self._pool.autodraft(num_autodraft)
        players = sorted([(self._score_player(roster, p, autodraftees), p) \
                for p in tqdm(self._short_circuit(roster))], reverse=True)
        rank_str = lambda p: '' if is_empty(p.rank) else f' ({int(p.rank)})'
        if self._separate:
            positions = defaultdict(list)
            for p in players:
                positions[p[1].pos].append(p)
            for k, v in positions.items():
                print(k)
                for score, player in v[:self._nrecs]:
                    print(f'{player}: {score}{rank_str(player)} {self._display_quantiles(player)}')
            print('Rank')
            for player in self._pool.autodraft(self._nrecs):
                if not is_empty(player.rank):
                    print(f'{player}{rank_str(player)}')
        else:
            for score, player in players[:self._nrecs]:
                print(f'{player}: {score}{rank_str(player)} {self._display_quantiles(player)}')

    def _display_quantiles(self, player):
        quantiles = self._pool.quantiles(player)
        return sorted(quantiles.keys(), key=lambda k: quantiles[k], reverse=True)[:MAX_CATS]

    def _short_circuit(self, roster):
        metrics = {p: p.expected() for p in self._pool.draftable_players() \
                if p.pos not in roster.full_positions()}
        players = set()
        for c in all_cats():
            players.update(sorted(metrics.keys(), key=lambda p: metrics[p][c].mean, 
                    reverse=True)[:SHORT_CIRCUIT])
        return players

    def _score_player(self, roster, player, autodraftees):
        score = 0
        for opp in self._rosters.values():
            if opp == roster:
                continue
            score += roster.with_player(player).with_placeholders(self._pool) \
                    .versus(opp.with_autodraft(autodraftees, roster, player) \
                    .with_placeholders(self._pool))
        for p in autodraftees:
            p.autodrafted = False
        return score