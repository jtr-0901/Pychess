from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, BooleanProperty
import threading
import os

from ui.board import ChessBoardUI
from engine.ai import get_best_move
from database.history import save_game, get_all_games
from engine.chess_logic import GameLogic
import chess

class RoundedButton(ButtonBehavior, BoxLayout):
    def __init__(self, text="", icon_source="", btn_color=(0.2, 0.6, 0.2, 1), font_size=24, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.padding = [20, 10, 20, 10]
        self.spacing = 15
        self.btn_color = btn_color
        
        with self.canvas.before:
            Color(*self.btn_color)
            self.rect = RoundedRectangle(radius=[12])
            
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        if icon_source:
            icon = Image(source=icon_source, size_hint_x=None, width=40)
            self.add_widget(icon)
            
        lbl = Label(text=text, font_size=font_size, bold=True, halign='left', valign='middle')
        lbl.bind(size=lbl.setter('text_size'))
        self.add_widget(lbl)
        
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        
    def on_state(self, instance, value):
        self.canvas.before.clear()
        with self.canvas.before:
            if value == 'down':
                Color(self.btn_color[0]*0.8, self.btn_color[1]*0.8, self.btn_color[2]*0.8, self.btn_color[3])
            else:
                Color(*self.btn_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12])

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=25)
        
        assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
        
        logo = Image(source=os.path.join(assets_dir, 'logo.jpg'), size_hint_y=0.4, allow_stretch=True, keep_ratio=True)
        layout.add_widget(logo)
        
        btn_bot = RoundedButton(text="Play vs Bot", icon_source=os.path.join(assets_dir, 'icons', 'bot.png'), size_hint_y=0.15, btn_color=(0.18, 0.6, 0.35, 1))
        btn_bot.bind(on_press=self.go_difficulty)
        layout.add_widget(btn_bot)
        
        btn_pass = RoundedButton(text="Pass & Play", icon_source=os.path.join(assets_dir, 'icons', 'pass.png'), size_hint_y=0.15, btn_color=(0.2, 0.45, 0.7, 1))
        btn_pass.bind(on_press=self.go_time_selection)
        layout.add_widget(btn_pass)
        
        btn_hist = RoundedButton(text="Game History", icon_source=os.path.join(assets_dir, 'icons', 'history.png'), size_hint_y=0.15, btn_color=(0.7, 0.45, 0.2, 1))
        btn_hist.bind(on_press=self.go_history)
        layout.add_widget(btn_hist)
        
        self.add_widget(layout)
        
    def go_difficulty(self, instance):
        self.manager.current = 'difficulty'
        
    def go_time_selection(self, instance):
        self.manager.current = 'time_select'
        
    def go_history(self, instance):
        hist_screen = self.manager.get_screen('history')
        hist_screen.load_history()
        self.manager.current = 'history'


class TimeSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        title = Label(text="Select Match Type", font_size=40, bold=True, size_hint_y=0.3, color=(0.9, 0.9, 0.9, 1))
        layout.add_widget(title)
        
        modes = [
            ("Bullet (1 min)", "bullet.png", 60, (0.8, 0.2, 0.2, 1)),
            ("Blitz (3 min)", "blitz.png", 180, (0.8, 0.6, 0.1, 1)),
            ("Rapid (10 min)", "rapid.png", 600, (0.3, 0.7, 0.3, 1)),
            ("Classical (30 min)", "classical.png", 1800, (0.2, 0.45, 0.7, 1))
        ]
        
        assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
        
        for name, icon, time_limit, color in modes:
            btn = RoundedButton(text=name, icon_source=os.path.join(assets_dir, 'icons', icon), font_size=26, size_hint_y=0.15, btn_color=color)
            btn.bind(on_press=lambda inst, t=time_limit: self.start_pvp_game(t))
            layout.add_widget(btn)
            
        btn_back = RoundedButton(text="Back", icon_source=os.path.join(assets_dir, 'icons', 'back.png'), font_size=26, size_hint_y=0.15, btn_color=(0.4, 0.4, 0.4, 1))
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_back)
        
        self.add_widget(layout)

    def start_pvp_game(self, time_limit):
        game_screen = self.manager.get_screen('game')
        game_screen.setup_game(mode="PvP", time_limit=time_limit)
        self.manager.current = 'game'


class DifficultyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        title = Label(text="Select Difficulty", font_size=40, bold=True, size_hint_y=0.3, color=(0.9, 0.9, 0.9, 1))
        layout.add_widget(title)
        
        colors = [
            (0.3, 0.7, 0.3, 1), # Easy
            (0.8, 0.6, 0.1, 1), # Medium
            (0.8, 0.4, 0.1, 1), # Hard
            (0.8, 0.2, 0.2, 1)  # Expert
        ]
        
        for i, diff in enumerate(["Easy", "Medium", "Hard", "Expert"]):
            btn = RoundedButton(text=diff, font_size=26, size_hint_y=0.15, btn_color=colors[i])
            btn.bind(on_press=lambda inst, d=diff: self.start_bot_game(d))
            layout.add_widget(btn)
            
        assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
        btn_back = RoundedButton(text="Back", icon_source=os.path.join(assets_dir, 'icons', 'back.png'), font_size=26, size_hint_y=0.15, btn_color=(0.4, 0.4, 0.4, 1))
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_back)
        
        self.add_widget(layout)

    def start_bot_game(self, difficulty):
        game_screen = self.manager.get_screen('game')
        game_screen.setup_game(mode="PvB", difficulty=difficulty, time_limit=None)
        self.manager.current = 'game'


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        
        # Top bar
        self.top_bar = BoxLayout(size_hint_y=0.12, padding=15)
        self.status_label = Label(text="White's Turn", font_size=22, bold=True, color=(0.95, 0.95, 0.95, 1))
        self.top_bar.add_widget(self.status_label)
        
        self.timer_label = Label(text="", font_size=20, color=(1, 0.8, 0.2, 1), size_hint_x=0.4, halign='right')
        self.top_bar.add_widget(self.timer_label)
        self.layout.add_widget(self.top_bar)
        
        # Board area
        self.board_container = BoxLayout(size_hint_y=0.68)
        self.layout.add_widget(self.board_container)
        
        # Bottom bar
        self.bottom_bar = BoxLayout(size_hint_y=0.12, spacing=15, padding=15)
        btn_undo = RoundedButton(text="Undo", font_size=20, btn_color=(0.3, 0.3, 0.35, 1))
        btn_undo.bind(on_press=self.undo_move)
        self.bottom_bar.add_widget(btn_undo)
        
        btn_resign = RoundedButton(text="Resign", font_size=20, btn_color=(0.7, 0.25, 0.25, 1))
        btn_resign.bind(on_press=self.resign_game)
        self.bottom_bar.add_widget(btn_resign)
        
        self.layout.add_widget(self.bottom_bar)
        self.add_widget(self.layout)
        
        self.game_logic = GameLogic()
        self.board_ui = None
        self.difficulty = "Medium"
        
        self.time_limit = None
        self.white_time = 0
        self.black_time = 0
        self.timer_event = None
        
    def setup_game(self, mode, difficulty="Medium", time_limit=None):
        self.game_logic.reset_game()
        self.game_logic.mode = mode
        self.difficulty = difficulty
        self.time_limit = time_limit
        
        if self.time_limit:
            self.white_time = self.time_limit
            self.black_time = self.time_limit
            self.update_timer_label()
            if self.timer_event:
                self.timer_event.cancel()
            self.timer_event = Clock.schedule_interval(self.tick_timer, 1)
        else:
            self.timer_label.text = ""
            if self.timer_event:
                self.timer_event.cancel()
        
        self.board_container.clear_widgets()
        self.board_ui = ChessBoardUI(game_logic=self.game_logic, on_move_callback=self.on_move_made)
        self.board_container.add_widget(self.board_ui)
        self.update_status()

    def format_time(self, seconds):
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m:02d}:{s:02d}"

    def tick_timer(self, dt):
        if self.game_logic.is_game_over():
            return False
            
        if self.game_logic.board.turn == chess.WHITE:
            self.white_time -= 1
            if self.white_time <= 0:
                self.white_time = 0
                self.end_game(timeout="White")
                return False
        else:
            self.black_time -= 1
            if self.black_time <= 0:
                self.black_time = 0
                self.end_game(timeout="Black")
                return False
                
        self.update_timer_label()

    def update_timer_label(self):
        if not self.time_limit:
            return
        if self.game_logic.board.turn == chess.WHITE:
            self.timer_label.text = f"White: {self.format_time(self.white_time)}"
        else:
            self.timer_label.text = f"Black: {self.format_time(self.black_time)}"

    def on_move_made(self):
        self.update_status()
        self.update_timer_label()
        
        if self.game_logic.is_game_over():
            self.end_game()
            return
            
        if self.game_logic.mode == "PvB" and self.game_logic.board.turn == chess.BLACK:
            self.status_label.text = f"Bot ({self.difficulty}) is thinking..."
            self.status_label.color = (0.7, 0.7, 0.9, 1)
            # Use a thread for AI so it doesn't freeze the UI
            threading.Thread(target=self._run_ai_thread, daemon=True).start()

    def _run_ai_thread(self):
        move = get_best_move(self.game_logic.board, self.difficulty)
        Clock.schedule_once(lambda dt: self.board_ui.process_bot_move(move), 0)

    def update_status(self):
        if self.game_logic.is_game_over():
            return
        turn = "White's Turn" if self.game_logic.board.turn == chess.WHITE else "Black's Turn"
        check = " (Check!)" if self.game_logic.is_check() else ""
        self.status_label.text = turn + check
        self.status_label.color = (0.95, 0.95, 0.95, 1)

    def end_game(self, timeout=None):
        if self.timer_event:
            self.timer_event.cancel()
            
        res = self.game_logic.get_game_result()
        
        if timeout == "White":
            res = "0-1"
            msg = "Black wins! (Timeout)"
            self.status_label.color = (0.9, 0.3, 0.3, 1)
        elif timeout == "Black":
            res = "1-0"
            msg = "White wins! (Timeout)"
            self.status_label.color = (0.3, 0.9, 0.3, 1)
        else:
            if res == "1-0":
                msg = "White wins!"
                self.status_label.color = (0.3, 0.9, 0.3, 1)
            elif res == "0-1":
                msg = "Black wins!"
                self.status_label.color = (0.9, 0.3, 0.3, 1)
            else:
                msg = "Draw!"
                self.status_label.color = (0.7, 0.7, 0.7, 1)
                
            if self.game_logic.is_checkmate():
                msg += " (Checkmate)"
            
        self.status_label.text = "Game Over! " + msg
        
        # Save game
        pgn = self.game_logic.get_pgn()
        save_game("Player 1", "Bot" if self.game_logic.mode == "PvB" else "Player 2", res, pgn)

    def undo_move(self, instance):
        if self.game_logic.is_game_over():
            return
        self.game_logic.undo_move()
        self.board_ui.selected_square = None
        self.board_ui.legal_moves_for_selected = []
        self.board_ui.draw_board()
        self.update_status()
        self.update_timer_label()

    def resign_game(self, instance):
        if self.timer_event:
            self.timer_event.cancel()
            
        if not self.game_logic.is_game_over():
            res = "0-1" if self.game_logic.board.turn == chess.WHITE else "1-0"
            pgn = self.game_logic.get_pgn()
            save_game("Player 1", "Bot" if self.game_logic.mode == "PvB" else "Player 2", res, pgn)
        self.manager.current = 'menu'


