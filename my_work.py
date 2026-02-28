"""
Attacker が攻撃すると波紋が拡がる
Player はそれを守る方
"""
import pyxel
import random

class Wave:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rad = 0
        self.speed = 1
        self.alive = True
    
    def update(self):
        self.rad += self.speed

    def draw(self):
        if self.alive:
            pyxel.circb(self.x, self.y, self.rad, 7)

class Attacker:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 1
        self.color = 8
        self.waves = []
    
    def update(self):
        if pyxel.btn(pyxel.KEY_A) and self.x-self.speed >=1:
            self.x -= self.speed
        if pyxel.btn(pyxel.KEY_D) and self.x+self.speed <=pyxel.width-3:
            self.x += self.speed
        if pyxel.btn(pyxel.KEY_W) and self.y-self.speed >=0:
            self.y -= self.speed
        if pyxel.btn(pyxel.KEY_S) and self.y+self.speed <=pyxel.height-10:
            self.y += self.speed
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.color = 1
            self.waves.append(Wave(self.x+1, self.y+9))
        else:
            self.color = 8

    def draw(self):
        pyxel.rect(self.x, self.y, 2, 10, self.color)
        pyxel.rect(self.x-1, self.y, 4, 6, self.color)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 2
        self.alive = True
    
    def update(self):
        if pyxel.btn(pyxel.KEY_LEFT) and self.x-self.speed >=0:
            self.x -= self.speed
        if pyxel.btn(pyxel.KEY_RIGHT) and self.x+self.speed <=pyxel.width-2:
            self.x += self.speed
        if pyxel.btn(pyxel.KEY_UP) and self.y-self.speed >=0:
            self.y -= self.speed
        if pyxel.btn(pyxel.KEY_DOWN) and self.y+self.speed <=pyxel.height-2:
            self.y += self.speed

    def draw(self):
        if self.alive:
            pyxel.rect(self.x, self.y, 2, 2, 2)

class App:
    def __init__(self):
        pyxel.init(160, 120, title="HaMon")
        #pyxel.load("my_work.pyxres")

        self.player = Player(4,4)
        self.attacker = Attacker(10,10)

        pyxel.run(self.update, self.draw)

    def update(self):
        self.player.update()
        for w in self.attacker.waves:
            w.update()
            #print(w.rad**2,(w.x-self.player.x)**2 +(w.y-self.player.y)**2)
            if w.rad**2//100 == ((w.x-self.player.x)**2 + (w.y-self.player.y)**2) //100:
                w.alive=False
                self.player.alive=False
        self.attacker.update()
        

    def draw(self):
        pyxel.cls(0)
        self.player.draw()
        for w in self.attacker.waves:
            w.draw()
        self.attacker.draw()
        

App()