#!/usr/bin/env python

import pyglet
from pyglet.window import key

CELL_SIZE = 32
MOVE_SPEED = 3

window = pyglet.window.Window()

game_over = False
win = False
score = 0
collidables = {}
apples = {}
wall = []

game_over_label = pyglet.text.Label('Game Over',
                                    font_name='Times New Roman',
                                    font_size=36,
                                    x=window.width//2, y=window.height//2,
                                    anchor_x='center', anchor_y='center')
win_label = pyglet.text.Label('You Win!',
                                    font_name='Times New Roman',
                                    font_size=36,
                                    x=window.width//2, y=window.height//2,
                                    anchor_x='center', anchor_y='center')
score_label = pyglet.text.Label(font_name='Times New Roman',
                                font_size=24,
                                x=window.width * 0.75, y=window.height * 0.9,
                                anchor_x='center', anchor_y='center')

class Sprite:
    image = pyglet.resource.image
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
class Apple(Sprite):
    image = pyglet.resource.image('apple.png')

class WallSegment(Sprite):
    image = pyglet.resource.image('wall.png')
    
class SnakeSegment(Sprite):
    image = pyglet.resource.image('smile_icon.png')

class Snake:
    def __init__(self, x=CELL_SIZE, y=window.height//2, tail_len=3):
        self.x = x
        self._x = self.x
        self.y = y
        self._y = self.y
        self.image = pyglet.resource.image('smile_icon.png')
        self.xdir = 1
        self.ydir = 0
        self.tail = []
        self.tail_len = tail_len

    def update(self, dt):
        self._x = (self.xdir * MOVE_SPEED) + self._x
        self._y = (self.ydir * MOVE_SPEED) + self._y
        rounded_x = (self._x // CELL_SIZE) * CELL_SIZE
        rounded_y = (self._y // CELL_SIZE) * CELL_SIZE
        if self.x != rounded_x or self.y != rounded_y:
            # Add a new tail segment and update location
            self.update_tail()
            self.x = rounded_x
            self.y = rounded_y

    def update_tail(self):
        if self.tail == [] or self.tail[0].x != self.x or self.tail[0].y != self.y:
            self.tail.insert(0, SnakeSegment(self.x, self.y))
            collidables[(self.x, self.y)] = self.tail[0]
            if len(self.tail) > self.tail_len:
                old_segment = self.tail.pop()
                del(collidables[(old_segment.x, old_segment.y)])

    def draw(self):
        self.image.blit(self.x, self.y)
        for s in self.tail:
            s.image.blit(s.x, s.y)

# Parse the level file and build the map
f = open('level.txt', 'r')
level_lines = f.readlines()
f.close()
for y in range(len(level_lines)):
    for x in range(len(level_lines[y])):
        elem = level_lines[y][x]
        x_cell = x * CELL_SIZE
        y_cell = window.height - (y * CELL_SIZE)
        if elem in ['+', '-', '|']:
            w = WallSegment(x_cell, y_cell)
            wall.append(w)
            collidables[(x_cell, y_cell)] = w
        elif elem == 'a':
            a = Apple(x_cell, y_cell)
            apples[(x_cell,y_cell)] = a
            

snake = Snake()

@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.LEFT:
        snake.xdir = -1
        snake.ydir = 0
    elif symbol == key.RIGHT:
        snake.xdir = 1
        snake.ydir = 0
    elif symbol == key.UP:
        snake.xdir = 0
        snake.ydir = 1
    elif symbol == key.DOWN:
        snake.xdir = 0
        snake.ydir = -1

@window.event
def on_draw():
    window.clear()
    for w in wall:
        w.image.blit(w.x, w.y)
    for a in apples.values():
        a.image.blit(a.x,a.y)    
    snake.draw()
    score_label.text = "Score: %d" % score
    score_label.draw()
    if game_over:
        game_over_label.draw()
    if win:
        win_label.draw()

def update(dt):
    global game_over
    global score
    global win
    if not game_over and not win:
        if (snake.x, snake.y) in apples.keys():
            del(apples[(snake.x, snake.y)])
            snake.tail_len += 1
            score += 1
            if apples == {}:
                win = True
        if (snake.x, snake.y) in collidables.keys():
            game_over = True
            return
        snake.update(dt)

pyglet.clock.schedule(update)
pyglet.app.run()
