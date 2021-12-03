## Steps to run the code
### Install necessary dependency
    pip install -U numpy pygame

### Run
In `main.py`, there are three methods to run the game. Use `wasd` or arrow key to move, `r` to reset game, `q`
to quit.
#### Player plays by terminal input
Uncomment this block then comment everything else
```python
sokoban_game = SokobanTerminal(input_file)
sokoban_game.play()
```

#### Player plays by pygame console
Uncomment this block then comment everything else
```python
sokoban_game = SokobanPygame(input_file)
sokoban_game.play()
```

#### Let the RNG god decide which move to play
Uncomment everything except the two block above. `q` to quit, `w` to speed up, `s` to slow down. 
Use and adapt this for MC/DFS/etc.

## Code structure if you want to understand
`util.py`: Utility function for converting txt to board data, etc. \
`main.py`: Example/script to run the game interactively. \
`SokobanGame.py`: Processing I/O like render/get input, game loop, etc. \
`Sokoban.py`: Probably the most important you need to know. This has the core game logic.
Two most important methods are `actions = get_current_valid_moves` and `move(action)`
