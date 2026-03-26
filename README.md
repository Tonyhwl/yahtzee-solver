# Yahtzee Markov Decision Process Solver

Optimal single-turn reroll policy via backward induction over all 252 sorted dice states.
Benchmarked against a greedy baseline over 10k simulated games.

## Results
- Optimal bot wins 92.5% of games vs greedy
- Average score: 210 (optimal) vs 140 (greedy)

## Notes
- First game will be much slower than subsequent runs due to MDP cache warming up

## Files
- `yahtzee.py` — game engine, bots (optimal, greedy, random) and benchmark runner

## Usage
- Download file
- Run `yahtzee.py`
- First game plays out, then simulation of 10k games

