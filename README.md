# Yahtzee Markov Decision Process Solver

Optimal single-turn reroll policy via backward induction over all 252 sorted dice states.
Benchmarked against a greedy baseline over 100k simulated games.

## Results
- Optimal bot wins 60.3% of games vs greedy
- Average score: 152 (optimal) vs 140 (greedy)

## Notes
- First game will be much slower than subsequent runs due to MDP cache warming up
- Total runtime might be long depending on machine (reduce to 10k runs if needed)

## Files
- `solver.py` — MDP solver, computes expected value for every (dice, rolls_left) state
- `yahtzee.py` — game engine, bots (optimal, greedy, random) and benchmark runner

## Usage
- Download both python files
- Run `yahtzee.py`
- First game plays out, then simulation of 100k games

