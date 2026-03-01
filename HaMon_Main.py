import pyxel
import math
import random

# --- 共通クラス ---

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

        # --- 画面外に出ないように制限 ---
        self.x = max(2, min(pyxel.width - 3, self.x))
        self.y = max(2, min(pyxel.height - 3, self.y))

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

# --- 敵クラス ---

class AttackerHuman:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.speed = 1.5
        self.waves = []
        self.shot_cooldown = 0
        self.cooldown_time = 20 
    
    def update(self, *args):
        if pyxel.btn(pyxel.KEY_A): self.x -= self.speed
        if pyxel.btn(pyxel.KEY_D): self.x += self.speed
        if pyxel.btn(pyxel.KEY_W): self.y -= self.speed
        if pyxel.btn(pyxel.KEY_S): self.y += self.speed
        
        # --- 画面外に出ないように制限 ---
        self.x = max(2, min(pyxel.width - 3, self.x))
        self.y = max(5, min(pyxel.height - 5, self.y))

        if self.shot_cooldown > 0: self.shot_cooldown -= 1
        
        if pyxel.btnp(pyxel.KEY_LSHIFT) and self.shot_cooldown == 0:
            self.waves.append(Wave(self.x, self.y))
            self.shot_cooldown = self.cooldown_time
            
        for w in self.waves: w.update()
        self.waves = [w for w in self.waves if w.alive]

    def draw(self):
        color = 8 if self.shot_cooldown == 0 else 2
        pyxel.rect(self.x - 2, self.y - 5, 4, 10, color)
        if self.shot_cooldown == 0: pyxel.pset(self.x, self.y - 7, 7)

