"""
HaMon - 対戦版（双方が攻撃・防御）
二人のファイターが互いに波を撃ち合い、ガードで防ぎつつ相手に当てる。
"""
import pyxel
import math
import random

# --- 共通クラス ---

class Wave:
    def __init__(self, x, y, is_critical=False, owner_id=0):
        self.x, self.y = x, y
        self.rad = 0
        self.speed = 1.5
        self.alive = True
        self.is_critical = is_critical
        self.owner_id = owner_id

    def update(self):
        self.rad += self.speed
        if self.rad > 200:
            self.alive = False

    def draw(self, color_normal=7, color_critical=8):
        if self.alive:
            color = color_critical if self.is_critical else color_normal
            pyxel.circb(self.x, self.y, self.rad, color)


class Fighter:
    """攻撃・防御の両方を行うキャラ。キー配置で P1 / P2 を切り替え。"""

    def __init__(self, x, y, keys, color_guard=10, color_idle=11, wave_color=7, wave_crit=8):
        self.x, self.y = x, y
        self.speed = 2
        self.alive = True
        self.gauge = 100
        self.max_gauge = 100
        self.is_guarding = False
        self.guard_block_frames = 0
        self.waves = []
        self.shot_cooldown = 0
        self.cooldown_time = 24
        self.keys = keys
        self.color_guard = color_guard
        self.color_idle = color_idle
        self.wave_color = wave_color
        self.wave_crit = wave_crit
        self.safe_zone_radius = 24

    def update(self, other_x, other_y):
        if not self.alive:
            return
        k = self.keys
        if pyxel.btn(k["left"]):  self.x -= self.speed
        if pyxel.btn(k["right"]): self.x += self.speed
        if pyxel.btn(k["up"]):    self.y -= self.speed
        if pyxel.btn(k["down"]):  self.y += self.speed

        self.x = max(2, min(pyxel.width - 3, self.x))
        self.y = max(2, min(pyxel.height - 3, self.y))

        if pyxel.btn(k["guard"]) and self.gauge > 0:
            if self.guard_block_frames <= 0:
                self.is_guarding = True
                self.gauge -= 0.6
            else:
                self.is_guarding = False
        else:
            self.is_guarding = False

        if self.guard_block_frames > 0:
            self.guard_block_frames -= 1

        if self.shot_cooldown > 0:
            self.shot_cooldown -= 1
        if pyxel.btnp(k["shoot"]) and self.shot_cooldown == 0:
            dist_to_other = math.sqrt((self.x - other_x) ** 2 + (self.y - other_y) ** 2)
            if dist_to_other >= self.safe_zone_radius:
                is_critical = random.random() < 0.12
                self.waves.append(
                    Wave(self.x, self.y, is_critical=is_critical, owner_id=id(self))
                )
                self.shot_cooldown = self.cooldown_time

        for w in self.waves:
            w.update()
        self.waves = [w for w in self.waves if w.alive]

    def draw(self):
        if not self.alive:
            return
        color = self.color_guard if self.is_guarding else self.color_idle
        pyxel.rect(self.x - 2, self.y - 2, 5, 5, color)
        if self.is_guarding:
            pyxel.circb(self.x, self.y, 6, self.color_guard)
        if self.guard_block_frames > 0:
            pyxel.text(self.x - 14, self.y - 24, "NO GUARD!", 8)


P1_KEYS = {
    "left": pyxel.KEY_LEFT, "right": pyxel.KEY_RIGHT,
    "up": pyxel.KEY_UP, "down": pyxel.KEY_DOWN,
    "guard": pyxel.KEY_K, "shoot": pyxel.KEY_L,
}
P2_KEYS = {
    "left": pyxel.KEY_A, "right": pyxel.KEY_D,
    "up": pyxel.KEY_W, "down": pyxel.KEY_S,
    "guard": pyxel.KEY_B, "shoot": pyxel.KEY_V,
}


