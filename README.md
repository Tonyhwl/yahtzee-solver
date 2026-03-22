# Yahtzee MDP Solver

Optimal single-turn reroll policy via backward induction over all 252 sorted dice states.
Benchmarked against a greedy baseline over 100k simulated games.

## Results
- Optimal bot wins 60.3% of games vs greedy
- Average score: 152 (optimal) vs 140 (greedy)

## Files
- `solver.py` — MDP solver, computes expected value for every (dice, rolls_left) state
- `yahtzee.py` — game engine, bots (optimal, greedy, random), and benchmark runner

## Usage
- Download both python files
- Run `yahtzee.py`