class AttackerAuto:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.speed = 1.2
        self.waves = []
        self.state = "IDLE"
        self.timer = 0
    
    def update(self, target_x, target_y):
        dist_x, dist_y = target_x - self.x, target_y - self.y
        distance = math.sqrt(dist_x**2 + dist_y**2)

        if distance > 45:
            self.x += self.speed if dist_x > 0 else -self.speed
            self.y += self.speed if dist_y > 0 else -self.speed
        elif distance < 35:
            self.x -= self.speed if dist_x > 0 else -self.speed
            self.y -= self.speed if dist_y > 0 else -self.speed
        
        # --- 画面外制限（AI用） ---
        self.x = max(5, min(pyxel.width - 5, self.x))
        self.y = max(5, min(pyxel.height - 5, self.y))

        self.timer -= 1
        if self.state == "IDLE" and self.timer <= 0:
            self.state = "CHARGING"
            self.timer = random.randint(10, 30)
        elif self.state == "CHARGING" and self.timer <= 0:
            self.waves.append(Wave(self.x, self.y))
            self.state = "IDLE"
            self.timer = random.randint(5, 50)
            
        for w in self.waves: w.update()
        self.waves = [w for w in self.waves if w.alive]

    def draw(self):
        color = (8 if pyxel.frame_count % 4 < 2 else 7) if self.state == "CHARGING" else 13
        pyxel.rect(self.x - 2, self.y - 5, 4, 10, color)
        if self.state == "CHARGING": pyxel.circb(self.x, self.y, self.timer // 2, 8)

# --- メインアプリケーションクラス ---

class App:
    def __init__(self):
        pyxel.init(160, 120, title="HaMon - Integrated")
        self.state = "MENU"
        self.selected_index = 0
        self.modes = ["1 PLAYER  [ VS CPU ]", "2 PLAYERS [ VS HUMAN ]"]
        self.time_limit = 30 * 30
        pyxel.run(self.update, self.draw)

    def reset(self, mode):
        # プレイヤーと敵が近すぎないように配置を決定
        while True:
            p_x, p_y = random.randint(10, 150), random.randint(10, 110)
            a_x, a_y = random.randint(10, 150), random.randint(10, 110)
            
            # 距離の計算 (ピタゴラスの定理)
            dist = math.sqrt((p_x - a_x)**2 + (p_y - a_y)**2)
            
            # 60ピクセル以上離れていればOK
            if dist > 60:
                break

        self.player = Player(p_x, p_y)
        
        if mode == 0: # Auto
            self.attacker = AttackerAuto(a_x, a_y)
            self.mode = "AUTO"
        else: # Human
            self.attacker = AttackerHuman(a_x, a_y)
            self.mode = "HUMAN"
            
        self.start_frame = pyxel.frame_count
        self.game_state = "PLAYING"
        self.cause = ""
        self.remaining_time = self.time_limit

    def update(self):
        if self.state == "MENU":
            if pyxel.btnp(pyxel.KEY_UP): self.selected_index = (self.selected_index - 1) % 2
            if pyxel.btnp(pyxel.KEY_DOWN): self.selected_index = (self.selected_index + 1) % 2
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
                self.reset(self.selected_index)
                self.state = "GAME"
        
        elif self.state == "GAME":
            if self.game_state != "PLAYING":
                if pyxel.btnp(pyxel.KEY_R): self.reset(0 if self.mode == "AUTO" else 1)
                if pyxel.btnp(pyxel.KEY_M): self.state = "MENU"
                return

            self.player.update()
            self.attacker.update(self.player.x, self.player.y)

            if not self.player.alive:
                self.game_state = "GAMEOVER"
                self.cause = "DON'T STOP!" if self.player.still_frames >= self.player.max_still_time else "RIPPLE HIT"

            elapsed = pyxel.frame_count - self.start_frame
            self.remaining_time = max(0, self.time_limit - elapsed)
            if self.remaining_time <= 0: self.game_state = "WIN"

            for w in self.attacker.waves:
                dist = math.sqrt((w.x - self.player.x)**2 + (w.y - self.player.y)**2)
                if abs(dist - w.rad) < 3:
                    if self.player.is_guarding:
                        w.alive = False
                        self.player.gauge = min(self.player.max_gauge, self.player.gauge + (11 if self.mode == "AUTO" else 15))
                    else:
                        self.player.alive = False
                        self.game_state = "GAMEOVER"
                        self.cause = "RIPPLE HIT"

    def draw(self):
        pyxel.cls(0)
        if self.state == "MENU":
            pyxel.text(65, 30, "Ha Mon", pyxel.frame_count % 16)
            pyxel.line(40, 40, 120, 40, 7)
            for i, m in enumerate(self.modes):
                color = 10 if i == self.selected_index else 7
                prefix = "> " if i == self.selected_index else "  "
                pyxel.text(45, 60 + i * 15, prefix + m, color)
            pyxel.text(35, 100, "PRESS ENTER TO START", 5)
        
        elif self.state == "GAME":
            for i in range(0, 160, 20): pyxel.line(i, 0, i, 120, 1)
            for w in self.attacker.waves: w.draw()
            self.attacker.draw()
            self.player.draw()
            
            pyxel.text(5, 5, "GAUGE", 7)
            pyxel.rect(30, 5, 50, 4, 13)
            pyxel.rect(30, 5, self.player.gauge // 2, 4, 10)
            if self.player.still_frames > 0:
                p_width = (self.player.still_frames / self.player.max_still_time) * 16
                pyxel.rect(self.player.x - 8, self.player.y + 6, 16, 2, 13)
                pyxel.rect(self.player.x - 8, self.player.y + 6, p_width, 2, 8)
            pyxel.text(120, 5, f"TIME: {self.remaining_time // 30}", 7)

            if self.game_state == "GAMEOVER":
                pyxel.text(60, 50, "GAME OVER", 8); pyxel.text(60, 60, self.cause, 7)
                pyxel.text(45, 75, "R:Restart / M:Menu", 6)
            elif self.game_state == "WIN":
                pyxel.text(65, 55, "YOU WIN!", 11)
                pyxel.text(45, 75, "R:Restart / M:Menu", 7)

App()
