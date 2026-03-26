"""
Simple yahtzee Markov Decision Processes solver 
Benchmarked with a greedy-roll baseline
"""
import random
import itertools
from collections import Counter
from functools import lru_cache

KEEP_MASKS = list(itertools.product([True, False], repeat=5))

# define scores
def score_roll(dice):
    counts = Counter(dice)
    values = list(counts.values())
    scores = [(sum(dice), 'Chance')]
    if max(values) >= 3:
        scores.append((sum(dice), 'Three of a Kind'))
    if max(values) >= 4:
        scores.append((sum(dice), 'Four of a Kind'))
    if sorted(values) == [2, 3]:
        scores.append((25, 'Full House'))
    unique = set(dice)
    if any(s.issubset(unique) for s in [{1,2,3,4},{2,3,4,5},{3,4,5,6}]):
        scores.append((30, 'Small Straight'))
    if any(s.issubset(unique) for s in [{1,2,3,4,5},{2,3,4,5,6}]):
        scores.append((40, 'Large Straight'))
    if max(values) == 5:
        scores.append((50, 'Yahtzee'))
    return max(scores)

# setup MDP
@lru_cache(maxsize=None)
def V(dice, rolls_left, available):

    dice = tuple(sorted(dice))

    # pick best available category
    best_cat = max(available, key=lambda c: calculate_score(c, dice))
    best_ev  = calculate_score(best_cat, dice)
    best_mask = None  

    if rolls_left == 0:
        return best_ev, None, best_cat

    # try all reroll patterns
    for mask in KEEP_MASKS:
        reroll_count = mask.count(False)
        if reroll_count == 0:
            continue  

        total_ev     = 0
        total_outcomes = 6 ** reroll_count

        for reroll in itertools.product(range(1, 7), repeat=reroll_count):
            new_dice = []
            i = 0
            for keep, val in zip(mask, dice):
                if keep:
                    new_dice.append(val)
                else:
                    new_dice.append(reroll[i])
                    i += 1
            ev, _, _ = V(tuple(sorted(new_dice)), rolls_left - 1, available)
            total_ev += ev

        avg_ev = total_ev / total_outcomes
        if avg_ev > best_ev:
            best_ev   = avg_ev
            best_mask = mask

    return best_ev, best_mask, best_cat

# calculating scores
def calculate_score(category, dice_values):
    """Module-level scoring used by the MDP solver."""
    counts = Counter(dice_values)
    UPPER = ['Ones','Twos','Threes','Fours','Fives','Sixes']
    if category in UPPER:
        n = UPPER.index(category) + 1
        return counts[n] * n
    elif category == 'Three of a Kind':
        return sum(dice_values) if max(counts.values()) >= 3 else 0
    elif category == 'Four of a Kind':
        return sum(dice_values) if max(counts.values()) >= 4 else 0
    elif category == 'Full House':
        return 25 if sorted(counts.values()) == [2, 3] else 0
    elif category == 'Small Straight':
        u = set(dice_values)
        return 30 if any(s <= u for s in [{1,2,3,4},{2,3,4,5},{3,4,5,6}]) else 0
    elif category == 'Large Straight':
        u = set(dice_values)
        return 40 if any(s <= u for s in [{1,2,3,4,5},{2,3,4,5,6}]) else 0
    elif category == 'Yahtzee':
        return 50 if max(counts.values()) == 5 else 0
    elif category == 'Chance':
        return sum(dice_values)
    return 0

# define classes
class Dice:
    def __init__(self):
        self.value = random.randint(1, 6)
        self.held = False

    def roll(self):
        if not self.held:
            self.value = random.randint(1, 6)
        return self.value

    def hold(self):
        self.held = not self.held

    def __str__(self):
        return f"Dice: {self.value} {'(held)' if self.held else ''}"

class DiceSet:
    def __init__(self):
        self.dice = [Dice() for _ in range(5)]

    def roll(self):
        for die in self.dice:
            die.roll()

    def get_values(self):
        return tuple(die.value for die in self.dice)

    def toggle_hold(self, index):
        if 0 <= index < len(self.dice):
            self.dice[index].hold()

    def __str__(self):
        return ' | '.join(str(die) for die in self.dice)

