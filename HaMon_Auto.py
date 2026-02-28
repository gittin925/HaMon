import pyxel
import math
import random

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
        self.speed = 1.2
        self.waves = []
        self.state = "IDLE" # "IDLE" (待機), "CHARGING" (タメ), "COOLDOWN" (反動)
        self.timer = 0
    
    def update(self, target_x, target_y):
        # --- 移動ロジック ---
        dist_x = target_x - self.x
        dist_y = target_y - self.y
        distance = math.sqrt(dist_x**2 + dist_y**2)

        if distance > 45:
            self.x += self.speed if dist_x > 0 else -self.speed
            self.y += self.speed if dist_y > 0 else -self.speed
        elif distance < 35: # 近すぎたら少し離れる
            self.x -= self.speed if dist_x > 0 else -self.speed
            self.y -= self.speed if dist_y > 0 else -self.speed
        
        # --- 不規則な攻撃ロジック (状態遷移マシン) ---
        self.timer -= 1
        
        if self.state == "IDLE":
            if self.timer <= 0:
                # 待機が終わったら「タメ」に入る (15~40フレームのランダム)
                self.state = "CHARGING"
                self.timer = random.randint(10, 30)
        
        elif self.state == "CHARGING":
            if self.timer <= 0:
                # タメが終わったら発射！
                self.waves.append(Wave(self.x, self.y))
                # 発射後の硬直/次の準備期間 (10~60フレームのランダムで不規則化)
                self.state = "IDLE"
                self.timer = random.randint(5, 50)
            
        for w in self.waves: w.update()
        self.waves = [w for w in self.waves if w.alive]

    def draw(self):
        # 状態に合わせて色を変える
        if self.state == "CHARGING":
            # 発射直前は赤と白で点滅
            color = 8 if pyxel.frame_count % 4 < 2 else 7
            # タメ演出（小さな円を表示）
            pyxel.circb(self.x, self.y, self.timer // 2, 8)
        else:
            color = 13 # 通常時は紫

        pyxel.rect(self.x - 2, self.y - 5, 4, 10, color)

# --- 他のクラス（Player, App）は前回と同じ ---
# （変更がないため省略しますが、そのまま組み合わせて動作します）

class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.speed = 2
        self.alive = True
        self.gauge = 100
        self.max_gauge = 100
        self.is_guarding = False
        self.still_frames = 0
        self.max_still_time = 30 * 3
    
    def update(self):
        if not self.alive: return
        moved = False
        if pyxel.btn(pyxel.KEY_LEFT): self.x -= self.speed; moved = True
        if pyxel.btn(pyxel.KEY_RIGHT): self.x += self.speed; moved = True
        if pyxel.btn(pyxel.KEY_UP): self.y -= self.speed; moved = True
        if pyxel.btn(pyxel.KEY_DOWN): self.y += self.speed; moved = True

        if moved: self.still_frames = 0
        else:
            self.still_frames += 1
            if self.still_frames >= self.max_still_time: self.alive = False

        if (pyxel.btn(pyxel.KEY_SPACE)) and self.gauge > 0:
            self.is_guarding = True
            self.gauge -= 0.6
        else:
            self.is_guarding = False

    def draw(self):
        if not self.alive: return
        color = 10 if self.is_guarding else 11
        pyxel.rect(self.x - 2, self.y - 2, 5, 5, color)
        if self.is_guarding: pyxel.circb(self.x, self.y, 6, 10)
        
        if self.still_frames > 30:
            warn_color = 7 if pyxel.frame_count % 10 < 5 else 8
            pyxel.text(self.x - 10, self.y - 12, "MOVE!", warn_color)

class App:
    def __init__(self):
        pyxel.init(160, 120, title="HaMon - Irregular Rhythm")
        self.time_limit = 30 * 30 
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.player = Player(80, 80)
        self.attacker = Attacker(20, 20)
        self.start_frame = pyxel.frame_count
        self.state = "PLAYING"
        self.cause = ""

    def update(self):
        if self.state != "PLAYING":
            if pyxel.btnp(pyxel.KEY_R): self.reset()
            return

        self.player.update()
        self.attacker.update(self.player.x, self.player.y)

        if not self.player.alive:
            self.state = "GAMEOVER"
            self.cause = "DON'T STOP!" if self.player.still_frames >= self.player.max_still_time else "RIPPLE HIT"

        elapsed = pyxel.frame_count - self.start_frame
        self.remaining_time = max(0, self.time_limit - elapsed)
        if self.remaining_time <= 0: self.state = "WIN"

        for w in self.attacker.waves:
            dist = math.sqrt((w.x - self.player.x)**2 + (w.y - self.player.y)**2)
            if abs(dist - w.rad) < 3:
                if self.player.is_guarding:
                    w.alive = False
                    self.player.gauge = min(self.player.max_gauge, self.player.gauge + 11)
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
        
        # UI
        pyxel.text(5, 5, "GAUGE", 7)
        pyxel.rect(30, 5, 50, 4, 13)
        pyxel.rect(30, 5, self.player.gauge // 2, 4, 10)
        
        if self.player.still_frames > 0:
            p_width = (self.player.still_frames / self.player.max_still_time) * 16
            pyxel.rect(self.player.x - 8, self.player.y + 6, 16, 2, 13)
            pyxel.rect(self.player.x - 8, self.player.y + 6, p_width, 2, 8)

        pyxel.text(120, 5, f"TIME: {self.remaining_time // 30}", 7)

        if self.state == "GAMEOVER":
            pyxel.text(60, 50, "GAME OVER", 8)
            pyxel.text(60, 60, self.cause, 7)
            pyxel.text(50, 75, "Press R to Restart", 6)
        elif self.state == "WIN":
            pyxel.text(65, 55, "YOU WIN!", 11)
            pyxel.text(50, 65, "Press R to Restart", 7)

App()