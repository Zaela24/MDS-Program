import random as rand


def generate_pairs(mds_type, hues, contrasts, greys):
    """
    Generates a list of pairs, randomizes it, then returns the list
    Arguments: takes a char indicating mds type ('a' or 'f'),
      and three non-negative integers indicating number of hues, contrasts, and greys.
    """
    pairs = list()
    if mds_type == 'a':
        pairs = _gen_adjacent(hues, contrasts, greys)
    elif mds_type == 'f':
        pairs = _gen_full(hues, contrasts, greys)
    else:
        print("ERROR: Unknown MDS type (not 'f' or 'a')")
        quit()
    rand.seed()  # place a number in seed() for testing, otherwise keep empty for true random
    rand.shuffle(pairs)  # shuffles pairs randomly
    return pairs


def _gen_adjacent(hues, contrasts, greys):
    """Generates randomly ordered list of tuple pairs, each pair being adjacent to on another or skipping over 1"""
    non_greys = hues * contrasts
    lst1 = lst2 = [x for x in range(1, non_greys + 1)]
    pairs = [(a, b) for a in lst1 for b in lst2 if a == b-1 or a == b-2]
    # cleanup missed pairs:
    pairs.append((lst1[-2], lst2[0]))
    pairs.append((lst1[-1], lst2[0]))
    pairs.append((lst1[-1], lst2[1]))
    # add greys (if any)
    for n in range(greys):
        for i in range(1, hues + 1):
            pairs.append((i, len(pairs) + 1))
    return pairs


def _gen_full(hues, contrasts, greys):
    """Generates full list of non-identical pairs"""
    total_colors = hues * contrasts + greys
    lst1 = lst2 = [x for x in range(1, total_colors + 1)]
    pairs = [(a, b) for a in lst1 for b in lst2 if a != b]
    return pairs
