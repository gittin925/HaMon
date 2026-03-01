import pyxel
import HaMon_PVP
import HaMon_Auto

# ここではHaMon.pyとHaMon_Auto.pyのAppクラスが、
# それぞれ HamonApp, HamonAutoApp という名前でインポートできる、
# あるいは同ファイル内に定義されていると想定しています。

class Menu:
    def __init__(self):
        # 初期化（すでに他でpyxel.initされている場合は不要ですが、単体起動用に記述）
        pyxel.init(160, 120, title="HaMon - Select Mode")
        
        self.selected_index = 0
        self.modes = ["1 PLAYER (VS CPU)", "2 PLAYERS (VS HUMAN)"]
        self.state = "MENU" # "MENU" or "GAME"
        
        pyxel.run(self.update, self.draw)

    def update(self):
        if self.state == "MENU":
            # 上下キーで選択
            if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_W):
                self.selected_index = (self.selected_index - 1) % len(self.modes)
            if pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.KEY_S):
                self.selected_index = (self.selected_index + 1) % len(self.modes)
            
            # EnterまたはSpaceで決定
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
                self.start_game()

    def start_game(self):
        # 既存のAppを呼び出す際、pyxel.runが重複しないよう注意が必要です。
        # 以下は、各モードのApp(クラス名)をインスタンス化する例です。
        if self.selected_index == 0:
            print("一人モードを起動します")
            HaMon_Auto.App() # 実装済みのAppクラスを呼び出す
        else:
            print("二人モードを起動します")
            HaMon_PVP.App() # 実装済みのAppクラスを呼び出す
        
        # 注意：Pyxelの仕様上、pyxel.runは一度しか呼べないため、
        # 実際にはAppクラスの中で「状態(state)」を切り替えて描画内容を変えるのが一般的です。

    def draw(self):
        pyxel.cls(0)
        
        # タイトル表示
        pyxel.text(65, 30, "Ha Mon", pyxel.frame_count % 16)
        pyxel.line(40, 40, 120, 40, 7)
        
        # メニュー項目表示
        for i, mode in enumerate(self.modes):
            color = 7
            prefix = ""
            if i == self.selected_index:
                color = 10 # 選択中の色は黄色/緑系
                prefix = "> "
            
            pyxel.text(45, 60 + i * 15, prefix + mode, color)
        
        pyxel.text(35, 100, "PRESS ENTER TO START", 5)

# 実行
if __name__ == "__main__":
    Menu()