class Scorecard:
    CATEGORIES = [
        'Ones', 'Twos', 'Threes', 'Fours', 'Fives', 'Sixes',
        'Three of a Kind', 'Four of a Kind', 'Full House',
        'Small Straight', 'Large Straight', 'Yahtzee', 'Chance'
    ]

    def __init__(self):
        self.scores = {category: None for category in self.CATEGORIES}

    def is_filled(self, category):
        return self.scores[category] is not None

    def available_categories(self):
        return [c for c in self.CATEGORIES if not self.is_filled(c)]

    def is_complete(self):
        return not self.available_categories()

    def upper_total(self):
        return sum(
            score for category, score in self.scores.items()
            if category in self.CATEGORIES[:6] and score is not None)

    def bonus(self):
        return 35 if self.upper_total() >= 63 else 0

    def total(self):
        return sum(s for s in self.scores.values() if s is not None) + self.bonus()

    def score_category(self, category, dice_values):
        if self.is_filled(category):
            raise ValueError(f"Category '{category}' is already filled.")
        score = self.calculate_score(category, dice_values)
        self.scores[category] = score
        return score

    def calculate_score(self, category, dice_values):
        counts = Counter(dice_values)
        if category in self.CATEGORIES[:6]:
            num = self.CATEGORIES.index(category) + 1
            return counts[num] * num
        elif category == 'Three of a Kind':
            return sum(dice_values) if max(counts.values()) >= 3 else 0
        elif category == 'Four of a Kind':
            return sum(dice_values) if max(counts.values()) >= 4 else 0
        elif category == 'Full House':
            return 25 if sorted(counts.values()) == [2, 3] else 0
        elif category == 'Small Straight':
            unique = set(dice_values)
            return 30 if any(s.issubset(unique) for s in [{1,2,3,4},{2,3,4,5},{3,4,5,6}]) else 0
        elif category == 'Large Straight':
            unique = set(dice_values)
            return 40 if any(s.issubset(unique) for s in [{1,2,3,4,5},{2,3,4,5,6}]) else 0
        elif category == 'Yahtzee':
            return 50 if max(counts.values()) == 5 else 0
        elif category == 'Chance':
            return sum(dice_values)
        else:
            raise ValueError(f"Unknown category: {category}")

class Player:
    def __init__(self, name):
        self.name = name
        self.scorecard = Scorecard()

    def choose_reroll(self, dice_values, rolls_left):
        raise NotImplementedError

    def choose_category(self, dice_values, available):
        raise NotImplementedError

class RandomBot(Player):
    def choose_reroll(self, dice_values, rolls_left):
        return [i for i in range(5) if random.choice([True, False])]

    def choose_category(self, dice_values, available):
        return random.choice(available)

class GreedyBot(Player):

    def choose_reroll(self, dice_values, rolls_left):
        counts = Counter(dice_values)
        best_value = max(counts, key=counts.get)
        return [i for i, v in enumerate(dice_values) if v != best_value]

    def choose_category(self, dice_values, available):
        best_category = None
        best_score = -1
        for category in available:
            score = self.scorecard.calculate_score(category, dice_values)
            if score > best_score:
                best_score = score
                best_category = category
        return best_category

class OptimalBot(Player):
    def choose_reroll(self, dice_values, rolls_left):
        available = frozenset(self.scorecard.available_categories())
        _, best_mask, _ = V(tuple(sorted(dice_values)), rolls_left, available)

        if best_mask is None:
            return []  # MDP says stop rolling

        # best_mask is aligned to SORTED dice — map back to original indices
        sorted_dice    = sorted(dice_values)
        values_to_keep = [val for val, keep in zip(sorted_dice, best_mask) if keep]

        reroll_indices = []
        keep_pool = list(values_to_keep)
        for i, val in enumerate(dice_values):
            if val in keep_pool:
                keep_pool.remove(val)
            else:
                reroll_indices.append(i)

        return reroll_indices

    def choose_category(self, dice_values, available):
        # MDP already computed the best category when rolls_left=0
        available_fs = frozenset(available)
        _, _, best_cat = V(tuple(sorted(dice_values)), 0, available_fs)
        return best_cat

