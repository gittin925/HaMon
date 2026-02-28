import pyxel
import math

class Wave:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.rad = 0
        self.speed = 1.5
        self.alive = True
    
    def update(self):
        self.rad += self.speed
        if self.rad > 200: self.alive = False

    def draw(self):
        if self.alive:
            pyxel.circb(self.x, self.y, self.rad, 7)

class Attacker:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.speed = 1.5
        self.waves = []
    
    def update(self):
        if pyxel.btn(pyxel.KEY_A): self.x -= self.speed
        if pyxel.btn(pyxel.KEY_D): self.x += self.speed
        if pyxel.btn(pyxel.KEY_W): self.y -= self.speed
        if pyxel.btn(pyxel.KEY_S): self.y += self.speed
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.waves.append(Wave(self.x, self.y))
        for w in self.waves: w.update()
        self.waves = [w for w in self.waves if w.alive]

    def draw(self):
        pyxel.rect(self.x - 2, self.y - 5, 4, 10, 8)

class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.speed = 2
        self.alive = True
        self.gauge = 100
        self.max_gauge = 100
        self.is_guarding = False
        
        # 静止ペナルティ用
        self.still_frames = 0
        self.max_still_time = 30 * 3  # 3秒間止まったらアウト
    
    def update(self):
        if not self.alive: return
        
        moved = False
        if pyxel.btn(pyxel.KEY_LEFT): self.x -= self.speed; moved = True
        if pyxel.btn(pyxel.KEY_RIGHT): self.x += self.speed; moved = True
        if pyxel.btn(pyxel.KEY_UP): self.y -= self.speed; moved = True
        if pyxel.btn(pyxel.KEY_DOWN): self.y += self.speed; moved = True

        # 静止判定の更新
        if moved:
            self.still_frames = 0
        else:
            self.still_frames += 1
            if self.still_frames >= self.max_still_time:
                self.alive = False

        # ガード
        if (pyxel.btn(pyxel.KEY_SHIFT) or pyxel.btn(pyxel.KEY_Z)) and self.gauge > 0:
            self.is_guarding = True
            self.gauge -= 0.5
        else:
            self.is_guarding = False

    def draw(self):
        if not self.alive: return
        color = 10 if self.is_guarding else 11
        pyxel.rect(self.x - 2, self.y - 2, 5, 5, color)
        if self.is_guarding:
            pyxel.circb(self.x, self.y, 6, 10)
        
        # 止まっている時の警告表示
        if self.still_frames > 30: # 1秒以上止まったら
            warn_color = 7 if pyxel.frame_count % 10 < 5 else 8
            pyxel.text(self.x - 10, self.y - 12, "MOVE!", warn_color)

class App:
    def __init__(self):
        pyxel.init(160, 120, title="HaMon - Don't Stop")
        self.time_limit = 30 * 30 
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.player = Player(80, 80)
        self.attacker = Attacker(80, 20)
        self.start_frame = pyxel.frame_count
        self.state = "PLAYING"
        self.cause = "" # ゲームオーバーの原因用

    def update(self):
        if self.state != "PLAYING":
            if pyxel.btnp(pyxel.KEY_R): self.reset()
            return

        self.player.update()
        self.attacker.update()

        # 静止死判定
        if not self.player.alive:
            self.state = "GAMEOVER"
            self.cause = "DON'T STOP!"

        # 時間勝利
        elapsed = pyxel.frame_count - self.start_frame
        self.remaining_time = max(0, self.time_limit - elapsed)
        if self.remaining_time <= 0:
            self.state = "WIN"

        # 波紋当たり判定
        for w in self.attacker.waves:
            dist = math.sqrt((w.x - self.player.x)**2 + (w.y - self.player.y)**2)
            if abs(dist - w.rad) < 3:
                if self.player.is_guarding:
                    w.alive = False
                    self.player.gauge = min(self.player.max_gauge, self.player.gauge + 20)
                else:
                    self.player.alive = False
                    self.state = "GAMEOVER"
                    self.cause = "RIPPLE HIT"

    def draw(self):
        pyxel.cls(0)
        for i in range(0, 160, 20): pyxel.line(i, 0, i, 120, 1)
        
        for w in self.attacker.waves: w.draw()
        self.attacker.draw()
        self.player.draw()
        
        # UI: ゲージ
        pyxel.text(5, 5, "GAUGE", 7)
        pyxel.rect(30, 5, 50, 4, 13)
        pyxel.rect(30, 5, self.player.gauge // 2, 4, 10)
        
        # UI: 静止警告ゲージ（足元）
        if self.player.still_frames > 0:
            p_width = (self.player.still_frames / self.player.max_still_time) * 16
            pyxel.rect(self.player.x - 8, self.player.y + 6, 16, 2, 13)
            pyxel.rect(self.player.x - 8, self.player.y + 6, p_width, 2, 8)

        # UI: タイマー
        pyxel.text(120, 5, f"TIME: {self.remaining_time // 30}", 7)

        if self.state == "GAMEOVER":
            pyxel.text(60, 50, "GAME OVER", 8)
            pyxel.text(60, 60, self.cause, 7)
            pyxel.text(50, 75, "Press R to Restart", 6)
        elif self.state == "WIN":
            pyxel.text(65, 55, "YOU WIN!", 11)
            pyxel.text(50, 65, "Press R to Restart", 7)

App()