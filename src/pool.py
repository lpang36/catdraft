from constants import *
from player import Player
from utils import is_empty

from collections import defaultdict

import numpy as np
import pandas as pd

class Pool:
    def __init__(self, data, cats, seasons, placeholders):
        self.has_placeholders = placeholders
        self._players = {}
        self._placeholders = {}
        df = pd.read_csv(data)
        for _, row in df.iterrows():
            metrics = defaultdict(list)
            gps = []
            for season in seasons:
                gps.append(row[f'{GP_COL}_{season}'])
                for cat in cats:
                    metrics[cat].append(row[f'{cat}_{season}'])
            self.add(Player(row[ID_COL], row[AGE_COL], row[RANK_COL], row[POS_COL], metrics, gps))
    
    def add(self, player):
        if player.id == PLACEHOLDER_ID:
            self._placeholders[player.pos] = player
        else:
            self._players[player.id] = player
    
    def draft(self, id):
        player = self._players[id]
        assert(not player.drafted)
        player.drafted = True
        return player

    def autodraft(self, n):
        if n <= 0:
            return []
        return sorted(self.draftable_players(), 
                key=lambda p: float('inf') if is_empty(p.rank) else p.rank)[:n]

    def draftable_players(self):
        return [p for p in self._players.values() if not p.drafted]

    def placeholder(self, position):
        return self._placeholders[position]

    def find(self, input):
        draftable = self.draftable_players()
        # guaranteed unique ids
        results = [p for p in draftable if \
                input.lower() == p.id.lower()]
        if len(results) > 0:
            print('Found player')
            return results[0]
        terms = input.lower().split(' ')
        # could use an actual fuzzy search here
        results = [p for p in draftable if \
                all(t in p.id.lower() for t in terms)]
        if len(results) == 0:
            print('No results found')
            return
        elif len(results) > 1:
            print('Ambiguous search term, try again')
            return
        print('Found player')
        return results[0]