class YahtzeeGame:
    def __init__(self, player1, player2):
        self.players = [player1, player2]

    def play_turn(self, player, silent=False):
        dice_set = DiceSet()
        dice_set.roll()  # initial roll
        for rolls_left in range(2, 0, -1):
            if not silent:
                print(f"{player.name} rolled: {dice_set}")
            reroll_indices = player.choose_reroll(dice_set.get_values(), rolls_left)
            if not reroll_indices:
                break
            # reset all holds, then hold keepers
            for i in range(5):
                if dice_set.dice[i].held:
                    dice_set.toggle_hold(i)
            for i in range(5):
                if i not in reroll_indices:
                    dice_set.toggle_hold(i)
            dice_set.roll()

        category = player.choose_category(dice_set.get_values(), player.scorecard.available_categories())
        score = player.scorecard.score_category(category, dice_set.get_values())
        if not silent:
            print(f"{player.name} scored {score} in '{category}'")

    def play_game(self, silent=False):
        while not all(p.scorecard.is_complete() for p in self.players):
            for player in self.players:
                if not player.scorecard.is_complete():
                    self.play_turn(player, silent=silent)

        scores = {p.name: p.scorecard.total() for p in self.players}
        winner = max(scores, key=scores.get)
        if not silent:
            print(f"\nFinal Scores: {scores}")
            print(f"The winner is: {winner}")


class Benchmark:
    def __init__(self, num_games=1000):
        self.num_games = num_games

    def run(self):
        optimal_wins = 0
        random_wins = 0
        optimal_scores = []
        random_scores = []

        for i in range(self.num_games):
            if (i + 1) % 100 == 0:
                print(f"  Running game {i+1}/{self.num_games}...")
            bot1 = OptimalBot("OptimalBot")
            bot2 = GreedyBot("GreedyBot")
            game = YahtzeeGame(bot1, bot2)
            game.play_game(silent=True)

            o = bot1.scorecard.total()
            r = bot2.scorecard.total()
            optimal_scores.append(o)
            random_scores.append(r)
            if o > r:
                optimal_wins += 1
            else:
                random_wins += 1

        o_avg = sum(optimal_scores) / len(optimal_scores)
        r_avg = sum(random_scores) / len(random_scores)
        o_max = max(optimal_scores)
        r_max = max(random_scores)
        o_min = min(optimal_scores)
        r_min = min(random_scores)

        print(f"\n{'='*44}")
        print(f"  BENCHMARK RESULTS  ({self.num_games} games)")
        print(f"{'='*44}")
        print(f"  {'':20} {'OptimalBot':>10} {'GreedyBot':>10}")
        print(f"  {'-'*40}")
        print(f"  {'Win rate':20} {f'{100*optimal_wins/self.num_games:.1f}%':>10} {f'{100*random_wins/self.num_games:.1f}%':>10}")
        print(f"  {'Avg score':20} {o_avg:>10.1f} {r_avg:>10.1f}")
        print(f"  {'Max score':20} {o_max:>10} {r_max:>10}")
        print(f"  {'Min score':20} {o_min:>10} {r_min:>10}")
        print(f"{'='*44}")
        self.plot(optimal_scores, random_scores)

    def plot(self, optimal_scores, random_scores):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(optimal_scores, bins=30, alpha=0.7, color='steelblue', label='OptimalBot')
        ax.hist(random_scores,  bins=30, alpha=0.7, color='tomato',    label='RandomBot')

        o_avg = sum(optimal_scores) / len(optimal_scores)
        r_avg = sum(random_scores)  / len(random_scores)

        ax.axvline(o_avg, color='steelblue', linestyle='--', linewidth=1.5, label=f'OptimalBot mean ({o_avg:.0f})')
        ax.axvline(r_avg, color='tomato',    linestyle='--', linewidth=1.5, label=f'RandomBot mean ({r_avg:.0f})')

        ax.set_title(f'Yahtzee Score Distribution over {len(optimal_scores)} Games', fontsize=14)
        ax.set_xlabel('Final Score')
        ax.set_ylabel('Frequency')
        ax.legend()
        plt.tight_layout()
        plt.savefig('yahtzee_benchmark.png', dpi=150)
        print(f"\n  Chart saved to yahtzee_benchmark.png")

# run
if __name__ == '__main__':
    print("Note: First run may be slow while MDP cache warms up.\n")

    # single game demo
    bot1 = OptimalBot("OptimalBot")
    bot2 = GreedyBot("GreedyBot")
    game = YahtzeeGame(bot1, bot2)
    game.play_game()

    # benchmark
    print("\nRunning benchmark (100000 games)...")
    Benchmark(num_games=100000).run()
