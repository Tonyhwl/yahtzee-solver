"""
Integratable Markov Decision Process solver
Used in the full yahtzee game (yahtzee.py)
"""

import random
import itertools
from collections import Counter
from functools import lru_cache

KEEP_MASKS = list(itertools.product([True, False], repeat=5))


def score_roll(dice):
    counts = Counter(dice)
    values = list(counts.values())
    scores = [(sum(dice), 'Chance')]  # chance

    if max(values) >= 3:
        scores.append((sum(dice), '3 of a Kind'))
    if max(values) >= 4:
        scores.append((sum(dice), '4 of a Kind'))

    if sorted(values) == [2, 3]:
        scores.append((25, 'Full House'))
    unique = set(dice)
    if any(s.issubset(unique) for s in [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]):
        scores.append((30, 'Small Straight'))
    if any(s.issubset(unique) for s in [{1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}]):
        scores.append((40, 'Large Straight'))

    if max(values) == 5:
        scores.append((50, 'Yahtzee'))

    return max(scores)

def apply_keep_mask(dice, mask):
    new_dice = []

    for i in range(5):
        dice_value = dice[i]  # current die value
        keep = mask[i]  # whether to keep it or not

        if keep:
            new_dice.append(dice_value)
        else:
            new_value = random.randint(1, 6)
            new_dice.append(new_value)

    return tuple(new_dice)

def get_sample_count(mask):
    return 6 ** mask.count(False)

@lru_cache(maxsize=None)
def V(dice, rolls_left):
    dice = tuple(sorted(dice))
    category_choice = score_roll(dice)

    if rolls_left == 0:
        score,category_choice = score_roll(dice)
        return score, None,category_choice  # no rerolls left

    best_ev = float ('-inf')
    best_mask = None

    # try all 32 reroll patterns
    for mask in KEEP_MASKS:

        reroll_count = mask.count(False)

        possible_outcomes = itertools.product(range(1, 7), repeat=reroll_count)
        total_ev = 0

        total_outcomes = 6 ** reroll_count

        for reroll in possible_outcomes:
            new_dice = []
            i = 0

            for keep, val in zip(mask, dice):
                if keep:
                    new_dice.append(val) # keep original die
                else:
                    new_dice.append(reroll[i]) # use rerolled value
                    i += 1

            new_dice = tuple(sorted(new_dice))
            ev, _, _ = V(new_dice, rolls_left - 1)
            total_ev += ev

        avg_ev = total_ev / total_outcomes

        if avg_ev > best_ev:
            best_ev = avg_ev
            best_mask = mask

    return best_ev,best_mask,category_choice

def average_turn_ev():
    total = 0.0
    for s in itertools.product(range(1, 7), repeat=5):
        ev, _, _ = V(tuple(sorted(s)), 2)
        total += ev
    return total / 7776

if __name__ == '__main__':
    avg = average_turn_ev()
    print(f"Average turn EV with optimal rerolling: {avg:.2f}")
