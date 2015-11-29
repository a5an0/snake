#!/usr/bin/env python

import pyglet
from pyglet.window import key

CELL_SIZE = 32
MOVE_SPEED = 3

window = pyglet.window.Window()

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
class Game:
    def __init__(self, level_file_name):
        self.level_file_name = level_file_name
        self.reset()
        
    def reset(self):
        self.game_over = False
        self.win = False
        self.score = 0
        self.level = Level.from_file(self.level_file_name)
        self.snake = Snake(self.level)

    def handle_key_press(self, symbol, modifiers):
        if symbol == key.LEFT:
            self.snake.xdir = -1
            self.snake.ydir = 0
        elif symbol == key.RIGHT:
            self.snake.xdir = 1
            self.snake.ydir = 0
        elif symbol == key.UP:
            self.snake.xdir = 0
            self.snake.ydir = 1
        elif symbol == key.DOWN:
            self.snake.xdir = 0
            self.snake.ydir = -1
        elif symbol == key.ENTER:
            if self.game_over or self.win:
                self.reset()

    def draw_handler(self, window):
        def draw():
            window.clear()
            self.level.draw()
            self.snake.draw()
            score_label.text = "Score: %d" % self.score
            score_label.draw()
            if self.game_over:
                game_over_label.draw()
            if self.win:
                win_label.draw()
        return draw

    def update(self, dt):
        if not self.game_over and not self.win:
            if (self.snake.x, self.snake.y) in self.level.apples.keys():
                del(self.level.apples[(self.snake.x, self.snake.y)])
                self.snake.tail_len += 1
                self.score += 1
                if self.level.apples == {}:
                    self.win = True
            if (self.snake.x, self.snake.y) in self.level.collidables.keys():
                self.game_over = True
                return
            self.snake.update(dt)

                
    
class Level:
    def __init__(self, walls=[], apples={}, collidables={}):
        self.walls = walls
        self.apples = apples
        self.collidables = collidables

    def draw(self):
        for w in self.walls:
            w.image.blit(w.x, w.y)
        for a in self.apples.values():
            a.image.blit(a.x,a.y)    

        
    @classmethod
    def from_file(cls, filename):
        apples = {}
        walls = []
        collidables = {}
        f = open(filename, 'r')
        level_lines = f.readlines()
        f.close()
        for y in range(len(level_lines)):
            for x in range(len(level_lines[y])):
                elem = level_lines[y][x]
                x_cell = x * CELL_SIZE
                y_cell = window.height - (y * CELL_SIZE)
                if elem in ['+', '-', '|']:
                    w = WallSegment(x_cell, y_cell)
                    walls.append(w)
                    collidables[(x_cell, y_cell)] = w
                elif elem == 'a':
                    a = Apple(x_cell, y_cell)
                    apples[(x_cell,y_cell)] = a
        return cls(walls, apples, collidables)


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
    def __init__(self, level, x=CELL_SIZE, y=window.height//2, tail_len=3):
        self.level = level
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
            self.level.collidables[(self.x, self.y)] = self.tail[0]
            if len(self.tail) > self.tail_len:
                old_segment = self.tail.pop()
                del(self.level.collidables[(old_segment.x, old_segment.y)])

    def draw(self):
        self.image.blit(self.x, self.y)
        for s in self.tail:
            s.image.blit(s.x, s.y)


game = Game('level.txt')

window.on_key_press = game.handle_key_press
window.on_draw = game.draw_handler(window)

pyglet.clock.schedule(game.update)
pyglet.app.run()
