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
        if self.rad > 200:
            self.alive = False

    def draw(self):
        # ガード成功で消える演出のため、aliveチェック
        if self.alive:
            pyxel.circb(self.x, self.y, self.rad, 7)

class Attacker:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.speed = 1.5
        self.waves = []
    
    def update(self):
        # 移動 (WASD)
        if pyxel.btn(pyxel.KEY_A): self.x -= self.speed
        if pyxel.btn(pyxel.KEY_D): self.x += self.speed
        if pyxel.btn(pyxel.KEY_W): self.y -= self.speed
        if pyxel.btn(pyxel.KEY_S): self.y += self.speed
        
        # 攻撃 (SPACE) - 30フレームに1回制限（連射防止）
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.waves.append(Wave(self.x, self.y))
            
        for w in self.waves:
            w.update()
        self.waves = [w for w in self.waves if w.alive]

    def draw(self):
        pyxel.rect(self.x - 2, self.y - 5, 4, 10, 8)

class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.speed = 2
        self.alive = True
        self.gauge = 100    # 最大100
        self.max_gauge = 100
        self.is_guarding = False
    
    def update(self):
        if not self.alive: return
        
        # 移動
        if pyxel.btn(pyxel.KEY_LEFT): self.x -= self.speed
        if pyxel.btn(pyxel.KEY_RIGHT): self.x += self.speed
        if pyxel.btn(pyxel.KEY_UP): self.y -= self.speed
        if pyxel.btn(pyxel.KEY_DOWN): self.y += self.speed

        # ガード (Shiftキー または Zキー)
        # ゲージがある時だけガード可能
        if (pyxel.btn(pyxel.KEY_SHIFT) or pyxel.btn(pyxel.KEY_Z)) and self.gauge > 0:
            self.is_guarding = True
            self.gauge -= 0.5  # ガード中はゲージを消費
        else:
            self.is_guarding = False

    def draw(self):
        if self.alive:
            # ガード中は円が表示される
            color = 10 if self.is_guarding else 11
            pyxel.rect(self.x - 2, self.y - 2, 5, 5, color)
            if self.is_guarding:
                pyxel.circb(self.x, self.y, 6, 10)

class App:
    def __init__(self):
        pyxel.init(160, 120, title="HaMon - Guard & Survive")
        self.time_limit = 30 * 30 # 30秒 (30fps * 30)
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.player = Player(80, 80)
        self.attacker = Attacker(80, 20)
        self.start_frame = pyxel.frame_count
        self.state = "PLAYING" # "PLAYING", "GAMEOVER", "WIN"

    def update(self):
        if self.state != "PLAYING":
            if pyxel.btnp(pyxel.KEY_R): self.reset()
            return

        self.player.update()
        self.attacker.update()

        # 残り時間の更新
        elapsed = pyxel.frame_count - self.start_frame
        self.remaining_time = max(0, self.time_limit - elapsed)
        if self.remaining_time <= 0:
            self.state = "WIN"

        # 当たり判定
        for w in self.attacker.waves:
            dist = math.sqrt((w.x - self.player.x)**2 + (w.y - self.player.y)**2)
            
            if abs(dist - w.rad) < 3: # 波紋に触れた
                if self.player.is_guarding:
                    # ガード成功！
                    w.alive = False # 波紋を消す
                    self.player.gauge = min(self.player.max_gauge, self.player.gauge + 20)
                    pyxel.play(3, 0) # 成功音（デフォルト音色）
                else:
                    # ガード失敗
                    self.player.alive = False
                    self.state = "GAMEOVER"

    def draw(self):
        pyxel.cls(0)
        
        # 背景（グリッド）
        for i in range(0, 160, 20):
            pyxel.line(i, 0, i, 120, 1)
        
        # キャラクタと波紋
        for w in self.attacker.waves: w.draw()
        self.attacker.draw()
        self.player.draw()
        
        # UI: ゲージの描画
        pyxel.text(5, 5, "GAUGE", 7)
        pyxel.rect(30, 5, self.player.max_gauge // 2, 4, 13) # 背景
        pyxel.rect(30, 5, self.player.gauge // 2, 4, 10)     # 現在値
        
        # UI: タイマー
        timer_text = f"TIME: {self.remaining_time // 30}"
        pyxel.text(120, 5, timer_text, 7)

        # 状態表示
        if self.state == "GAMEOVER":
            pyxel.text(60, 55, "GAME OVER", 8)
            pyxel.text(50, 65, "Press R to Restart", 7)
        elif self.state == "WIN":
            pyxel.text(65, 55, "YOU WIN!", 11)
            pyxel.text(50, 65, "Press R to Restart", 7)

App()