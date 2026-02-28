import pyxel
import math

class Wave:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rad = 0
        self.speed = 1.5
        self.alive = True
    
    def update(self):
        self.rad += self.speed
        # 画面外（対角線最大値程度）まで広がったら消す
        if self.rad > 200:
            self.alive = False

    def draw(self):
        if self.alive:
            # 波紋の描画（円）
            pyxel.circb(self.x, self.y, self.rad, 7)

class Attacker:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.speed = 2
        self.color = 8
        self.waves = []
    
    def update(self):
        # 移動 (WASD)
        if pyxel.btn(pyxel.KEY_A) and self.x > 0: self.x -= self.speed
        if pyxel.btn(pyxel.KEY_D) and self.x < pyxel.width: self.x += self.speed
        if pyxel.btn(pyxel.KEY_W) and self.y > 0: self.y -= self.speed
        if pyxel.btn(pyxel.KEY_S) and self.y < pyxel.height: self.y += self.speed
        
        # 攻撃 (SPACE)
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.waves.append(Wave(self.x, self.y))
            self.color = 1 # 撃った瞬間だけ色を変える
        else:
            self.color = 8
            
        # 波紋の更新と、不要な波紋の削除
        for w in self.waves:
            w.update()
        self.waves = [w for w in self.waves if w.alive]

    def draw(self):
        # 攻撃側のキャラ表示
        pyxel.rect(self.x - 2, self.y - 5, 4, 10, self.color)

class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.speed = 2
        self.alive = True
    
    def update(self):
        if not self.alive: return
        # 移動 (矢印キー)
        if pyxel.btn(pyxel.KEY_LEFT): self.x -= self.speed
        if pyxel.btn(pyxel.KEY_RIGHT): self.x += self.speed
        if pyxel.btn(pyxel.KEY_UP): self.y -= self.speed
        if pyxel.btn(pyxel.KEY_DOWN): self.y += self.speed

    def draw(self):
        if self.alive:
            # プレイヤーの表示
            pyxel.rect(self.x - 1, self.y - 1, 3, 3, 11)

class App:
    def __init__(self):
        pyxel.init(160, 120, title="HaMon - Ripple Defense")
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.player = Player(80, 60)
        self.attacker = Attacker(20, 20)
        self.game_over = False

    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R): self.reset()
            return

        self.player.update()
        self.attacker.update()

        # 当たり判定のチェック
        for w in self.attacker.waves:
            # プレイヤーと波紋の中心点との距離を計算
            dist = math.sqrt((w.x - self.player.x)**2 + (w.y - self.player.y)**2)
            
            # 距離が波紋の半径とほぼ一致（誤差2ピクセル以内）したら当たり
            if abs(dist - w.rad) < 2:
                self.player.alive = False
                self.game_over = True

    def draw(self):
        pyxel.cls(0)
        
        # 波紋の描画
        for w in self.attacker.waves:
            w.draw()
            
        self.attacker.draw()
        self.player.draw()
        
        if self.game_over:
            pyxel.text(60, 55, "GAME OVER", 7)
            pyxel.text(50, 65, "Press R to Restart", 6)

App()