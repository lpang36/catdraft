count_cats = set()
pct_cats = set()
positions = {}

def init_utils(args):
    count_cats.update(args.countcats)
    pct_cats.update(args.pctcats)
    cur_pos = ''
    for i, arg in enumerate(args.positions):
        if i % 2 == 0:
            cur_pos = arg
        else:
            positions[cur_pos] = int(arg)

def is_count(cat):
    return cat in count_cats

def is_pct(cat):
    return cat in pct_cats

def is_empty(x):
    return x == '' or x is None or x != x

def all_cats():
    return count_cats | pct_cats

def all_positions():
    return positions

def add_stats(a, b):
    # assumes both have all cats keys
    output = {}
    for k in all_cats():
        output[k] = a[k] + b[k]
    return output