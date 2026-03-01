"""
HaMon - マウスクリック攻撃版
アタッカーはWASDではなくマウス位置＋左クリックで波を発射する。
"""
import pyxel
import math
import random

# --- 共通クラス ---

class Wave:
    def __init__(self, x, y, is_critical=False):
        self.x, self.y = x, y
        self.rad = 0
        self.speed = 1.5
        self.alive = True
        self.is_critical = is_critical

    def update(self):
        self.rad += self.speed
        if self.rad > 200:
            self.alive = False

    def draw(self):
        if self.alive:
            color = 8 if self.is_critical else 7
            pyxel.circb(self.x, self.y, self.rad, color)


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
        self.guard_block_frames = 0  # 0でない間はガード不可（クリティカル対策後）

    def update(self):
        if not self.alive:
            return
        moved = False
        if pyxel.btn(pyxel.KEY_LEFT): self.x -= self.speed; moved = True
        if pyxel.btn(pyxel.KEY_RIGHT): self.x += self.speed; moved = True
        if pyxel.btn(pyxel.KEY_UP): self.y -= self.speed; moved = True
        if pyxel.btn(pyxel.KEY_DOWN): self.y += self.speed; moved = True

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


# --- 敵クラス（マウス操作） ---

class AttackerMouse:
    """マウス位置が攻撃起点。左クリックで波を発射。"""

    def __init__(self):
        self.waves = []
        self.shot_cooldown = 0
        self.cooldown_time = 36  # 攻撃頻度を下げる（約1.2秒に1回）

    def update(self, target_x, target_y, safe_zone_radius):
        if self.shot_cooldown > 0:
            self.shot_cooldown -= 1

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.shot_cooldown == 0:
            mx = max(2, min(pyxel.width - 3, pyxel.mouse_x))
            my = max(2, min(pyxel.height - 3, pyxel.mouse_y))
            dist_to_player = math.sqrt((mx - target_x) ** 2 + (my - target_y) ** 2)
            if dist_to_player >= safe_zone_radius:
                is_critical = random.random() < 0.12  # 12%でクリティカル
                self.waves.append(Wave(mx, my, is_critical=is_critical))
                self.shot_cooldown = self.cooldown_time

        for w in self.waves:
            w.update()
        self.waves = [w for w in self.waves if w.alive]

    def draw(self):
        mx = max(0, min(pyxel.width, pyxel.mouse_x))
        my = max(0, min(pyxel.height, pyxel.mouse_y))
        color = 7 if self.shot_cooldown == 0 else 2
        pyxel.line(mx - 4, my, mx + 4, my, color)
        pyxel.line(mx, my - 4, mx, my + 4, color)
        pyxel.pset(mx, my, color)


# --- メインアプリケーション ---

class App:
    def __init__(self):
        pyxel.init(160, 120, title="HaMon - Click Attack")
        self.state = "MENU"
        self.selected_index = 0
        self.modes = ["1 PLAYER [ CLICK ATTACK ]"]
        self.time_limit = 30 * 30
        self.safe_zone_radius = 28  # プレイヤー中心の禁止円の半径
        pyxel.run(self.update, self.draw)

    def reset(self):
        p_x = random.randint(10, 150)
        p_y = random.randint(10, 110)
        self.player = Player(p_x, p_y)
        self.attacker = AttackerMouse()
        self.start_frame = pyxel.frame_count
        self.game_state = "PLAYING"
        self.cause = ""
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

            self.player.update()
            self.attacker.update(self.player.x, self.player.y, self.safe_zone_radius)

            if not self.player.alive:
                self.game_state = "GAMEOVER"
                self.cause = (
                    "DON'T STOP!"
                    if self.player.still_frames >= self.player.max_still_time
                    else "RIPPLE HIT"
                )

            elapsed = pyxel.frame_count - self.start_frame
            self.remaining_time = max(0, self.time_limit - elapsed)
            if self.remaining_time <= 0:
                self.game_state = "WIN"

            for w in self.attacker.waves:
                dist = math.sqrt((w.x - self.player.x) ** 2 + (w.y - self.player.y) ** 2)
                if abs(dist - w.rad) < 3:
                    if self.player.is_guarding:
                        w.alive = False
                        if w.is_critical:
                            self.player.guard_block_frames = 30 * 1.5  # 1.5秒間ガード不可
                            self.player.is_guarding = False  # 即時ガード解除
                        self.player.gauge = min(
                            self.player.max_gauge, self.player.gauge + 14
                        )
                    else:
                        self.player.alive = False
                        self.game_state = "GAMEOVER"
                        self.cause = "RIPPLE HIT"

    def draw(self):
        pyxel.cls(0)
        if self.state == "MENU":
            pyxel.text(55, 30, "HaMon Click", pyxel.frame_count % 16)
            pyxel.line(40, 42, 120, 42, 7)
            color = 10
            pyxel.text(35, 65, "> " + self.modes[0], color)
            pyxel.text(25, 90, "CLICK: Attack  ENTER: Start", 6)

        elif self.state == "GAME":
            for i in range(0, 160, 20):
                pyxel.line(i, 0, i, 120, 1)
            if self.player.alive:
                pyxel.circb(
                    self.player.x, self.player.y,
                    self.safe_zone_radius, 3
                )
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


App()
