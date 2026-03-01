"""
HaMon - 4モード統合版
1. VS CPU  2. VS HUMAN  3. CLICK ATTACK  4. VERSUS
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


class Player:
    """1P用。移動・ガード。クリティカル時は guard_block_frames を使用。"""

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.speed = 2
        self.alive = True
        self.gauge = 100
        self.max_gauge = 100
        self.is_guarding = False
        self.still_frames = 0
        self.max_still_time = 30 * 3
        self.guard_block_frames = 0

    def update(self):
        if not self.alive:
            return
        moved = False
        if pyxel.btn(pyxel.KEY_LEFT):  self.x -= self.speed; moved = True
        if pyxel.btn(pyxel.KEY_RIGHT): self.x += self.speed; moved = True
        if pyxel.btn(pyxel.KEY_UP):    self.y -= self.speed; moved = True
        if pyxel.btn(pyxel.KEY_DOWN):  self.y += self.speed; moved = True

        self.x = max(2, min(pyxel.width - 3, self.x))
        self.y = max(2, min(pyxel.height - 3, self.y))

        if moved:
            self.still_frames = 0
        else:
            self.still_frames += 1
            if self.still_frames >= self.max_still_time:
                self.alive = False

        if pyxel.btn(pyxel.KEY_SPACE) and self.gauge > 0:
            if self.guard_block_frames <= 0:
                self.is_guarding = True
                self.gauge -= 0.6
            else:
                self.is_guarding = False
        else:
            self.is_guarding = False

        if self.guard_block_frames > 0:
            self.guard_block_frames -= 1

    def draw(self):
        if not self.alive:
            return
        color = 10 if self.is_guarding else 11
        pyxel.rect(self.x - 2, self.y - 2, 5, 5, color)
        if self.is_guarding:
            pyxel.circb(self.x, self.y, 6, 10)
        if self.still_frames > 30:
            warn_color = 7 if pyxel.frame_count % 10 < 5 else 8
            pyxel.text(self.x - 10, self.y - 12, "MOVE!", warn_color)
        if self.guard_block_frames > 0:
            pyxel.text(self.x - 14, self.y - 24, "NO GUARD!", 8)


# --- 敵クラス ---

class AttackerAuto:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.speed = 1.2
        self.waves = []
        self.state = "IDLE"
        self.timer = 0

    def update(self, target_x, target_y):
        dist_x, dist_y = target_x - self.x, target_y - self.y
        distance = math.sqrt(dist_x ** 2 + dist_y ** 2)
        if distance > 45:
            self.x += self.speed if dist_x > 0 else -self.speed
            self.y += self.speed if dist_y > 0 else -self.speed
        elif distance < 35:
            self.x -= self.speed if dist_x > 0 else -self.speed
            self.y -= self.speed if dist_y > 0 else -self.speed
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

        for w in self.waves:
            w.update()
        self.waves = [w for w in self.waves if w.alive]

    def draw(self):
        color = (8 if pyxel.frame_count % 4 < 2 else 7) if self.state == "CHARGING" else 13
        pyxel.rect(self.x - 2, self.y - 5, 4, 10, color)
        if self.state == "CHARGING":
            pyxel.circb(self.x, self.y, self.timer // 2, 8)


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
        self.x = max(2, min(pyxel.width - 3, self.x))
        self.y = max(5, min(pyxel.height - 5, self.y))

        if self.shot_cooldown > 0:
            self.shot_cooldown -= 1
        if pyxel.btnp(pyxel.KEY_LSHIFT) and self.shot_cooldown == 0:
            self.waves.append(Wave(self.x, self.y))
            self.shot_cooldown = self.cooldown_time

        for w in self.waves:
            w.update()
        self.waves = [w for w in self.waves if w.alive]

    def draw(self):
        color = 8 if self.shot_cooldown == 0 else 2
        pyxel.rect(self.x - 2, self.y - 5, 4, 10, color)
        if self.shot_cooldown == 0:
            pyxel.pset(self.x, self.y - 7, 7)


class AttackerMouse:
    """マウス座標は表示スケール時は画面ピクセルで返るため、ゲーム座標に変換する。"""

    def __init__(self):
        self.waves = []
        self.shot_cooldown = 0
        self.cooldown_time = 36

    @staticmethod
    def _mouse_game_coords():
        """Pyxelのマウスをゲーム座標(0..width-1, 0..height-1)に変換する。"""
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        w, h = pyxel.width, pyxel.height
        if mx >= w or my >= h:
            scale_x = max(1, (mx + w - 1) // w) if mx >= w else 1
            scale_y = max(1, (my + h - 1) // h) if my >= h else 1
            scale = max(scale_x, scale_y)
            mx = mx // scale
            my = my // scale
        return max(0, min(w - 1, mx)), max(0, min(h - 1, my))

    def update(self, target_x, target_y, safe_zone_radius):
        if self.shot_cooldown > 0:
            self.shot_cooldown -= 1
        mx, my = self._mouse_game_coords()
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.shot_cooldown == 0:
            mx_clamp = max(2, min(pyxel.width - 3, mx))
            my_clamp = max(2, min(pyxel.height - 3, my))
            dist_to_player = math.sqrt((mx_clamp - target_x) ** 2 + (my_clamp - target_y) ** 2)
            if dist_to_player >= safe_zone_radius:
                is_critical = random.random() < 0.12
                self.waves.append(Wave(mx_clamp, my_clamp, is_critical=is_critical))
                self.shot_cooldown = self.cooldown_time
        for w in self.waves:
            w.update()
        self.waves = [w for w in self.waves if w.alive]

    def draw(self):
        mx, my = self._mouse_game_coords()
        color = 7 if self.shot_cooldown == 0 else 2
        pyxel.line(mx - 4, my, mx + 4, my, color)
        pyxel.line(mx, my - 4, mx, my + 4, color)
        pyxel.pset(mx, my, color)


class Fighter:
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
        if pyxel.btn(k["down"]): self.y += self.speed
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


# --- メインアプリケーション ---

class App:
    def __init__(self):
        pyxel.init(160, 120, title="HaMon - All Modes")
        self.state = "MENU"
        self.selected_index = 0
        self.modes = [
            "MODE 1: VS CPU",
            "MODE 2: VS HUMAN",
            "MODE 3: CLICK ATTACK",
            "MODE 4: VERSUS",
        ]
        self.time_limit = 30 * 30
        self.time_limit_versus = 30 * 60
        self.safe_zone_radius = 28
        pyxel.run(self.update, self.draw)

    def reset(self, mode):
        self.mode_index = mode
        if mode == 0 or mode == 1:
            while True:
                p_x, p_y = random.randint(10, 150), random.randint(10, 110)
                a_x, a_y = random.randint(10, 150), random.randint(10, 110)
                if math.sqrt((p_x - a_x) ** 2 + (p_y - a_y) ** 2) > 60:
                    break
            self.player = Player(p_x, p_y)
            if mode == 0:
                self.attacker = AttackerAuto(a_x, a_y)
                self.game_type = "VS_CPU"
            else:
                self.attacker = AttackerHuman(a_x, a_y)
                self.game_type = "VS_HUMAN"
            self.attacker_waves = self.attacker.waves
            self.remaining_time = self.time_limit
        elif mode == 2:
            p_x, p_y = random.randint(10, 150), random.randint(10, 110)
            self.player = Player(p_x, p_y)
            self.attacker = AttackerMouse()
            self.attacker_waves = self.attacker.waves
            self.game_type = "CLICK"
            self.remaining_time = self.time_limit
        else:
            while True:
                p1_x, p1_y = random.randint(20, 70), random.randint(30, 90)
                p2_x, p2_y = random.randint(90, 140), random.randint(30, 90)
                if math.sqrt((p1_x - p2_x) ** 2 + (p1_y - p2_y) ** 2) > 50:
                    break
            self.p1 = Fighter(
                p1_x, p1_y, P1_KEYS,
                color_guard=10, color_idle=11, wave_color=7, wave_crit=8
            )
            self.p2 = Fighter(
                p2_x, p2_y, P2_KEYS,
                color_guard=12, color_idle=13, wave_color=4, wave_crit=2
            )
            self.game_type = "VERSUS"
            self.remaining_time = self.time_limit_versus
            self.winner = None

        self.start_frame = pyxel.frame_count
        self.game_state = "PLAYING"
        self.cause = ""

    def update(self):
        if self.state == "MENU":
            if pyxel.btnp(pyxel.KEY_UP):
                self.selected_index = (self.selected_index - 1) % 4
            if pyxel.btnp(pyxel.KEY_DOWN):
                self.selected_index = (self.selected_index + 1) % 4
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
                self.reset(self.selected_index)
                self.state = "GAME"
            return

        if self.state != "GAME":
            return

        if self.game_state != "PLAYING":
            if pyxel.btnp(pyxel.KEY_R):
                self.reset(self.mode_index)
            if pyxel.btnp(pyxel.KEY_M):
                self.state = "MENU"
            return

        if self.game_type == "VS_CPU" or self.game_type == "VS_HUMAN":
            self._update_vs_attacker()
        elif self.game_type == "CLICK":
            self._update_click()
        else:
            self._update_versus()

    def _update_vs_attacker(self):
        self.player.update()
        self.attacker.update(self.player.x, self.player.y)

        if not self.player.alive:
            self.game_state = "GAMEOVER"
            self.cause = "DON'T STOP!" if self.player.still_frames >= self.player.max_still_time else "RIPPLE HIT"
            return

        elapsed = pyxel.frame_count - self.start_frame
        self.remaining_time = max(0, self.time_limit - elapsed)
        if self.remaining_time <= 0:
            self.game_state = "WIN"
            return

        for w in self.attacker.waves:
            dist = math.sqrt((w.x - self.player.x) ** 2 + (w.y - self.player.y) ** 2)
            if abs(dist - w.rad) < 3:
                if self.player.is_guarding:
                    w.alive = False
                    self.player.gauge = min(
                        self.player.max_gauge,
                        self.player.gauge + (11 if self.game_type == "VS_CPU" else 15),
                    )
                else:
                    self.player.alive = False
                    self.game_state = "GAMEOVER"
                    self.cause = "RIPPLE HIT"

    def _update_click(self):
        self.player.update()
        self.attacker.update(self.player.x, self.player.y, self.safe_zone_radius)

        if not self.player.alive:
            self.game_state = "GAMEOVER"
            self.cause = "DON'T STOP!" if self.player.still_frames >= self.player.max_still_time else "RIPPLE HIT"
            return

        elapsed = pyxel.frame_count - self.start_frame
        self.remaining_time = max(0, self.time_limit - elapsed)
        if self.remaining_time <= 0:
            self.game_state = "WIN"
            return

        for w in self.attacker.waves:
            dist = math.sqrt((w.x - self.player.x) ** 2 + (w.y - self.player.y) ** 2)
            if abs(dist - w.rad) < 3:
                if self.player.is_guarding:
                    w.alive = False
                    if getattr(w, "is_critical", False):
                        self.player.guard_block_frames = 30
                        self.player.is_guarding = False
                    self.player.gauge = min(self.player.max_gauge, self.player.gauge + 14)
                else:
                    self.player.alive = False
                    self.game_state = "GAMEOVER"
                    self.cause = "RIPPLE HIT"

    def _update_versus(self):
        self.p1.update(self.p2.x, self.p2.y)
        self.p2.update(self.p1.x, self.p1.y)

        if not self.p1.alive:
            self.game_state = "GAMEOVER"
            self.winner = "P2"
        if not self.p2.alive:
            self.game_state = "GAMEOVER"
            self.winner = "P1"

        elapsed = pyxel.frame_count - self.start_frame
        self.remaining_time = max(0, self.time_limit_versus - elapsed)
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
            pyxel.text(25, 20, "HaMon", pyxel.frame_count % 16)
            pyxel.line(5, 32, 155, 32, 7)
            for i, m in enumerate(self.modes):
                color = 10 if i == self.selected_index else 7
                prefix = "> " if i == self.selected_index else "  "
                pyxel.text(10, 48 + i * 14, prefix + m, color)
            pyxel.text(15, 108, "ENTER: Start  R:Restart  M:Menu", 6)
            return

        if self.game_type == "VS_CPU" or self.game_type == "VS_HUMAN":
            self._draw_vs_attacker()
        elif self.game_type == "CLICK":
            self._draw_click()
        else:
            self._draw_versus()

    def _draw_vs_attacker(self):
        for i in range(0, 160, 20):
            pyxel.line(i, 0, i, 120, 1)
        for w in self.attacker.waves:
            w.draw()
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
            pyxel.text(60, 50, "GAME OVER", 8)
            pyxel.text(60, 60, self.cause, 7)
            pyxel.text(45, 75, "R:Restart / M:Menu", 6)
        elif self.game_state == "WIN":
            pyxel.text(65, 55, "YOU WIN!", 11)
            pyxel.text(45, 75, "R:Restart / M:Menu", 7)

    def _draw_click(self):
        for i in range(0, 160, 20):
            pyxel.line(i, 0, i, 120, 1)
        if self.player.alive:
            pyxel.circb(self.player.x, self.player.y, self.safe_zone_radius, 3)
        for w in self.attacker.waves:
            w.draw()
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
            pyxel.text(60, 50, "GAME OVER", 8)
            pyxel.text(60, 60, self.cause, 7)
            pyxel.text(45, 75, "R:Restart / M:Menu", 6)
        elif self.game_state == "WIN":
            pyxel.text(65, 55, "YOU WIN!", 11)
            pyxel.text(45, 75, "R:Restart / M:Menu", 7)

    def _draw_versus(self):
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
