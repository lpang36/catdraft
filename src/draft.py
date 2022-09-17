from pool import Pool
from league import League
from utils import init_utils, all_positions
from player import Player

import cProfile
import argparse

if __name__ == '__main__':
    # TODO: support negative stats (e.g. losses)
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', help='path to player data csv')
    parser.add_argument('--countcats', nargs='+', help='column names of counting categories', default=[])
    parser.add_argument('--pctcats', nargs='+', help='column names of non counting/percentage categories', default=[])
    parser.add_argument('--seasons', nargs='+', help='column names of seasons from most to least recent')
    parser.add_argument('--order', help='path to csv with draft order')
    parser.add_argument('--positions', nargs='+', help='positional requirements')
    parser.add_argument('--nrecs', type=int, help='number of recommendations to show', default=10)
    parser.add_argument('--placeholders', action='store_true', help='whether data csv includes placeholders')
    parser.add_argument('--autodraft', action='store_true', help='whether to fill undersized rosters by autodrafting')
    parser.add_argument('--lookahead', type=int, help='number of years to extrapolate', default=1)
    parser.add_argument('--separate', action='store_true', help='whether to recommend positions separately')
    args = parser.parse_args()

    init_utils(args)
    Player.LOOKAHEAD = args.lookahead
    pool = Pool(args.data, args.countcats + args.pctcats, args.seasons, args.placeholders)
    league = League(pool, args.order, all_positions(), args.nrecs, args.separate, args.autodraft)
    cProfile.run('league.draft()')