class App:
    def __init__(self):
        pyxel.init(160, 120, title="HaMon - Versus")
        self.state = "MENU"
        self.time_limit = 30 * 60
        pyxel.run(self.update, self.draw)

    def reset(self):
        while True:
            p1_x, p1_y = random.randint(20, 70), random.randint(30, 90)
            p2_x, p2_y = random.randint(90, 140), random.randint(30, 90)
            dist = math.sqrt((p1_x - p2_x) ** 2 + (p1_y - p2_y) ** 2)
            if dist > 50:
                break
        self.p1 = Fighter(
            p1_x, p1_y, P1_KEYS,
            color_guard=10, color_idle=11, wave_color=7, wave_crit=8
        )
        self.p2 = Fighter(
            p2_x, p2_y, P2_KEYS,
            color_guard=12, color_idle=13, wave_color=4, wave_crit=2
        )
        self.start_frame = pyxel.frame_count
        self.game_state = "PLAYING"
        self.winner = None
        self.remaining_time = self.time_limit

    def update(self):
        if self.state == "MENU":
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
                self.reset()
                self.state = "GAME"

        elif self.state == "GAME":
            if self.game_state != "PLAYING":
                if pyxel.btnp(pyxel.KEY_R):
                    self.reset()
                if pyxel.btnp(pyxel.KEY_M):
                    self.state = "MENU"
                return

            self.p1.update(self.p2.x, self.p2.y)
            self.p2.update(self.p1.x, self.p1.y)

            if not self.p1.alive:
                self.game_state = "GAMEOVER"
                self.winner = "P2"
            if not self.p2.alive:
                self.game_state = "GAMEOVER"
                self.winner = "P1"

            elapsed = pyxel.frame_count - self.start_frame
            self.remaining_time = max(0, self.time_limit - elapsed)
            if self.remaining_time <= 0 and self.winner is None:
                self.game_state = "DRAW"
                return

            for w in self.p1.waves:
                dist = math.sqrt((w.x - self.p2.x) ** 2 + (w.y - self.p2.y) ** 2)
                if abs(dist - w.rad) < 3:
                    if self.p2.is_guarding:
                        w.alive = False
                        if w.is_critical:
                            self.p2.guard_block_frames = 30
                            self.p2.is_guarding = False
                        self.p2.gauge = min(self.p2.max_gauge, self.p2.gauge + 14)
                    else:
                        self.p2.alive = False
                        self.game_state = "GAMEOVER"
                        self.winner = "P1"

            for w in self.p2.waves:
                dist = math.sqrt((w.x - self.p1.x) ** 2 + (w.y - self.p1.y) ** 2)
                if abs(dist - w.rad) < 3:
                    if self.p1.is_guarding:
                        w.alive = False
                        if w.is_critical:
                            self.p1.guard_block_frames = 30
                            self.p1.is_guarding = False
                        self.p1.gauge = min(self.p1.max_gauge, self.p1.gauge + 14)
                    else:
                        self.p1.alive = False
                        self.game_state = "GAMEOVER"
                        self.winner = "P2"

    def draw(self):
        pyxel.cls(0)
        if self.state == "MENU":
            pyxel.text(25, 28, "HaMon Versus", pyxel.frame_count % 16)
            pyxel.line(5, 40, 155, 40, 7)
            pyxel.text(5, 55, "P1: Arrows Move  K Guard  L Shoot", 11)
            pyxel.text(5, 68, "P2: WASD Move   B Guard  V Shoot", 13)
            pyxel.text(15, 95, "ENTER: Start  R:Restart  M:Menu", 6)

        elif self.state == "GAME":
            for i in range(0, 160, 20):
                pyxel.line(i, 0, i, 120, 1)
            pyxel.line(80, 0, 80, 120, 1)

            for w in self.p1.waves:
                w.draw(color_normal=self.p1.wave_color, color_critical=self.p1.wave_crit)
            for w in self.p2.waves:
                w.draw(color_normal=self.p2.wave_color, color_critical=self.p2.wave_crit)
            self.p1.draw()
            self.p2.draw()

            pyxel.text(5, 3, "P1", 11)
            pyxel.rect(18, 3, 25, 4, 13)
            pyxel.rect(18, 3, self.p1.gauge // 4, 4, 10)
            pyxel.text(95, 3, "P2", 13)
            pyxel.rect(108, 3, 25, 4, 13)
            pyxel.rect(108, 3, self.p2.gauge // 4, 4, 12)
            pyxel.text(60, 3, f"{self.remaining_time // 30}s", 7)

            if self.game_state == "GAMEOVER":
                if self.winner == "P1":
                    pyxel.text(55, 48, "P1 WIN!", 11)
                else:
                    pyxel.text(55, 48, "P2 WIN!", 13)
                pyxel.text(45, 72, "R:Restart / M:Menu", 6)
            elif self.game_state == "DRAW":
                pyxel.text(60, 55, "DRAW!", 7)
                pyxel.text(45, 75, "R:Restart / M:Menu", 6)


App()