class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        
        self.title = Label(text="Game History", font_size=35, bold=True, size_hint_y=0.15)
        self.layout.add_widget(self.title)
        
        self.scroll = ScrollView(size_hint_y=0.7)
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=15)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        self.layout.add_widget(self.scroll)
        
        assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
        btn_back = RoundedButton(text="Back", icon_source=os.path.join(assets_dir, 'icons', 'back.png'), font_size=24, size_hint_y=0.15, btn_color=(0.4, 0.4, 0.4, 1))
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        self.layout.add_widget(btn_back)
        
        self.add_widget(self.layout)

    def load_history(self):
        self.grid.clear_widgets()
        games = get_all_games()
        if not games:
            self.grid.add_widget(Label(text="No games played yet.", font_size=20, size_hint_y=None, height=50))
            return
            
        for g in games:
            res_color = "🟢" if g['result'] == "1-0" else ("🔴" if g['result'] == "0-1" else "⚪")
            text = f"{res_color} {g['white']} vs {g['black']}\n[size=14]{g['timestamp']}[/size]"
            btn = RoundedButton(text=text, size_hint_y=None, height=80, font_size=16, btn_color=(0.15, 0.16, 0.2, 1))
            # Button properties are not perfectly aligned with Markup Label natively inside our RoundedButton but we can try
            btn.children[0].markup = True # Because lbl is the first child added, wait, add_widget puts new children at index 0. 
            self.grid.add_widget(btn)
